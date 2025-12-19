# Installation Guide

Complete step-by-step installation instructions for the Camera Feed Monitor application.

## Prerequisites

### Required Software
- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** - Usually comes with Python
- **Git** (optional) - For cloning the repository

### Required Services
- **OpenAI API Account** - [Sign up here](https://platform.openai.com/)
- **IP Camera** - Accessible on your network

### System Requirements
- **OS**: Windows, macOS, or Linux
- **RAM**: 512 MB minimum (2 GB recommended)
- **Disk Space**: 10 GB+ (for storing captured frames)
- **Network**: Access to camera and internet (for OpenAI API)

## Step-by-Step Installation

### 1. Get the Code

**Option A: If you already have the files**
```bash
cd Q:\Projects\TeleOps\Programming
```

**Option B: If cloning from a repository**
```bash
git clone <repository-url>
cd camera-feed-monitor
```

### 2. Create Environment (Recommended)

**Option A: Using Conda (Recommended for this project)**
```bash
conda create -n teleops_prompter python=3.10 -y
conda activate teleops_prompter
```

You should see `(teleops_prompter)` in your terminal prompt.

**Option B: Using Virtual Environment (venv)**

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- flask-cors (CORS support)
- requests (HTTP client)
- Pillow (image processing)
- openai (OpenAI API client)
- python-dotenv (environment variables)

### 4. Configure OpenAI API Key

**Step 4.1: Get your API key**
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign in or create an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-`)

**Step 4.2: Create .env file**

Create a file named `.env` in the project root:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
notepad .env
```

**macOS/Linux:**
```bash
cp .env.example .env
nano .env
```

**Step 4.3: Add your API key**

Edit the `.env` file:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
CAMERA_URL=http://10.0.0.197:8080/cam_c
CAPTURE_INTERVAL=1.0
```

Replace `sk-your-actual-api-key-here` with your actual OpenAI API key.

### 5. Configure Camera URL

If your camera is at a different address, update the `CAMERA_URL` in `.env`:

```env
CAMERA_URL=http://YOUR_CAMERA_IP:PORT/cam_c
```

**Finding your camera URL:**
- Check your camera's documentation
- Look for "MJPEG stream" or "snapshot URL"
- Common formats:
  - `http://192.168.1.100:8080/video`
  - `http://10.0.0.50/mjpeg`
  - `http://camera.local/snapshot.jpg`

### 6. Test Your Setup

Run the setup test script:

```bash
python test_setup.py
```

This will check:
- ✓ Python version
- ✓ Required packages
- ✓ Environment configuration
- ✓ Custom modules
- ✓ Camera connection
- ✓ OpenAI API

**Expected output:**
```
============================================================
Camera Feed Monitor - Setup Test
============================================================
Testing Python version...
✓ Python 3.11.0 - OK

Testing required packages...
✓ Flask - Installed
✓ Flask-CORS - Installed
...

Results: 6/6 tests passed
============================================================

🎉 All tests passed! You're ready to run the application.
```

### 7. Run the Application

**Option A: Using the startup script (Recommended)**

**Windows (automatically handles Conda environment):**
```cmd
run.bat
```
This will automatically create/activate the `teleops_prompter` Conda environment.

**macOS/Linux:**
```bash
chmod +x run.sh
./run.sh
```

**Option B: Direct Python command (Conda)**
```bash
conda activate teleops_prompter
python app.py
```

**Option C: Direct Python command (no environment)**
```bash
python app.py
```

### 8. Access the Application

Open your web browser and navigate to:

```
http://localhost:5000
```

You should see the Camera Feed Monitor interface with three panels.

## Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
# Make sure conda environment is activated
conda activate teleops_prompter

# Or if using venv:
# Windows:
.\venv\Scripts\Activate.ps1

# macOS/Linux:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "OPENAI_API_KEY not set"

**Solution:**
1. Check that `.env` file exists in project root
2. Verify the API key is correct (starts with `sk-`)
3. No quotes needed around the key in `.env`
4. Restart the application after editing `.env`

### Issue: "Cannot connect to camera"

**Solution:**
1. Verify camera IP address is correct
2. Test camera URL in web browser
3. Check network connectivity
4. Ensure camera is powered on
5. Try accessing camera from same machine

**Test camera URL:**
```bash
# Windows PowerShell
Invoke-WebRequest -Uri "http://10.0.0.197:8080/cam_c"

# macOS/Linux
curl -I http://10.0.0.197:8080/cam_c
```

### Issue: "Port 5000 already in use"

**Solution:**

**Option A: Stop the other process**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

**Option B: Use a different port**

Edit `app.py`, change the last line:
```python
app.run(host='0.0.0.0', port=5001, debug=False)
```

Then access at `http://localhost:5001`

### Issue: OpenAI API errors

**Common errors and solutions:**

1. **"Invalid API key"**
   - Verify key is correct
   - Check for extra spaces
   - Regenerate key on OpenAI platform

2. **"Rate limit exceeded"**
   - Reduce number of active filters
   - Increase capture interval
   - Check API usage limits

3. **"Insufficient quota"**
   - Add payment method on OpenAI platform
   - Check billing status
   - Verify account has credits

### Issue: Slow performance

**Solutions:**
1. Reduce capture interval in `.env`:
   ```env
   CAPTURE_INTERVAL=2.0
   ```

2. Limit number of active filters (toggle off unused ones)

3. Check internet connection speed

4. Monitor OpenAI API response times

### Issue: Frames not appearing

**Solution:**
1. Check browser console for errors (F12)
2. Verify camera is capturing (check `exp_time_*` folder)
3. Check file permissions
4. Try refreshing the page
5. Check browser compatibility (use Chrome/Firefox/Edge)

## Verification Checklist

After installation, verify:

- [ ] Application starts without errors
- [ ] Browser opens to `http://localhost:5000`
- [ ] Three panels visible (Frame, Filters, Chat)
- [ ] Theme toggle works (sun/moon icon)
- [ ] Latest frame appears in left panel
- [ ] Can add a filter in middle panel
- [ ] Filter switch toggles on/off
- [ ] Filter results show (green/red)
- [ ] Chat panel displays messages
- [ ] No console errors in browser (F12)

## Next Steps

Once installed successfully:

1. **Read the Quick Start Guide**: `QUICKSTART.md`
2. **Explore the interface**: Try adding filters
3. **Review the documentation**: `README.md`
4. **Understand the architecture**: `ARCHITECTURE.md`
5. **Customize settings**: Edit `.env` file

## Updating the Application

To update to a newer version:

```bash
# Activate virtual environment
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows

# Pull latest changes (if using git)
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart the application
python app.py
```

## Uninstallation

To remove the application:

1. **Deactivate virtual environment:**
   ```bash
   deactivate
   ```

2. **Delete the project folder:**
   ```bash
   # Windows
   rmdir /s /q Q:\Projects\TeleOps\Programming
   
   # macOS/Linux
   rm -rf /path/to/project
   ```

3. **Remove captured frames** (if stored elsewhere)

## Getting Help

If you encounter issues:

1. Check this installation guide
2. Review `README.md` and `QUICKSTART.md`
3. Run `python test_setup.py` to diagnose
4. Check the console output for error messages
5. Verify all prerequisites are met

## Additional Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **OpenAI API Docs**: https://platform.openai.com/docs/
- **Python Documentation**: https://docs.python.org/3/
- **Pillow Documentation**: https://pillow.readthedocs.io/

---

**Installation complete! Enjoy monitoring your camera feed with AI! 🚀**

