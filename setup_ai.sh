#!/bin/bash

echo "🔧 CloudEngineered Platform Setup"
echo ""
echo "This platform uses Google Gemini AI for real-time tool comparisons."
echo ""
echo "📝 To enable AI comparisons:"
echo "1. Get a free API key from: https://makersuite.google.com/app/apikey"
echo "2. Set the environment variable:"
echo "   export GEMINI_API_KEY='your-api-key-here'"
echo ""
echo "Or create a .env file in the backend directory with:"
echo "   GEMINI_API_KEY=your-api-key-here"
echo ""
echo "⚠️  Without an API key, the system will use the fallback knowledge base"
echo "   which has limited tool coverage (Docker, Kubernetes, Jenkins, etc.)"
echo ""
echo "✅ With an API key, you can compare ANY DevOps tools in real-time!"
echo ""

# Check if API key is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY not set - using fallback mode"
else
    echo "✅ GEMINI_API_KEY is configured"
fi

echo ""
echo "🚀 Starting servers..."
