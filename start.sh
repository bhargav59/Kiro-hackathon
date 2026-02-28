#!/bin/bash

echo "🚀 Starting CloudEngineered Platform..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Setup backend
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Install Python dependencies
echo "Installing Python dependencies..."
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements_simple.txt -q

# Seed database
echo "Seeding database with professional blog content..."
./venv/bin/python seed_professional_blogs.py 2>/dev/null || echo "Blog data already exists"
./venv/bin/python seed_remaining_blogs.py 2>/dev/null || echo "Blog data already exists"

# Start backend in background
echo "🔧 Starting FastAPI backend on http://localhost:8000..."
./venv/bin/python blog_main.py &
BACKEND_PID=$!

# Setup frontend
echo "📦 Setting up frontend..."
cd ../frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Start frontend
echo "🎨 Starting React frontend on http://localhost:3000..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ CloudEngineered Platform is running!"
echo "🔧 Backend API: http://localhost:8000"
echo "🎨 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for user to stop
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
