#!/bin/bash

# CloudEngineered Platform - Production Ready Startup
echo "🚀 Starting CloudEngineered Platform..."

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Setup Python virtual environment
echo "📦 Setting up Python environment..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r requirements.txt -q
cd ..

# Initialize database if it doesn't exist
if [ ! -f "backend/cloudengineered.db" ]; then
    echo "🗄️  Initializing database..."
    cd backend
    ./venv/bin/python init_db.py
    ./venv/bin/python simple_seed.py
    cd ..
fi

# Build frontend for production
echo "🎨 Building frontend..."
cd frontend
npm install --silent
npm run build
cd ..

# Start backend server
echo "🔧 Starting backend server..."
cd backend
./venv/bin/python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Backend server started successfully"
else
    echo "❌ Backend server failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend server
echo "🎨 Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 5

echo ""
echo "🎉 CloudEngineered Platform is now running!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🔍 Enhanced Docker tool available with comprehensive details!"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
