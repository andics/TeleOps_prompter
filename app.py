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
filters = []
filter_results = {}
latest_frame_path = None

# Evaluation interval in seconds
EVALUATION_INTERVAL = 3.0

print(f"[APP] Evaluation interval set to: {EVALUATION_INTERVAL} seconds", flush=True)


class FilterManager:
    """Manages filters and their evaluation"""
    
    def __init__(self, openai_handler):
        print("[FilterManager] INITIALIZING", flush=True)
        self.filters = []
        self.results = {}
        self.openai_handler = openai_handler
        self.lock = threading.Lock()
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
            self.results[filter_id] = {"response": None, "timestamp": None}
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
    
    def evaluate_filters(self, image_path, log_folder=None):
        """Evaluate all active filters against the latest image"""
        print("=" * 60, flush=True)
        print(f"[FilterManager] evaluate_filters CALLED", flush=True)
        print(f"[FilterManager] image_path: {image_path}", flush=True)
        print(f"[FilterManager] log_folder: {log_folder}", flush=True)
        
        if not image_path:
            print("[FilterManager] ERROR: image_path is None/empty", flush=True)
            return
        
        print(f"[FilterManager] os.path.exists(image_path): {os.path.exists(image_path)}", flush=True)
        
        if not os.path.exists(image_path):
            print(f"[FilterManager] ERROR: image file does not exist: {image_path}", flush=True)
            return
        
        with self.lock:
            active_filters = [f for f in self.filters if f["is_active"]]
            print(f"[FilterManager] Total filters: {len(self.filters)}", flush=True)
            print(f"[FilterManager] Active filters: {len(active_filters)}", flush=True)
            for f in active_filters:
                print(f"[FilterManager]   - {f['id']}: {f['prompt'][:50]}...", flush=True)
        
        if len(active_filters) == 0:
            print("[FilterManager] No active filters to evaluate", flush=True)
            print("=" * 60, flush=True)
            return
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for filter_obj in active_filters:
            print("-" * 40, flush=True)
            print(f"[FilterManager] Evaluating filter: {filter_obj['id']}", flush=True)
            print(f"[FilterManager] Prompt: {filter_obj['prompt']}", flush=True)
            print(f"[FilterManager] Calling openai_handler.evaluate_image()...", flush=True)
            
            # NO TRY/EXCEPT - let errors propagate
            result = self.openai_handler.evaluate_image(
                image_path, 
                filter_obj["prompt"],
                log_folder=log_folder,
                filter_id=filter_obj["id"]
            )
            
            print(f"[FilterManager] RESULT RECEIVED: {result}", flush=True)
            
            with self.lock:
                self.results[filter_obj["id"]] = {
                    "response": result,
                    "timestamp": current_time
                }
                print(f"[FilterManager] Result stored for {filter_obj['id']}", flush=True)
        
        print("=" * 60, flush=True)
    
    def get_filters_with_results(self):
        """Get all filters with their current results"""
        with self.lock:
            return [
                {
                    **f,
                    "result": self.results.get(f["id"], {}).get("response"),
                    "timestamp": self.results.get(f["id"], {}).get("timestamp")
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
    capture_interval = float(os.environ.get("CAPTURE_INTERVAL", "1.0"))
    
    print(f"[initialize_app] CAMERA_URL: {camera_url}", flush=True)
    print(f"[initialize_app] CAPTURE_INTERVAL: {capture_interval}", flush=True)
    
    print("[initialize_app] Creating CameraCapture...", flush=True)
    camera_capture = CameraCapture(
        camera_url=camera_url,
        capture_interval=capture_interval
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
    
    # Start filter evaluation loop (runs every 3 seconds)
    print("[initialize_app] Starting filter evaluation loop thread...", flush=True)
    eval_thread = threading.Thread(target=filter_evaluation_loop, daemon=True)
    eval_thread.start()
    print(f"[initialize_app] Filter evaluation thread started: {eval_thread}", flush=True)
    
    print(f"[initialize_app] Filter evaluation will run every {EVALUATION_INTERVAL} seconds", flush=True)
    print("=" * 80, flush=True)


def filter_evaluation_loop():
    """Background loop to evaluate filters on new frames every 3 seconds"""
    global camera_capture, filter_manager
    
    print("[filter_evaluation_loop] THREAD STARTED", flush=True)
    
    loop_count = 0
    
    while True:
        loop_count += 1
        print("", flush=True)
        print("*" * 60, flush=True)
        print(f"[filter_evaluation_loop] LOOP #{loop_count}", flush=True)
        print(f"[filter_evaluation_loop] Time: {datetime.now()}", flush=True)
        
        print(f"[filter_evaluation_loop] camera_capture: {camera_capture}", flush=True)
        print(f"[filter_evaluation_loop] filter_manager: {filter_manager}", flush=True)
        
        latest_frame = camera_capture.get_latest_frame()
        print(f"[filter_evaluation_loop] latest_frame: {latest_frame}", flush=True)
        
        if latest_frame:
            print(f"[filter_evaluation_loop] os.path.exists(latest_frame): {os.path.exists(latest_frame)}", flush=True)
        
        if latest_frame and os.path.exists(latest_frame):
            # Get the log folder from the camera capture's base folder
            log_folder = str(camera_capture.base_folder) if camera_capture.base_folder else None
            
            print(f"[filter_evaluation_loop] log_folder: {log_folder}", flush=True)
            print(f"[filter_evaluation_loop] Calling filter_manager.evaluate_filters()...", flush=True)
            
            # NO TRY/EXCEPT - let errors propagate and crash if needed
            filter_manager.evaluate_filters(latest_frame, log_folder=log_folder)
            
            print(f"[filter_evaluation_loop] evaluate_filters() completed", flush=True)
        else:
            print(f"[filter_evaluation_loop] No valid frame available, skipping evaluation", flush=True)
        
        print(f"[filter_evaluation_loop] Sleeping for {EVALUATION_INTERVAL} seconds...", flush=True)
        print("*" * 60, flush=True)
        
        time.sleep(EVALUATION_INTERVAL)


# Routes
@app.route('/')
def index():
    """Serve the main page"""
    print("[ROUTE /] Serving index.html", flush=True)
    return render_template('index.html')


@app.route('/api/latest-frame')
def get_latest_frame():
    """Get the latest captured frame"""
    print(f"[ROUTE /api/latest-frame] Called", flush=True)
    
    if camera_capture:
        frame_path = camera_capture.get_latest_frame()
        print(f"[ROUTE /api/latest-frame] frame_path: {frame_path}", flush=True)
        
        if frame_path and os.path.exists(frame_path):
            with open(frame_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
            
            mod_time = os.path.getmtime(frame_path)
            
            print(f"[ROUTE /api/latest-frame] Success, image size: {len(img_data)} chars", flush=True)
            
            return jsonify({
                "success": True,
                "image": f"data:image/jpeg;base64,{img_data}",
                "path": frame_path,
                "timestamp": mod_time
            })
        else:
            print(f"[ROUTE /api/latest-frame] Frame not available", flush=True)
            return jsonify({"success": False, "error": f"Frame path invalid or missing: {frame_path}"})
    
    print("[ROUTE /api/latest-frame] Camera capture not initialized", flush=True)
    return jsonify({"success": False, "error": "Camera capture not initialized"})


@app.route('/api/filters', methods=['GET'])
def get_filters():
    """Get all filters with their results"""
    filters_data = filter_manager.get_filters_with_results()
    print(f"[ROUTE /api/filters GET] Returning {len(filters_data)} filters", flush=True)
    for f in filters_data:
        print(f"[ROUTE /api/filters GET]   - {f['id']}: result={f.get('result')}", flush=True)
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
    app.run(host='0.0.0.0', port=5000, debug=False)
