# Zobot — Intelligent Wealth Operating System

> AI-powered wealth management platform for Indian retail banking. Replaces traditional DSAs with a deterministic financial intelligence engine backed by a local LLM, real-time market data, and enterprise-grade security.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Security](#security)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## Overview

Zobot is a full-stack financial intelligence platform built for Indian retail banking. It combines deterministic financial analysis engines with a locally-hosted LLM (Ollama) to deliver personalized, compliant, and revenue-optimized investment guidance — without sending any customer data to external AI services.

**Core philosophy:** LLM explains. Engines decide.

| Layer | Technology |
|---|---|
| Frontend | Vanilla HTML / CSS / JavaScript |
| Backend | FastAPI (Python 3.11+) |
| AI | Ollama — llama3.2:1b (local) |
| Database | SQLite via SQLAlchemy ORM |
| Market Data | Groww API (NSE/BSE live data) |
| Charts | TradingView Widgets |

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                    FRONTEND                          │
│   index.html · script.js · api.js · styles.css      │
│   login.html · security-dashboard.html              │
└──────────────────────┬───────────────────────────────┘
                       │ HTTP / REST
┌──────────────────────▼───────────────────────────────┐
│              PROMPT INJECTION FIREWALL               │
│   SYSTEM_OVERRIDE · ROLE_MANIPULATION                │
│   DATA_EXFILTRATION · FINANCIAL_FRAUD                │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│                  FASTAPI BACKEND                     │
│   routes.py · ollama_service · indian_stock_api      │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│              ANALYSIS ENGINES                        │
│   Income Engine · Stress Score · Emergency Radar     │
│   Spend Analyzer · Recommendation Engine            │
└──────────────────────┬───────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────┐
│              SQLite DATABASE                         │
│   Users · Transactions · Investments · Audit Logs   │
└──────────────────────────────────────────────────────┘
```

---

## Features

### Financial Analysis Engines

| Engine | Description |
|---|---|
| **Income Variability Engine** | Detects income stability, recommends Fixed / Dynamic / Flexible SIP |
| **Financial Stress Score** | 0–100 composite score across 5 weighted factors |
| **Emergency Risk Radar** | Blocks high-risk products if liquidity < 3 months expenses |
| **Spend Analyzer** | Categorizes transactions, surfaces savings opportunities |
| **Recommendation Engine** | Ranks bank products by suitability, tax fit, and revenue yield |

### AI Conversational Layer
- Powered by **Ollama llama3.2:1b** — runs fully locally, zero data leakage
- Multi-language: English, Hindi, Telugu, Bilingual
- Intent detection: stock queries, investment advice, spending analysis, financial health
- Anti-hallucination: LLM only narrates data provided by deterministic engines

### Live Market Data
- Real-time stock quotes via **Groww API** (NSE/BSE)
- Dynamic stock detection from natural language queries
- TradingView chart auto-updates on stock mentions
- Market indices: NIFTY 50, SENSEX

### Prompt Injection Firewall
- 4 attack categories with regex pattern matching and confidence scoring
- Whitelist for legitimate financial queries
- Real-time statistics and audit logging
- Dedicated security testing dashboard

---

## Project Structure

```
Zobot/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py              # All API endpoints
│   │   ├── engines/
│   │   │   ├── income_engine.py       # Income variability analysis
│   │   │   ├── stress_score.py        # Financial stress scoring
│   │   │   ├── emergency_radar.py     # Emergency fund gating
│   │   │   └── spend_analyzer.py      # Transaction categorization
│   │   ├── security/
│   │   │   ├── __init__.py
│   │   │   └── prompt_firewall.py     # Prompt injection firewall
│   │   ├── services/
│   │   │   ├── ollama_service.py      # LLM integration
│   │   │   ├── indian_stock_api.py    # Groww API wrapper
│   │   │   └── recommendation.py     # Product ranking engine
│   │   ├── database.py                # SQLAlchemy models
│   │   ├── models.py                  # Pydantic schemas
│   │   └── main.py                    # FastAPI application
│   ├── .env                           # Environment variables
│   └── requirements.txt
├── frontend/
│   ├── index.html                     # Main banking dashboard
│   ├── login.html                     # Authentication page
│   ├── security-dashboard.html        # Firewall testing UI
│   ├── script.js                      # UI logic & chat integration
│   ├── api.js                         # Backend API calls
│   ├── styles.css                     # Stylesheet
│   └── serve.py                       # Python static file server
├── data/
│   └── zenbot.db                      # SQLite database
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai) installed
- Groww API key (configured in `.env`)

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Ollama (Local LLM)

