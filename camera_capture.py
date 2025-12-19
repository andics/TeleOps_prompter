"""
Camera Capture Module
Captures frames from a camera feed at regular intervals
Supports both snapshot URLs and MJPEG video streams
"""
import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
import requests
from PIL import Image
from io import BytesIO
import cv2
import numpy as np

# Force output to flush immediately
sys.stdout.flush()


class CameraCapture:
    """Handles capturing frames from a camera feed"""
    
    def __init__(self, camera_url, capture_interval=1.0):
        """
        Initialize camera capture
        
        Args:
            camera_url: URL of the camera feed (supports snapshots and MJPEG streams)
            capture_interval: Time between captures in seconds
        """
        self.camera_url = camera_url
        self.capture_interval = capture_interval
        self.is_running = False
        self.capture_thread = None
        self.latest_frame_path = None
        self.base_folder = None
        self.lock = threading.Lock()
        self.use_opencv = False  # Whether to use OpenCV for video streams
        self.video_capture = None  # OpenCV VideoCapture object
        
        # Create base storage folder
        self._create_storage_folder()
    
    def _create_storage_folder(self):
        """Create the storage folder with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.base_folder = Path(f"exp_time_{timestamp}")
        self.base_folder.mkdir(exist_ok=True)
        print(f"Created storage folder: {self.base_folder}")
    
    def start(self):
        """Start capturing frames in a background thread"""
        if not self.is_running:
            self.is_running = True
            
            # Try to determine if this is a stream or snapshot URL
            self._detect_camera_type()
            
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            if self.use_opencv:
                print(f"Started camera capture from video stream: {self.camera_url}")
            else:
                print(f"Started camera capture from snapshot URL: {self.camera_url}")
    
    def stop(self):
        """Stop capturing frames"""
        self.is_running = False
        
        # Release OpenCV video capture if active
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None
        
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
        print("Stopped camera capture")
    
    def _detect_camera_type(self):
        """Detect if camera URL is a snapshot or stream"""
        try:
            # Try a quick request to see what we get
            response = requests.get(self.camera_url, timeout=2, stream=True)
            content_type = response.headers.get('Content-Type', '').lower()
            
            # Check if it's a multipart stream (MJPEG)
            if 'multipart' in content_type or 'mjpeg' in content_type:
                print(f"Detected MJPEG video stream - using OpenCV")
                self.use_opencv = True
            elif 'video' in content_type:
                print(f"Detected video stream - using OpenCV")
                self.use_opencv = True
            # If it times out or takes too long, likely a stream
            elif response.headers.get('Transfer-Encoding') == 'chunked':
                print(f"Detected streaming response - using OpenCV")
                self.use_opencv = True
            else:
                print(f"Detected snapshot URL - using requests")
                self.use_opencv = False
            
            response.close()
        except requests.exceptions.Timeout:
            # Timeout likely means it's a stream
            print(f"URL timeout detected - assuming video stream, using OpenCV")
            self.use_opencv = True
        except Exception as e:
            print(f"Could not detect camera type, defaulting to OpenCV: {e}")
            self.use_opencv = True
    
    def _capture_loop(self):
        """Main loop for capturing frames"""
        if self.use_opencv:
            self._capture_loop_opencv()
        else:
            self._capture_loop_requests()
    
    def _capture_loop_requests(self):
        """Capture loop using requests (for snapshot URLs)"""
        while self.is_running:
            try:
                self._capture_frame()
            except Exception as e:
                print(f"Error capturing frame: {e}")
            
            time.sleep(self.capture_interval)
    
    def _capture_loop_opencv(self):
        """Capture loop using OpenCV (for video streams)"""
        try:
            # Open video stream
            print(f"Opening video stream with OpenCV...")
            print(f"Camera URL: {self.camera_url}")
            self.video_capture = cv2.VideoCapture(self.camera_url)
            
            if not self.video_capture.isOpened():
                print(f"ERROR: Could not open video stream: {self.camera_url}")
                print(f"Make sure the URL is correct and the camera is accessible")
                return
            
            print(f"SUCCESS: Video stream opened successfully", flush=True)
        except Exception as e:
            print(f"EXCEPTION opening video stream: {e}")
            import traceback
            traceback.print_exc()
            return
        
        while self.is_running:
            try:
                # Read frame from stream
                ret, frame = self.video_capture.read()
                
                if not ret:
                    print("Failed to read frame from stream, reconnecting...")
                    self.video_capture.release()
                    time.sleep(1)
                    self.video_capture = cv2.VideoCapture(self.camera_url)
                    continue
                
                # Convert BGR to RGB (OpenCV uses BGR by default)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to PIL Image
                img = Image.fromarray(frame_rgb)
                
                # Save frame
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"frame_{timestamp}.jpg"
                filepath = self.base_folder / filename
                
                img.save(filepath, "JPEG", quality=95)
                
                # Update latest frame path
                with self.lock:
                    self.latest_frame_path = str(filepath)
                
                print(f"Captured frame from stream: {filename} -> Path: {self.latest_frame_path}", flush=True)
                
                # Wait for next capture
                time.sleep(self.capture_interval)
                
            except Exception as e:
                print(f"Error capturing frame from stream: {e}")
                time.sleep(1)
    
    def _capture_frame(self):
        """Capture a single frame from the camera"""
        try:
            # Request frame from camera
            response = requests.get(self.camera_url, timeout=5)
            response.raise_for_status()
            
            # Check if response is HTML (common issue with IP cameras)
            content_type = response.headers.get('Content-Type', '').lower()
            
            if 'html' in content_type or response.content[:15].lower().startswith(b'<!doctype') or response.content[:6].lower().startswith(b'<html'):
                # URL returned HTML instead of image - try common snapshot endpoints
                print(f"Warning: Camera URL returned HTML. Trying alternative endpoints...")
                self._try_alternative_endpoints()
                return  # _try_alternative_endpoints will handle the capture
            else:
                # Response looks like an image, try to open it
                img = Image.open(BytesIO(response.content))
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # milliseconds
            filename = f"frame_{timestamp}.jpg"
            filepath = self.base_folder / filename
            
            # Save image
            img.save(filepath, "JPEG", quality=95)
            
            # Update latest frame path
            with self.lock:
                self.latest_frame_path = str(filepath)
            
            print(f"Captured frame: {filename} -> Path: {self.latest_frame_path}")
            
        except requests.exceptions.Timeout:
            # Timeout likely means this is a stream endpoint, not a snapshot
            print(f"Warning: Camera URL timed out (likely a stream endpoint). Trying snapshot alternatives...")
            self._try_alternative_endpoints()
        except requests.exceptions.RequestException as e:
            print(f"Network error capturing frame: {e}")
        except Exception as e:
            print(f"Error saving frame: {e}")
    
    def _try_alternative_endpoints(self):
        """Try common IP camera snapshot endpoints"""
        # Try common IP camera snapshot URLs
        base_url = self.camera_url.rsplit('/', 1)[0]  # Get base URL
        alternative_urls = [
            f"{base_url}/shot.jpg",
            f"{base_url}/photo.jpg",
            f"{base_url}/photoaf.jpg",
            f"{base_url}/snapshot.jpg",
            f"{base_url}/image.jpg",
            f"{base_url}/current.jpg",
        ]
        
        img = None
        working_url = None
        
        for alt_url in alternative_urls:
            try:
                print(f"  Trying: {alt_url}")
                alt_response = requests.get(alt_url, timeout=3)
                alt_response.raise_for_status()
                
                # Check if this is an image
                alt_content_type = alt_response.headers.get('Content-Type', '').lower()
                if 'image' in alt_content_type:
                    img = Image.open(BytesIO(alt_response.content))
                    working_url = alt_url
                    print(f"  SUCCESS! Found working endpoint: {alt_url}")
                    break
            except Exception as e:
                print(f"    FAILED: {alt_url}")
                continue
        
        if img is None:
            print(f"ERROR: Could not find valid image endpoint.")
            print(f"Please manually set CAMERA_URL in .env file to one of:")
            for url in alternative_urls:
                print(f"  - {url}")
            return
        
        # Update the camera URL for future captures
        self.camera_url = working_url
        print(f"Camera URL updated to: {working_url}")
        
        # Save the captured frame
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"frame_{timestamp}.jpg"
        filepath = self.base_folder / filename
        
        img.save(filepath, "JPEG", quality=95)
        
        with self.lock:
            self.latest_frame_path = str(filepath)
        
        print(f"Captured frame: {filename}")
    
    def get_latest_frame(self):
        """Get path to the latest captured frame"""
        with self.lock:
            return self.latest_frame_path
    
    def get_frame_count(self):
        """Get total number of captured frames"""
        if self.base_folder and self.base_folder.exists():
            return len(list(self.base_folder.glob("frame_*.jpg")))
        return 0

