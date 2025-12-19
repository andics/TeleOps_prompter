"""
Camera URL Tester
Quick script to find the correct camera URL endpoint
"""
import requests
from PIL import Image
from io import BytesIO

def test_camera_url(base_url):
    """Test various camera endpoints to find the working one"""
    
    print("=" * 60)
    print("Camera URL Tester")
    print("=" * 60)
    print(f"\nBase URL: {base_url}")
    print("\nTesting common IP camera endpoints...\n")
    
    # Common endpoints to test
    endpoints = [
        "/shot.jpg",
        "/photo.jpg",
        "/photoaf.jpg",
        "/snapshot.jpg",
        "/image.jpg",
        "/current.jpg",
        "/cam_c",
        "/video",
    ]
    
    working_urls = []
    
    for endpoint in endpoints:
        url = base_url + endpoint
        try:
            print(f"Testing: {url}")
            response = requests.get(url, timeout=3)
            
            # Check status
            if response.status_code != 200:
                print(f"  FAILED: HTTP {response.status_code}\n")
                continue
            
            # Check content type
            content_type = response.headers.get('Content-Type', '').lower()
            print(f"  Content-Type: {content_type}")
            print(f"  Content-Length: {len(response.content)} bytes")
            
            # Try to open as image
            if 'image' in content_type:
                try:
                    img = Image.open(BytesIO(response.content))
                    print(f"  SUCCESS! Valid JPEG image ({img.size[0]}x{img.size[1]})")
                    print(f"  This URL works!\n")
                    working_urls.append(url)
                except Exception as e:
                    print(f"  FAILED to parse image: {e}\n")
            elif 'html' in content_type:
                print(f"  FAILED: Returns HTML (not suitable for direct capture)\n")
            elif 'multipart' in content_type or 'mjpeg' in content_type:
                print(f"  WARNING: MJPEG stream (continuous, not snapshot)\n")
            else:
                print(f"  ? Unknown content type\n")
                
        except requests.exceptions.Timeout:
            print(f"  FAILED: Timeout (likely a stream endpoint, not snapshot)\n")
        except requests.exceptions.RequestException as e:
            print(f"  FAILED: Network error: {e}\n")
        except Exception as e:
            print(f"  FAILED: Error: {e}\n")
    
    # Summary
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if working_urls:
        print("\nSUCCESS: Working URLs found:\n")
        for url in working_urls:
            print(f"  {url}")
        
        print("\n" + "=" * 60)
        print("RECOMMENDED ACTION")
        print("=" * 60)
        print(f"\nAdd this to your .env file:\n")
        print(f"CAMERA_URL={working_urls[0]}")
        print("\nThen restart the application.")
    else:
        print("\nFAILED: No working snapshot URLs found.")
        print("\nTroubleshooting:")
        print("  1. Verify the camera is running and accessible")
        print("  2. Check the IP address is correct")
        print("  3. Try accessing the camera in a web browser")
        print("  4. Check the camera app documentation for the correct endpoint")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    # Get camera base URL
    import sys
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        # Default from your camera
        base_url = "http://10.0.0.197:8080"
    
    # Remove any endpoint path if provided
    if '/cam_c' in base_url or '/shot' in base_url or '/photo' in base_url:
        base_url = base_url.rsplit('/', 1)[0]
    
    test_camera_url(base_url)

