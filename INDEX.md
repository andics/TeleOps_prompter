# Camera Feed Monitor - Documentation Index

Welcome to the Camera Feed Monitor documentation! This index will help you find the information you need.

## 🚀 Getting Started

Start here if you're new to the project:

1. **[INSTALLATION.md](INSTALLATION.md)** - Complete installation guide
   - Prerequisites and requirements
   - Step-by-step setup instructions
   - Troubleshooting common issues
   - Verification checklist

2. **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes
   - Quick installation steps
   - Basic usage instructions
   - Keyboard shortcuts
   - Example filters to try

## 📖 Main Documentation

### Core Documentation

- **[README.md](README.md)** - Main project documentation
  - Project overview and features
  - Installation and usage
  - API endpoints
  - Configuration options
  - Troubleshooting guide

- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Detailed project information
  - Architecture and design
  - Component descriptions
  - Data flow diagrams
  - Performance characteristics
  - Future enhancements

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
  - High-level overview diagrams
  - Component details
  - Threading model
  - API request/response formats
  - Deployment architecture

## 🎯 Usage Guides

- **[CAMERA_SETUP.md](CAMERA_SETUP.md)** - Camera configuration guide
  - Fix HTML vs Image issues
  - IP Webcam app setup
  - Finding the correct camera URL
  - Testing camera endpoints
  - Troubleshooting camera connections

- **[FILTER_EXAMPLES.md](FILTER_EXAMPLES.md)** - Vision filter examples
  - 100+ example prompts
  - Use case scenarios
  - Tips for writing effective filters
  - Troubleshooting filter results
  - Performance optimization

## 🔧 Configuration

- **[.env.example](.env.example)** - Environment variables template
  - OpenAI API key configuration
  - Camera URL settings
  - Flask configuration options

- **[config.example.py](config.example.py)** - Advanced configuration
  - Development/production configs
  - Performance tuning
  - Feature toggles

## 🛠️ Development

### Source Code Files

#### Backend (Python)
- **[app.py](app.py)** - Main Flask application
  - REST API endpoints
  - Filter management
  - Background threads

- **[camera_capture.py](camera_capture.py)** - Camera capture module
  - Frame capture logic
  - Thread-safe operations
  - Storage management

- **[openai_handler.py](openai_handler.py)** - OpenAI API integration
  - GPT-4o Vision API wrapper
  - Image encoding
  - Response parsing

#### Frontend
- **[templates/index.html](templates/index.html)** - Main HTML template
  - 3-column layout
  - Semantic structure

- **[static/css/styles.css](static/css/styles.css)** - Application styles
  - Dark/light themes
  - Responsive design
  - Modern flat UI

- **[static/js/app.js](static/js/app.js)** - Frontend JavaScript
  - State management
  - API communication
  - Real-time updates

### Utility Scripts

- **[test_setup.py](test_setup.py)** - Setup verification script
  - Test Python version
  - Verify dependencies
  - Check API connectivity
  - Validate configuration

- **[run.bat](run.bat)** - Windows startup script
  - Auto-creates virtual environment
  - Installs dependencies
  - Starts application

- **[run.sh](run.sh)** - Linux/Mac startup script
  - Auto-creates virtual environment
  - Installs dependencies
  - Starts application

### Dependencies

- **[requirements.txt](requirements.txt)** - Python package dependencies
  - Flask, flask-cors
  - requests, Pillow
  - openai, python-dotenv

## 📚 Documentation by Topic

### Installation & Setup
1. [INSTALLATION.md](INSTALLATION.md) - Complete installation guide
2. [QUICKSTART.md](QUICKSTART.md) - Quick start guide
3. [test_setup.py](test_setup.py) - Setup verification

### Usage & Features
1. [README.md](README.md) - Main usage documentation
2. [FILTER_EXAMPLES.md](FILTER_EXAMPLES.md) - Filter examples
3. [QUICKSTART.md](QUICKSTART.md) - Basic usage

