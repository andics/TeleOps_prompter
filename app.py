"""
Main Flask Application for Camera Feed Monitor with AI Vision Filters
"""
import os
import sys
import base64
import json
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
print("[APP] Starting Camera Feed Monitor", flush=True)
print(f"[APP] Current time: {datetime.now()}", flush=True)
print(f"[APP] Working directory: {os.getcwd()}", flush=True)
print("=" * 80, flush=True)

app = Flask(__name__)
CORS(app)

# Global state
camera_capture = None
openai_handler = None
filter_manager = None

# Get CAPTURE_INTERVAL from environment - this controls EVERYTHING:
# - How often camera captures a frame
# - How often GPT is called
# - How often UI should poll
CAPTURE_INTERVAL = float(os.environ.get("CAPTURE_INTERVAL", "3.0"))

print(f"[APP] CAPTURE_INTERVAL set to: {CAPTURE_INTERVAL} seconds", flush=True)
print(f"[APP] This interval controls: camera capture, GPT evaluation, and UI polling", flush=True)

# Thread pool for non-blocking API calls
executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)


class FilterManager:
    """Manages filters and their evaluation"""
    
    def __init__(self, openai_handler):
        print("[FilterManager] INITIALIZING", flush=True)
        self.filters = []
        self.results = {}
        self.openai_handler = openai_handler
        self.lock = threading.Lock()
        self.pending_evaluations = {}  # Track which filters are being evaluated
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
            print(f"[FilterManager] Total filters: {len(self.filters)}", flush=True)
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
            print(f"[FilterManager] Filter removed. Total: {len(self.filters)}", flush=True)
    
    def move_filter(self, filter_id, direction):
        """Move filter up (-1) or down (1)"""
        print(f"[FilterManager] move_filter: {filter_id}, direction: {direction}", flush=True)
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
        print(f"[FilterManager] toggle_filter: {filter_id}", flush=True)
        with self.lock:
            for f in self.filters:
                if f["id"] == filter_id:
                    f["is_active"] = not f["is_active"]
                    print(f"[FilterManager] Filter {filter_id} is_active now: {f['is_active']}", flush=True)
                    break
    
    def _reorder(self):
        """Update order values"""
        for i, f in enumerate(self.filters):
            f["order"] = i
    
    def _evaluate_single_filter(self, filter_obj, image_path, log_folder):
        """Evaluate a single filter - runs in background thread"""
        filter_id = filter_obj["id"]
        print(f"[FilterManager] _evaluate_single_filter STARTED for {filter_id}", flush=True)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Mark as evaluating
        with self.lock:
            self.results[filter_id] = {
                "response": "Evaluating...",
                "timestamp": current_time,
                "status": "evaluating"
            }
        
        # Make the API call (this is the slow part)
        result = self.openai_handler.evaluate_image(
            image_path, 
            filter_obj["prompt"],
            log_folder=log_folder,
            filter_id=filter_id
        )
        
        print(f"[FilterManager] _evaluate_single_filter COMPLETED for {filter_id}: {result}", flush=True)
        
        # Store result
        with self.lock:
            self.results[filter_id] = {
                "response": result,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "completed"
            }
            if filter_id in self.pending_evaluations:
                del self.pending_evaluations[filter_id]
    
    def evaluate_filters_async(self, image_path, log_folder=None):
        """Evaluate all active filters ASYNCHRONOUSLY - does not block"""
        print("=" * 60, flush=True)
        print(f"[FilterManager] evaluate_filters_async CALLED", flush=True)
        print(f"[FilterManager] image_path: {image_path}", flush=True)
        print(f"[FilterManager] log_folder: {log_folder}", flush=True)
        
        if not image_path:
            print("[FilterManager] ERROR: image_path is None/empty", flush=True)
            return
        
        if not os.path.exists(image_path):
            print(f"[FilterManager] ERROR: image file does not exist: {image_path}", flush=True)
            return
        
        with self.lock:
            active_filters = [f for f in self.filters if f["is_active"]]
            print(f"[FilterManager] Total filters: {len(self.filters)}", flush=True)
            print(f"[FilterManager] Active filters: {len(active_filters)}", flush=True)
        
        if len(active_filters) == 0:
            print("[FilterManager] No active filters to evaluate", flush=True)
            print("=" * 60, flush=True)
            return
        
        # Submit each filter evaluation to the thread pool (NON-BLOCKING)
        for filter_obj in active_filters:
            filter_id = filter_obj["id"]
            
            # Skip if already being evaluated
            with self.lock:
                if filter_id in self.pending_evaluations:
                    print(f"[FilterManager] Filter {filter_id} already being evaluated, skipping", flush=True)
                    continue
                self.pending_evaluations[filter_id] = True
            
            print(f"[FilterManager] Submitting filter {filter_id} to thread pool", flush=True)
            
            # Submit to thread pool - this returns immediately
            executor.submit(
                self._evaluate_single_filter,
                filter_obj,
                image_path,
                log_folder
            )
        
        print(f"[FilterManager] All filters submitted to thread pool (non-blocking)", flush=True)
        print("=" * 60, flush=True)
    
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


