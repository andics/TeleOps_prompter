"""
Camera Capture Module - With verbose logging
"""
import os
import time
import threading
import queue
from datetime import datetime
from pathlib import Path
import requests
from PIL import Image
from io import BytesIO
import cv2


def cam_log(cam_id, msg, log_folder=None):
    """Log with camera prefix to console and file"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [CAM_{cam_id}] {msg}"
    print(line, flush=True)
    
    if log_folder:
        try:
            with open(os.path.join(log_folder, "teleops.log"), "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except:
            pass


class BufferlessVideoCapture:
    """Wrapper that always returns the LATEST frame (drains buffer)"""
    
    def __init__(self, source, cam_id="", log_folder=None):
        self.cam_id = cam_id
        self.log_folder = log_folder
        cam_log(cam_id, f"Opening video stream: {source}", log_folder)
        
        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.running = True
        self.last_frame = None
        self.frame_count = 0
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._reader, daemon=True)
        self.thread.start()
        
        cam_log(cam_id, f"Buffer reader thread started", log_folder)
    
    def _reader(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.last_frame = frame
                    self.frame_count += 1
                
                # Log every 50 frames
                if self.frame_count % 50 == 0:
                    cam_log(self.cam_id, f"Buffer drained {self.frame_count} frames", self.log_folder)
            else:
                time.sleep(0.1)
    
    def read(self):
        with self.lock:
            if self.last_frame is not None:
                return True, self.last_frame.copy()
        return False, None
    
    def isOpened(self):
        return self.cap.isOpened()
    
    def release(self):
        cam_log(self.cam_id, "Releasing video capture", self.log_folder)
        self.running = False
        self.cap.release()


class CameraCapture:
    def __init__(self, camera_url, capture_interval=1.0, camera_id="", shared_folder=None):
        self.camera_id = camera_id
        self.camera_url = camera_url
        self.capture_interval = capture_interval
        self.is_running = False
        self.capture_thread = None
        self.latest_frame_path = None
        self.lock = threading.Lock()
        self.use_opencv = False
        self.video_capture = None
        self.frame_count = 0
        
        # Use shared folder or create own
        if shared_folder:
            self.base_folder = Path(shared_folder)
            self.log_folder = shared_folder
        else:
            self.base_folder = Path(f"cam_{camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            self.log_folder = str(self.base_folder)
        self.base_folder.mkdir(exist_ok=True)
        
        cam_log(camera_id, f"Initialized", self.log_folder)
        cam_log(camera_id, f"  URL: {camera_url}", self.log_folder)
        cam_log(camera_id, f"  Interval: {capture_interval}s", self.log_folder)
        cam_log(camera_id, f"  Folder: {self.base_folder}", self.log_folder)
    
    def start(self):
        if self.is_running:
            cam_log(self.camera_id, "Already running", self.log_folder)
            return
        
        self.is_running = True
        self._detect_camera_type()
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        cam_log(self.camera_id, f"Capture thread started (using {'OpenCV' if self.use_opencv else 'HTTP'})", self.log_folder)
    
    def stop(self):
        cam_log(self.camera_id, "Stopping...", self.log_folder)
        self.is_running = False
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        cam_log(self.camera_id, "Stopped", self.log_folder)
    
    def _detect_camera_type(self):
        cam_log(self.camera_id, f"Detecting camera type for: {self.camera_url}", self.log_folder)
        try:
            r = requests.get(self.camera_url, timeout=2, stream=True)
            ct = r.headers.get('Content-Type', '').lower()
            r.close()
            
            cam_log(self.camera_id, f"Content-Type: {ct}", self.log_folder)
            
            if 'multipart' in ct or 'mjpeg' in ct or 'video' in ct:
                self.use_opencv = True
                cam_log(self.camera_id, "Detected: MJPEG/Video stream -> using OpenCV", self.log_folder)
            else:
                self.use_opencv = False
                cam_log(self.camera_id, "Detected: Snapshot URL -> using HTTP", self.log_folder)
        except Exception as e:
            self.use_opencv = True
            cam_log(self.camera_id, f"Detection failed ({e}), defaulting to OpenCV", self.log_folder)
    
    def _capture_loop(self):
        cam_log(self.camera_id, "Capture loop starting...", self.log_folder)
        if self.use_opencv:
            self._opencv_loop()
        else:
            self._http_loop()
        cam_log(self.camera_id, "Capture loop ended", self.log_folder)
    
    def _http_loop(self):
        cam_log(self.camera_id, "HTTP capture loop running", self.log_folder)
        
        while self.is_running:
            try:
                r = requests.get(self.camera_url, timeout=5, headers={'Connection': 'close'})
                ct = r.headers.get('Content-Type', '')
                
                if r.status_code == 200 and 'image' in ct:
                    img = Image.open(BytesIO(r.content))
                    self._save_frame(img)
                else:
                    cam_log(self.camera_id, f"Bad response: status={r.status_code}, type={ct}", self.log_folder)
                    
            except Exception as e:
                cam_log(self.camera_id, f"HTTP error: {e}", self.log_folder)
            
            time.sleep(self.capture_interval)
    
    def _opencv_loop(self):
        cam_log(self.camera_id, "OpenCV capture loop running", self.log_folder)
        
        self.video_capture = BufferlessVideoCapture(self.camera_url, self.camera_id, self.log_folder)
        
        if not self.video_capture.isOpened():
            cam_log(self.camera_id, "ERROR: Failed to open video stream!", self.log_folder)
            return
        
        cam_log(self.camera_id, "Video stream opened successfully", self.log_folder)
        time.sleep(0.5)  # Wait for first frame
        
        while self.is_running:
            ret, frame = self.video_capture.read()
            if ret and frame is not None:
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                self._save_frame(img)
            else:
                cam_log(self.camera_id, "No frame available", self.log_folder)
            
            time.sleep(self.capture_interval)
    
    def _save_frame(self, img):
        self.frame_count += 1
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"cam_{self.camera_id}_{ts}.jpg"
        filepath = self.base_folder / filename
        img.save(filepath, "JPEG", quality=95)
        
        with self.lock:
            self.latest_frame_path = str(filepath)
        
        # Log every 10th frame to avoid spam
        if self.frame_count % 10 == 0:
            cam_log(self.camera_id, f"Saved frame #{self.frame_count}: {filename} ({img.size[0]}x{img.size[1]})", self.log_folder)
    
    def get_latest_frame(self):
        with self.lock:
            return self.latest_frame_path
