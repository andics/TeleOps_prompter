# 🎥 Camera Feed Monitor - START HERE

## What is this?

A **Python-based web application** that:
- 📸 Captures frames from your IP camera every second
- 🤖 Analyzes images using OpenAI's GPT-4o Vision AI
- ✅ Applies custom filters to detect objects, conditions, and events
- 🎨 Provides a beautiful, modern web interface with dark/light themes

## Quick Visual Overview

```
┌─────────────────────────────────────────────────────────────┐
│  🎥 Camera Feed Monitor                          [🌓 Theme] │
├──────────────┬──────────────────────┬──────────────────────┤
│              │                      │                      │
│  📷 Latest   │  🎯 Vision Filters   │  💬 Chat            │
│  Frame       │                      │                      │
│              │  ┌─────────────────┐ │                      │
│  [Image]     │  │ Is there a cap  │ │  System ready...    │
│              │  │ on the bottle?  │ │                      │
│              │  │           [🟢]  │ │  [Type message...]  │
│              │  │        [↑][↓][×]│ │  [Send]             │
│              │  └─────────────────┘ │                      │
│              │                      │                      │
│              │  [Add Filter...]     │                      │
└──────────────┴──────────────────────┴──────────────────────┘

🟢 Green = True    🔴 Red = False    ⚪ Gray = Inactive
```

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies (2 minutes)

**Using Conda (Recommended):**
```bash
conda create -n teleops_prompter python=3.10 -y
conda activate teleops_prompter
pip install -r requirements.txt
```

**Or using pip directly:**
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Key (1 minute)

Create a `.env` file:
```env
OPENAI_API_KEY=sk-your-key-here
```

### Step 3: Run the Application (1 minute)

**Windows (Automated with Conda):**
```cmd
run.bat
```
This automatically creates/activates the `teleops_prompter` environment.

**Mac/Linux:**
```bash
./run.sh
```

**Or manually with Conda:**
```bash
conda activate teleops_prompter
python app.py
```

**Or directly:**
```bash
python app.py
```

Then open: **http://localhost:5000**

## ✨ Try Your First Filter

In the middle panel, enter:
```
Is there a person in this photo? Respond only True for Yes and False for No.
```

Click **"Add Filter"** and watch it work! 🎉

## 📚 Full Documentation

| Document | What's Inside | When to Read |
|----------|---------------|--------------|
| **[INDEX.md](INDEX.md)** | Documentation index | Finding specific info |
| **[QUICKSTART.md](QUICKSTART.md)** | 5-minute guide | First time setup |
| **[INSTALLATION.md](INSTALLATION.md)** | Detailed setup | Troubleshooting install |
| **[README.md](README.md)** | Complete manual | Understanding features |
| **[FILTER_EXAMPLES.md](FILTER_EXAMPLES.md)** | 100+ filter ideas | Creating filters |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System design | Understanding how it works |
| **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** | Project details | Deep dive |

## 🎯 Common Use Cases

### 🏭 Manufacturing
Monitor production lines for defects, proper assembly, and quality control.

### 🔒 Security
Detect unauthorized access, monitor restricted areas, check door states.

### 📦 Inventory
Track stock levels, verify product placement, monitor shelf conditions.

### 🏢 Office
Monitor occupancy, check equipment status, verify safety compliance.

### 🚗 Parking
Detect available spots, monitor entrance/exit, track vehicle presence.

## 🎨 Features Highlights

- ✅ **Real-time Monitoring** - Updates every 2-3 seconds
- ✅ **AI-Powered** - GPT-4o Vision for accurate detection
- ✅ **Beautiful UI** - Modern, flat design with dark/light themes
- ✅ **Easy Filters** - Add, remove, reorder, toggle on/off
- ✅ **Visual Feedback** - Green (True), Red (False), Gray (Inactive)
- ✅ **Modular Code** - Clean, object-oriented Python
- ✅ **Well Documented** - Comprehensive guides and examples
- ✅ **Easy Setup** - Automated scripts for quick start

