# Changelog

## v0.2.0 (2026-03-20)

### Added
- Feedback system z zapisem recenzji
- System uczenia się z adaptacyjnymi progami
- Automatyczne outdated przy merge
- Endpointy API:
  - `GET /api/feedback/stats` - statystyki
  - `GET /api/feedback/recent` - ostatnie recenzje
  - `POST /api/feedback/helpful` - oznacz jako pomocne
  - `POST /api/feedback/not-helpful` - oznacz jako niepomocne
  - `GET /api/feedback/tips` - wskazówki
  - `GET /api/learning/status` - status uczenia
  - `GET /api/learning/summary` - podsumowanie
- Lepsze prompty dla code review (CRITICAL/HIGH/MEDIUM/LOW)
- Groq API integration (Llama 3.3)
- Dokumentacja README.md

### Features
- Klasyfikacja problemów: security, bug, quality, performance
- Adaptacyjne progi zgłaszania problemów
- Historia lekcji agenta

## v0.1.0 (2026-03-19)

### Added
- Podstawowy GitMind Flask API
- GitLab webhook integration
- Code review dla MR
- SimpleAgent z tool registry
- Q-Learning brain (qbrain)
- Web search z Exa API

---

## Data Files

| File | Description |
|------|-------------|
| `gitmind/review_feedback.json` | Historia recenzji i feedback |
| `qbrain/memories.json` | Pamięć agenta |
| `qbrain/brain.json` | Q-Learning weights |

---

## API Reference

### POST /api/review
```json
{
  "project_id": 80272702,
  "mr_iid": 1
}
```

### POST /api/feedback/helpful
```json
{
  "project_id": 80272702,
  "mr_iid": 1
}
```

### Response
```json
{
  "success": true,
  "marked": "helpful",
  "message": "📊 Statystyki Feedbacku:\n\n• Wszystkie recenzje: 1\n..."
}
```
