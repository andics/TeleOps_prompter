# Camera Feed Monitor - Project Overview

## 🎯 Project Goal

A Python-based web application that monitors a camera feed, captures frames every second, and applies AI-powered vision filters using OpenAI's GPT-4o model to analyze the images in real-time.

## 🏗️ Architecture

### Backend (Python/Flask)

#### Core Modules

1. **app.py** - Main Flask application
   - REST API endpoints for filters, frames, and chat
   - Filter management system with threading
   - Real-time filter evaluation loop
   - Serves the web interface

2. **camera_capture.py** - Camera capture module
   - Threaded frame capture from IP camera
   - Saves frames to timestamped folders (`exp_time_YYYYMMDD_HHMMSS/`)
   - Captures 1 frame per second (configurable)
   - Thread-safe latest frame tracking

3. **openai_handler.py** - OpenAI API integration
   - GPT-4o Vision API wrapper
   - Base64 image encoding
   - Boolean response parsing (True/False)
   - Error handling and retry logic

### Frontend (HTML/CSS/JavaScript)

#### Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│  Header: Camera Feed Monitor        [Theme Toggle 🌓]  │
├──────────────┬──────────────────┬──────────────────────┤
│              │                  │                      │
│  Latest      │  Vision Filters  │      Chat           │
│  Frame       │                  │                      │
│              │  [Add Filter]    │  [Messages]         │
│  [Image]     │                  │                      │
│              │  ┌─────────────┐ │  [Input]            │
│              │  │ Filter 1    │ │  [Send]             │
│              │  │ [●] ↑↓✕     │ │                      │
│              │  └─────────────┘ │                      │
│              │  ┌─────────────┐ │                      │
│              │  │ Filter 2    │ │                      │
│              │  │ [●] ↑↓✕     │ │                      │
│              │  └─────────────┘ │                      │
└──────────────┴──────────────────┴──────────────────────┘
```

#### Files

1. **templates/index.html** - Main HTML structure
   - 3-column responsive grid layout
   - Semantic HTML5 elements
   - Accessible controls

2. **static/css/styles.css** - Modern styling
   - CSS variables for theming
   - Dark/light mode support
   - Flat, modern design
   - Smooth transitions and animations
   - Responsive breakpoints

3. **static/js/app.js** - Frontend logic
   - State management
   - API communication
   - Real-time updates (polling)
   - Filter CRUD operations
   - Theme persistence

## 🔄 Data Flow

### Frame Capture Flow
```
Camera Feed → camera_capture.py → Save to disk → Update latest_frame_path
                                                          ↓
                                                   API: /api/latest-frame
                                                          ↓
                                                   Frontend displays
```

### Filter Evaluation Flow
```
User adds filter → POST /api/filters → FilterManager.add_filter()
                                              ↓
                                    Background evaluation loop
                                              ↓
                        Get latest frame + active filters
                                              ↓
                        For each filter: OpenAI API call
                                              ↓
                        Parse response (True/False)
                                              ↓
                        Update filter results
                                              ↓
                        GET /api/filters → Frontend updates UI
```

## 🎨 Design Features

### Color Scheme
- **Light Theme**: Clean whites and grays with purple accents
- **Dark Theme**: Deep navy with bright accents
- **Status Colors**:
  - Green (#10b981): Active/True
  - Red (#ef4444): False
  - Gray (#6b7280): Inactive

### UI/UX Features
- **Responsive Design**: Works on desktop, tablet, mobile
- **Real-time Updates**: Auto-refresh every 2-3 seconds
- **Visual Feedback**: Animated transitions, hover effects
- **Keyboard Shortcuts**: Ctrl+Enter to submit
- **Persistent Theme**: Saved to localStorage
- **Smooth Animations**: CSS transitions for all state changes

### Filter Block Design
```
┌─────────────────────────────────────────┐
│ Is there a cap on the bottle?    [●]   │  ← Switch (Green/Red/Gray)
│                                         │
│                              [↑][↓][✕] │  ← Controls
└─────────────────────────────────────────┘
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main application page |
| GET | `/api/latest-frame` | Get latest frame (base64) |
| GET | `/api/filters` | Get all filters with results |
| POST | `/api/filters` | Add new filter |
| DELETE | `/api/filters/<id>` | Remove filter |
| POST | `/api/filters/<id>/move` | Move filter up/down |
| POST | `/api/filters/<id>/toggle` | Toggle filter on/off |
| POST | `/api/chat` | Send chat message |

## 🔧 Configuration

### Environment Variables (.env)
```env
OPENAI_API_KEY=sk-...           # Required
CAMERA_URL=http://...           # Optional (default: 10.0.0.197:8080/cam_c)
CAPTURE_INTERVAL=1.0            # Optional (default: 1.0 seconds)
```

### Adjustable Parameters

