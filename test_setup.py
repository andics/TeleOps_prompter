"""
Setup Test Script
Run this to verify your environment is configured correctly
"""
import sys
import os

def test_python_version():
    """Check Python version"""
    print("Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} - Need 3.8+")
        return False

def test_imports():
    """Check if required packages are installed"""
    print("\nTesting required packages...")
    packages = [
        ('flask', 'Flask'),
        ('flask_cors', 'Flask-CORS'),
        ('requests', 'Requests'),
        ('PIL', 'Pillow'),
        ('openai', 'OpenAI'),
        ('dotenv', 'python-dotenv')
    ]
    
    all_ok = True
    for module_name, display_name in packages:
        try:
            __import__(module_name)
            print(f"✓ {display_name} - Installed")
        except ImportError:
            print(f"✗ {display_name} - Missing")
            all_ok = False
    
    return all_ok

def test_env_file():
    """Check for .env file and API key"""
    print("\nTesting environment configuration...")
    
    if os.path.exists('.env'):
        print("✓ .env file exists")
        
        # Try to load it
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            masked_key = api_key[:7] + '...' + api_key[-4:] if len(api_key) > 11 else '***'
            print(f"✓ OPENAI_API_KEY found ({masked_key})")
            return True
        else:
            print("✗ OPENAI_API_KEY not set in .env file")
            return False
    else:
        print("✗ .env file not found")
        print("  Create .env file with: OPENAI_API_KEY=your_key_here")
        return False

def test_camera_url():
    """Test camera URL accessibility"""
    print("\nTesting camera connection...")
    
    try:
        import requests
        from dotenv import load_dotenv
        load_dotenv()
        
        camera_url = os.environ.get('CAMERA_URL', 'http://10.0.0.197:8080/cam_c')
        print(f"  Trying to connect to: {camera_url}")
        
        response = requests.get(camera_url, timeout=5)
        if response.status_code == 200:
            print(f"✓ Camera accessible (Status: {response.status_code})")
            print(f"  Content-Type: {response.headers.get('Content-Type', 'unknown')}")
            print(f"  Content-Length: {len(response.content)} bytes")
            return True
        else:
            print(f"⚠ Camera responded with status: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("✗ Camera connection timeout")
        print("  Make sure the camera is on and accessible")
        return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to camera")
        print("  Check the IP address and network connection")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\nTesting OpenAI API connection...")
    
    try:
        from openai import OpenAI
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("✗ No API key to test")
            return False
        
        client = OpenAI(api_key=api_key)
        
        # Try a simple API call
        print("  Making test API call...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print("✓ OpenAI API connection successful")
        print(f"  Model: {response.model}")
        return True
        
    except Exception as e:
        print(f"✗ OpenAI API error: {e}")
        return False

def test_modules():
    """Test custom modules"""
    print("\nTesting custom modules...")
    
    try:
        from camera_capture import CameraCapture
        print("✓ camera_capture.py - OK")
    except Exception as e:
        print(f"✗ camera_capture.py - Error: {e}")
        return False
    
    try:
        from openai_handler import OpenAIHandler
        print("✓ openai_handler.py - OK")
    except Exception as e:
        print(f"✗ openai_handler.py - Error: {e}")
        return False
    
    try:
        import app
        print("✓ app.py - OK")
    except Exception as e:
        print(f"✗ app.py - Error: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Camera Feed Monitor - Setup Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Python Version", test_python_version()))
    results.append(("Required Packages", test_imports()))
    results.append(("Environment Config", test_env_file()))
    results.append(("Custom Modules", test_modules()))
    results.append(("Camera Connection", test_camera_url()))
    results.append(("OpenAI API", test_openai_connection()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to run the application.")
        print("\nRun: python app.py")
        print("Then open: http://localhost:5000")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install packages: pip install -r requirements.txt")
        print("  - Create .env file with your OPENAI_API_KEY")
        print("  - Check camera IP address and network connection")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

