# 🛡️ SafePrompt

**Prompt injection detection and sanitization API** — detect and neutralize malicious prompts before they reach your LLM pipelines.

---

## Features

- ⚡ **Fast detection** — regex + heuristic scanning under 5ms
- 🔐 **Risk scoring** — 0.0 → 1.0 confidence score per request
- 🧹 **Auto-sanitization** — strips dangerous patterns from input
- 🐳 **Docker-first** — multi-stage builds, non-root runtime, health checks
- 🔄 **Full CI/CD** — lint → test → scan → build → push → deploy

---

## Quick Start

```bash
# Clone
git clone https://github.com/your-org/safeprompt
cd safeprompt

# Start the stack
make up

# Hit the API
curl -X POST http://localhost/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the capital of France?"}'
```

---

## API

### `POST /analyze`

```json
{
  "prompt": "string",
  "strict_mode": false
}
```

**Response:**
```json
{
  "safe": true,
  "risk_score": 0.0,
  "threats_detected": [],
  "sanitized_prompt": "What is the capital of France?",
  "processing_time_ms": 0.42
}
```

### `GET /health`
```json
{ "status": "ok", "version": "1.0.0" }
```

---

## Development

```bash
# Hot-reload dev mode
make dev

# Run tests
make test

# Lint
make lint

# Vulnerability scan
make scan
```

---

## CI/CD Pipeline (GitHub Actions)

```
push / PR
   │
   ├─ 1. Lint & Static Analysis (Ruff, mypy)
   │
   ├─ 2. Unit Tests (pytest inside Docker)
   │
   ├─ 3. Security Scan (Trivy — CRITICAL/HIGH)
   │
   ├─ 4. Build & Push multi-arch image (amd64, arm64)
   │       → ghcr.io/<org>/safeprompt-api:<tag>
   │
   ├─ 5. Integration Tests (docker-compose smoke tests)
   │
   └─ 6. Deploy
        ├─ develop branch → Staging
        └─ GitHub Release → Production
```

### Required Secrets

| Secret | Description |
|--------|-------------|
| `GITHUB_TOKEN` | Auto-provided by GitHub Actions |
| `DEPLOY_KEY` | SSH key for deploy targets |

---

## Project Structure

```
safeprompt/
├── app/
│   ├── main.py          # FastAPI application
│   ├── requirements.txt
│   ├── Dockerfile       # Multi-stage build
│   └── .dockerignore
├── tests/
│   └── test_api.py      # Pytest test suite
├── nginx/
│   └── nginx.conf       # Reverse proxy + rate limiting
├── .github/
│   └── workflows/
│       └── ci-cd.yml    # Full CI/CD pipeline
├── docker-compose.yml       # Production stack
├── docker-compose.dev.yml   # Dev overrides
├── Makefile             # Developer shortcuts
└── README.md
```

---

## Architecture

```
Internet → Nginx (rate limit, headers) → SafePrompt API → Response
                    :80                       :8000
```

---

## License

MIT
