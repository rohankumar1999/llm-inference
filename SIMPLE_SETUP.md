# Simple Setup Guide

## Overview

- **Backend**: Runs on cloud GPU environment (Lightning.ai, RunPod, etc.)
- **Frontend**: Hardcoded to point to backend URL
- **No environment files needed!**

## Step 1: Deploy Backend on Cloud

### Upload Backend Files

Upload the `backend/` folder to your cloud environment (Lightning.ai, RunPod, Vast.ai, etc.)

### Configure TGI Endpoints

Edit `backend/.env`:
```bash
# Point to your TGI instances
TGI_GPT2_ENDPOINT=http://localhost:8080
TGI_TINYLLAMA_ENDPOINT=http://localhost:8081

# Allow all origins (for simplicity - not recommended for production)
ALLOWED_ORIGINS=*

HOST=0.0.0.0
PORT=8000
```

### Run Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Get Backend URL

Your cloud provider will give you a public URL like:
- `https://abc123.lightning.ai`
- `http://12.34.56.78:8000`
- `https://xyz-8000.proxy.runpod.net`

**Copy this URL!** You'll need it for Step 2.

## Step 2: Configure Frontend

### Edit App.js

Open `src/App.js` and change line 5:

**Before:**
```javascript
const API_URL = 'http://localhost:8000';
```

**After:**
```javascript
const API_URL = 'https://abc123.lightning.ai';  // Your backend URL
```

That's it! The frontend is now hardcoded to use your backend.

## Step 3: Run Frontend Locally

```bash
npm install
npm start
```

Opens at `http://localhost:3000`

## Step 4: Deploy Frontend (Optional)

### Option A: Deploy to Vercel (Easiest)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
npm run build
vercel --prod
```

### Option B: Deploy to Netlify

```bash
npm install -g netlify-cli
npm run build
netlify deploy --prod --dir=build
```

### Option C: Self-Host

```bash
npm run build

# Upload build/ folder to your server
scp -r build/* user@server:/var/www/html/
```

## Complete Example

### Backend on Lightning.ai

1. Upload backend files
2. Run: `uvicorn main:app --host 0.0.0.0 --port 8000`
3. Get URL: `https://abc123-8000.lightning.ai`

### Frontend Update

Edit `src/App.js`:
```javascript
const API_URL = 'https://abc123-8000.lightning.ai';
```

### Test Locally

```bash
npm start
# Visit http://localhost:3000
# Should connect to Lightning.ai backend
```

### Deploy Frontend

```bash
npm run build
vercel --prod
```

Done! Frontend at `https://your-app.vercel.app` connects to backend at `https://abc123-8000.lightning.ai`

## Troubleshooting

### "Backend Disconnected"

1. Check `src/App.js` has correct URL
2. Verify backend is running: `curl https://your-backend-url/`
3. Check backend allows CORS: Set `ALLOWED_ORIGINS=*` in backend/.env

### CORS Error

In `backend/.env`:
```bash
ALLOWED_ORIGINS=*
```

Then restart backend.

## That's It!

No environment files, no complex configs. Just hardcode the URL and you're done! 🚀

