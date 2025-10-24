# LLM Inference - Model Comparison Tool

Compare responses from different Large Language Models (LLMs) side by side.

**Simple Setup:**
- Backend runs on cloud GPU (Lightning.ai, RunPod, etc.)
- Frontend hardcoded with backend URL
- No complex configs needed!

## Features

- 🔄 Side-by-side model comparison
- 🎨 Modern, responsive UI
- ☁️ Cloud-ready backend
- 📊 Multiple model support (GPT-2, TinyLlama, Mistral, Llama 2, etc.)

## Quick Start

### 1. Deploy Backend to Cloud

Upload `backend/` folder to your cloud GPU environment and run:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Get your backend URL (e.g., `https://abc123.lightning.ai`)

### 2. Update Frontend

Edit `src/App.js` line 5:
```javascript
const API_URL = 'https://your-backend-url.com';  // Replace with your URL
```

### 3. Run Frontend

```bash
npm install
npm start
```

Done! See [SIMPLE_SETUP.md](SIMPLE_SETUP.md) for details.

## Prerequisites

- Node.js 14+ and npm
- Python 3.8+
- Cloud GPU environment for backend

## Backend Configuration

Edit `backend/.env`:
```bash
# TGI Endpoints (where your models are running)
TGI_GPT2_ENDPOINT=http://localhost:8080
TGI_TINYLLAMA_ENDPOINT=http://localhost:8081

# CORS (allow all for simplicity)
ALLOWED_ORIGINS=*

HOST=0.0.0.0
PORT=8000
```

## Frontend Configuration

Edit `src/App.js` line 5:
```javascript
const API_URL = 'https://your-backend-url.com';
```

That's it!

## Troubleshooting

**Frontend shows "Backend Disconnected":**
- Check `src/App.js` has correct backend URL
- Verify backend is running: `curl https://your-backend-url/`

**Models show as unavailable (✗):**
- Check TGI containers are running
- Verify endpoints in `backend/.env`

**CORS errors:**
- Set `ALLOWED_ORIGINS=*` in `backend/.env`

## Documentation

- [SIMPLE_SETUP.md](SIMPLE_SETUP.md) - Step-by-step setup guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Cloud deployment details
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation
- [backend/README.md](backend/README.md) - Backend details