**In app.py:**
- Camera URL
- Capture interval
- Filter evaluation frequency

**In static/js/app.js:**
- Frame update interval (line 273)
- Filter update interval (line 276)

## 🚀 Deployment

### Local Development
```bash
python app.py
# Access at http://localhost:5000
```

### Production Considerations
- Use a production WSGI server (gunicorn, waitress)
- Set up reverse proxy (nginx, Apache)
- Enable HTTPS
- Configure CORS properly
- Monitor disk space for captured frames
- Set up log rotation
- Monitor OpenAI API usage/costs

### Example Production Setup
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📊 Performance Characteristics

### Resource Usage
- **CPU**: Low (mostly I/O bound)
- **Memory**: ~50-100 MB base + images in memory
- **Disk**: ~100-500 KB per frame (depends on image size)
- **Network**: Continuous camera stream + OpenAI API calls

### Scalability Considerations
- **Frames**: 1 frame/second = ~86,400 frames/day
- **Disk Space**: ~8-40 GB/day (estimate)
- **API Calls**: 1 call per active filter per second
- **Cost**: OpenAI Vision API pricing applies

### Optimization Tips
1. Reduce capture interval if less frequent monitoring is acceptable
2. Implement frame cleanup (delete old frames)
3. Compress images before saving
4. Batch filter evaluations
5. Cache results for unchanged frames
6. Use webhooks instead of polling

## 🔒 Security Considerations

1. **API Key Protection**
   - Never commit .env file
   - Use environment variables
   - Rotate keys regularly

2. **Network Security**
   - Camera feed should be on private network
   - Use HTTPS in production
   - Implement authentication for web interface

3. **Input Validation**
   - Sanitize filter prompts
   - Validate image data
   - Rate limit API calls

## 🧪 Testing Recommendations

### Manual Testing Checklist
- [ ] Camera connection and frame capture
- [ ] Add/remove/reorder filters
- [ ] Toggle filter active state
- [ ] Theme switching
- [ ] Real-time updates
- [ ] Error handling (no camera, no API key)
- [ ] Responsive design on different screens

### Automated Testing (Future)
- Unit tests for each module
- Integration tests for API endpoints
- Frontend tests with Jest/Cypress
- Load testing for concurrent users

## 📈 Future Enhancements

### Potential Features
1. **Advanced Chat**: Full conversation with GPT-4o about images
2. **Filter Templates**: Pre-built filter library
3. **Alerts**: Notifications when filters trigger
4. **History**: View past frames and results
5. **Analytics**: Charts and statistics
6. **Multi-Camera**: Support multiple camera feeds
7. **Recording**: Video recording on trigger
8. **Export**: Download frames and results
9. **Scheduling**: Time-based filter activation
10. **Mobile App**: Native iOS/Android app

### Technical Improvements
1. WebSocket for real-time updates (instead of polling)
2. Database for persistent storage (SQLite/PostgreSQL)
3. User authentication and multi-user support
4. Docker containerization
5. Kubernetes deployment
6. CI/CD pipeline
7. Automated testing suite
8. Performance monitoring (Prometheus/Grafana)

## 🐛 Known Limitations

1. **Polling**: Uses polling instead of WebSockets (simpler but less efficient)
2. **No Persistence**: Filters lost on server restart
3. **Single User**: No multi-user support
4. **No History**: Can't view past results
5. **Manual Cleanup**: Old frames not automatically deleted
6. **API Costs**: Can be expensive with many filters
7. **No Retry Logic**: Failed API calls not retried
8. **Camera Format**: Assumes JPEG/MJPEG stream

## 📚 Dependencies

### Python Packages
- **Flask**: Web framework
- **flask-cors**: CORS support
- **requests**: HTTP client for camera
- **Pillow**: Image processing
- **openai**: OpenAI API client
- **python-dotenv**: Environment variable loading

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **CSS3**: Modern styling features
- **HTML5**: Semantic markup

## 🤝 Contributing

### Code Style
- Python: PEP 8
- JavaScript: ES6+
- CSS: BEM-like naming

### Project Structure
```
.
├── app.py                    # Main application
├── camera_capture.py         # Camera module
├── openai_handler.py         # OpenAI module
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
├── README.md                # Main documentation
├── QUICKSTART.md            # Quick start guide
├── PROJECT_OVERVIEW.md      # This file
├── run.bat                  # Windows startup script
├── run.sh                   # Linux/Mac startup script
├── templates/
│   └── index.html          # Main HTML
└── static/
    ├── css/
    │   └── styles.css      # Styles
    └── js/
        └── app.js          # Frontend logic
```

## 📞 Support

For issues or questions:
1. Check README.md and QUICKSTART.md
2. Review code comments
3. Check Flask and OpenAI documentation
4. Verify environment configuration

---

**Built with ❤️ using Python, Flask, and OpenAI GPT-4o**