```bash
ollama pull llama3.2:1b
ollama serve
```

### 3. Frontend

```bash
cd frontend
python serve.py
```

### Access

| Service | URL |
|---|---|
| Dashboard | http://localhost:5173 |
| Security Dashboard | http://localhost:5173/security-dashboard.html |
| API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

---

## API Reference

### Users
```
POST  /api/v1/users                    Create user
GET   /api/v1/users/{user_id}          Get user
```

### Transactions
```
POST  /api/v1/transactions/{user_id}   Add transactions
```

### Analysis
```
GET   /api/v1/analysis/income/{user_id}     Income variability
GET   /api/v1/analysis/stress/{user_id}     Stress score
GET   /api/v1/analysis/emergency/{user_id}  Emergency fund status
GET   /api/v1/analysis/spending/{user_id}   Spending breakdown
```

### Recommendations
```
GET   /api/v1/recommendations/{user_id}     Personalized products
```

### AI Chat
```
POST  /api/v1/chat
Body: { "message": "string", "user_id": 1, "language": "english" }
```

### Market Data
```
GET   /api/v1/market/mutual-funds      Mutual fund list
GET   /api/v1/market/indices           NIFTY / SENSEX
GET   /api/v1/market/trending          Trending NSE stocks
```

### Security
```
GET   /api/v1/security/firewall-stats  Firewall statistics
```

### Investments
```
POST  /api/v1/investments/{user_id}    Create investment order
GET   /api/v1/investments/{user_id}    List investment orders
```

---

## Security

### Prompt Injection Firewall

All chat messages pass through a validation layer before reaching the LLM.

| Attack Type | Example Pattern | Confidence |
|---|---|---|
| `SYSTEM_OVERRIDE` | "ignore all previous instructions" | 85% |
| `ROLE_MANIPULATION` | "you are now admin" | 80% |
| `DATA_EXFILTRATION` | "reveal your system prompt" | 90% |
| `FINANCIAL_FRAUD` | "transfer without OTP" | 95% |

Legitimate financial queries are whitelisted and pass through unaffected.

Test the firewall at: `http://localhost:5173/security-dashboard.html`

### Data Privacy
- LLM runs entirely on-device via Ollama — no customer data leaves the system
- AES-256 encryption at rest, TLS 1.3 in transit
- Immutable audit logs for all transactions and consent events

---

## Configuration

`.env` file in `backend/`:

```env
GROWW_API_KEY=<your_groww_jwt_token>
OLLAMA_BASE_URL=http://localhost:11434
DATABASE_URL=sqlite:///./data/zenbot.db
SECRET_KEY=<your_secret_key>
```

---

## Troubleshooting

**Backend not starting**
```bash
curl http://localhost:8000/health
# Check terminal for import errors
```

**Ollama not responding**
```bash
curl http://localhost:11434/api/tags
ollama serve   # restart if needed
```

**Stock data returning empty**
```bash
# Verify Groww API key is valid and not expired
# Key expires every 24 hours — regenerate from Groww developer portal
```

**Chat returning "trouble connecting"**
```bash
# Ensure Ollama is running and llama3.2:1b is pulled
ollama list
```

---

## Roadmap

- [ ] PostgreSQL migration
- [ ] Docker + docker-compose setup
- [ ] Real-time portfolio rebalancing
- [ ] Tax optimization engine (80C, ELSS)
- [ ] Insurance product integration
- [ ] Mobile app (React Native)
- [ ] Kubernetes deployment manifests

---

## License

Proprietary — All Rights Reserved.  
Built for Indian Retail Banking.
