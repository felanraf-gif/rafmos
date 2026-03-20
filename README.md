# GitMind - AI Code Review Assistant

## Overview

GitMind to AI asystent do automatycznej recenzji kodu dla GitLab Merge Requests.

## Features

- **Automatic Code Review** - AI analizuje zmiany i dodaje komentarze
- **Feedback Loop** - Agent uczy się z akceptacji/odrzuceń
- **Multi-LLM Support** - Groq, LMStudio, OpenAI
- **Security Focus** - Wykrywa problemy bezpieczeństwa

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

### Webhook
```
POST /webhook - GitLab webhook endpoint
```

### Code Review
```
POST /api/review - Recenzja MR
Body: {"project_id": 123, "mr_iid": 1}
```

### Feedback
```
GET  /api/feedback/stats     - Statystyki
GET  /api/feedback/recent    - Ostatnie recenzje  
POST /api/feedback/helpful   - Oznacz jako pomocne
POST /api/feedback/not-helpful - Oznacz jako niepomocne
GET  /api/feedback/tips      - Wskazówki dla agenta
```

## System Architecture

```
GitLab Webhook
     ↓
WebhookHandler
     ↓
GitLab API (pobierz MR)
     ↓
LLM (Groq) - generuj recenzję
     ↓
GitLab API (dodaj komentarz)
     ↓
FeedbackStorage (zapisz)
     ↓
LearningEngine (analizuj)
```

## Feedback System

### Status Recenzji
- `pending` - Nowa recenzja
- `accepted` - Developer uznał za pomocną
- `rejected` - Developer uznał za niepomocną  
- `outdated` - MR został zmergowany

### Typy Feedback
- `security` - Problemy bezpieczeństwa
- `bug` - Błędy logiczne
- `quality` - Jakość kodu
- `performance` - Wydajność

### Metryki
- `accuracy` - Dokładność = accepted / (accepted + rejected)
- `by_type` - Statystyki per typ problemu

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| GITLAB_TOKEN | GitLab Personal Access Token | - |
| GITLAB_WEBHOOK_SECRET | Webhook secret | - |
| GROQ_API_KEY | Groq API key | - |
| GROQ_MODEL | Model (llama-3.3-70b-versatile) | - |
| PORT | Server port | 8000 |

### LLM Providers

**Groq (default)**
```python
GROQ_CONFIG = {
    "api_key": "gsk_...",
    "model": "llama-3.3-70b-versatile",
    "temperature": 0.7,
}
```

**LMStudio (local)**
```python
LMSTUDIO_CONFIG = {
    "base_url": "http://localhost:1234/v1",
    "model": "qwen2.5-7b-instruct.gguf",
}
```

## Deployment

### Local
```bash
python gitmind/main.py
```

### Production
```bash
gunicorn -w 4 -b 0.0.0.0:8000 gitmind.main:app
```

### Docker
```dockerfile
FROM python:3.11
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "gitmind/main.py"]
```

## Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Feedback Stats
```bash
curl http://localhost:8000/api/feedback/stats
```

## Roadmap

- [x] Podstawowa recenzja kodu
- [x] System feedback  
- [x] Groq API integration
- [x] Automatyczne outdated przy merge
- [ ] Dashboard z wykresami
- [ ] Więcej LLM providerów (OpenAI, Anthropic)
- [ ] Security scanning
- [ ] Performance analysis

## License

MIT
