# Zobot — Intelligent Wealth Operating System: Project Summary

## Project Short Description
**Zobot** is an AI-powered, full-stack financial intelligence platform designed for Indian retail banking and personal wealth management. It replaces traditional Direct Selling Agents (DSAs) with a deterministic financial intelligence engine backed by a locally-hosted Large Language Model (LLM). The platform's primary goal is to provide users with personalized, compliant, and highly secure investment guidance and financial tracking without ever sending sensitive customer data to external AI services.

**Target Users:** Retail banking customers, young professionals, and individuals seeking smart, private, and data-driven financial advice and wealth management.

## Problem Statement
Users need intelligent financial guidance, spending analysis, and investment recommendations, but utilizing third-party cloud AI models (like OpenAI or Anthropic) introduces massive data privacy and security risks for sensitive financial data. Furthermore, traditional LLMs are prone to hallucination, which is unacceptable in financial advisory. Users need a system that offers the conversational ease of an AI, but with absolute mathematical certainty and zero data exfiltration.

## Solution & Uniqueness
Zobot solves this by employing a unique **"LLM explains. Engines decide."** architecture. 
Instead of relying on the LLM to do financial math, the system uses custom-built, deterministic Python engines to analyze income, calculate stress scores, and gate risky investments. A locally hosted LLM (Ollama - llama3.2:1b) is then used purely as a conversational layer to explain these deterministic results to the user. This ensures **zero hallucination** and **100% data privacy** since the data never leaves the local environment.

## Key Features & What We Have Integrated

### 1. Deterministic Financial Analysis Engines
- **Spend Analyzer:** Automatically categorizes transactions and surfaces savings opportunities.
- **Financial Stress Score:** Calculates a 0–100 composite score based on 5 weighted financial factors.
- **Income Variability Engine:** Detects income stability to recommend Fixed, Dynamic, or Flexible SIPs.
- **Emergency Risk Radar:** Blocks high-risk product investments if user liquidity is under 3 months of expenses.
- **Recommendation Engine:** Ranks banking and investment products by suitability and tax fit.

### 2. Localized AI Conversational Layer
- **Powered by Ollama (llama3.2:1b):** Runs fully locally, guaranteeing zero data leakage.
- **Multi-language Support:** Capable of conversing in English, Hindi, Telugu, and bilingual formats.
- **Anti-Hallucination:** The AI only narrates data explicitly provided by the deterministic engines.

### 3. Prompt Injection Firewall (Security)
- A dedicated security layer that intercepts all chat messages before they reach the LLM.
- **Pattern Matching:** Protects against `SYSTEM_OVERRIDE`, `ROLE_MANIPULATION`, `DATA_EXFILTRATION`, and `FINANCIAL_FRAUD` with confidence scoring.
- **Dedicated Security UI:** Includes a separate testing dashboard (`security-dashboard.html`) to visualize firewall stats and audit logs.

### 4. Live Market Data Integration
- **Groww API Integration:** Fetches real-time NSE/BSE stock quotes and mutual fund data.
- **Dynamic Charting:** Integrates TradingView widgets that auto-update based on natural language stock mentions.
- **Market Indices:** Real-time tracking of NIFTY 50 and SENSEX.

### 5. Full-Stack Architecture
- **Frontend:** Responsive vanilla HTML/CSS/JS with a real-time banking dashboard and dark mode.
- **Backend:** High-performance FastAPI (Python 3.11+) backend.
- **Database:** Local SQLite database using SQLAlchemy ORM for managing users, transactions, and audit logs securely.
