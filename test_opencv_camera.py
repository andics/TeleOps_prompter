"""
Test OpenCV Camera Connection
Quick script to test if OpenCV can connect to the camera stream
"""
import cv2
import sys

camera_url = "http://10.0.0.197:8080/cam_c"

print(f"Testing OpenCV connection to: {camera_url}")
print(f"OpenCV version: {cv2.__version__}")
print()

# Try to open the video stream
print("Attempting to open video stream...")
cap = cv2.VideoCapture(camera_url)

if not cap.isOpened():
    print("ERROR: Could not open video stream!")
    print()
    print("Possible issues:")
    print("  1. Camera URL is incorrect")
    print("  2. Camera is not accessible on the network")
    print("  3. OpenCV doesn't support this stream format")
    print()
    print("Try these alternatives:")
    print("  - http://10.0.0.197:8080/video")
    print("  - http://10.0.0.197:8080/shot.jpg (snapshot, not stream)")
    sys.exit(1)

print("SUCCESS: Video stream opened!")
print()

# Try to read a frame
print("Attempting to read a frame...")
ret, frame = cap.read()

if not ret:
    print("ERROR: Could not read frame from stream!")
    cap.release()
    sys.exit(1)

print(f"SUCCESS: Frame read! Size: {frame.shape}")
print()

# Save the frame
output_file = "test_frame.jpg"
cv2.imwrite(output_file, frame)
print(f"Frame saved to: {output_file}")
print()

# Release the capture
cap.release()

print("=" * 60)
print("TEST PASSED!")
print("=" * 60)
print()
print("OpenCV can successfully connect to your camera stream.")
print("The main application should work now.")

