#!/bin/bash

# Start script for LLM Inference application
# This script starts both the backend and frontend

echo "🚀 Starting LLM Inference Application"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✓ Docker is running"

# Check if backend dependencies are installed
if [ ! -d "backend/venv" ] && [ ! -f "backend/.venv/bin/activate" ]; then
    echo "⚠️  Backend virtual environment not found."
    echo "Creating virtual environment and installing dependencies..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo "✓ Backend dependencies installed"
fi

# Check if frontend dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "⚠️  Frontend dependencies not found."
    echo "Installing npm packages..."
    npm install
    echo "✓ Frontend dependencies installed"
fi

# Start backend in background
echo ""
echo "Starting backend server..."
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi
python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "✓ Backend started (PID: $BACKEND_PID)"
echo "  Logs: backend.log"
echo "  API: http://localhost:8000"
echo "  Docs: http://localhost:8000/docs"

# Wait a moment for backend to start
sleep 3

# Start frontend
echo ""
echo "Starting frontend..."
echo "✓ Frontend will open at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Trap Ctrl+C to kill both processes
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID 2>/dev/null; exit" INT

# Start frontend (this blocks)
npm start

# Cleanup (in case npm start exits normally)
kill $BACKEND_PID 2>/dev/null

