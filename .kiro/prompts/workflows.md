# CloudEngineered - Reusable Workflows

## AI Integration Workflows

### 1. Gemini AI Setup & Testing
```bash
# Workflow: setup_ai_integration
echo "🤖 Setting up AI integration..."

# Test API key
export GEMINI_API_KEY=$GEMINI_API_KEY
python -c "
import google.generativeai as genai
genai.configure(api_key='$GEMINI_API_KEY')
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content('Hello')
print('✅ Gemini AI connected successfully')
"

# Test comparison endpoint
curl -X POST "http://localhost:8000/api/ai/compare" \
  -H "Content-Type: application/json" \
  -d '{"tool_ids": [1, 2]}' | jq .

echo "✅ AI integration verified"
```

### 2. Natural Language Query Testing
```bash
# Workflow: test_nl_queries
echo "🗣️ Testing natural language queries..."

queries=(
  "Find me a Docker alternative for containers"
  "What's the best CI/CD tool for small teams"
  "Compare Kubernetes vs Docker Swarm"
  "Show me monitoring tools like Prometheus"
)

for query in "${queries[@]}"; do
  echo "Testing: $query"
  curl -X POST "http://localhost:8000/api/ai/search" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$query\"}" | jq .summary
done

echo "✅ Natural language testing complete"
```

## OAuth Integration Workflows

### 3. OAuth Provider Setup
```bash
# Workflow: setup_oauth
echo "🔐 Setting up OAuth integration..."

# Test provider endpoints
curl -s http://localhost:8000/api/auth/providers | jq .

# Verify OAuth URLs
echo "Google OAuth: http://localhost:8000/api/auth/google"
echo "GitHub OAuth: http://localhost:8000/api/auth/github"

# Test callback handling
echo "Callback URL configured: http://localhost:8000/api/auth/callback"

echo "✅ OAuth setup verified"
```

### 4. Authentication Flow Testing
```bash
# Workflow: test_auth_flow
echo "🔑 Testing authentication flows..."

# Test registration
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }' | jq .

# Test login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }' | jq .

echo "✅ Authentication flow tested"
```

## Data Enhancement Workflows

### 5. Multi-Source Data Pipeline
```bash
# Workflow: data_enhancement_pipeline
echo "📊 Running data enhancement pipeline..."

cd backend && source venv/bin/activate

# Stage 1: Base data seeding
echo "Stage 1: Seeding base data..."
python comprehensive_seed.py

# Stage 2: GitHub API enhancement
echo "Stage 2: GitHub enhancement..."
python enhance_tools.py

# Stage 3: Web scraping enhancement
echo "Stage 3: Web scraping..."
python web_scraper.py

# Stage 4: AI-powered descriptions
echo "Stage 4: AI enhancement..."
python comprehensive_enhancement.py

echo "✅ Data enhancement pipeline complete"
```

### 6. Real-time Data Updates
```bash
# Workflow: update_live_data
echo "🔄 Updating live data..."

cd backend && source venv/bin/activate

# Update GitHub statistics
python -c "
from enhance_tools import update_github_stats
update_github_stats()
print('✅ GitHub stats updated')
"

# Update package manager data
python -c "
from web_scraper import update_package_data
update_package_data()
print('✅ Package data updated')
"

echo "✅ Live data updates complete"
```

## Component Development Workflows

### 7. React Component Creation
```bash
# Workflow: create_component
# Usage: create_component ComponentName
COMPONENT_NAME=$1
if [ -z "$COMPONENT_NAME" ]; then
  echo "❌ Usage: create_component ComponentName"
  exit 1
fi

cat > "frontend/src/components/${COMPONENT_NAME}.tsx" << EOF
import React from 'react';

interface ${COMPONENT_NAME}Props {
  // Define props here
}

const ${COMPONENT_NAME}: React.FC<${COMPONENT_NAME}Props> = ({ }) => {
  return (
    <div className="p-4">
      <h2 className="text-xl font-bold">${COMPONENT_NAME}</h2>
      {/* Component content */}
    </div>
  );
};

export default ${COMPONENT_NAME};
EOF

echo "✅ Component created: ${COMPONENT_NAME}.tsx"
```

### 8. Component Testing Workflow
```bash
# Workflow: test_components
echo "🧩 Testing React components..."

cd frontend

# TypeScript compilation check
npx tsc --noEmit || echo "❌ TypeScript errors found"

# Build test
npm run build 2>&1 | grep -E "(error|Error)" && echo "❌ Build errors" || echo "✅ Build successful"

# Component file validation
find src/components -name "*.tsx" -exec echo "Checking {}" \;

echo "✅ Component testing complete"
```

## Database Management Workflows

### 9. Database Migration Workflow
```bash
# Workflow: migrate_database
echo "🗄️ Running database migrations..."

cd backend && source venv/bin/activate

# Backup existing database
cp cloudengineered.db cloudengineered.db.backup.$(date +%Y%m%d_%H%M%S)

# Run migrations
python -c "
from main import engine, Base
Base.metadata.create_all(bind=engine)
print('✅ Database schema updated')
"

echo "✅ Database migration complete"
```

### 10. Data Validation Workflow
```bash
# Workflow: validate_data
echo "✅ Validating database data..."

cd backend && source venv/bin/activate

python -c "
from main import SessionLocal, Tool, User, Review
session = SessionLocal()

# Validate tools
tools = session.query(Tool).all()
print(f'Tools count: {len(tools)}')

# Validate users
users = session.query(User).all()
print(f'Users count: {len(users)}')

# Validate reviews
reviews = session.query(Review).all()
print(f'Reviews count: {len(reviews)}')

session.close()
print('✅ Data validation complete')
"
```

## Performance Optimization Workflows

### 11. Performance Profiling
```bash
# Workflow: profile_performance
echo "⚡ Profiling application performance..."

# Backend API performance
echo "Testing API endpoints..."
for endpoint in "/api/tools" "/api/analytics/dashboard" "/api/auth/providers"; do
  echo "Testing $endpoint"
  time curl -s "http://localhost:8000$endpoint" > /dev/null
done

# Frontend bundle analysis
cd frontend
echo "Analyzing bundle size..."
npm run build
ls -lh dist/assets/

echo "✅ Performance profiling complete"
```

### 12. Optimization Implementation
```bash
# Workflow: optimize_app
echo "🚀 Implementing optimizations..."

# Backend optimizations
cd backend && source venv/bin/activate
echo "Optimizing database queries..."
python -c "
# Add database indexes
from main import engine
engine.execute('CREATE INDEX IF NOT EXISTS idx_tools_category ON tools(category)')
engine.execute('CREATE INDEX IF NOT EXISTS idx_reviews_tool_id ON reviews(tool_id)')
print('✅ Database indexes created')
"

# Frontend optimizations
cd ../frontend
echo "Optimizing frontend bundle..."
npm run build
echo "✅ Frontend optimized"

echo "✅ Application optimization complete"
```
