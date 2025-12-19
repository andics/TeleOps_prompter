# Camera Feed Monitor with AI Vision Filters

A modern web application that captures frames from a camera feed and applies real-time AI vision filters using OpenAI's GPT-4o Vision API.

## Features

- **Real-time Camera Feed Capture**: Automatically captures frames every second from IP cameras (supports both snapshot URLs and MJPEG video streams)
- **AI Vision Filters**: Apply custom vision prompts to analyze images using GPT-4o
- **Modern UI**: Beautiful, responsive interface with dark/light theme toggle
- **Filter Management**: Add, remove, reorder, and toggle filters dynamically
- **Visual Feedback**: Green/red indicators show filter results in real-time
- **Chat Interface**: Interactive chat panel for monitoring and communication

## Project Structure

```
.
├── app.py                  # Main Flask application
├── camera_capture.py       # Camera feed capture module
├── openai_handler.py       # OpenAI API integration
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── css/
│   │   └── styles.css     # Application styles
│   └── js/
│       └── app.js         # Frontend JavaScript
└── exp_time_*/            # Captured frames (auto-created)
```

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Camera feed accessible at `http://10.0.0.197:8080/cam_c` (or modify the URL in `app.py`)

### Setup Steps

1. **Clone or navigate to the project directory**

```bash
cd Q:\Projects\TeleOps\Programming
```

2. **Create an environment (recommended)**

**Using Conda (Recommended):**
```bash
conda create -n teleops_prompter python=3.10 -y
conda activate teleops_prompter
```

**Or using venv:**
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/Mac
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up OpenAI API key**

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Or set it as an environment variable:

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your_openai_api_key_here"

# Linux/Mac
export OPENAI_API_KEY="your_openai_api_key_here"
```

5. **Update camera URL (if needed)**

If your camera feed is at a different address, edit `.env` file:

```env
CAMERA_URL=http://YOUR_CAMERA_IP:PORT/shot.jpg
```

**Supported endpoints:**
- `/shot.jpg` - Single snapshot
- `/photo.jpg` - Alternative snapshot  
- `/video` - MJPEG stream ✓ **Now supported!**
- `/cam_c` - IP Webcam stream ✓ **Now supported!**

**Note:** The app automatically detects whether your URL is a snapshot or video stream and handles it appropriately!

## Usage

### Starting the Application

1. **Run the Flask server**

**Windows (automated with Conda):**
```cmd
run.bat
```

**Or manually:**
```bash
conda activate teleops_prompter  # If using Conda
python app.py
```

2. **Open your browser**

Navigate to: `http://localhost:5000`

### Using the Interface

#### Left Panel: Latest Frame
- Displays the most recent captured frame from the camera
- Updates automatically every 2 seconds
- Status indicator shows connection status (green = active)

#### Middle Panel: Vision Filters
- **Add a Filter**: Enter a prompt in the text area and click "Add Filter"
  - Example: "Is there a cap on the bottle in this photo? Respond only True for Yes and False for No."
- **Toggle Filter**: Click the switch to enable/disable a filter
  - Green = True result
  - Red = False result
  - Gray = Inactive
- **Reorder Filters**: Use ↑↓ buttons to change filter order
- **Remove Filter**: Click × to delete a filter

#### Right Panel: Chat
- Monitor system messages
- Future expansion for AI chat about the images

#### Top Right: Theme Toggle
- Click the sun/moon icon to switch between light and dark themes
- Theme preference is saved locally

## Example Filter Prompts

Here are some example prompts you can use:

```
"Is there a cap on the bottle in this photo? Respond only True for Yes and False for No."

"Is there a person visible in this image? Respond only True for Yes and False for No."

"Is the red light turned on? Respond only True for Yes and False for No."

"Are there more than 3 objects on the table? Respond only True for Yes and False for No."

"Is the door open? Respond only True for Yes and False for No."
```

## How It Works

1. **Frame Capture**: The `camera_capture.py` module continuously fetches frames from the camera URL and saves them to a timestamped folder (`exp_time_YYYYMMDD_HHMMSS/`)

2. **Filter Evaluation**: Every second, the application:
   - Gets the latest captured frame
   - Sends it to GPT-4o Vision API with each active filter prompt
   - Parses the response (True/False)
   - Updates the UI with visual feedback

3. **Real-time Updates**: The frontend polls the backend every 2-3 seconds to get:
   - Latest frame image
   - Updated filter results
   - System status

## Architecture

### Backend (Python/Flask)
- **app.py**: Main application with REST API endpoints
- **camera_capture.py**: Threaded frame capture system
- **openai_handler.py**: OpenAI API wrapper with base64 image encoding

### Frontend (HTML/CSS/JavaScript)
- **index.html**: Responsive 3-column layout
- **styles.css**: Modern flat design with CSS variables for theming
- **app.js**: State management, API communication, and UI updates

## API Endpoints

- `GET /` - Main application page
- `GET /api/latest-frame` - Get latest captured frame (base64)
- `GET /api/filters` - Get all filters with results
- `POST /api/filters` - Add a new filter
- `DELETE /api/filters/<id>` - Remove a filter
- `POST /api/filters/<id>/move` - Move filter up/down
- `POST /api/filters/<id>/toggle` - Toggle filter active state
- `POST /api/chat` - Send chat message

## Troubleshooting

### Camera Connection Issues
- Verify the camera URL is accessible: `http://10.0.0.197:8080/cam_c`
- Check network connectivity
- Ensure camera is streaming in a compatible format (JPEG/MJPEG)

### OpenAI API Issues
- Verify API key is set correctly
- Check API quota/billing status
- Review console logs for error messages

### Performance
- Adjust `capture_interval` in `app.py` if 1 frame/second is too frequent
- Reduce number of active filters to decrease API calls
- Monitor OpenAI API usage costs

## Customization

### Changing Capture Interval
Edit `app.py` line 109:
```python
capture_interval=2.0  # Capture every 2 seconds instead
```

### Adjusting Update Frequency
Edit `static/js/app.js` lines 273-277:
```javascript
setInterval(updateLatestFrame, 5000);  // Update frame every 5 seconds
setInterval(loadFilters, 5000);  // Update filters every 5 seconds
```

### Styling
- Edit `static/css/styles.css` to customize colors and layout
- CSS variables are defined at the top for easy theming

## License

This project is provided as-is for educational and monitoring purposes.

## Notes

- Captured frames are stored locally and not deleted automatically
- Monitor disk space if running for extended periods
- OpenAI API calls incur costs - monitor your usage
- The application is designed for local network use

## Support

For issues or questions, refer to:
- Flask documentation: https://flask.palletsprojects.com/
- OpenAI API docs: https://platform.openai.com/docs/
- Project source code comments

