"""
Main Flask Application for TeleOps - Camera Feed Monitor with AI Vision Filters
"""
import os
import sys
import base64
import json
import re
import traceback
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import threading
import time
from dotenv import load_dotenv
import concurrent.futures

from camera_capture import CameraCapture
from openai_handler import OpenAIHandler

# Force unbuffered output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)

# Load environment variables from .env file
load_dotenv()

print("=" * 80, flush=True)
print("[APP] Starting TeleOps Camera Feed Monitor", flush=True)
print(f"[APP] Current time: {datetime.now()}", flush=True)
print(f"[APP] Working directory: {os.getcwd()}", flush=True)
print("=" * 80, flush=True)

app = Flask(__name__)
CORS(app)

# Global state
camera_captures = {}  # Dictionary to hold all camera captures
openai_handler = None
filter_manager = None

# Activity log for the UI
activity_log = []
activity_log_lock = threading.Lock()

# Prompt suffix to append to the FIRST SENTENCE of all filter prompts
PROMPT_SUFFIX = ' Answer only using "True" if the answer is "Yes" and "False" if the answer is "No".'

# Get CAPTURE_INTERVAL from environment
CAPTURE_INTERVAL = float(os.environ.get("CAPTURE_INTERVAL", "3.0"))

# Camera URLs
CAMERA_BASE_URL = os.environ.get("CAMERA_BASE_URL", "http://10.0.0.197:8080")
CAMERA_URLS = {
    "A": f"{CAMERA_BASE_URL}/cam_a",
    "B": f"{CAMERA_BASE_URL}/cam_b",
    "C": f"{CAMERA_BASE_URL}/cam_c",  # Primary camera for AI analysis
}

print(f"[APP] CAPTURE_INTERVAL set to: {CAPTURE_INTERVAL} seconds", flush=True)
print(f"[APP] Camera URLs: {CAMERA_URLS}", flush=True)

# Thread pool for non-blocking API calls
executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)


def extract_first_sentence(text):
    """
    Extract the first sentence from a prompt.
    A sentence ends with . or ? or !
    Returns the first sentence (including the punctuation).
    """
    text = text.strip()
    
    # Find the first sentence-ending punctuation
    match = re.search(r'^(.*?[.?!])(?:\s|$)', text)
    
    if match:
        return match.group(1).strip()
    else:
        return text


def add_log(message, log_type="info"):
    """Add a message to the activity log"""
    with activity_log_lock:
        timestamp = datetime.now().strftime("%H:%M:%S")
        activity_log.append({
            "message": message,
            "type": log_type,
            "timestamp": timestamp
        })
        # Keep only last 100 messages
        if len(activity_log) > 100:
            activity_log.pop(0)
    
    type_colors = {
        "info": "[INFO]",
        "success": "[SUCCESS]",
        "error": "[ERROR]",
        "warning": "[WARNING]",
        "vlm": "[VLM]",
        "camera": "[CAMERA]",
        "filter": "[FILTER]"
    }
    prefix = type_colors.get(log_type, "[LOG]")
    print(f"{prefix} {timestamp} - {message}", flush=True)