# Initialize components
def initialize_app():
    """Initialize camera capture and OpenAI handler"""
    global camera_capture, openai_handler, filter_manager
    
    print("=" * 80, flush=True)
    print("[initialize_app] STARTING INITIALIZATION", flush=True)
    
    # Get OpenAI API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    print(f"[initialize_app] OPENAI_API_KEY from env: {'SET (' + api_key[:8] + '...)' if api_key else 'NOT SET'}", flush=True)
    
    if not api_key:
        print("[initialize_app] WARNING: OPENAI_API_KEY not set in environment variables", flush=True)
        print("[initialize_app] Please set it in .env file or as an environment variable", flush=True)
    
    # Get camera configuration from environment or use defaults
    camera_url = os.environ.get("CAMERA_URL", "http://10.0.0.197:8080/cam_c")
    
    print(f"[initialize_app] CAMERA_URL: {camera_url}", flush=True)
    print(f"[initialize_app] CAPTURE_INTERVAL: {CAPTURE_INTERVAL} seconds (used for camera, GPT, and UI)", flush=True)
    
    print("[initialize_app] Creating CameraCapture...", flush=True)
    camera_capture = CameraCapture(
        camera_url=camera_url,
        capture_interval=CAPTURE_INTERVAL  # Use the same interval
    )
    print(f"[initialize_app] CameraCapture created: {camera_capture}", flush=True)
    print(f"[initialize_app] CameraCapture base_folder: {camera_capture.base_folder}", flush=True)
    
    print("[initialize_app] Creating OpenAIHandler...", flush=True)
    openai_handler = OpenAIHandler(api_key=api_key)
    print(f"[initialize_app] OpenAIHandler created: {openai_handler}", flush=True)
    print(f"[initialize_app] OpenAIHandler.client: {openai_handler.client}", flush=True)
    
    print("[initialize_app] Creating FilterManager...", flush=True)
    filter_manager = FilterManager(openai_handler)
    print(f"[initialize_app] FilterManager created: {filter_manager}", flush=True)
    
    # Start camera capture in background thread
    print("[initialize_app] Starting camera capture...", flush=True)
    camera_capture.start()
    print("[initialize_app] Camera capture started", flush=True)
    
    # Start filter evaluation loop (runs every CAPTURE_INTERVAL seconds)
    print("[initialize_app] Starting filter evaluation loop thread...", flush=True)
    eval_thread = threading.Thread(target=filter_evaluation_loop, daemon=True)
    eval_thread.start()
    print(f"[initialize_app] Filter evaluation thread started: {eval_thread}", flush=True)
    
    print(f"[initialize_app] Filter evaluation will run every {CAPTURE_INTERVAL} seconds", flush=True)
    print("=" * 80, flush=True)


