#!/bin/bash

# TGI Deployment Script for Cloud GPU Instances
# This script helps you deploy TGI containers on your GPU server

set -e

# Configuration
MODEL_NAME="${1:-gpt2}"
PORT="${2:-8080}"
GPU_ID="${3:-0}"

echo "🚀 Deploying TGI for model: $MODEL_NAME"
echo "   Port: $PORT"
echo "   GPU: $GPU_ID"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if nvidia-docker is available (for GPU support)
if ! docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi &> /dev/null; then
    echo "⚠️  Warning: GPU support not detected. Running on CPU (will be slow)."
    GPU_FLAG=""
else
    echo "✓ GPU support detected"
    GPU_FLAG="--gpus device=$GPU_ID"
fi

# Pull TGI image
echo "📦 Pulling TGI Docker image..."
docker pull ghcr.io/huggingface/text-generation-inference:latest

# Stop existing container if running
CONTAINER_NAME="tgi-${MODEL_NAME//\//-}"
if docker ps -a | grep -q $CONTAINER_NAME; then
    echo "🛑 Stopping existing container..."
    docker stop $CONTAINER_NAME || true
    docker rm $CONTAINER_NAME || true
fi

# Start TGI container
echo "🚀 Starting TGI container..."

docker run -d \
    --name $CONTAINER_NAME \
    $GPU_FLAG \
    --shm-size 1g \
    -p $PORT:80 \
    -e MODEL_ID=$MODEL_NAME \
    -e NUM_SHARD=1 \
    -e MAX_TOTAL_TOKENS=2048 \
    -e MAX_INPUT_LENGTH=1024 \
    -e HUGGING_FACE_HUB_TOKEN=${HUGGING_FACE_HUB_TOKEN:-} \
    -v $HOME/.cache/huggingface:/data \
    ghcr.io/huggingface/text-generation-inference:latest

echo "⏳ Waiting for TGI to be ready..."

# Wait for health check
MAX_WAIT=300  # 5 minutes
ELAPSED=0
INTERVAL=5

while [ $ELAPSED -lt $MAX_WAIT ]; do
    if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
        echo "✅ TGI is ready!"
        echo ""
        echo "Model: $MODEL_NAME"
        echo "Endpoint: http://localhost:$PORT"
        echo "Container: $CONTAINER_NAME"
        echo ""
        echo "Test it:"
        echo "  curl -X POST http://localhost:$PORT/generate \\"
        echo "    -H 'Content-Type: application/json' \\"
        echo "    -d '{\"inputs\": \"Hello\", \"parameters\": {\"max_new_tokens\": 20}}'"
        exit 0
    fi
    
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
    echo "  Waiting... (${ELAPSED}s / ${MAX_WAIT}s)"
done

echo "❌ TGI failed to start within $MAX_WAIT seconds"
echo "Check logs with: docker logs $CONTAINER_NAME"
exit 1

