# LLM Inference - Model Comparison Tool

A full-stack application for comparing responses from different Large Language Models (LLMs) side by side. Built with React frontend and FastAPI backend that connects to cloud-hosted TGI (Text Generation Inference) instances.

## Features

- 🚀 **Cloud-Native**: Designed for cloud GPU deployments with TGI
- 🔄 **Side-by-Side Comparison**: Compare responses from two different models simultaneously
- 🎨 **Modern UI**: Beautiful, responsive interface with real-time status indicators
- ☁️ **Flexible Deployment**: Backend can run anywhere, TGI on GPU instances
- 📊 **Multiple Models**: Support for GPT-2, TinyLlama, Mistral, Llama 2, Falcon, and more
- 💚 **Health Monitoring**: Real-time TGI endpoint health checking

## Architecture

```
React Frontend → FastAPI Backend → Cloud GPU TGI Instances
```

- **Frontend**: React with modern hooks and state management
- **Backend**: FastAPI that proxies requests to TGI endpoints
- **Inference**: HuggingFace Text Generation Inference on cloud GPUs
- **Deployment**: TGI containers run on dedicated GPU instances

## Prerequisites

### For Frontend & Backend:
- Node.js 14+ and npm
- Python 3.8+

### For TGI (on GPU instances):
- Docker with NVIDIA GPU support
- NVIDIA GPU with 4GB+ VRAM
- 16GB+ system RAM for larger models

## Quick Start

### 1. Deploy TGI on Cloud GPU Instances

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed cloud deployment instructions.

Quick example on a GPU instance:
```bash
# On your GPU server
./backend/deploy_tgi.sh "gpt2" 8080
./backend/deploy_tgi.sh "TinyLlama/TinyLlama-1.1B-Chat-v1.0" 8081
```

### 2. Configure Backend

```bash
cd backend
cp .env.example .env
# Edit .env with your TGI endpoint URLs
nano .env
```

Example `.env`:
```bash
TGI_GPT2_ENDPOINT=http://your-gpu-server.com:8080
TGI_TINYLLAMA_ENDPOINT=http://your-gpu-server.com:8081
```

### 3. Install Dependencies

**Frontend:**
```bash
npm install
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

## Usage

### 1. Start TGI Instances (on GPU servers)

```bash
# Already running from deployment step
# Verify they're healthy:
curl http://your-gpu-server:8080/health
```

### 2. Start the Backend Server

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

On startup, you'll see health status of all configured TGI endpoints:
```
Starting LLM Inference API...
Configured models: ['gpt-2', 'tiny-llama', ...]
  gpt-2: http://gpu-server:8080
    ✓ Available
  tiny-llama: http://gpu-server:8081
    ✓ Available
```

### 3. Start the Frontend

In a new terminal:

```bash
npm start
```

The React app will open at `http://localhost:3000`

### 4. Use the Application

1. Select two different models from the dropdown menus (✓ = available, ✗ = unavailable)
2. Type your prompt in the input box
3. Press Enter or click "Send"
4. Both models will generate responses simultaneously
5. Compare the responses side by side!

## Available Models

- **GPT-2**: Small, fast model good for testing (~500MB)
- **TinyLlama 1.1B**: Lightweight but capable (~2GB)
- **Mistral 7B**: High-quality 7B parameter model (~14GB)
- **Llama 2 7B Chat**: Meta's chat model (requires HF access)
- **Falcon 7B Instruct**: Strong open-source model (~14GB)
- **Microsoft Phi-2**: Efficient 2.7B parameter model (~5GB)

## Configuration

### Backend Configuration

1. **Environment Variables** (`.env`):
   ```bash
   # TGI Endpoints
   TGI_GPT2_ENDPOINT=http://gpu1.example.com:8080
   TGI_TINYLLAMA_ENDPOINT=http://gpu2.example.com:8080
   
   # Server
   HOST=0.0.0.0
   PORT=8000
   
   # CORS
   ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
   ```

2. **Add New Models**:
   
   Edit `backend/main.py` MODELS dict:
   ```python
   MODELS = {
       "my-model": {
           "name": "My Model",
           "hf_name": "org/model-name",
           "endpoint": os.getenv("TGI_MYMODEL_ENDPOINT"),
       }
   }
   ```

### Frontend Configuration

Edit `src/App.js`:
```javascript
const API_URL = 'http://localhost:8000';  // Change for production
```

## API Endpoints

- `GET /` - API information and status
- `GET /models` - List all available models with health status
- `GET /models/{model_id}/health` - Check health of specific model endpoint
- `POST /generate` - Generate text from a model

See [API_REFERENCE.md](API_REFERENCE.md) for complete documentation.

## Troubleshooting

### Backend Can't Connect to TGI

```bash
# Check if TGI is running
curl http://your-tgi-endpoint:8080/health

# Check backend logs
cd backend && python main.py
# Look for "✓ Available" or "✗ Unavailable" messages
```

### Models Show as Unavailable (✗)

This means the TGI endpoint is not reachable:
1. Verify TGI container is running: `docker ps`
2. Check firewall/security groups allow the port
3. Verify the endpoint URL in `.env` is correct
4. Test directly: `curl http://endpoint:8080/health`

### Frontend Shows "Backend Disconnected"

```bash
# Make sure backend is running
cd backend
python main.py

# Check CORS settings in backend/main.py
# Ensure your frontend URL is in allowed_origins
```

### Generation Timeout

- TGI might be overloaded
- Model is too large for GPU memory
- Network issue between backend and TGI
- Increase timeout in `backend/main.py`

For more help, see [DEPLOYMENT.md](DEPLOYMENT.md) for cloud-specific troubleshooting.

## Development

### Adding New Models

1. Add to `backend/main.py` MODELS dict:
```python
MODELS = {
    "my-model": "organization/model-name-on-huggingface",
}
```

2. The frontend will automatically fetch and display new models

### Custom Generation Parameters

Modify the generation request in `src/App.js`:
```javascript
{
  model_id: modelId,
  prompt: userMessage,
  max_new_tokens: 200,    // Adjust these
  temperature: 0.7,
  top_p: 0.95,
}
```

## License

MIT

## Credits

- [HuggingFace TGI](https://github.com/huggingface/text-generation-inference)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
