# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Web Browser (Client)                        │
│  ┌──────────────┐  ┌──────────────────┐  ┌─────────────────────┐  │
│  │ Latest Frame │  │ Vision Filters   │  │ Chat Interface      │  │
│  │ Display      │  │ Management       │  │                     │  │
│  └──────────────┘  └──────────────────┘  └─────────────────────┘  │
│         ▲                   ▲                        ▲              │
│         │                   │                        │              │
│         └───────────────────┴────────────────────────┘              │
│                             │                                        │
│                    JavaScript (app.js)                               │
│                    Polling every 2-3 seconds                         │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ HTTP/JSON
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Flask Web Server (app.py)                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                        REST API                                 │ │
│  │  /api/latest-frame  /api/filters  /api/chat                   │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              │                                        │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    FilterManager                                │ │
│  │  - Add/Remove/Move/Toggle filters                              │ │
│  │  - Evaluate filters against latest frame                       │ │
│  │  - Store results                                               │ │
│  └────────────────────────────────────────────────────────────────┘ │
│         │                                              │              │
│         ▼                                              ▼              │
│  ┌──────────────────┐                        ┌──────────────────┐   │
│  │ CameraCapture    │                        │ OpenAIHandler    │   │
│  │ (camera_capture) │                        │ (openai_handler) │   │
│  └──────────────────┘                        └──────────────────┘   │
└─────────┬────────────────────────────────────────────┬───────────────┘
          │                                            │
          ▼                                            ▼
┌──────────────────────┐                    ┌──────────────────────┐
│   IP Camera Feed     │                    │   OpenAI GPT-4o      │
│ http://10.0.0.197... │                    │   Vision API         │
└──────────────────────┘                    └──────────────────────┘
          │                                            │
          ▼                                            ▼
┌──────────────────────┐                    ┌──────────────────────┐
│  Local File System   │                    │   API Response       │
│  exp_time_XXXXXX/    │                    │   True / False       │
│  - frame_001.jpg     │                    └──────────────────────┘
│  - frame_002.jpg     │
│  - ...               │
└──────────────────────┘
```

## Component Details

### 1. Camera Capture Thread

```
┌─────────────────────────────────────────────────────────┐
│              CameraCapture Thread                        │
│                                                          │
│  Loop (every 1 second):                                 │
│    1. HTTP GET → Camera URL                             │
│    2. Receive JPEG image                                │
│    3. Save to disk: exp_time_XXXXXX/frame_XXXXXX.jpg   │
│    4. Update latest_frame_path (thread-safe)           │
│    5. Sleep until next interval                         │
└─────────────────────────────────────────────────────────┘
```

### 2. Filter Evaluation Thread

```
┌─────────────────────────────────────────────────────────┐
│           Filter Evaluation Thread                       │
│                                                          │
│  Loop (every 1 second):                                 │
│    1. Get latest frame path                             │
│    2. Get all active filters                            │
│    3. For each active filter:                           │
│       a. Encode image to base64                         │
│       b. Call OpenAI API with prompt + image            │
│       c. Parse response (True/False)                    │
│       d. Store result                                   │
│    4. Sleep until next interval                         │
└─────────────────────────────────────────────────────────┘
```

### 3. Frontend Update Cycle

```
┌─────────────────────────────────────────────────────────┐
│              Frontend Update Cycle                       │
│                                                          │
│  Timer 1 (every 2 seconds):                             │
│    → GET /api/latest-frame                              │
│    → Update image display                               │
│                                                          │
│  Timer 2 (every 3 seconds):                             │
│    → GET /api/filters                                   │
│    → Update filter list with results                    │
│    → Update switch colors (green/red/gray)              │
└─────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### Adding a New Filter

```
User Input
    │
    ▼
[Enter Prompt] → [Click "Add Filter"]
    │
    ▼
POST /api/filters
    │
    ▼
FilterManager.add_filter()
    │
    ├─→ Create filter object
    │   - id: unique timestamp
    │   - prompt: user input
    │   - is_active: true
    │   - order: position
    │
    ├─→ Add to filters list
    │
    └─→ Initialize result: None
    │
    ▼
Return filter object
    │
    ▼
Frontend updates UI
    │
    └─→ New filter block appears
```

### Filter Evaluation Process

```
Latest Frame Available
    │
    ▼
Filter Evaluation Loop
    │
    ├─→ Get active filters
    │
    └─→ For each filter:
            │
            ▼
        Encode image (base64)
            │
            ▼
        OpenAI API Call
            │
            ├─→ Headers: Authorization
            │
            ├─→ Body: {
            │       model: "gpt-4o",
            │       messages: [
            │         {
            │           role: "user",
            │           content: [
            │             {type: "text", text: prompt},
            │             {type: "image_url", url: base64_image}
            │           ]
            │         }
            │       ]
            │     }
            │
            ▼
        Response: "True" or "False"
            │
            ▼
        Parse to Boolean
            │
            ├─→ "true"/"yes" → True
            ├─→ "false"/"no" → False
            └─→ other → None
            │
            ▼
        Store result in FilterManager
            │
            ▼
        Frontend polls and updates switch color
```

### Theme Toggle Flow

