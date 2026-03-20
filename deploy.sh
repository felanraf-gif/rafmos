#!/bin/bash
set -e

echo "🚀 GitMind Deployment Script"

# Check for required environment variables
if [ -z "$GITLAB_TOKEN" ]; then
    echo "❌ Error: GITLAB_TOKEN is not set"
    exit 1
fi

if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ Error: GROQ_API_KEY is not set"
    exit 1
fi

echo "✅ Environment variables validated"

# Option 1: Docker
if command -v docker &> /dev/null; then
    echo "🐳 Building Docker image..."
    docker build -t gitmind .
    echo "✅ Docker image built"
    
    echo "🚀 Starting GitMind..."
    docker run -d \
        --name gitmind \
        -p 8000:8000 \
        -e GITLAB_TOKEN="$GITLAB_TOKEN" \
        -e GITLAB_WEBHOOK_SECRET="$GITLAB_WEBHOOK_SECRET" \
        -e GROQ_API_KEY="$GROQ_API_KEY" \
        -e EXA_API_KEY="$EXA_API_KEY" \
        --restart unless-stopped \
        gitmind
    
    echo "✅ GitMind started on http://localhost:8000"
    echo "📊 Health check: curl http://localhost:8000/health"

# Option 2: Docker Compose
elif [ -f "docker-compose.yml" ]; then
    echo "🐳 Starting with Docker Compose..."
    docker-compose up -d
    echo "✅ GitMind started"

# Option 3: Virtual Environment
else
    echo "📦 Using virtual environment..."
    
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements.txt
    
    echo "🚀 Starting GitMind with gunicorn..."
    gunicorn --bind 0.0.0.0:8000 --workers 4 --threads 2 gitmind.main:app &
    
    echo "✅ GitMind started on http://localhost:8000"
fi

echo ""
echo "📝 Next steps:"
echo "1. Set up webhook in GitLab: Settings → Webhooks"
echo "2. URL: http://your-domain.com/webhook"
echo "3. Test: curl -X POST http://localhost:8000/api/review -H 'Content-Type: application/json' -d '{\"project_id\": YOUR_ID, \"mr_iid\": 1}'"
