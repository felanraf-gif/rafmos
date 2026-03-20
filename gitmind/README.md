# GitMind - AI Assistant for GitLab

AI-powered code review and issue assistance for GitLab.

## Features

- **Automatic Code Review** - AI analyzes merge requests and provides feedback
- **Issue Assistance** - Helps users with GitLab issues
- **MR Description Generator** - Creates merge request descriptions
- **Hybrid Deployment** - Works as SaaS or self-hosted

## Quick Start

### 1. Install dependencies
```bash
cd gitmind
pip install -r requirements.txt
```

### 2. Configure environment
```bash
export GITLAB_TOKEN="your_gitlab_token"
export GITLAB_WEBHOOK_SECRET="your_secret"
export LLM_URL="http://localhost:1234/v1"
export LLM_MODEL="qwen2.5-7b-instruct.gguf"
```

### 3. Run locally
```bash
python main.py
```

### 4. Set up GitLab webhook
1. Go to your GitLab project → Settings → Webhooks
2. Add webhook URL: `https://your-domain.com/webhook`
3. Select events: Merge requests, Issues, Comments

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/webhook` | POST | GitLab webhook |
| `/api/review` | POST | Trigger MR review |
| `/api/issue` | POST | Get issue help |
| `/api/chat` | POST | Chat with AI |

## Configuration

Environment variables:
- `GITLAB_TOKEN` - GitLab personal access token
- `GITLAB_WEBHOOK_SECRET` - Webhook secret token
- `LLM_URL` - LLM API URL (default: http://localhost:1234/v1)
- `LLM_MODEL` - Model name
- `PORT` - Server port (default: 8000)

## Deployment

### Docker
```dockerfile
FROM python:3.11
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

### Railway/Render
1. Connect your GitHub repository
2. Set environment variables
3. Deploy

## Pricing

| Plan | Price | Features |
|------|-------|----------|
| Free | $0 | 50 MR/month, 1 repo |
| Pro | $9/mo | Unlimited MR, 10 repos |
| Team | $29/mo | Multi-repo, team features |

## License

MIT
