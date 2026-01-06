#!/bin/bash

echo "🧪 Testing CloudEngineered Platform..."

# Test backend
echo "📡 Testing Backend API..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

# Start backend in background for testing
python main.py &
BACKEND_PID=$!
sleep 3

# Test API endpoints
echo "Testing API endpoints..."

# Test root endpoint
curl -s http://localhost:8000/ | grep -q "CloudEngineered API" && echo "✅ Root endpoint working" || echo "❌ Root endpoint failed"

# Test tools endpoint
curl -s http://localhost:8000/api/tools | grep -q "name" && echo "✅ Tools endpoint working" || echo "❌ Tools endpoint failed"

# Test registration
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"testpass123"}')

if echo "$REGISTER_RESPONSE" | grep -q "username"; then
    echo "✅ User registration working"
    
    # Test login
    LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"test@example.com","password":"testpass123"}')
    
    if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
        echo "✅ User login working"
        TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        
        # Test authenticated endpoint
        curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/users/me | grep -q "username" && echo "✅ Authentication working" || echo "❌ Authentication failed"
    else
        echo "❌ User login failed"
    fi
else
    echo "❌ User registration failed"
fi

# Stop backend
kill $BACKEND_PID
cd ..

# Test frontend
echo "🎨 Testing Frontend..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install > /dev/null 2>&1
fi

# Build frontend to check for errors
echo "Building frontend..."
npm run build > /dev/null 2>&1 && echo "✅ Frontend build successful" || echo "❌ Frontend build failed"

cd ..

echo ""
echo "🎉 Testing completed!"
echo ""
echo "To start the full platform:"
echo "  ./start.sh"
echo ""
echo "Manual testing checklist:"
echo "  ✓ Register a new user"
echo "  ✓ Login with credentials"
echo "  ✓ Browse tools catalog"
echo "  ✓ View tool details"
echo "  ✓ Write a review"
echo "  ✓ Compare multiple tools"
echo "  ✓ Add new tool via admin panel"
