# Quick Start Guide

## Prerequisites Check

Before starting, ensure you have:

1. **Docker Desktop** installed and running
   ```bash
   docker --version
   # Should show: Docker version XX.X.X
   ```

2. **Python 3.8+** installed
   ```bash
   python3 --version
   # Should show: Python 3.8.x or higher
   ```

3. **Node.js 14+** and npm installed
   ```bash
   node --version
   npm --version
   ```

## Easy Start (Recommended)

### Option 1: Using the Start Script (Mac/Linux)

```bash
chmod +x start.sh
./start.sh
```

This will:
- Check if Docker is running
- Install dependencies if needed
- Start the backend server
- Start the frontend app
- Open your browser automatically

### Option 2: Manual Start

#### Terminal 1 - Backend:
```bash
cd backend
pip install -r requirements.txt
python main.py
```

Wait until you see: `INFO: Uvicorn running on http://0.0.0.0:8000`

#### Terminal 2 - Frontend:
```bash
npm install
npm start
```

Your browser should open to `http://localhost:3000`

## First Time Usage

1. **Select Models**: Choose two different models from the dropdowns
   - Start with **GPT-2** and **TinyLlama** (smaller, faster)
   - Avoid larger models (Mistral, Llama 2) unless you have 16GB+ RAM

2. **First Message**: Type a prompt and press Enter
   - First time: Container will start and download model (~2-5 minutes for GPT-2)
   - You'll see "Generating response..." while the model loads
   - Subsequent messages are faster

3. **Compare Responses**: View side-by-side outputs from both models

## Testing the Backend

After starting the backend, you can test it:

```bash
cd backend
python test_api.py
```

This will:
- Check if the API is running
- List available models
- Test text generation with GPT-2

## Troubleshooting

### "Backend Disconnected" shown in UI

**Solution**: Make sure the backend is running:
```bash
cd backend
python main.py
```

### Docker Permission Errors

**On Mac/Linux**:
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

**On Windows**: Run Docker Desktop as Administrator

### Port Already in Use

**Backend (port 8000)**:
```bash
# Find what's using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill it or change the port in backend/main.py (last line)
```

**Frontend (port 3000)**:
```bash
# Create .env file
echo "PORT=3001" > .env
npm start
```

### Model Download is Slow/Fails

Models are downloaded to `~/.cache/huggingface/`

**Solutions**:
- Use a faster internet connection
- Start with GPT-2 (only ~500MB)
- Check disk space (7B models need ~15GB free)

### Out of Memory Errors

**Solutions**:
- Use smaller models (GPT-2, Phi-2, TinyLlama)
- Close other applications
- Reduce `MAX_TOTAL_TOKENS` in backend/main.py
- Increase Docker memory limit (Docker Desktop → Settings → Resources)

## Recommended First Models

For testing (fast, small):
- Model 1: **GPT-2** (~500MB, 2GB RAM)
- Model 2: **TinyLlama** (~2GB download, 4GB RAM)

For better quality (slower, larger):
- Model 1: **Mistral 7B** (~14GB download, 16GB RAM)
- Model 2: **Phi-2** (~5GB download, 8GB RAM)

## What to Expect

### First Run Timeline:
1. Start backend: ~5 seconds
2. Start frontend: ~10 seconds
3. Send first message: 2-10 minutes (downloading model)
4. Subsequent messages: 2-30 seconds (depending on model)

### Model Download Sizes:
- GPT-2: ~500MB
- Phi-2: ~5GB
- TinyLlama: ~2GB
- Mistral/Llama/Falcon 7B: ~14GB each

## Next Steps

Once everything is running:

1. Try different prompts
2. Compare how different models respond
3. Experiment with model combinations
4. Check the API docs: http://localhost:8000/docs

## Getting Help

- Check backend logs: `backend.log` (if using start.sh)
- Check browser console (F12) for frontend errors
- Verify Docker is running: `docker ps`
- Check API health: http://localhost:8000/

Enjoy comparing LLMs! 🚀

