"""
Main Flask Application for TeleOps - Camera Feed Monitor with AI Vision Filters
"""
import os
import sys
import base64
import re
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import threading
import time
from dotenv import load_dotenv
import concurrent.futures

# Force unbuffered output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)

# Load environment variables
load_dotenv()

# Create shared folder for ALL images and logs
SHARED_FOLDER = Path(f"teleops_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
SHARED_FOLDER.mkdir(exist_ok=True)
LOG_FILE = open(SHARED_FOLDER / "teleops.log", "a", encoding="utf-8", buffering=1)

# Activity log for UI (initialized early so add_log works)
activity_log = []
activity_log_lock = threading.Lock()


def log(msg):
    """Log to console AND file only (not UI)"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    LOG_FILE.write(line + "\n")
    LOG_FILE.flush()


def add_log(message, log_type="info"):
    """Add to UI activity log AND console/file"""
    with activity_log_lock:
        ts = datetime.now().strftime("%H:%M:%S")
        activity_log.append({"message": message, "type": log_type, "timestamp": ts})
        if len(activity_log) > 100:
            activity_log.pop(0)
    log(f"[{log_type.upper()}] {message}")


add_log("=== TeleOps Starting ===", "info")
add_log(f"Log folder: {SHARED_FOLDER.absolute()}", "info")

# Now import modules
from camera_capture import CameraCapture
from openai_handler import OpenAIHandler

app = Flask(__name__)
CORS(app)

# Config from env 
CAPTURE_INTERVAL = float(os.environ.get("CAPTURE_INTERVAL", "3.0"))
FILTER_INTERVAL = float(os.environ.get("FILTER_INTERVAL", "5.0"))
CAMERA_BASE_URL = os.environ.get("CAMERA_BASE_URL", "http://10.0.0.197:8080")

CAMERA_URLS = {
    "A": f"{CAMERA_BASE_URL}/cam_a",
    "B": f"{CAMERA_BASE_URL}/cam_b",
    "C": f"{CAMERA_BASE_URL}/cam_c",
}

add_log(f"Capture interval: {CAPTURE_INTERVAL}s", "info")
add_log(f"Filter interval: {FILTER_INTERVAL}s", "info")
add_log(f"Camera base URL: {CAMERA_BASE_URL}", "info")

# Global state
camera_captures = {}
openai_handler = None
filter_manager = None
camera_enabled = {"A": True, "B": True, "C": True}
camera_order = ["A", "B", "C"]
vlm_camera = "C"
camera_state_lock = threading.Lock()

# Thread pool
executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

PROMPT_SUFFIX = ' Answer only using "True" if the answer is "No" and "False" if the answer is "Yes".'


def extract_first_sentence(text):
    text = text.strip()
    match = re.search(r'^(.*?[.?!])(?:\s|$)', text)
    return match.group(1).strip() if match else text


class FilterManager:
    def __init__(self, vlm_handler):
        self.filters = []
        self.results = {}
        self.vlm_handler = vlm_handler
        self.lock = threading.Lock()
        self.pending = {}
        add_log("Filter Manager initialized", "success")
    
    def add_filter(self, prompt, is_active=True):
        with self.lock:
            fid = f"filter_{int(time.time() * 1000)}"
            f = {"id": fid, "prompt": prompt, "is_active": is_active, "order": len(self.filters)}
            self.filters.append(f)
            self.results[fid] = {"response": None, "timestamp": None, "status": "pending"}
            add_log(f"Filter added: '{prompt[:50]}{'...' if len(prompt) > 50 else ''}'", "filter")
            return f
    
    def remove_filter(self, fid):
        with self.lock:
            for f in self.filters:
                if f["id"] == fid:
                    add_log(f"Filter removed: '{f['prompt'][:30]}...'", "filter")
                    break
            self.filters = [f for f in self.filters if f["id"] != fid]
            self.results.pop(fid, None)
            self.pending.pop(fid, None)
            self._reorder()
    
    def move_filter(self, fid, direction):
        with self.lock:
            for i, f in enumerate(self.filters):
                if f["id"] == fid:
                    new_i = i + direction
                    if 0 <= new_i < len(self.filters):
                        self.filters[i], self.filters[new_i] = self.filters[new_i], self.filters[i]
                        add_log(f"Filter moved {'up' if direction < 0 else 'down'}", "filter")
                    break
            self._reorder()
    
    def toggle_filter(self, fid):
        with self.lock:
            for f in self.filters:
                if f["id"] == fid:
                    f["is_active"] = not f["is_active"]
                    status = "enabled" if f["is_active"] else "disabled"
                    add_log(f"Filter {status}: '{f['prompt'][:30]}...'", "filter")
                    break
    
    def _reorder(self):
        for i, f in enumerate(self.filters):
            f["order"] = i
    
    def _evaluate_single(self, fobj, img_path):
        fid = fobj["id"]
        full_prompt = fobj["prompt"]
        first_sentence = extract_first_sentence(full_prompt)
        vlm_prompt = first_sentence + PROMPT_SUFFIX
        
        add_log(f"Sending to VLM: '{first_sentence[:40]}...'", "vlm")
        log(f"[VLM] Full VLM prompt: {vlm_prompt}")
        log(f"[VLM] Image path: {img_path}")
        
        with self.lock:
            self.results[fid] = {"response": "Evaluating...", "timestamp": datetime.now().strftime("%H:%M:%S"), "status": "evaluating"}
        
        try:
            result = self.vlm_handler.evaluate_image(img_path, vlm_prompt, str(SHARED_FOLDER), fid)
            
            add_log(f"VLM Response: '{result}'", "success")
            log(f"[VLM] Raw result for {fid}: {result}")
            log(f"[VLM] Result type: {type(result)}")
            
            with self.lock:
                self.results[fid] = {"response": result, "timestamp": datetime.now().strftime("%H:%M:%S"), "status": "completed"}
                self.pending.pop(fid, None)
                
        except Exception as e:
            add_log(f"VLM Error: {str(e)}", "error")
            log(f"[VLM] Exception: {e}")
            with self.lock:
                self.results[fid] = {"response": f"Error: {e}", "timestamp": datetime.now().strftime("%H:%M:%S"), "status": "error"}
                self.pending.pop(fid, None)
    
    def evaluate_async(self, img_path):
        if not img_path or not os.path.exists(img_path):
            log(f"[VLM] Skipping evaluation - no valid image path")
            return
        
        with self.lock:
            active = [f for f in self.filters if f["is_active"]]
        
        if not active:
            return
        
        log(f"[VLM] Starting evaluation of {len(active)} active filter(s)")
        add_log(f"Evaluating {len(active)} filter(s) on image...", "vlm")
        
        for f in active:
            fid = f["id"]
            with self.lock:
                if fid in self.pending:
                    log(f"[VLM] Filter {fid} already pending, skipping")
                    continue
                self.pending[fid] = True
            executor.submit(self._evaluate_single, f, img_path)
    
    def get_filters_with_results(self):
        with self.lock:
            return [{
                **f,
                "result": self.results.get(f["id"], {}).get("response"),
                "timestamp": self.results.get(f["id"], {}).get("timestamp"),
                "status": self.results.get(f["id"], {}).get("status", "pending")
            } for f in self.filters]


def initialize_app():
    global camera_captures, openai_handler, filter_manager
    
    add_log("Initializing system...", "info")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        add_log(f"VLM API key found: {api_key[:8]}...{api_key[-4:]}", "success")
    else:
        add_log("WARNING: VLM API key NOT SET!", "error")
    
    # Init cameras with shared folder
    for cam_id, url in CAMERA_URLS.items():
        add_log(f"Initializing Camera {cam_id}: {url}", "camera")
        camera_captures[cam_id] = CameraCapture(url, CAPTURE_INTERVAL, cam_id, str(SHARED_FOLDER))
    
    openai_handler = OpenAIHandler(api_key)
    filter_manager = FilterManager(openai_handler)
    
    # Start cameras
    for cam_id, cap in camera_captures.items():
        cap.start()
        add_log(f"Camera {cam_id} capture started", "camera")
    
    # Start filter loop
    threading.Thread(target=filter_loop, daemon=True).start()
    add_log("Filter evaluation loop started", "success")
    
    add_log(f"VLM active on Camera {vlm_camera}", "vlm")
    add_log("=== TeleOps Ready! ===", "success")


def filter_loop():
    global vlm_camera
    loop_count = 0
    
    while True:
        loop_count += 1
        
        with camera_state_lock:
            cam_id = vlm_camera
        
        cam = camera_captures.get(cam_id)
        if cam:
            frame = cam.get_latest_frame()
            if frame and os.path.exists(frame):
                log(f"[LOOP #{loop_count}] Processing frame from Camera {cam_id}: {os.path.basename(frame)}")
                filter_manager.evaluate_async(frame)
            else:
                log(f"[LOOP #{loop_count}] No frame available from Camera {cam_id}")
        
        time.sleep(FILTER_INTERVAL)


# === ROUTES ===

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/config')
def get_config():
    with camera_state_lock:
        return jsonify({
            "success": True,
            "capture_interval": CAPTURE_INTERVAL,
            "filter_interval": FILTER_INTERVAL,
            "cameras_enabled": dict(camera_enabled),
            "cameras_order": list(camera_order),
            "vlm_camera": vlm_camera
        })


@app.route('/api/camera/<cam_id>/toggle', methods=['POST'])
def toggle_camera(cam_id):
    cam_id = cam_id.upper()
    if cam_id not in CAMERA_URLS:
        return jsonify({"success": False, "error": "Unknown camera"})
    with camera_state_lock:
        camera_enabled[cam_id] = not camera_enabled[cam_id]
        status = "enabled" if camera_enabled[cam_id] else "disabled"
        add_log(f"Camera {cam_id} {status}", "camera")
        return jsonify({"success": True, "enabled": camera_enabled[cam_id]})


@app.route('/api/camera/<cam_id>/move', methods=['POST'])
def move_camera(cam_id):
    global camera_order
    cam_id = cam_id.upper()
    direction = request.json.get('direction', 0)
    with camera_state_lock:
        if cam_id in camera_order:
            idx = camera_order.index(cam_id)
            new_idx = idx + direction
            if 0 <= new_idx < len(camera_order):
                camera_order[idx], camera_order[new_idx] = camera_order[new_idx], camera_order[idx]
                add_log(f"Camera {cam_id} moved {'up' if direction < 0 else 'down'}", "camera")
        return jsonify({"success": True, "order": list(camera_order)})


@app.route('/api/vlm-camera', methods=['POST'])
def set_vlm_camera():
    global vlm_camera
    new_cam = request.json.get('camera', '').upper()
    if new_cam not in CAMERA_URLS:
        return jsonify({"success": False, "error": "Unknown camera"})
    with camera_state_lock:
        old_cam = vlm_camera
        vlm_camera = new_cam
    add_log(f"VLM switched from Camera {old_cam} to Camera {new_cam}", "vlm")
    return jsonify({"success": True, "vlm_camera": new_cam})


@app.route('/api/latest-frame/<cam_id>')
def get_latest_frame(cam_id):
    cam_id = cam_id.upper()
    if cam_id not in camera_captures:
        return jsonify({"success": False, "error": "Unknown camera"})
    
    with camera_state_lock:
        if not camera_enabled.get(cam_id, True):
            return jsonify({"success": False, "disabled": True})
    
    cap = camera_captures[cam_id]
    frame = cap.get_latest_frame()
    
    if frame and os.path.exists(frame):
        with open(frame, 'rb') as f:
            img = base64.b64encode(f.read()).decode('utf-8')
        return jsonify({
            "success": True,
            "image": f"data:image/jpeg;base64,{img}",
            "path": frame,
            "timestamp": os.path.getmtime(frame)
        })
    return jsonify({"success": False, "error": "No frame"})


@app.route('/api/filters', methods=['GET'])
def get_filters():
    return jsonify({"success": True, "filters": filter_manager.get_filters_with_results()})


@app.route('/api/filters', methods=['POST'])
def add_filter_route():
    prompt = request.json.get('prompt', '')
    if not prompt:
        return jsonify({"success": False, "error": "Prompt required"}), 400
    f = filter_manager.add_filter(prompt)
    return jsonify({"success": True, "filter": f})


@app.route('/api/filters/<fid>', methods=['DELETE'])
def delete_filter(fid):
    filter_manager.remove_filter(fid)
    return jsonify({"success": True})


@app.route('/api/filters/<fid>/move', methods=['POST'])
def move_filter(fid):
    direction = request.json.get('direction', 0)
    filter_manager.move_filter(fid, direction)
    return jsonify({"success": True})


@app.route('/api/filters/<fid>/toggle', methods=['POST'])
def toggle_filter(fid):
    filter_manager.toggle_filter(fid)
    return jsonify({"success": True})


@app.route('/api/logs')
def get_logs():
    with activity_log_lock:
        return jsonify({"success": True, "logs": list(activity_log)})


@app.route('/api/status')
def get_status():
    """
    Returns True ONLY if ALL active filters have VLM response containing "false".
    Returns False otherwise.
    """
    filters = filter_manager.get_filters_with_results()
    active = [f for f in filters if f.get('is_active') == True]
    
    log(f"")
    log(f"{'='*60}")
    log(f"[STATUS] API Status Check")
    log(f"[STATUS] Total filters: {len(filters)}, Active: {len(active)}")
    
    add_log(f"Status check: {len(active)} active filter(s)", "info")
    
    if not active:
        log("[STATUS] No active filters -> returning FALSE")
        add_log("Status: No active filters", "warning")
        return jsonify({"result": False, "reason": "No active filters"})
    
    all_contain_false = True
    
    for i, f in enumerate(active):
        resp = f.get('result')
        prompt_preview = f.get('prompt', '')[:30]
        
        log(f"[STATUS] Filter #{i+1}: '{prompt_preview}...'")
        log(f"[STATUS]   Response: '{resp}'")
        log(f"[STATUS]   Type: {type(resp)}")
        
        if resp is None:
            log(f"[STATUS]   -> NONE (not evaluated) -> FALSE")
            add_log(f"Status: Filter not yet evaluated", "warning")
            return jsonify({"result": False, "reason": "Filter not evaluated"})
        
        if resp == "Evaluating...":
            log(f"[STATUS]   -> Still evaluating -> FALSE")
            add_log(f"Status: Filter still evaluating", "warning")
            return jsonify({"result": False, "reason": "Filter evaluating"})
        
        resp_lower = str(resp).lower()
        has_false = "false" in resp_lower
        has_true = "true" in resp_lower
        
        log(f"[STATUS]   Lowercase: '{resp_lower}'")
        log(f"[STATUS]   Contains 'false': {has_false}")
        log(f"[STATUS]   Contains 'true': {has_true}")
        
        if has_false:
            log(f"[STATUS]   -> PASS (contains 'false')")
        else:
            log(f"[STATUS]   -> FAIL (does NOT contain 'false')")
            all_contain_false = False
    
    log(f"[STATUS] Final: all_contain_false = {all_contain_false}")
    
    if all_contain_false:
        log(f"[STATUS] RETURNING: TRUE")
        add_log("Status API: TRUE (all filters show 'False')", "success")
        return jsonify({"result": True})
    else:
        log(f"[STATUS] RETURNING: FALSE")
        add_log("Status API: FALSE (some filters don't show 'False')", "warning")
        return jsonify({"result": False})


@app.route('/api/chat', methods=['POST'])
def chat():
    msg = request.json.get('message', '')
    add_log(f"User message: {msg}", "info")
    return jsonify({"success": True})


if __name__ == '__main__':
    print("[MAIN] Starting TeleOps...", flush=True)
    initialize_app()
    print("[MAIN] Running Flask server on 0.0.0.0:5000", flush=True)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
