"""
Camera Capture Module
Captures frames from a camera feed at regular intervals
Supports both snapshot URLs and MJPEG video streams

IMPORTANT: For video streams, we use a continuous reader thread to drain
the buffer and always keep the LATEST frame. Otherwise OpenCV buffers
old frames and you get delayed video.
"""
import os
import sys
import time
import threading
import queue
from datetime import datetime
from pathlib import Path
import requests
from PIL import Image
from io import BytesIO
import cv2
import numpy as np

# Force output to flush immediately
sys.stdout.flush()


class BufferlessVideoCapture:
    """
    A wrapper around cv2.VideoCapture that always returns the LATEST frame.
    
    OpenCV's VideoCapture buffers frames internally. If you only read every few
    seconds, the buffer fills up and you get old frames. This class continuously
    reads frames in a background thread, discarding old ones, so you always get
    the most recent frame.
    """
    
    def __init__(self, source):
        print(f"[BufferlessVideoCapture] Initializing with source: {source}", flush=True)
        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize OpenCV's internal buffer
        
        self.q = queue.Queue(maxsize=2)
        self.running = True
        self.last_frame = None
        self.last_frame_time = None
        self.lock = threading.Lock()
        
        # Start the reader thread
        self.reader_thread = threading.Thread(target=self._reader, daemon=True)
        self.reader_thread.start()
        print(f"[BufferlessVideoCapture] Reader thread started", flush=True)
    
    def _reader(self):
        """Continuously read frames to drain the buffer, keeping only the latest"""
        print(f"[BufferlessVideoCapture] Reader thread running...", flush=True)
        frame_count = 0
        
        while self.running:
            ret, frame = self.cap.read()
            
            if not ret:
                print(f"[BufferlessVideoCapture] Failed to read frame, reconnecting...", flush=True)
                time.sleep(0.5)
                continue
            
            frame_count += 1
            
            # Store the latest frame (overwrite previous)
            with self.lock:
                self.last_frame = frame
                self.last_frame_time = datetime.now()
            
            # Log every 100 frames to show we're draining the buffer
            if frame_count % 100 == 0:
                print(f"[BufferlessVideoCapture] Drained {frame_count} frames from buffer", flush=True)
        
        print(f"[BufferlessVideoCapture] Reader thread stopped", flush=True)
    
    def read(self):
        """Get the most recent frame"""
        with self.lock:
            if self.last_frame is not None:
                # Return a copy to avoid race conditions
                return True, self.last_frame.copy()
            return False, None
    
    def isOpened(self):
        return self.cap.isOpened()
    
    def release(self):
        print(f"[BufferlessVideoCapture] Releasing...", flush=True)
        self.running = False
        if self.reader_thread.is_alive():
            self.reader_thread.join(timeout=2)
        self.cap.release()
        print(f"[BufferlessVideoCapture] Released", flush=True)


