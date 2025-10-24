# Backend - LLM Inference API

FastAPI-based backend server that proxies requests to cloud-hosted TGI (Text Generation Inference) instances.

## Overview

This backend acts as an orchestrator and proxy between the frontend and TGI containers running on GPU instances. It does NOT manage Docker containers or perform inference itself - it routes requests to pre-deployed TGI endpoints.

## Architecture

```
Frontend → Backend API → Cloud TGI Instances
```

The backend:
- ✅ Maintains registry of TGI endpoints
- ✅ Performs health checks on TGI instances
- ✅ Routes generation requests
- ✅ Handles errors and retries
- ❌ Does NOT manage Docker containers
- ❌ Does NOT need GPU access
- ❌ Does NOT load models

## Installation

```bash
cd backend
pip install -r requirements.txt
```

Or with virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

### 1. Copy environment template

```bash
cp .env.example .env
```

### 2. Configure TGI endpoints

Edit `.env`:

```bash
# Point to your TGI instances
TGI_GPT2_ENDPOINT=http://your-gpu-server-1.com:8080
TGI_TINYLLAMA_ENDPOINT=http://your-gpu-server-2.com:8080
TGI_MISTRAL_ENDPOINT=http://your-gpu-server-3.com:8080

# Server config
HOST=0.0.0.0
PORT=8000

# CORS (add your frontend URL)
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com
```

### 3. Add new models

Edit `main.py`:

```python
MODELS = {
    "my-model": {
        "name": "My Custom Model",
        "hf_name": "organization/model-name",
        "endpoint": os.getenv("TGI_MYMODEL_ENDPOINT"),
    }
}
```

Then add to `.env`:
```bash
TGI_MYMODEL_ENDPOINT=http://gpu-server:8080
```

## Running

### Development

```bash
python main.py
```

Or with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

With gunicorn:

```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Endpoints

### GET /

API information

### GET /models

List all configured models with their health status

**Response**:
```json
[
  {
    "id": "gpt-2",
    "name": "GPT-2",
    "hf_name": "gpt2",
    "endpoint": "http://gpu-server:8080",
    "available": true
  }
]
```

### GET /models/{model_id}/health

Check health of a specific model's TGI endpoint

**Response**:
```json
{
  "model_id": "gpt-2",
  "endpoint": "http://gpu-server:8080",
  "healthy": true,
  "status": "available"
}
```

### POST /generate

Generate text using a model

**Request**:
```json
{
  "model_id": "gpt-2",
  "prompt": "Once upon a time",
  "max_new_tokens": 200,
  "temperature": 0.7,
  "top_p": 0.95,
  "repetition_penalty": 1.0
}
```

**Response**:
```json
{
  "generated_text": "Once upon a time, in a land far away...",
  "model_id": "gpt-2"
}
```

## Testing

### Test Script

```bash
python test_api.py
```

This will:
1. Check if API is running
2. List available models
3. Test text generation with GPT-2

### Manual Testing

```bash
# Check API is running
curl http://localhost:8000/

# List models
curl http://localhost:8000/models

# Check model health
curl http://localhost:8000/models/gpt-2/health

# Generate text
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "gpt-2",
    "prompt": "Hello, world!",
    "max_new_tokens": 50
  }'
```

## Deployment

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t llm-backend .
docker run -p 8000:8000 --env-file .env llm-backend
```

### Systemd Service

```bash
sudo tee /etc/systemd/system/llm-backend.service > /dev/null <<EOF
[Unit]
Description=LLM Inference Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
EnvironmentFile=$(pwd)/.env
ExecStart=$(pwd)/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable llm-backend
sudo systemctl start llm-backend
```

## Troubleshooting

### TGI Endpoint Unreachable

**Symptoms**: Models show as unavailable (✗)

**Solutions**:
1. Check TGI is running: `curl http://endpoint:8080/health`
2. Check firewall allows connection
3. Verify endpoint URL in `.env`
4. Check network connectivity
5. Review backend logs

### CORS Errors

**Symptoms**: Frontend can't connect

**Solution**: Add frontend URL to `ALLOWED_ORIGINS` in `.env`

### Timeout Errors

**Symptoms**: Generation takes too long

**Solutions**:
1. Increase timeout in `main.py` (default: 120s)
2. Use smaller models
3. Reduce `max_new_tokens`
4. Check TGI instance isn't overloaded

### Import Errors

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

## Logging

Backend logs include:
- Startup model endpoint checks
- Health check results
- Generation requests with model ID
- Errors and exceptions

Customize logging level in `main.py`:

```python
logging.basicConfig(level=logging.DEBUG)  # More verbose
logging.basicConfig(level=logging.WARNING)  # Less verbose
```

## Performance Tips

1. **Connection Pooling**: HTTPX automatically pools connections
2. **Async Requests**: Use `asyncio.gather()` for parallel requests
3. **Health Check Caching**: Results cached for 30 seconds (frontend)
4. **Timeout Tuning**: Adjust based on model size
5. **Multiple Workers**: Run with `--workers 4` for production

## Security

For production:

1. **HTTPS**: Use reverse proxy (nginx) with SSL
2. **Rate Limiting**: Add rate limiting middleware
3. **Authentication**: Add API key or OAuth
4. **Input Validation**: Already handled by Pydantic
5. **CORS**: Restrict to specific origins
6. **Secrets**: Use environment variables, not hardcoded

Example nginx config:

```nginx
server {
    listen 443 ssl;
    server_name api.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Dependencies

- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **pydantic**: Data validation
- **httpx**: Async HTTP client
- **python-dotenv**: Environment variables

## License

MIT