### Architecture & Design
1. [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
2. [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Project overview
3. Source code files (well-commented)

### Configuration & Customization
1. [.env.example](.env.example) - Environment variables
2. [config.example.py](config.example.py) - Advanced config
3. [README.md](README.md) - Configuration section

### Troubleshooting
1. [INSTALLATION.md](INSTALLATION.md) - Installation issues
2. [README.md](README.md) - Common problems
3. [test_setup.py](test_setup.py) - Diagnostic tool

## 🎓 Learning Path

### For End Users

```
1. Read QUICKSTART.md
   ↓
2. Run test_setup.py
   ↓
3. Start the application
   ↓
4. Try examples from FILTER_EXAMPLES.md
   ↓
5. Refer to README.md as needed
```

### For Developers

```
1. Read PROJECT_OVERVIEW.md
   ↓
2. Study ARCHITECTURE.md
   ↓
3. Review source code files
   ↓
4. Read inline code comments
   ↓
5. Experiment with modifications
```

### For System Administrators

```
1. Read INSTALLATION.md
   ↓
2. Review ARCHITECTURE.md (Deployment section)
   ↓
3. Configure .env file
   ↓
4. Run test_setup.py
   ↓
5. Deploy and monitor
```

## 📋 Quick Reference

### Common Tasks

| Task | Documentation |
|------|---------------|
| Install the application | [INSTALLATION.md](INSTALLATION.md) |
| Quick start | [QUICKSTART.md](QUICKSTART.md) |
| Add a filter | [FILTER_EXAMPLES.md](FILTER_EXAMPLES.md) |
| Configure API key | [INSTALLATION.md](INSTALLATION.md#step-4-configure-openai-api-key) |
| Change camera URL | [CAMERA_SETUP.md](CAMERA_SETUP.md) or [INSTALLATION.md](INSTALLATION.md#step-5-configure-camera-url) |
| Troubleshoot issues | [INSTALLATION.md](INSTALLATION.md#troubleshooting) |
| Understand architecture | [ARCHITECTURE.md](ARCHITECTURE.md) |
| API endpoints | [README.md](README.md#api-endpoints) |
| Customize UI | [static/css/styles.css](static/css/styles.css) |
| Modify behavior | [app.py](app.py) |

### File Purpose Quick Reference

| File | Purpose |
|------|---------|
| `app.py` | Main Flask application and API |
| `camera_capture.py` | Camera frame capture logic |
| `openai_handler.py` | OpenAI API integration |
| `templates/index.html` | Web interface HTML |
| `static/css/styles.css` | UI styling and themes |
| `static/js/app.js` | Frontend JavaScript logic |
| `requirements.txt` | Python dependencies |
| `.env` | Configuration (create from .env.example) |
| `test_setup.py` | Setup verification tool |
| `run.bat` / `run.sh` | Startup scripts |

## 🔍 Search Tips

Looking for specific information? Use these keywords:

- **Installation**: INSTALLATION.md, QUICKSTART.md
- **API Key**: INSTALLATION.md, .env.example
- **Camera Setup**: CAMERA_SETUP.md, INSTALLATION.md, README.md
- **Filters**: FILTER_EXAMPLES.md, README.md
- **Troubleshooting**: INSTALLATION.md, README.md
- **Architecture**: ARCHITECTURE.md, PROJECT_OVERVIEW.md
- **Configuration**: .env.example, config.example.py
- **API Endpoints**: README.md, ARCHITECTURE.md
- **Themes**: styles.css, app.js
- **Performance**: PROJECT_OVERVIEW.md, ARCHITECTURE.md

## 📞 Support Resources

### Documentation
- Start with the relevant .md file from this index
- Check inline code comments
- Review example configurations

### External Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Python Documentation](https://docs.python.org/3/)

### Diagnostic Tools
- Run `python test_setup.py` to check your setup
- Check browser console (F12) for frontend errors
- Review terminal output for backend errors

## 🎯 Next Steps

### If you're just starting:
→ Go to [QUICKSTART.md](QUICKSTART.md)

### If you need detailed installation:
→ Go to [INSTALLATION.md](INSTALLATION.md)

### If you want to understand the system:
→ Go to [ARCHITECTURE.md](ARCHITECTURE.md)

### If you need filter examples:
→ Go to [FILTER_EXAMPLES.md](FILTER_EXAMPLES.md)

### If you have issues:
→ Go to [INSTALLATION.md](INSTALLATION.md#troubleshooting)

## 📝 Documentation Version

This documentation is for Camera Feed Monitor v1.0

Last updated: December 18, 2025

---

**Happy monitoring! 🎥✨**

