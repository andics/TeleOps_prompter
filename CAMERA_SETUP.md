# Camera Setup Guide

## ✨ NEW: Video Stream Support

The application now supports **MJPEG video streams** directly! You can use streaming URLs like `/cam_c` or `/video`, and the app will automatically:
- Detect it's a video stream
- Use OpenCV to connect to the stream
- Grab frames at your specified interval (default: 1/second)

**Just use your video stream URL directly - no need for snapshot endpoints!**

Example:
```env
CAMERA_URL=http://10.0.0.197:8080/cam_c
```

## Common Camera Types

### Video Streams (MJPEG) - ✓ Now Supported!

If your camera only provides a video stream endpoint:
- `/cam_c` - Works now!
- `/video` - Works now!
- `/videostream.cgi` - Works now!

The app will automatically detect the stream and use OpenCV to capture frames.

### Snapshot URLs (Also Supported)

If your camera provides snapshot endpoints:
- `/shot.jpg` - Single JPEG image
- `/photo.jpg` - Alternative snapshot
- `/snapshot.jpg` - Common snapshot URL

Both types work automatically!

## IP Webcam (Android App)

If you're using the "IP Webcam" Android app, use these endpoints:

### Recommended: Snapshot Endpoint
```env
CAMERA_URL=http://10.0.0.197:8080/shot.jpg
```

This returns a single JPEG image - perfect for this application.

### Alternative Endpoints

```env
# Alternative snapshot
CAMERA_URL=http://10.0.0.197:8080/photo.jpg

# Current frame from video stream
CAMERA_URL=http://10.0.0.197:8080/photoaf.jpg

# Lower quality snapshot
CAMERA_URL=http://10.0.0.197:8080/shot.jpg?rand=12345
```

### Video Streams - Now Fully Supported! ✓

```env
# MJPEG video stream - NOW WORKS!
CAMERA_URL=http://10.0.0.197:8080/video

# IP Webcam stream endpoint - NOW WORKS!
CAMERA_URL=http://10.0.0.197:8080/cam_c
```

The app will automatically detect these are streams and use OpenCV to grab frames.

## How to Find the Right URL

### Method 1: Check Camera Documentation

Look for:
- "Snapshot URL"
- "Still image URL"
- "JPEG endpoint"
- "Photo URL"

### Method 2: Test in Browser

Try these URLs in your browser and see which one downloads/displays a single image:

```
http://10.0.0.197:8080/shot.jpg
http://10.0.0.197:8080/photo.jpg
http://10.0.0.197:8080/snapshot.jpg
http://10.0.0.197:8080/image.jpg
http://10.0.0.197:8080/current.jpg
```

The correct URL should:
- ✅ Display a single image
- ✅ Show `Content-Type: image/jpeg` in headers
- ✅ Download a .jpg file

### Method 3: Use the Auto-Detection

The updated `camera_capture.py` now automatically tries common endpoints if it detects HTML:

1. `/shot.jpg`
2. `/photo.jpg`
3. `/snapshot.jpg`
4. `/image.jpg`
5. `/current.jpg`

Check the console output - it will tell you which URL worked!

## Configuration

### Option 1: Using .env File (Recommended)

Create/edit `.env`:

```env
OPENAI_API_KEY=your_key_here
CAMERA_URL=http://10.0.0.197:8080/shot.jpg
CAPTURE_INTERVAL=1.0
```

### Option 2: Direct in app.py

Edit `app.py` around line 115:

```python
camera_url = os.environ.get("CAMERA_URL", "http://10.0.0.197:8080/shot.jpg")
```

## Testing Your Camera URL

### Quick Test with curl

**Windows PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://10.0.0.197:8080/shot.jpg" -OutFile "test.jpg"
```

**Linux/Mac:**
```bash
curl -o test.jpg http://10.0.0.197:8080/shot.jpg
```

If successful, you'll have a `test.jpg` file you can open.

### Quick Test with Python

```python
import requests
from PIL import Image
from io import BytesIO

url = "http://10.0.0.197:8080/shot.jpg"
response = requests.get(url)

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Content-Length: {len(response.content)} bytes")

# Try to open as image
try:
    img = Image.open(BytesIO(response.content))
    print(f"Success! Image size: {img.size}")
    img.save("test_frame.jpg")
except Exception as e:
    print(f"Error: {e}")
```

## Other Camera Types

### Generic IP Cameras

Common patterns:
```
http://CAMERA_IP/snapshot.jpg
http://CAMERA_IP/snap.jpg
http://CAMERA_IP/image/jpeg.cgi
http://CAMERA_IP/cgi-bin/snapshot.cgi
```

### RTSP Cameras

If your camera only provides RTSP, you'll need to convert it:

1. Use FFmpeg to extract frames
2. Use a streaming server like `rtsp-simple-server`
3. Use OpenCV to capture frames (requires code modification)

### USB Webcams

For local USB webcams, you'd need to modify the code to use OpenCV:

```python
import cv2

cap = cv2.VideoCapture(0)  # 0 for first webcam
ret, frame = cap.read()
cv2.imwrite("frame.jpg", frame)
```

## Troubleshooting

### Error: "Could not find valid image endpoint"

**Solution:**
1. Check that the camera is accessible: `ping 10.0.0.197`
2. Try the URLs in your browser
3. Check the IP Webcam app settings
4. Make sure "Start server" is enabled in the app
5. Check firewall settings

### Error: "Connection timeout"

**Solution:**
1. Verify the IP address is correct
2. Make sure you're on the same network
3. Check if the camera app is running
4. Try accessing from a browser first

### Error: "Cannot identify image file"

**Solution:**
1. The URL is returning HTML, not an image
2. Change from `/cam_c` to `/shot.jpg`
3. Check the auto-detection output in console

### Camera works in browser but not in app

**Solution:**
1. Browser might be using JavaScript to load the image
2. Find the actual image URL (right-click image → "Copy image address")
3. Use that URL in the app

## IP Webcam App Settings

For best results with IP Webcam app:

1. **Video Resolution**: 640x480 or 1280x720 (balance quality vs speed)
2. **Quality**: 80-90% (good balance)
3. **FPS Limit**: 10-15 fps (we only capture 1/second anyway)
4. **Photo Resolution**: Same as video or higher
5. **Server Port**: 8080 (default)

## Example Working Configuration

```env
# .env file
OPENAI_API_KEY=sk-your-key-here
CAMERA_URL=http://10.0.0.197:8080/shot.jpg
CAPTURE_INTERVAL=1.0
```

This should work with IP Webcam app on Android!

## Still Having Issues?

1. Run the app and check console output
2. Look for "Trying: http://..." messages
3. The app will auto-detect the correct endpoint
4. Once it finds one, update your `.env` file with that URL

---

**Quick Fix:** Change `CAMERA_URL` from `/cam_c` to `/shot.jpg` in your `.env` file!