class CameraCapture:
    """Handles capturing frames from a camera feed"""
    
    def __init__(self, camera_url, capture_interval=1.0):
        """
        Initialize camera capture
        
        Args:
            camera_url: URL of the camera feed (supports snapshots and MJPEG streams)
            capture_interval: Time between captures in seconds
        """
        print("=" * 60, flush=True)
        print("[CameraCapture] INITIALIZING", flush=True)
        print(f"[CameraCapture] camera_url: {camera_url}", flush=True)
        print(f"[CameraCapture] capture_interval: {capture_interval}", flush=True)
        
        self.camera_url = camera_url
        self.capture_interval = capture_interval
        self.is_running = False
        self.capture_thread = None
        self.latest_frame_path = None
        self.base_folder = None
        self.lock = threading.Lock()
        self.use_opencv = False  # Whether to use OpenCV for video streams
        self.video_capture = None  # BufferlessVideoCapture object
        
        # Create base storage folder
        self._create_storage_folder()
        
        print(f"[CameraCapture] base_folder: {self.base_folder}", flush=True)
        print("[CameraCapture] INITIALIZED", flush=True)
        print("=" * 60, flush=True)
    
    def _create_storage_folder(self):
        """Create the storage folder with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_folder = Path(f"exp_time_{timestamp}")
        self.base_folder.mkdir(exist_ok=True)
        print(f"[CameraCapture] Created storage folder: {self.base_folder}", flush=True)
        print(f"[CameraCapture] Absolute path: {self.base_folder.absolute()}", flush=True)
    
    def start(self):
        """Start capturing frames in a background thread"""
        print("[CameraCapture] start() called", flush=True)
        
        if not self.is_running:
            self.is_running = True
            
            # Try to determine if this is a stream or snapshot URL
            print("[CameraCapture] Detecting camera type...", flush=True)
            self._detect_camera_type()
            
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            if self.use_opencv:
                print(f"[CameraCapture] Started camera capture from video stream: {self.camera_url}", flush=True)
            else:
                print(f"[CameraCapture] Started camera capture from snapshot URL: {self.camera_url}", flush=True)
        else:
            print("[CameraCapture] Already running", flush=True)
    
    def stop(self):
        """Stop capturing frames"""
        print("[CameraCapture] stop() called", flush=True)
        self.is_running = False
        
        # Release video capture if active
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None
        
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
        print("[CameraCapture] Stopped camera capture", flush=True)
    
    def _detect_camera_type(self):
        """Detect if camera URL is a snapshot or stream"""
        print("[CameraCapture] _detect_camera_type() called", flush=True)
        
        try:
            # Try a quick request to see what we get
            print(f"[CameraCapture] Testing URL: {self.camera_url}", flush=True)
            response = requests.get(self.camera_url, timeout=2, stream=True)
            content_type = response.headers.get('Content-Type', '').lower()
            print(f"[CameraCapture] Content-Type: {content_type}", flush=True)
            
            # Check if it's a multipart stream (MJPEG)
            if 'multipart' in content_type or 'mjpeg' in content_type:
                print(f"[CameraCapture] Detected MJPEG video stream - using OpenCV with buffer draining", flush=True)
                self.use_opencv = True
            elif 'video' in content_type:
                print(f"[CameraCapture] Detected video stream - using OpenCV with buffer draining", flush=True)
                self.use_opencv = True
            elif response.headers.get('Transfer-Encoding') == 'chunked':
                print(f"[CameraCapture] Detected streaming response - using OpenCV with buffer draining", flush=True)
                self.use_opencv = True
            else:
                print(f"[CameraCapture] Detected snapshot URL - using requests", flush=True)
                self.use_opencv = False
            
            response.close()
        except requests.exceptions.Timeout:
            print(f"[CameraCapture] URL timeout detected - assuming video stream, using OpenCV", flush=True)
            self.use_opencv = True
        except Exception as e:
            print(f"[CameraCapture] Could not detect camera type: {e}", flush=True)
            print(f"[CameraCapture] Defaulting to OpenCV", flush=True)
            self.use_opencv = True
    
    def _capture_loop(self):
        """Main loop for capturing frames"""
        print("[CameraCapture] _capture_loop() started", flush=True)
        print(f"[CameraCapture] use_opencv: {self.use_opencv}", flush=True)
        
        if self.use_opencv:
            self._capture_loop_opencv()
        else:
            self._capture_loop_requests()
    
    def _capture_loop_requests(self):
        """Capture loop using requests (for snapshot URLs)"""
        print("[CameraCapture] _capture_loop_requests() started", flush=True)
        frame_count = 0
        
        while self.is_running:
            frame_count += 1
            print(f"[CameraCapture] Snapshot capture #{frame_count}", flush=True)
            
            self._capture_frame_request()
            
            time.sleep(self.capture_interval)
    
    def _capture_loop_opencv(self):
        """Capture loop using OpenCV with BufferlessVideoCapture (for video streams)"""
        print("[CameraCapture] _capture_loop_opencv() started", flush=True)
        
        # Open video stream with our bufferless wrapper
        print(f"[CameraCapture] Opening video stream with BufferlessVideoCapture...", flush=True)
        print(f"[CameraCapture] Camera URL: {self.camera_url}", flush=True)
        
        self.video_capture = BufferlessVideoCapture(self.camera_url)
        
        print(f"[CameraCapture] BufferlessVideoCapture created", flush=True)
        print(f"[CameraCapture] isOpened(): {self.video_capture.isOpened()}", flush=True)
        
        if not self.video_capture.isOpened():
            print(f"[CameraCapture] ERROR: Could not open video stream: {self.camera_url}", flush=True)
            print(f"[CameraCapture] Make sure the URL is correct and the camera is accessible", flush=True)
            return
        
        print(f"[CameraCapture] SUCCESS: Video stream opened with buffer draining", flush=True)
        
        # Wait a moment for the buffer reader to get the first frame
        time.sleep(0.5)
        
        frame_count = 0
        
        while self.is_running:
            frame_count += 1
            
            # Get the LATEST frame (buffer is being drained continuously)
            ret, frame = self.video_capture.read()
            
            if not ret or frame is None:
                print(f"[CameraCapture] No frame available yet, waiting...", flush=True)
                time.sleep(0.5)
                continue
            
            # Convert BGR to RGB (OpenCV uses BGR by default)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            img = Image.fromarray(frame_rgb)
            
            # Save frame with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"frame_{timestamp}.jpg"
            filepath = self.base_folder / filename
            
            img.save(filepath, "JPEG", quality=95)
            
            # Update latest frame path
            with self.lock:
                self.latest_frame_path = str(filepath)
            
            print(f"[CameraCapture] Saved LATEST frame #{frame_count}: {filename}", flush=True)
            
            # Wait for next capture interval
            time.sleep(self.capture_interval)
    
    def _capture_frame_request(self):
        """Capture a single frame using HTTP request (for snapshot URLs)"""
        print(f"[CameraCapture] _capture_frame_request() called", flush=True)
        
        # Create a new session for each request to avoid connection reuse issues
        session = requests.Session()
        
        try:
            print(f"[CameraCapture] Requesting from: {self.camera_url}", flush=True)
            
            # Use a fresh connection each time
            response = session.get(
                self.camera_url, 
                timeout=5,
                headers={'Connection': 'close'}  # Force close connection after request
            )
            response.raise_for_status()
            
            print(f"[CameraCapture] Response status: {response.status_code}", flush=True)
            print(f"[CameraCapture] Response content-type: {response.headers.get('Content-Type', 'unknown')}", flush=True)
            print(f"[CameraCapture] Response content length: {len(response.content)} bytes", flush=True)
            
            # Check if response is HTML
            content_type = response.headers.get('Content-Type', '').lower()
            
            if 'html' in content_type or response.content[:15].lower().startswith(b'<!doctype') or response.content[:6].lower().startswith(b'<html'):
                print(f"[CameraCapture] Warning: Camera URL returned HTML. Trying alternative endpoints...", flush=True)
                self._try_alternative_endpoints()
                return
            
            # Open image from response
            print(f"[CameraCapture] Opening image from response...", flush=True)
            img = Image.open(BytesIO(response.content))
            print(f"[CameraCapture] Image opened: size={img.size}, mode={img.mode}", flush=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"frame_{timestamp}.jpg"
            filepath = self.base_folder / filename
            
            # Save image
            img.save(filepath, "JPEG", quality=95)
            print(f"[CameraCapture] Saved to: {filepath}", flush=True)
            
            # Update latest frame path
            with self.lock:
                self.latest_frame_path = str(filepath)
            
            print(f"[CameraCapture] latest_frame_path updated: {self.latest_frame_path}", flush=True)
            
        finally:
            # Always close the session to release connection
            session.close()
    
    def _try_alternative_endpoints(self):
        """Try common IP camera snapshot endpoints"""
        print("[CameraCapture] _try_alternative_endpoints() called", flush=True)
        
        base_url = self.camera_url.rsplit('/', 1)[0]
        alternative_urls = [
            f"{base_url}/shot.jpg",
            f"{base_url}/photo.jpg",
            f"{base_url}/photoaf.jpg",
            f"{base_url}/snapshot.jpg",
            f"{base_url}/image.jpg",
            f"{base_url}/current.jpg",
        ]
        
        print(f"[CameraCapture] Base URL: {base_url}", flush=True)
        print(f"[CameraCapture] Trying {len(alternative_urls)} alternatives...", flush=True)
        
        img = None
        working_url = None
        
        for alt_url in alternative_urls:
            print(f"[CameraCapture]   Trying: {alt_url}", flush=True)
            try:
                session = requests.Session()
                alt_response = session.get(alt_url, timeout=3, headers={'Connection': 'close'})
                alt_response.raise_for_status()
                
                alt_content_type = alt_response.headers.get('Content-Type', '').lower()
                print(f"[CameraCapture]     Content-Type: {alt_content_type}", flush=True)
                
                if 'image' in alt_content_type:
                    img = Image.open(BytesIO(alt_response.content))
                    working_url = alt_url
                    print(f"[CameraCapture]     SUCCESS! Found working endpoint", flush=True)
                    session.close()
                    break
                session.close()
            except Exception as e:
                print(f"[CameraCapture]     FAILED: {e}", flush=True)
                continue
        
        if img is None:
            print(f"[CameraCapture] ERROR: Could not find valid image endpoint.", flush=True)
            print(f"[CameraCapture] Please manually set CAMERA_URL in .env file", flush=True)
            return
        
        self.camera_url = working_url
        print(f"[CameraCapture] Camera URL updated to: {working_url}", flush=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"frame_{timestamp}.jpg"
        filepath = self.base_folder / filename
        
        img.save(filepath, "JPEG", quality=95)
        
        with self.lock:
            self.latest_frame_path = str(filepath)
        
        print(f"[CameraCapture] Captured frame: {filename}", flush=True)
    
    def get_latest_frame(self):
        """Get path to the latest captured frame"""
        with self.lock:
            path = self.latest_frame_path
        return path
    
    def get_frame_count(self):
        """Get total number of captured frames"""
        if self.base_folder and self.base_folder.exists():
            count = len(list(self.base_folder.glob("frame_*.jpg")))
            return count
        return 0