class FilterManager:
    """Manages filters and their evaluation"""
    
    def __init__(self, openai_handler):
        print("[FilterManager] INITIALIZING", flush=True)
        self.filters = []
        self.results = {}
        self.openai_handler = openai_handler
        self.lock = threading.Lock()
        self.pending_evaluations = {}
        print(f"[FilterManager] OpenAI handler: {openai_handler}", flush=True)
        print("[FilterManager] INITIALIZED", flush=True)
    
    def add_filter(self, prompt, is_active=True):
        """Add a new filter"""
        print(f"[FilterManager] add_filter called with prompt: {prompt}", flush=True)
        with self.lock:
            filter_id = f"filter_{int(time.time() * 1000)}"
            new_filter = {
                "id": filter_id,
                "prompt": prompt,
                "is_active": is_active,
                "order": len(self.filters)
            }
            self.filters.append(new_filter)
            self.results[filter_id] = {"response": None, "timestamp": None, "status": "pending"}
            print(f"[FilterManager] Filter added: {filter_id}", flush=True)
            add_log(f"Filter added: {prompt[:50]}{'...' if len(prompt) > 50 else ''}", "filter")
            return new_filter
    
    def remove_filter(self, filter_id):
        """Remove a filter by ID"""
        print(f"[FilterManager] remove_filter called: {filter_id}", flush=True)
        with self.lock:
            self.filters = [f for f in self.filters if f["id"] != filter_id]
            if filter_id in self.results:
                del self.results[filter_id]
            if filter_id in self.pending_evaluations:
                del self.pending_evaluations[filter_id]
            self._reorder()
            add_log(f"Filter removed: {filter_id}", "filter")
    
    def move_filter(self, filter_id, direction):
        """Move filter up (-1) or down (1)"""
        with self.lock:
            for i, f in enumerate(self.filters):
                if f["id"] == filter_id:
                    new_index = i + direction
                    if 0 <= new_index < len(self.filters):
                        self.filters[i], self.filters[new_index] = self.filters[new_index], self.filters[i]
                    break
            self._reorder()
    
    def toggle_filter(self, filter_id):
        """Toggle filter active state"""
        with self.lock:
            for f in self.filters:
                if f["id"] == filter_id:
                    f["is_active"] = not f["is_active"]
                    status = "enabled" if f["is_active"] else "disabled"
                    add_log(f"Filter {status}: {f['prompt'][:30]}...", "filter")
                    break
    
    def _reorder(self):
        """Update order values"""
        for i, f in enumerate(self.filters):
            f["order"] = i
    
    def _evaluate_single_filter(self, filter_obj, image_path, log_folder):
        """Evaluate a single filter - runs in background thread"""
        filter_id = filter_obj["id"]
        full_prompt = filter_obj["prompt"]
        
        first_sentence = extract_first_sentence(full_prompt)
        vlm_prompt = first_sentence + PROMPT_SUFFIX
        
        print(f"[FilterManager] Evaluating filter {filter_id}", flush=True)
        print(f"[FilterManager] Full prompt (display): {full_prompt}", flush=True)
        print(f"[FilterManager] First sentence extracted: {first_sentence}", flush=True)
        print(f"[FilterManager] VLM prompt being sent: {vlm_prompt}", flush=True)
        
        add_log(f"Sending to VLM: {vlm_prompt}", "vlm")
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with self.lock:
            self.results[filter_id] = {
                "response": "Evaluating...",
                "timestamp": current_time,
                "status": "evaluating"
            }
        
        result = self.openai_handler.evaluate_image(
            image_path, 
            vlm_prompt,
            log_folder=log_folder,
            filter_id=filter_id
        )
        
        print(f"[FilterManager] Result for {filter_id}: {result}", flush=True)
        
        if result:
            add_log(f"VLM response: {result}", "success")
        else:
            add_log(f"VLM returned no response", "error")
        
        with self.lock:
            self.results[filter_id] = {
                "response": result,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "completed"
            }
            if filter_id in self.pending_evaluations:
                del self.pending_evaluations[filter_id]
    
    def evaluate_filters_async(self, image_path, log_folder=None):
        """Evaluate all active filters ASYNCHRONOUSLY"""
        if not image_path or not os.path.exists(image_path):
            return
        
        with self.lock:
            active_filters = [f for f in self.filters if f["is_active"]]
        
        if len(active_filters) == 0:
            return
        
        add_log(f"Evaluating {len(active_filters)} filter(s) on Camera C", "camera")
        
        for filter_obj in active_filters:
            filter_id = filter_obj["id"]
            
            with self.lock:
                if filter_id in self.pending_evaluations:
                    continue
                self.pending_evaluations[filter_id] = True
            
            executor.submit(
                self._evaluate_single_filter,
                filter_obj,
                image_path,
                log_folder
            )
    
    def get_filters_with_results(self):
        """Get all filters with their current results"""
        with self.lock:
            return [
                {
                    **f,
                    "result": self.results.get(f["id"], {}).get("response"),
                    "timestamp": self.results.get(f["id"], {}).get("timestamp"),
                    "status": self.results.get(f["id"], {}).get("status", "pending")
                }
                for f in self.filters
            ]


def initialize_app():
    """Initialize camera captures and OpenAI handler"""
    global camera_captures, openai_handler, filter_manager
    
    add_log("TeleOps initializing...", "info")
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        add_log("OpenAI API key loaded", "success")
    else:
        add_log("OpenAI API key NOT SET!", "error")
    
    # Initialize all three cameras
    for cam_id, cam_url in CAMERA_URLS.items():
        add_log(f"Camera {cam_id}: {cam_url}", "camera")
        camera_captures[cam_id] = CameraCapture(
            camera_url=cam_url,
            capture_interval=CAPTURE_INTERVAL,
            camera_id=cam_id
        )
    
    add_log(f"Capture interval: {CAPTURE_INTERVAL}s", "info")
    
    openai_handler = OpenAIHandler(api_key=api_key)
    filter_manager = FilterManager(openai_handler)
    
    # Start all camera captures
    for cam_id, capture in camera_captures.items():
        capture.start()
        add_log(f"Camera {cam_id} capture started", "camera")
    
    eval_thread = threading.Thread(target=filter_evaluation_loop, daemon=True)
    eval_thread.start()
    
    add_log("TeleOps ready!", "success")


