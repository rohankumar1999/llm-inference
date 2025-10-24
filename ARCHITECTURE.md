# Architecture Overview

## System Design

### Cloud-Native Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     User's Browser                            │
│                                                               │
│  ┌─────────────────────────────────────────────────┐        │
│  │  React Frontend (Port 3000)                     │        │
│  │  - Model selection UI                           │        │
│  │  - Chat interface                               │        │
│  │  - Side-by-side comparison view                 │        │
│  │  - Real-time health status indicators           │        │
│  └────────────────────┬────────────────────────────┘        │
│                       │                                       │
└───────────────────────┼───────────────────────────────────────┘
                        │
                        │ HTTP/JSON
                        │ /models, /generate
                        ▼
┌──────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                      │
│  Can run on: Local, Cloud VM, Serverless, Docker             │
│                                                               │
│  ┌─────────────────────────────────────────────────┐        │
│  │  API Server (main.py)                           │        │
│  │  - Model endpoint registry                      │        │
│  │  - Health checking                              │        │
│  │  - Request proxying                             │        │
│  │  - Error handling                               │        │
│  └────────────────────┬────────────────────────────┘        │
│                       │                                       │
└───────────────────────┼───────────────────────────────────────┘
                        │
                        │ HTTP/JSON
                        │ /generate, /health
                        ▼
┌──────────────────────────────────────────────────────────────┐
│         Cloud GPU Instances (AWS/GCP/Azure/etc)               │
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  GPU Instance 1  │  │  GPU Instance 2  │  ...            │
│  │                  │  │                  │                  │
│  │ ┌──────────────┐ │  │ ┌──────────────┐ │                 │
│  │ │ TGI Container│ │  │ │ TGI Container│ │                 │
│  │ │   :8080      │ │  │ │   :8080      │ │                 │
│  │ │              │ │  │ │              │ │                 │
│  │ │ GPT-2        │ │  │ │ Mistral-7B   │ │                 │
│  │ │ (T4 GPU)     │ │  │ │ (A100 GPU)   │ │                 │
│  │ └──────────────┘ │  │ └──────────────┘ │                 │
│  │                  │  │                  │                  │
│  │ Model Cache:     │  │ Model Cache:     │                 │
│  │ ~/.cache/hf      │  │ ~/.cache/hf      │                 │
│  └──────────────────┘  └──────────────────┘                 │
└──────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Frontend (React)

**Location**: Can be hosted anywhere (Vercel, Netlify, S3, etc.)

**Responsibilities**:
- User interface rendering
- Model selection
- Message display (side-by-side comparison)
- Backend API communication
- Real-time status updates

**State Management**:
- Models list with availability status
- Conversation history
- Loading states
- Error handling

**Tech Stack**:
- React 18 with Hooks
- Fetch API for HTTP requests
- CSS3 for styling
- No external state library needed

### Backend (FastAPI)

