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

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Seed database
echo "Seeding database with sample data..."
python seed_data.py

# Start backend in background
echo "🔧 Starting FastAPI backend on http://localhost:8000..."
python main.py &
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
