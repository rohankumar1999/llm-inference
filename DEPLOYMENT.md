# Deployment Guide - Cloud GPU Setup

This guide explains how to deploy the LLM Inference application with TGI containers running on cloud GPU instances.

## Architecture Overview

```
┌─────────────────────┐
│  Frontend (React)   │
│  Your Cloud/Local   │
└──────────┬──────────┘
           │ HTTP
           ▼
┌─────────────────────┐
│  Backend (FastAPI)  │
│  Any Server         │
└──────────┬──────────┘
           │ HTTP
           ▼
┌─────────────────────────────────────────┐
│  Cloud GPU Instances                    │
│                                         │
│  ┌─────────────┐  ┌─────────────┐     │
│  │ TGI (GPU 1) │  │ TGI (GPU 2) │ ... │
│  │ Model A     │  │ Model B     │     │
│  │ :8080       │  │ :8080       │     │
│  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────┘
```

## Step 1: Set Up Cloud GPU Instances

### Option A: AWS EC2 with GPU

1. **Launch GPU Instance**
   ```bash
   # Recommended: g4dn.xlarge (T4 GPU, ~$0.50/hr)
   # For larger models: p3.2xlarge (V100 GPU)
   ```

2. **Install NVIDIA Docker**
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Install NVIDIA Docker runtime
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
     sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   
   sudo apt-get update
   sudo apt-get install -y nvidia-docker2
   sudo systemctl restart docker
   ```

3. **Verify GPU Access**
   ```bash
   docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
   ```

### Option B: Google Cloud Platform (GCP)

```bash
# Create GPU instance
gcloud compute instances create tgi-instance \
  --zone=us-central1-a \
  --machine-type=n1-standard-4 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --maintenance-policy=TERMINATE \
  --image-family=pytorch-latest-gpu \
  --image-project=deeplearning-platform-release
```

### Option C: RunPod / Lambda Labs / Vast.ai

These platforms provide pre-configured GPU instances with Docker and NVIDIA drivers.

## Step 2: Deploy TGI Containers on GPU Instances

### Using the Deployment Script

On each GPU instance:

```bash
# Copy the script to your GPU instance
scp backend/deploy_tgi.sh user@gpu-instance:~

# SSH into the instance
ssh user@gpu-instance

# Make executable
chmod +x deploy_tgi.sh

# Deploy a model
./deploy_tgi.sh "gpt2" 8080 0
```

### Manual TGI Deployment

```bash
# Example: Deploy GPT-2
docker run -d \
  --name tgi-gpt2 \
  --gpus all \
  --shm-size 1g \
  -p 8080:80 \
  -e MODEL_ID=gpt2 \
  -e NUM_SHARD=1 \
  -e MAX_TOTAL_TOKENS=2048 \
  -v $HOME/.cache/huggingface:/data \
  ghcr.io/huggingface/text-generation-inference:latest

# Wait for startup (2-5 minutes first time)
docker logs -f tgi-gpt2

# Test it
curl -X POST http://localhost:8080/generate \
  -H 'Content-Type: application/json' \
  -d '{"inputs": "Hello", "parameters": {"max_new_tokens": 20}}'
```

### Deploy Multiple Models

You can run multiple TGI instances on different ports:

```bash
# GPU Instance 1
./deploy_tgi.sh "gpt2" 8080
./deploy_tgi.sh "TinyLlama/TinyLlama-1.1B-Chat-v1.0" 8081

# GPU Instance 2
./deploy_tgi.sh "mistralai/Mistral-7B-Instruct-v0.1" 8080

# GPU Instance 3
./deploy_tgi.sh "meta-llama/Llama-2-7b-chat-hf" 8080
```

## Step 3: Configure Backend

1. **Copy `.env.example` to `.env`**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Update `.env` with your TGI endpoints**
   ```bash
   # If on same GPU instance
   TGI_GPT2_ENDPOINT=http://localhost:8080
   TGI_TINYLLAMA_ENDPOINT=http://localhost:8081
   
   # If on different instances (use public IPs or domain names)
   TGI_MISTRAL_ENDPOINT=http://34.123.45.67:8080
   TGI_LLAMA2_ENDPOINT=http://35.234.56.78:8080
   
   # If using domain names
   TGI_FALCON_ENDPOINT=https://falcon.yourdomain.com
   ```

3. **Security: Use Private Network or VPN**
   
   For production, don't expose TGI ports publicly. Instead:
   
   - Use VPC/Private Network between instances
   - Or use SSH tunneling:
     ```bash
     ssh -L 8080:localhost:8080 user@gpu-instance
     ```
   - Or setup nginx reverse proxy with SSL

## Step 4: Deploy Backend

### Option A: Same Instance as TGI

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Option B: Separate Instance (Recommended)

```bash
# On a cheaper CPU instance
cd backend
pip install -r requirements.txt