```
User clicks theme button
    │
    ▼
JavaScript toggles state
    │
    ├─→ Current: "light" → New: "dark"
    └─→ Current: "dark" → New: "light"
    │
    ▼
Update DOM attribute
    │
    └─→ document.documentElement.setAttribute('data-theme', newTheme)
    │
    ▼
CSS variables update
    │
    ├─→ --bg-primary
    ├─→ --text-primary
    ├─→ --border-color
    └─→ ... (all theme variables)
    │
    ▼
Save to localStorage
    │
    └─→ localStorage.setItem('theme', newTheme)
```

## Threading Model

```
┌─────────────────────────────────────────────────────────┐
│                    Main Thread                           │
│  - Flask HTTP Server                                    │
│  - Handle API requests                                  │
│  - Serve static files                                   │
└─────────────────────────────────────────────────────────┘
                    │
                    ├─→ Spawns
                    │
┌─────────────────────────────────────────────────────────┐
│              Background Thread 1                         │
│  - CameraCapture.capture_loop()                         │
│  - Continuously fetches frames                          │
│  - Thread-safe: uses lock for latest_frame_path        │
└─────────────────────────────────────────────────────────┘
                    │
                    ├─→ Spawns
                    │
┌─────────────────────────────────────────────────────────┐
│              Background Thread 2                         │
│  - filter_evaluation_loop()                             │
│  - Evaluates active filters                             │
│  - Thread-safe: uses FilterManager.lock                │
└─────────────────────────────────────────────────────────┘
```

## State Management

### Backend State (Python)

```python
# Global state in app.py
camera_capture: CameraCapture
    - latest_frame_path: str (thread-safe)
    - base_folder: Path
    - is_running: bool

filter_manager: FilterManager
    - filters: List[dict] (thread-safe with lock)
    - results: Dict[str, bool] (thread-safe with lock)
    - lock: threading.Lock
```

### Frontend State (JavaScript)

```javascript
// State object in app.js
state = {
    theme: 'light' | 'dark',        // Persisted to localStorage
    filters: Array<Filter>,          // Synced from backend
    latestFrame: string | null,      // Latest frame path
    updateInterval: number | null    // Timer reference
}

// Filter object structure
Filter = {
    id: string,           // Unique identifier
    prompt: string,       // User's question
    is_active: boolean,   // Toggle state
    order: number,        // Display order
    result: boolean | null // True/False/None
}
```

## API Request/Response Formats

### GET /api/latest-frame

**Response:**
```json
{
    "success": true,
    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "path": "exp_time_20231218_143022/frame_20231218_143045_123.jpg"
}
```

### GET /api/filters

**Response:**
```json
{
    "success": true,
    "filters": [
        {
            "id": "filter_1702912345678",
            "prompt": "Is there a cap on the bottle?",
            "is_active": true,
            "order": 0,
            "result": true
        },
        {
            "id": "filter_1702912345679",
            "prompt": "Is there a person visible?",
            "is_active": true,
            "order": 1,
            "result": false
        }
    ]
}
```

### POST /api/filters

**Request:**
```json
{
    "prompt": "Is there a cap on the bottle? Respond only True for Yes and False for No."
}
```

**Response:**
```json
{
    "success": true,
    "filter": {
        "id": "filter_1702912345680",
        "prompt": "Is there a cap on the bottle?",
        "is_active": true,
        "order": 2
    }
}
```

## Security Considerations

### API Key Protection

```
.env file (NOT in git)
    │
    ▼
Environment Variables
    │
    ▼
Python os.environ.get()
    │
    ▼
OpenAI Client
    │
    └─→ HTTPS to api.openai.com
```

### Network Security

```
Camera (Private Network)
    │
    └─→ 10.0.0.197:8080 (Local IP)
    
Flask Server
    │
    ├─→ Development: localhost:5000
    └─→ Production: Should use HTTPS + Auth
```

## Performance Optimization Opportunities

### Current Implementation
- Polling every 2-3 seconds
- Sequential filter evaluation
- No caching

### Potential Improvements

```
1. WebSocket Communication
   Polling → WebSocket
   - Real-time updates
   - Lower latency
   - Reduced overhead

2. Parallel Filter Evaluation
   Sequential → ThreadPoolExecutor
   - Faster evaluation
   - Better resource usage

3. Result Caching
   No cache → LRU Cache
   - Skip unchanged frames
   - Reduce API calls
   - Lower costs

4. Frame Compression
   Full quality → Optimized
   - Smaller files
   - Less disk space
   - Faster transmission
```

## Deployment Architecture

### Development
```
Single Machine
    │
    ├─→ Python Flask (Development Server)
    ├─→ Static Files (Served by Flask)
    └─→ SQLite (Future: if adding persistence)
```

### Production (Recommended)
```
┌─────────────────────────────────────────┐
│         Reverse Proxy (nginx)           │
│  - HTTPS termination                    │
│  - Static file serving                  │
│  - Load balancing                       │
└─────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│      WSGI Server (gunicorn)             │
│  - Multiple worker processes            │
│  - Better performance                   │
└─────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│         Flask Application               │
│  - app.py                               │
│  - Background threads                   │
└─────────────────────────────────────────┘
```

---

**Note:** This architecture is designed for simplicity and clarity. For production use, consider adding authentication, database persistence, WebSocket support, and proper error handling.

