# API Reference

Base URL: `http://localhost:8000`

## Endpoints

### 1. Get API Info

```http
GET /
```

**Response:**
```json
{
  "message": "LLM Inference API",
  "models": ["gpt-2", "tiny-llama", "mistral-7b", ...],
  "running_containers": ["gpt-2"]
}
```

---

### 2. List Available Models

```http
GET /models
```

**Response:**
```json
{
  "models": [
    {
      "id": "gpt-2",
      "name": "gpt-2",
      "hf_name": "gpt2",
      "running": true
    },
    {
      "id": "tiny-llama",
      "name": "tiny-llama",
      "hf_name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
      "running": false
    }
  ]
}
```

---

### 3. Start Model Container

```http
POST /models/{model_id}/start
```

**Parameters:**
- `model_id` (path): Model identifier (e.g., "gpt-2")

**Response:**
```json
{
  "message": "Container for gpt-2 started",
  "port": 8080,
  "container_name": "tgi-gpt-2"
}
```

**Notes:**
- First start downloads model weights (can take 1-10 minutes)
- Container startup takes 1-5 minutes
- Returns 503 if container fails to start
- Returns existing info if already running

---

### 4. Stop Model Container

```http
POST /models/{model_id}/stop
```

**Parameters:**
- `model_id` (path): Model identifier

**Response:**
```json
{
  "message": "Container for gpt-2 stopped"
}
```

**Errors:**
- 404: Container not running
- 500: Failed to stop container

---

### 5. Generate Text

```http
POST /generate
```

**Request Body:**
```json
{
  "model_id": "gpt-2",
  "prompt": "Once upon a time",
  "max_new_tokens": 200,
  "temperature": 0.7,
  "top_p": 0.95
}
```

**Parameters:**
- `model_id` (required): Model to use
- `prompt` (required): Input text
- `max_new_tokens` (optional): Maximum tokens to generate (default: 200)
- `temperature` (optional): Sampling temperature 0.0-2.0 (default: 0.7)
- `top_p` (optional): Nucleus sampling parameter (default: 0.95)

**Response:**
```json
{
  "generated_text": "Once upon a time, in a land far away...",
  "model_id": "gpt-2"
}
```

**Notes:**
- Automatically starts container if not running
- First generation may take several minutes (downloading + startup)
- Subsequent generations: 2-30 seconds depending on model size
- Timeout: 60 seconds

**Errors:**
- 404: Model not found
- 503: Container failed to start
- 504: Generation timeout

---

## Model IDs

| Model ID | HuggingFace Name | Size | RAM Required |
|----------|------------------|------|--------------|
| `gpt-2` | `gpt2` | ~500MB | 2-4GB |
| `tiny-llama` | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | ~2GB | 4-6GB |
| `phi-2` | `microsoft/phi-2` | ~5GB | 6-8GB |
| `mistral-7b` | `mistralai/Mistral-7B-Instruct-v0.1` | ~14GB | 12-16GB |
| `llama-2-7b` | `meta-llama/Llama-2-7b-chat-hf` | ~14GB | 12-16GB |
| `falcon-7b` | `tiiuae/falcon-7b-instruct` | ~14GB | 12-16GB |

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `404`: Resource not found
- `500`: Internal server error
- `503`: Service unavailable (container issue)
- `504`: Gateway timeout

---

## Usage Examples

### Python

```python
import httpx

async def generate():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/generate",
            json={
                "model_id": "gpt-2",
                "prompt": "What is AI?",
                "max_new_tokens": 100,
            }
        )
        return response.json()
```

### cURL

```bash
# List models
curl http://localhost:8000/models

# Generate text
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "gpt-2",
    "prompt": "Hello world",
    "max_new_tokens": 50
  }'
```

### JavaScript/Fetch

```javascript
async function generate(modelId, prompt) {
  const response = await fetch('http://localhost:8000/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model_id: modelId,
      prompt: prompt,
      max_new_tokens: 200,
    })
  });
  return await response.json();
}
```

---

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation where you can test all endpoints directly in your browser.