**Location**: Can run on any server (doesn't need GPU)

**Responsibilities**:
- TGI endpoint registry and configuration
- Health monitoring of TGI instances
- Request routing to appropriate TGI endpoints
- Response formatting
- Error handling and retries
- CORS management

**NOT Responsible For**:
- Model loading (done by TGI)
- GPU management (done by cloud provider)
- Actual inference (done by TGI)

**Tech Stack**:
- FastAPI (async Python web framework)
- Pydantic (data validation)
- HTTPX (async HTTP client)
- Uvicorn (ASGI server)

### TGI Containers (Inference Layer)

**Location**: Must run on GPU instances

**Responsibilities**:
- Loading and caching models
- GPU-accelerated inference
- Handling generation parameters
- Memory management
- Batch processing (if enabled)

**Tech Stack**:
- HuggingFace Text Generation Inference
- Docker for containerization
- CUDA for GPU acceleration
- Rust-based inference engine

## Data Flow

### 1. Initialization

```
Frontend                Backend               TGI Instances
   |                      |                         |
   |-- GET /models ------>|                         |
   |                      |-- GET /health --------->|
   |                      |<-- 200 OK --------------|
   |                      |                         |
   |<-- Models List ------|                         |
   |    (with status)     |                         |
```

### 2. Text Generation

```
User                Frontend              Backend              TGI (GPU 1)      TGI (GPU 2)
 |                     |                    |                      |                 |
 |-- Type prompt ----->|                    |                      |                 |
 |                     |-- POST /generate ->|                      |                 |
 |                     |   (model_id: m1)   |                      |                 |
 |                     |                    |-- POST /generate --->|                 |
 |                     |                    |                      |                 |
 |                     |-- POST /generate ->|                      |                 |
 |                     |   (model_id: m2)   |                      |                 |
 |                     |                    |-- POST /generate ------------------->|
 |                     |                    |                      |                 |
 |                     |                    |                      |-- Processing -->|
 |                     |                    |                      |                 |
 |                     |                    |<-- Response ---------|                 |
 |                     |<-- Response 1 -----|                      |                 |
 |                     |                    |<-- Response 2 -----------------------|
 |                     |<-- Response 2 -----|                      |                 |
 |<-- Display Both ----|                    |                      |                 |
```

### 3. Health Monitoring

```
Frontend Timer          Backend              TGI Instances
    |                     |                         |
    |-- Every 30s ------->|                         |
    |   GET /models       |                         |
    |                     |-- Parallel health ----->|
    |                     |   checks for all        |
    |                     |<-- Health status -------|
    |                     |                         |
    |<-- Updated status --|                         |
    |   (✓ or ✗)          |                         |
```

## Network Configuration

### Development Setup

```
localhost:3000 (Frontend)
    ↓
localhost:8000 (Backend)
    ↓
localhost:8080, 8081, ... (TGI instances)
```

### Production Setup

```
https://app.yourdomain.com (Frontend via CDN)
    ↓
https://api.yourdomain.com (Backend via Load Balancer)
    ↓
Private Network
    ↓
10.0.1.10:8080 (TGI Instance 1 - GPT-2)
10.0.1.11:8080 (TGI Instance 2 - Mistral)
10.0.1.12:8080 (TGI Instance 3 - Llama)
```

### Security Considerations

1. **TGI Instances**: Should be on private network, not exposed to internet
2. **Backend**: Public endpoint with rate limiting
3. **Frontend**: Served via CDN with HTTPS
4. **Communication**: 
   - Frontend ↔ Backend: HTTPS
   - Backend ↔ TGI: Private network or VPN

## Scaling Strategies

### Horizontal Scaling

```
                    Load Balancer
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
    Backend 1        Backend 2        Backend 3
        │                │                │
        └────────────────┼────────────────┘
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
         TGI Pool    TGI Pool     TGI Pool
```

### Auto-Scaling TGI Instances

1. **On-Demand**: Start TGI when model is requested
2. **Pre-warmed Pool**: Keep popular models always running
3. **Spot Instances**: Use spot/preemptible instances for cost savings
4. **Geographic Distribution**: Deploy TGI close to users

### Caching Strategies

1. **Model Weights**: Cached on disk at `~/.cache/huggingface`
2. **Response Cache**: Optional Redis cache for repeated prompts
3. **Connection Pool**: Reuse HTTP connections to TGI

## Performance Characteristics

### Latency Breakdown

```
Total Response Time = Frontend + Backend + TGI + Network

Frontend Processing:  ~10ms
Network (F→B):        ~50ms
Backend Processing:   ~20ms
Network (B→TGI):      ~10ms (private network)
TGI Inference:        500ms - 10s (model dependent)
Network (TGI→B):      ~10ms
Network (B→F):        ~50ms
Frontend Rendering:   ~20ms

Total: ~670ms - ~10.2s
```

### Optimization Opportunities

1. **Parallel Requests**: Both models generate simultaneously
2. **Streaming**: Use SSE for real-time token streaming
3. **Batching**: TGI can batch multiple requests
4. **Quantization**: Use 4-bit/8-bit models for faster inference
5. **Speculative Decoding**: Advanced TGI feature

## Deployment Models

### Model 1: All-in-One GPU Instance

```
Single GPU Instance
├── TGI Container 1 (Model A)
├── TGI Container 2 (Model B)
└── Backend Server
```

**Pros**: Simple setup, low latency
**Cons**: Single point of failure, GPU sharing

### Model 2: Dedicated GPU Instances

```
Backend Server (CPU)
    ↓
GPU Instance 1 → TGI (Model A)
GPU Instance 2 → TGI (Model B)
GPU Instance 3 → TGI (Model C)
```

**Pros**: Isolated resources, better scaling
**Cons**: Higher cost, network latency

### Model 3: Serverless Backend

```
Static Frontend (Vercel)
    ↓
Serverless Functions (AWS Lambda)
    ↓
Dedicated GPU Instances (EC2)
```

**Pros**: Auto-scaling backend, pay-per-use
**Cons**: Cold starts, complexity

## Cost Analysis

### Monthly Cost Estimates

**Small Setup** (Development):
- 1× g4dn.xlarge (T4): $0.526/hr × 730hr = ~$384/mo
- Backend on t3.small: $0.023/hr × 730hr = ~$17/mo
- **Total**: ~$400/mo

**Medium Setup** (Production):
- 2× g4dn.2xlarge (T4): $1.052/hr × 730hr × 2 = ~$1,536/mo
- Backend on t3.medium: $0.042/hr × 730hr = ~$31/mo
- **Total**: ~$1,567/mo

**Large Setup** (Enterprise):
- 4× p3.2xlarge (V100): $3.06/hr × 730hr × 4 = ~$8,936/mo
- Auto-scaling backend cluster: ~$200/mo
- **Total**: ~$9,136/mo

### Cost Optimization

1. Use spot instances: 70% savings
2. Auto-shutdown unused instances
3. Use smaller models where possible
4. Implement request batching
5. Use quantized models

## Monitoring and Observability

### Metrics to Track

**Frontend**:
- Page load time
- API response time
- Error rate
- User engagement

**Backend**:
- Request rate
- Response time (p50, p95, p99)
- Error rate by endpoint
- TGI health check success rate

**TGI**:
- GPU utilization
- Memory usage
- Inference time per token
- Queue depth
- Model loading time

### Recommended Tools

- **Logging**: CloudWatch, Datadog, ELK Stack
- **Metrics**: Prometheus + Grafana
- **Tracing**: Jaeger, OpenTelemetry
- **Alerts**: PagerDuty, Slack webhooks

## Disaster Recovery

### Backup Strategy

1. **Frontend**: Source code in Git, builds reproducible
2. **Backend**: Source code in Git, stateless design
3. **TGI**: Models auto-download from HuggingFace Hub
4. **Configuration**: `.env` files backed up securely

### Failover Procedures

1. **TGI Instance Failure**: Backend retries with exponential backoff
2. **Backend Failure**: Load balancer routes to healthy instance
3. **Region Failure**: Multi-region deployment with DNS failover

---

This architecture is designed for:
- **Flexibility**: Components can be deployed independently
- **Scalability**: Each layer scales independently
- **Reliability**: Failure isolation and health monitoring
- **Cost-Efficiency**: GPU resources only where needed

