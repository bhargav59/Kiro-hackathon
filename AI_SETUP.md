# AI-Powered Real-Time Comparison Setup

## Overview
CloudEngineered can compare **ANY** DevOps tools in real-time using Google Gemini AI. This means you're not limited to tools in our database!

## How It Works

### Without AI API Key (Fallback Mode)
- Uses built-in knowledge base
- Covers popular tools: Docker, Kubernetes, Jenkins, GitHub Actions, Terraform, OpenTofu, Podman
- Provides quantitative data for these tools
- Generic comparisons for unknown tools

### With AI API Key (Real-Time Mode) ✨
- Compares **ANY** tools you enter
- Fetches real-time data and metrics
- Provides quantitative analysis with sources
- No database limitations!

## Setup Instructions

### 1. Get a Free API Key
Visit: https://makersuite.google.com/app/apikey
- Sign in with Google account
- Click "Create API Key"
- Copy the key

### 2. Configure the Key

**Option A: Environment Variable (Recommended)**
```bash
export GEMINI_API_KEY='your-api-key-here'
```

**Option B: .env File**
Create `backend/.env`:
```
GEMINI_API_KEY=your-api-key-here
```

### 3. Restart Backend
```bash
cd backend
source venv/bin/activate
python main.py
```

## Testing

Try comparing tools not in the database:
- Spacelift vs Atlantis
- ArgoCD vs Flux
- Pulumi vs CDK
- CircleCI vs Travis CI
- Any tools you want!

## Features with AI

✅ Real-time data fetching
✅ Quantitative metrics (GitHub stars, pricing, market share)
✅ Compliance certifications (SOC2, ISO27001)
✅ Performance benchmarks
✅ ROI calculations
✅ Source citations
✅ No database limitations

## Fallback Behavior

If AI fails or API key is not set:
- System automatically uses knowledge base
- Provides generic but structured comparisons
- No errors shown to users
- Seamless experience

## Cost

Google Gemini API:
- **Free tier**: 60 requests/minute
- **Sufficient for**: Hackathon demos and small deployments
- **Upgrade**: Available for production use

## Privacy

- Tool names are sent to Google Gemini API
- No user data or sensitive information shared
- Comparisons are not stored
- Real-time generation each time