def filter_evaluation_loop():
    """Background loop to trigger filter evaluations using Camera C only"""
    global camera_captures, filter_manager
    
    while True:
        # Only use Camera C for AI analysis
        camera_c = camera_captures.get("C")
        if camera_c:
            latest_frame = camera_c.get_latest_frame()
            
            if latest_frame and os.path.exists(latest_frame):
                log_folder = str(camera_c.base_folder) if camera_c.base_folder else None
                filter_manager.evaluate_filters_async(latest_frame, log_folder=log_folder)
        
        time.sleep(CAPTURE_INTERVAL)


# Routes
@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/config')
def get_config():
    """Return the capture interval"""
    return jsonify({
        "success": True,
        "capture_interval": CAPTURE_INTERVAL
    })


@app.route('/api/latest-frame/<camera_id>')
def get_latest_frame(camera_id):
    """Get the latest captured frame for a specific camera"""
    camera_id = camera_id.upper()
    
    if camera_id not in camera_captures:
        return jsonify({"success": False, "error": f"Unknown camera: {camera_id}"})
    
    capture = camera_captures[camera_id]
    frame_path = capture.get_latest_frame()
    
    if frame_path and os.path.exists(frame_path):
        with open(frame_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
        
        mod_time = os.path.getmtime(frame_path)
        
        return jsonify({
            "success": True,
            "image": f"data:image/jpeg;base64,{img_data}",
            "path": frame_path,
            "timestamp": mod_time,
            "camera": camera_id
        })
    else:
        return jsonify({"success": False, "error": f"Frame not available for Camera {camera_id}"})


@app.route('/api/filters', methods=['GET'])
def get_filters():
    """Get all filters with their results"""
    return jsonify({
        "success": True,
        "filters": filter_manager.get_filters_with_results()
    })


@app.route('/api/filters', methods=['POST'])
def add_filter():
    """Add a new filter"""
    data = request.json
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({"success": False, "error": "Prompt is required"}), 400
    
    new_filter = filter_manager.add_filter(prompt, is_active=True)
    return jsonify({"success": True, "filter": new_filter})


@app.route('/api/filters/<filter_id>', methods=['DELETE'])
def delete_filter(filter_id):
    """Remove a filter"""
    filter_manager.remove_filter(filter_id)
    return jsonify({"success": True})


@app.route('/api/filters/<filter_id>/move', methods=['POST'])
def move_filter(filter_id):
    """Move filter up or down"""
    data = request.json
    direction = data.get('direction', 0)
    filter_manager.move_filter(filter_id, direction)
    return jsonify({"success": True})


@app.route('/api/filters/<filter_id>/toggle', methods=['POST'])
def toggle_filter(filter_id):
    """Toggle filter active state"""
    filter_manager.toggle_filter(filter_id)
    return jsonify({"success": True})


@app.route('/api/logs')
def get_logs():
    """Get activity logs"""
    with activity_log_lock:
        return jsonify({
            "success": True,
            "logs": list(activity_log)
        })


@app.route('/api/status')
def get_status():
    """Get combined status of all filters - True only if ALL active filters are False"""
    filters_with_results = filter_manager.get_filters_with_results()
    
    # If no filters exist, return False
    if not filters_with_results:
        return jsonify({"result": False, "reason": "No filters configured"})
    
    # Check only active filters
    active_filters = [f for f in filters_with_results if f.get('is_active', True)]
    
    if not active_filters:
        return jsonify({"result": False, "reason": "No active filters"})
    
    # Check if all active filters have "False" response
    all_false = True
    for f in active_filters:
        response = f.get('result', {}).get('response')
        if response is None:
            return jsonify({"result": False, "reason": f"Filter '{f.get('prompt', '')[:30]}...' not yet evaluated"})
        if response.strip().lower() != "false":
            all_false = False
            break
    
    return jsonify({"result": all_false})


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.json
    message = data.get('message', '')
    add_log(f"User: {message}", "info")
    return jsonify({
        "success": True,
        "response": "Message logged"
    })


if __name__ == '__main__':
    print("[MAIN] Starting TeleOps...", flush=True)
    initialize_app()
    print("[MAIN] Running Flask server on 0.0.0.0:5000", flush=True)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
