# GitMind Deployment Guide

## Prerequisites

- Docker (recommended) or Python 3.11+
- GitLab account with Personal Access Token
- Groq API key (free at console.groq.com)
- Optional: Exa API key for web search

## Quick Start

### 1. Clone and Configure

```bash
git clone <repo>
cd rafmos-main

# Copy environment template
cp .env.deploy .env

# Edit .env with your keys
nano .env
```

### 2. Deploy

#### Option A: Docker (Recommended)

```bash
chmod +x deploy.sh
./deploy.sh
```

#### Option B: Docker Compose

```bash
cp .env.deploy .env
docker-compose up -d
```

#### Option C: Manual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:8000 --workers 4 gitmind.main:app
```

## GitLab Webhook Setup

1. Go to your GitLab project → **Settings** → **Webhooks**

2. Add webhook:
   - **URL**: `https://your-domain.com/webhook`
   - **Secret Token**: (your secret from .env)
   - **Triggers**: ✅ Merge request events

3. Click **Add webhook**

4. Test by creating a Merge Request

## API Usage

### Health Check
```bash
curl http://localhost:8000/health
```

### Manual Review
```bash
curl -X POST http://localhost:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{"project_id": 12345678, "mr_iid": 1}'
```

### Feedback Stats
```bash
curl http://localhost:8000/api/feedback/stats
```

## Production Checklist

- [ ] Set `DEBUG=false` in .env
- [ ] Use HTTPS (Cloudflare, Nginx proxy)
- [ ] Set secure `GITLAB_WEBHOOK_SECRET`
- [ ] Configure firewall (only port 80/443)
- [ ] Set up monitoring (optional)
- [ ] Regular backups of `review_feedback.json`

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| GITLAB_TOKEN | Yes | - | GitLab Personal Access Token |
| GITLAB_WEBHOOK_SECRET | Yes | - | Webhook secret |
| GROQ_API_KEY | Yes | - | Groq API key |
| GROQ_MODEL | No | llama-3.3-70b-versatile | LLM model |
| EXA_API_KEY | No | - | Exa API key for search |
| PORT | No | 8000 | Server port |

## Troubleshooting

### Webhook not working
```bash
# Check if server is accessible
curl https://your-domain.com/health

# Check webhook logs
docker logs gitmind
```

### LLM errors
```bash
# Test Groq connection
curl -X POST https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -d '{"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": "test"}]}'
```

## Backup

```bash
# Backup feedback data
cp gitmind/review_feedback.json review_feedback_backup.json
```
