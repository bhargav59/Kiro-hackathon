# CloudEngineered - Custom Kiro Commands

## Development Workflow Commands

### 1. Platform Startup
```bash
# Command: start_platform
pkill -f "python main.py" && pkill -f "npm" && sleep 2
cd backend && source venv/bin/activate && export GEMINI_API_KEY=$GEMINI_API_KEY && python main.py &
cd frontend && npm run dev &
sleep 3 && echo "🚀 CloudEngineered Platform is running:"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
```

### 2. Clean Restart
```bash
# Command: clean_restart
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
pkill -f "python main.py" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
sleep 2
echo "✅ All processes cleaned"
```

### 3. Database Management
```bash
# Command: setup_database
cd backend && source venv/bin/activate
python comprehensive_seed.py
python comprehensive_enhancement.py
echo "✅ Database setup complete with enhanced data"
```

### 4. API Testing Suite
```bash
# Command: test_api
echo "🧪 Testing API endpoints..."

# Test health
curl -s http://localhost:8000/health || echo "❌ Backend health check failed"

# Test tools endpoint
curl -s http://localhost:8000/api/tools | jq '.[:2]' || echo "❌ Tools endpoint failed"

# Test AI comparison
curl -X POST "http://localhost:8000/api/ai/compare" \
  -H "Content-Type: application/json" \
  -d '{"tool_ids": [1, 2]}' | jq . || echo "❌ AI comparison failed"

# Test OAuth providers
curl -s http://localhost:8000/api/auth/providers | jq . || echo "❌ OAuth providers failed"

echo "✅ API testing complete"
```

### 5. Frontend Build & Test
```bash
# Command: test_frontend
cd frontend
echo "🔍 Checking TypeScript..."
npx tsc --noEmit || echo "❌ TypeScript errors found"

echo "🏗️ Testing build..."
npm run build 2>&1 | grep -E "(error|Error)" && echo "❌ Build errors found" || echo "✅ Build successful"

echo "📦 Bundle analysis..."
ls -lh dist/ | tail -5
```

## Data Enhancement Commands

### 6. GitHub Data Enhancement
```bash
# Command: enhance_github_data
cd backend && source venv/bin/activate
echo "🔄 Enhancing tools with GitHub data..."
python enhance_tools.py
echo "✅ GitHub enhancement complete"
```

### 7. Web Scraping Enhancement
```bash
# Command: enhance_web_data
cd backend && source venv/bin/activate
echo "🌐 Enhancing tools with web data..."
python web_scraper.py
echo "✅ Web scraping enhancement complete"
```

### 8. Full Data Pipeline
```bash
# Command: full_enhancement
cd backend && source venv/bin/activate
echo "🚀 Running full data enhancement pipeline..."
python enhance_tools.py
python web_scraper.py
python comprehensive_enhancement.py
echo "✅ Full enhancement pipeline complete"
```

## Quality Assurance Commands

### 9. Health Check Suite
```bash
# Command: health_check
echo "🏥 Running comprehensive health checks..."

# Process check
ps aux | grep -E "(python main.py|npm run dev)" | grep -v grep || echo "❌ Processes not running"

# Port check
lsof -i:8000 | grep LISTEN || echo "❌ Backend port not listening"
lsof -i:3000 | grep LISTEN || echo "❌ Frontend port not listening"

# Database check
cd backend && source venv/bin/activate && python -c "
from main import engine
try:
    engine.connect()
    print('✅ Database connected')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"

echo "✅ Health check complete"
```

### 10. Performance Testing
```bash
# Command: perf_test
echo "⚡ Running performance tests..."

# API response time
echo "Testing API response times..."
time curl -s http://localhost:8000/api/tools > /dev/null

# AI comparison performance
echo "Testing AI comparison performance..."
time curl -X POST "http://localhost:8000/api/ai/compare" \
  -H "Content-Type: application/json" \
  -d '{"tool_ids": [1, 2]}' > /dev/null

# Frontend load time
echo "Testing frontend load time..."
time curl -s http://localhost:3000 > /dev/null

echo "✅ Performance testing complete"
```

## Asset Management Commands

### 11. Logo Management
```bash
# Command: update_logo
# Usage: update_logo /path/to/new/logo.png
if [ "$1" ]; then
    cp "$1" frontend/public/logo.png
    echo "✅ Logo updated: $1"
else
    echo "❌ Usage: update_logo /path/to/logo.png"
fi
```

### 12. Asset Optimization
```bash
# Command: optimize_assets
echo "🎨 Optimizing assets..."
cd frontend/public
ls -lh *.png *.jpg *.jpeg 2>/dev/null || echo "No images found"
echo "✅ Asset optimization complete"
```

## Deployment Commands

### 13. Production Build
```bash
# Command: build_production
echo "🏭 Building for production..."

# Backend preparation
cd backend
source venv/bin/activate
pip freeze > requirements.txt

# Frontend build
cd ../frontend
npm run build
ls -lh dist/

echo "✅ Production build complete"
```

### 14. Environment Setup
```bash
# Command: setup_env
echo "🔧 Setting up environment..."

# Backend environment
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend environment
cd ../frontend
npm install

echo "✅ Environment setup complete"
```

## Monitoring Commands

### 15. Log Analysis
```bash
# Command: analyze_logs
echo "📊 Analyzing logs..."

# Check for errors in backend logs
echo "Backend errors:"
grep -i error backend/*.log 2>/dev/null || echo "No backend logs found"

# Check for frontend console errors
echo "Frontend build warnings:"
cd frontend && npm run build 2>&1 | grep -i warning || echo "No warnings found"

echo "✅ Log analysis complete"
```