# Use systemd for auto-restart
sudo tee /etc/systemd/system/llm-backend.service > /dev/null <<EOF
[Unit]
Description=LLM Inference Backend
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable llm-backend
sudo systemctl start llm-backend
```

## Step 5: Deploy Frontend

### Option A: Static Hosting (Vercel/Netlify)

```bash
# Build production bundle
npm run build

# Deploy to Vercel
npm install -g vercel
vercel --prod

# Update API URL in src/App.js
const API_URL = 'https://your-backend-api.com';
```

### Option B: Self-Hosted with Nginx

```bash
# Build
npm run build

# Install nginx
sudo apt-get install nginx

# Copy build files
sudo cp -r build/* /var/www/html/

# Configure nginx
sudo tee /etc/nginx/sites-available/llm-frontend > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/html;
    index index.html;
    
    location / {
        try_files \$uri /index.html;
    }
    
    # Proxy API requests
    location /api {
        proxy_pass http://your-backend:8000;
        proxy_set_header Host \$host;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/llm-frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Cost Optimization

### 1. Auto-Scaling

Only run GPU instances when needed:

```python
# Add to backend: auto-start instances via cloud API
import boto3

def start_gpu_instance(model_id):
    ec2 = boto3.client('ec2')
    ec2.start_instances(InstanceIds=['i-xxxxx'])
```

### 2. Spot Instances

Use spot instances for 70% cost savings (AWS, GCP):

```bash
aws ec2 request-spot-instances \
  --instance-count 1 \
  --type "persistent" \
  --launch-specification file://spec.json
```

### 3. Model Quantization

Use quantized models to fit on smaller GPUs:

```bash
# Instead of full precision 7B model (14GB)
# Use 4-bit quantized version (4GB)
MODEL_ID=TheBloke/Mistral-7B-Instruct-v0.1-GPTQ
```

## Production Checklist

- [ ] TGI endpoints use HTTPS
- [ ] Backend API uses HTTPS
- [ ] Environment variables properly set
- [ ] CORS configured for production domain
- [ ] Rate limiting enabled
- [ ] Monitoring setup (CloudWatch, Datadog, etc.)
- [ ] Log aggregation configured
- [ ] Backup/restore procedures documented
- [ ] Auto-scaling rules defined
- [ ] Cost alerts configured
- [ ] Security groups/firewalls configured
- [ ] Health checks implemented
- [ ] Graceful shutdown handlers

## Monitoring

### Health Check Endpoints

```bash
# Check backend
curl http://your-backend:8000/

# Check specific model
curl http://your-backend:8000/models/gpt-2/health

# Check TGI directly
curl http://gpu-instance:8080/health
```

### Logging

View backend logs:
```bash
journalctl -u llm-backend -f
```

View TGI logs:
```bash
docker logs -f tgi-gpt2
```

## Troubleshooting

### TGI Won't Start

```bash
# Check GPU availability
nvidia-smi

# Check Docker GPU support
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# View container logs
docker logs tgi-gpt2

# Common issues:
# - Out of GPU memory: reduce MAX_TOTAL_TOKENS
# - Model download failed: check internet connection
# - Permission denied: check volume permissions
```

### Backend Can't Reach TGI

```bash
# Test connection
curl http://tgi-endpoint:8080/health

# Check firewall
sudo ufw status
sudo ufw allow 8080

# Check security groups (AWS)
aws ec2 describe-security-groups --group-ids sg-xxxxx
```

### High Latency

- Use faster GPU (T4 → A100)
- Enable model quantization
- Increase NUM_SHARD for larger models
- Add caching layer (Redis)
- Use connection pooling

## Example Deployment Configurations

### Small Setup (Development)
- 1x g4dn.xlarge (GPT-2 + TinyLlama)
- Cost: ~$0.50/hour
- Good for: Testing, demos

### Medium Setup (Production)
- 2x g4dn.2xlarge (Mistral, Llama 2)
- 1x t3.medium (Backend)
- Cost: ~$1.50/hour
- Good for: Small teams, prototypes

### Large Setup (Enterprise)
- 4x p3.2xlarge (Multiple 7B+ models)
- Auto-scaling backend cluster
- Load balancer, CDN
- Cost: ~$15/hour
- Good for: High traffic, multiple models

---

**Need help?** Check the logs first, then consult TGI docs: https://github.com/huggingface/text-generation-inference

