# GitMind - AI Code Review Assistant

## Overview

GitMind to AI asystent do automatycznej recenzji kodu dla GitLab Merge Requests.

## Live Demo

**API:** https://felanraf-gif-project.onrender.com
**Landing:** https://felanraf-gif.github.io/rafmos/

## Features

- **Automatic Code Review** - AI analizuje zmiany i dodaje komentarze z emoji i statystykami
- **Security Scanning** - Wykrywa hardcoded secrets, API keys, tokens (automatycznie ukrywane)
- **Feedback Loop** - Agent uczy się z akceptacji/odrzuceń
- **Multi-LLM Support** - Groq, LMStudio, OpenAI
- **Rate Limiting** - Ochrona przed abuse
- **Input Validation** - Walidacja wszystkich danych wejściowych
- **Retry Logic** - Automatyczne powtórzenia przy błędach GitLab API
- **Caching** - Cache dla MR data
- **Async Processing** - Background processing
- **Uptime Monitoring** - Health checks i status

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
export GITLAB_TOKEN="your-token"
export GROQ_API_KEY="your-key"

# Run
python gitmind/main.py
```

## API Endpoints

### Status
```
GET  /                   - Root info
GET  /health            - Health check
GET  /api/status         - Service status + uptime
GET  /api/uptime         - Uptime metrics
```

### Webhook
```
POST /webhook - GitLab webhook endpoint (automatyczna recenzja)
```

### Code Review
```
POST /api/review         - Recenzja MR (rate limited: 10/min)
POST /api/chat          - Chat z AI (rate limited: 5/min)
```

### Feedback
```
GET  /api/feedback/stats         - Statystyki
GET  /api/feedback/recent        - Ostatnie recenzje
POST /api/feedback/helpful       - Oznacz jako pomocne
POST /api/feedback/not-helpful   - Oznacz jako niepomocne
GET  /api/feedback/tips          - Wskazówki dla agenta
```

### Infrastructure
```
GET  /api/cache/stats           - Cache stats
GET  /api/tasks/status/<id>    - Task status
```

## Security

- Input validation (wszystkie endpointy)
- Secret sanitization (API keys nigdy nie są ujawniane)
- Rate limiting (per IP)
- HMAC token verification (webhook)
- Constant-time comparison (tokeny)

## System Architecture

```
GitLab Webhook
     ↓
InputValidation
     ↓
WebhookHandler
     ↓
GitLab API (pobierz MR) ← Retry Logic
     ↓
LLM (Groq) - generuj recenzję
     ↓
SecretSanitization
     ↓
GitLab API (dodaj komentarz)
     ↓
FeedbackStorage (zapisz)
     ↓
LearningEngine (analizuj)
```

## Monitoring

### Health Check
```bash
curl https://felanraf-gif-project.onrender.com/health
```

### Uptime Metrics
```bash
curl https://felanraf-gif-project.onrender.com/api/uptime
```

### Feedback Stats
```bash
curl https://felanraf-gif-project.onrender.com/api/feedback/stats
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| GITLAB_TOKEN | GitLab Personal Access Token | Yes |
| GITLAB_WEBHOOK_SECRET | Webhook secret | No |
| GROQ_API_KEY | Groq API key | Yes |
| GROQ_MODEL | Model (llama-3.3-70b-versatile) | No |
| SENTRY_DSN | Sentry DSN for error tracking | No |
| PORT | Server port | No (8000) |

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_validators.py -v
pytest tests/test_sanitization.py -v
pytest tests/test_integration.py -v
```

## Deployment

### Render (Recommended)
1. Connect GitHub repo
2. Set environment variables
3. Deploy

### Docker
```bash
docker build -t gitmind .
docker run -p 8000:8000 \
  -e GITLAB_TOKEN=xxx \
  -e GROQ_API_KEY=xxx \
  gitmind
```

## Roadmap

- [x] Podstawowa recenzja kodu
- [x] System feedback  
- [x] Groq API integration
- [x] Automatyczne outdated przy merge
- [x] Security scanning
- [x] Rate limiting
- [x] Input validation
- [x] Retry logic
- [x] Caching
- [x] Uptime monitoring
- [x] 66+ tests passing
- [ ] Dashboard z wykresami
- [ ] SaaS / Freemium model
- [ ] GitLab Marketplace app

## License

MIT