## 🔧 Requirements

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **OpenAI API Key** - [Get one](https://platform.openai.com/)
- **IP Camera** - Any MJPEG/JPEG stream

## 📁 Project Structure

```
Camera-Feed-Monitor/
│
├── 📄 START_HERE.md          ← You are here!
├── 📄 INDEX.md               ← Documentation index
├── 📄 QUICKSTART.md          ← Quick start guide
├── 📄 INSTALLATION.md        ← Detailed setup
├── 📄 README.md              ← Main documentation
├── 📄 FILTER_EXAMPLES.md     ← Filter examples
├── 📄 ARCHITECTURE.md        ← System architecture
├── 📄 PROJECT_OVERVIEW.md    ← Project details
│
├── 🐍 app.py                 ← Main Flask app
├── 🐍 camera_capture.py      ← Camera module
├── 🐍 openai_handler.py      ← OpenAI integration
├── 🐍 test_setup.py          ← Setup verification
│
├── 📋 requirements.txt       ← Python dependencies
├── ⚙️ .env.example           ← Config template
├── ⚙️ config.example.py      ← Advanced config
│
├── 🪟 run.bat                ← Windows startup
├── 🐧 run.sh                 ← Linux/Mac startup
│
├── 📁 templates/
│   └── 🌐 index.html         ← Web interface
│
├── 📁 static/
│   ├── 📁 css/
│   │   └── 🎨 styles.css     ← Styling
│   └── 📁 js/
│       └── ⚡ app.js          ← Frontend logic
│
└── 📁 exp_time_*/            ← Captured frames (auto-created)
```

## ⚡ Quick Commands

### Verify Setup
```bash
python test_setup.py
```

### Start Application
```bash
python app.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Create Conda Environment
```bash
conda create -n teleops_prompter python=3.10 -y
conda activate teleops_prompter  # Activate the environment
```

### Or Create Virtual Environment (venv)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

## 🎓 Learning Path

### 👤 I'm a User
```
1. Read this file (START_HERE.md)
2. Follow QUICKSTART.md
3. Try FILTER_EXAMPLES.md
4. Refer to README.md as needed
```

### 👨‍💻 I'm a Developer
```
1. Read PROJECT_OVERVIEW.md
2. Study ARCHITECTURE.md
3. Review source code
4. Experiment with modifications
```

### 🔧 I'm an Admin
```
1. Read INSTALLATION.md
2. Run test_setup.py
3. Configure .env
4. Deploy and monitor
```

## ❓ Need Help?

### Installation Issues?
→ [INSTALLATION.md](INSTALLATION.md#troubleshooting)

### Camera not working?
→ [CAMERA_SETUP.md](CAMERA_SETUP.md) - Fix HTML vs Image issues

### Don't know what filter to create?
→ [FILTER_EXAMPLES.md](FILTER_EXAMPLES.md)

### Want to understand how it works?
→ [ARCHITECTURE.md](ARCHITECTURE.md)

### Looking for specific info?
→ [INDEX.md](INDEX.md)

### General questions?
→ [README.md](README.md)

## 🎯 Next Steps

Choose your path:

### 🏃 I want to start NOW
→ Run: `python test_setup.py` then `python app.py`

### 📖 I want to read first
→ Open: [QUICKSTART.md](QUICKSTART.md)

### 🔍 I want detailed setup
→ Open: [INSTALLATION.md](INSTALLATION.md)

### 💡 I want filter ideas
→ Open: [FILTER_EXAMPLES.md](FILTER_EXAMPLES.md)

### 🏗️ I want to understand the system
→ Open: [ARCHITECTURE.md](ARCHITECTURE.md)

## 🎉 Example Session

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
echo "OPENAI_API_KEY=sk-your-key" > .env

# 3. Test
python test_setup.py

# 4. Run
python app.py

# 5. Open browser
# http://localhost:5000

# 6. Add a filter
# "Is there a bottle in this photo? Respond only True for Yes and False for No."

# 7. Watch it work! 🎉
```

## 📊 What You'll See

### Left Panel
- Latest frame from your camera
- Updates every 2 seconds
- Status indicator (green = active)

### Middle Panel
- Your vision filters
- Add/remove/reorder controls
- Toggle switches with color feedback
- Green = True, Red = False, Gray = Inactive

### Right Panel
- Chat interface
- System messages
- Future: AI conversation about images

### Top Right
- Theme toggle (sun/moon icon)
- Switch between light and dark modes

## 🌟 Key Features Explained

### Real-time Capture
Frames are captured every second and saved to `exp_time_XXXXXX/` folder.

### AI Vision Analysis
Each active filter sends the latest frame to GPT-4o with your prompt.

### Visual Feedback
- **Green Switch** = Filter condition is TRUE
- **Red Switch** = Filter condition is FALSE
- **Gray Switch** = Filter is inactive (toggle to activate)

### Filter Controls
- **↑** = Move filter up in list
- **↓** = Move filter down in list
- **×** = Remove filter
- **Switch** = Toggle active/inactive

## 💰 Cost Considerations

- OpenAI GPT-4o Vision API charges per image
- 1 active filter = 1 API call per second
- 5 active filters = 5 API calls per second
- Monitor your OpenAI usage dashboard
- Toggle off filters you don't need right now

## 🔒 Security Notes

- Keep your `.env` file private (never commit to git)
- API key starts with `sk-` and should be kept secret
- Camera should be on a private network
- Consider adding authentication for production use

## 🎨 Customization

### Change Camera URL
Edit `.env`:
```env
CAMERA_URL=http://your-camera-ip:port/path
```

### Change Capture Interval
Edit `.env`:
```env
CAPTURE_INTERVAL=2.0  # Capture every 2 seconds
```

### Change Theme Colors
Edit `static/css/styles.css` - CSS variables at the top

### Change Update Frequency
Edit `static/js/app.js` - lines 273-277

## 🏁 Ready to Start?

### Fastest Path (2 minutes):
```bash
# Windows - just run:
run.bat
# Then add your API key to .env when prompted

# Or manually:
conda create -n teleops_prompter python=3.10 -y
conda activate teleops_prompter
pip install -r requirements.txt
echo OPENAI_API_KEY=sk-your-key-here > .env
python app.py
# Open http://localhost:5000
```

### Safest Path (5 minutes):
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Run `python test_setup.py`
3. Follow the verification checklist
4. Start the application

### Learning Path (15 minutes):
1. Read this file completely
2. Skim [README.md](README.md)
3. Browse [FILTER_EXAMPLES.md](FILTER_EXAMPLES.md)
4. Run the application
5. Experiment!

---

## 🎊 You're All Set!

Pick your next step above and dive in. The application is designed to be intuitive and well-documented. Have fun monitoring your camera feed with AI! 🚀

**Questions?** Check [INDEX.md](INDEX.md) for the full documentation index.

**Issues?** See [INSTALLATION.md](INSTALLATION.md#troubleshooting) for troubleshooting.

**Ready?** Run `python app.py` and open http://localhost:5000

---

**Made with ❤️ using Python, Flask, and OpenAI GPT-4o Vision**

