# Project Structure

```
llm-inference/
│
├── 📱 FRONTEND (React)
│   ├── public/                      # Static assets
│   │   ├── index.html              # Main HTML template
│   │   ├── favicon.ico
│   │   └── manifest.json
│   │
│   ├── src/
│   │   ├── App.js                  # Main React component
│   │   │                           # - Model selection dropdowns
│   │   │                           # - Chat interface
│   │   │                           # - Backend API integration
│   │   │
│   │   ├── App.css                 # Styling
│   │   │                           # - Gradient background
│   │   │                           # - Side-by-side layout
│   │   │                           # - Responsive design
│   │   │
│   │   ├── index.js                # React entry point
│   │   └── index.css               # Global styles
│   │
│   ├── package.json                # npm dependencies
│   └── package-lock.json
│
├── 🔧 BACKEND (FastAPI)
│   └── backend/
│       ├── main.py                 # FastAPI server
│       │                           # - TGI container management
│       │                           # - Docker integration
│       │                           # - API endpoints
│       │                           # - Model lifecycle management
│       │
│       ├── requirements.txt        # Python dependencies
│       │                           # - fastapi
│       │                           # - uvicorn
│       │                           # - docker
│       │                           # - httpx
│       │
│       ├── test_api.py            # API testing script
│       └── README.md              # Backend documentation
│
├── 📚 DOCUMENTATION
│   ├── README.md                   # Main project documentation
│   ├── QUICKSTART.md              # Getting started guide
│   ├── API_REFERENCE.md           # Complete API documentation
│   └── PROJECT_STRUCTURE.md       # This file
│
├── 🚀 SCRIPTS
│   └── start.sh                    # Easy startup script
│                                   # - Checks dependencies
│                                   # - Starts backend & frontend
│
└── ⚙️ CONFIG
    ├── .gitignore                 # Git ignore rules
    └── .env.example               # Environment variables template

```

## Component Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                          │
│                     http://localhost:3000                    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  React App (src/App.js)                            │    │
│  │                                                     │    │
│  │  • Model Selection Dropdowns                       │    │
│  │  • Chat Interface                                  │    │
│  │  • Message History                                 │    │
│  │  • Status Indicators                               │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                  │
│                           │ HTTP Requests                    │
│                           ▼                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            │ fetch('/generate', ...)
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                    FastAPI Backend                           │
│                  http://localhost:8000                       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  main.py                                           │    │
│  │                                                     │    │
│  │  Endpoints:                                        │    │
│  │  • GET  /models          (list available)         │    │
│  │  • POST /models/{id}/start  (start container)     │    │
│  │  • POST /models/{id}/stop   (stop container)      │    │
│  │  • POST /generate           (generate text)       │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                  │
│                           │ Docker Python SDK                │
│                           ▼                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            │ docker.containers.run(...)
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                      Docker Engine                           │
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  TGI Container  │  │  TGI Container  │                  │
│  │  (Model 1)      │  │  (Model 2)      │  ...             │
│  │                 │  │                 │                  │
│  │  GPT-2          │  │  TinyLlama      │                  │
│  │  Port: 8080     │  │  Port: 8081     │                  │
│  │                 │  │                 │                  │
│  │  /generate      │  │  /generate      │                  │
│  │  /health        │  │  /health        │                  │
│  └─────────────────┘  └─────────────────┘                  │
└──────────────────────────────────────────────────────────────┘
                            │
                            │ Model weights cached at:
                            ▼
                   ~/.cache/huggingface/
```

## Request Flow Example

1. **User** types "What is AI?" and selects GPT-2 & TinyLlama
2. **Frontend** sends two parallel POST requests to `/generate`
3. **Backend** receives requests:
   - Checks if containers are running
   - Starts containers if needed (downloads models first time)
   - Waits for containers to be ready
4. **Backend** forwards requests to TGI containers
5. **TGI Containers** generate text using the models
6. **Backend** returns generated text to frontend
7. **Frontend** displays both responses side-by-side

## Key Files Explained

### Frontend

**`src/App.js`** (176 lines)
- State management for models, messages, loading states
- API integration with backend
- Message handling and display logic
- Model selection UI

**`src/App.css`** (290 lines)
- Modern gradient design
- Responsive grid layout
- Smooth animations
- Mobile-friendly breakpoints

### Backend

**`backend/main.py`** (250+ lines)
- FastAPI application setup
- Docker client integration
- Container lifecycle management
- TGI communication
- Error handling

**`backend/requirements.txt`**
- Production-ready dependencies
- Minimal and focused

### Documentation

**`README.md`**
- Complete project overview
- Installation instructions
- Usage guide
- Troubleshooting

**`QUICKSTART.md`**
- Step-by-step getting started
- Common issues and solutions
- First-time user guide

**`API_REFERENCE.md`**
- Complete API documentation
- Request/response examples
- Error codes
- Model specifications

## Technologies Used

### Frontend
- **React 18** - UI framework
- **Fetch API** - HTTP requests
- **CSS3** - Modern styling with gradients and animations
- **Hooks** - useState, useEffect for state management

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Docker SDK** - Container management
- **HTTPX** - Async HTTP client
- **Pydantic** - Data validation

### Infrastructure
- **Docker** - Container runtime
- **HuggingFace TGI** - Text generation inference
- **HuggingFace Hub** - Model repository

## Model Storage

Models are cached locally to avoid re-downloading:

```
~/.cache/huggingface/
├── hub/
│   ├── models--gpt2/
│   ├── models--TinyLlama--TinyLlama-1.1B-Chat-v1.0/
│   └── models--mistralai--Mistral-7B-Instruct-v0.1/
└── ...
```

## Port Usage

- **3000**: React development server
- **8000**: FastAPI backend server
- **8080-8089**: TGI containers (dynamically allocated)

## Development vs Production

### Development (Current Setup)
- Frontend: React dev server (hot reload)
- Backend: Uvicorn with auto-reload
- Models: Downloaded on-demand

### Production Considerations
- Frontend: Build with `npm run build`, serve with nginx
- Backend: Use gunicorn with multiple workers
- Models: Pre-download and cache
- Add authentication and rate limiting
- Use environment variables for configuration
- Implement proper logging and monitoring

## Extending the Application

### Add a New Model

1. Edit `backend/main.py`:
```python
MODELS = {
    "my-model": "organization/model-name-on-hf",
}
```

2. Frontend will automatically fetch and display it!

### Add Model Configuration UI

Add to `src/App.js`:
- Temperature slider
- Max tokens input
- Top-p slider

### Add Streaming Responses

Modify backend to use TGI's streaming endpoint and frontend to handle Server-Sent Events (SSE).

### Add Authentication

Add middleware in backend:
```python
from fastapi.security import HTTPBearer
```

## Performance Considerations

### Memory Usage
- GPT-2: ~2GB RAM
- TinyLlama: ~4GB RAM  
- 7B models: ~16GB RAM

### Optimization Tips
1. Use smaller models for development
2. Limit concurrent containers
3. Implement container pooling
4. Add request queuing
5. Cache frequent prompts

## Security Notes

⚠️ **This is a development setup**

For production:
- Add authentication
- Implement rate limiting
- Validate all inputs
- Use HTTPS
- Secure Docker socket access
- Set resource limits on containers
- Add CORS restrictions
- Implement request timeouts

---

Built with ❤️ using React, FastAPI, and HuggingFace TGI