def filter_evaluation_loop():
    """Background loop to trigger filter evaluations every CAPTURE_INTERVAL seconds"""
    global camera_capture, filter_manager
    
    print("[filter_evaluation_loop] THREAD STARTED", flush=True)
    print(f"[filter_evaluation_loop] Will run every {CAPTURE_INTERVAL} seconds", flush=True)
    
    loop_count = 0
    
    while True:
        loop_count += 1
        print("", flush=True)
        print("*" * 60, flush=True)
        print(f"[filter_evaluation_loop] LOOP #{loop_count} at {datetime.now()}", flush=True)
        
        latest_frame = camera_capture.get_latest_frame()
        print(f"[filter_evaluation_loop] latest_frame: {latest_frame}", flush=True)
        
        if latest_frame and os.path.exists(latest_frame):
            log_folder = str(camera_capture.base_folder) if camera_capture.base_folder else None
            print(f"[filter_evaluation_loop] log_folder: {log_folder}", flush=True)
            
            # This call is NON-BLOCKING - it submits to thread pool and returns immediately
            filter_manager.evaluate_filters_async(latest_frame, log_folder=log_folder)
            
            print(f"[filter_evaluation_loop] Async evaluation triggered (non-blocking)", flush=True)
        else:
            print(f"[filter_evaluation_loop] No valid frame available", flush=True)
        
        print(f"[filter_evaluation_loop] Sleeping for {CAPTURE_INTERVAL} seconds...", flush=True)
        print("*" * 60, flush=True)
        
        time.sleep(CAPTURE_INTERVAL)


# Routes
@app.route('/')
def index():
    """Serve the main page"""
    print("[ROUTE /] Serving index.html", flush=True)
    return render_template('index.html')


@app.route('/api/config')
def get_config():
    """Return the capture interval so the UI knows how often to poll"""
    return jsonify({
        "success": True,
        "capture_interval": CAPTURE_INTERVAL
    })


@app.route('/api/latest-frame')
def get_latest_frame():
    """Get the latest captured frame"""
    if camera_capture:
        frame_path = camera_capture.get_latest_frame()
        
        if frame_path and os.path.exists(frame_path):
            with open(frame_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
            
            mod_time = os.path.getmtime(frame_path)
            
            return jsonify({
                "success": True,
                "image": f"data:image/jpeg;base64,{img_data}",
                "path": frame_path,
                "timestamp": mod_time
            })
        else:
            return jsonify({"success": False, "error": f"Frame path invalid or missing: {frame_path}"})
    
    return jsonify({"success": False, "error": "Camera capture not initialized"})


@app.route('/api/filters', methods=['GET'])
def get_filters():
    """Get all filters with their results"""
    filters_data = filter_manager.get_filters_with_results()
    return jsonify({
        "success": True,
        "filters": filters_data
    })


@app.route('/api/filters', methods=['POST'])
def add_filter():
    """Add a new filter"""
    data = request.json
    prompt = data.get('prompt', '')
    
    print(f"[ROUTE /api/filters POST] Adding filter with prompt: {prompt}", flush=True)
    
    if not prompt:
        return jsonify({"success": False, "error": "Prompt is required"}), 400
    
    new_filter = filter_manager.add_filter(prompt, is_active=True)
    print(f"[ROUTE /api/filters POST] Filter added: {new_filter['id']}", flush=True)
    return jsonify({"success": True, "filter": new_filter})


@app.route('/api/filters/<filter_id>', methods=['DELETE'])
def delete_filter(filter_id):
    """Remove a filter"""
    print(f"[ROUTE /api/filters DELETE] Removing filter: {filter_id}", flush=True)
    filter_manager.remove_filter(filter_id)
    return jsonify({"success": True})


@app.route('/api/filters/<filter_id>/move', methods=['POST'])
def move_filter(filter_id):
    """Move filter up or down"""
    data = request.json
    direction = data.get('direction', 0)
    print(f"[ROUTE /api/filters/move] Moving filter {filter_id} direction {direction}", flush=True)
    
    filter_manager.move_filter(filter_id, direction)
    return jsonify({"success": True})


@app.route('/api/filters/<filter_id>/toggle', methods=['POST'])
def toggle_filter(filter_id):
    """Toggle filter active state"""
    print(f"[ROUTE /api/filters/toggle] Toggling filter: {filter_id}", flush=True)
    filter_manager.toggle_filter(filter_id)
    return jsonify({"success": True})


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages (can be used for general queries)"""
    data = request.json
    message = data.get('message', '')
    print(f"[ROUTE /api/chat] Message: {message}", flush=True)
    
    return jsonify({
        "success": True,
        "response": "Chat functionality ready for extension"
    })


if __name__ == '__main__':
    print("[MAIN] Starting Flask application...", flush=True)
    initialize_app()
    print("[MAIN] Running Flask server on 0.0.0.0:5000", flush=True)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
