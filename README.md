# AI Voice Interview Bot

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?logo=fastapi&logoColor=white)
![Vapi AI](https://img.shields.io/badge/Vapi_AI-Voice_SDK-6366f1)
![License](https://img.shields.io/badge/license-MIT-green)

A fun experiment: an AI-powered introduction bot you can actually talk to. Visitors click a button and interview me out loud — ask about my work, projects, opinions on AI, whatever. The assistant answers as me in real time.

> **Screenshot:** *(drop a screenshot of the UI here)*

---

## What it does

Instead of reading a static bio or portfolio, visitors can have a live voice conversation with an AI trained on context about me. Ask it anything you'd ask in a first conversation — what I'm working on, how I think about AI engineering, what 100x.inc does. It responds naturally, in real time.

Under the hood: a minimal FastAPI backend serves the frontend and exposes a `/api/config` endpoint that securely passes Vapi credentials to the browser. [Vapi AI](https://vapi.ai) handles all the voice processing (STT → LLM → TTS) in the cloud — the server never touches audio.

---

## Architecture

```
Browser
  │
  ├─── GET /           → FastAPI → serves static/index.html
  ├─── GET /api/config → FastAPI → returns Vapi public key + assistant ID
  │
  └─── Voice call ─────→ Vapi AI (cloud)
                             ├─ Speech-to-text (STT)
                             ├─ LLM (conversation)
                             └─ Text-to-speech (TTS)
```

The server never touches audio — all voice processing happens in Vapi's cloud. The backend's only jobs are serving the frontend and keeping credentials server-side.

---

## Local Setup

**Prerequisites:** Python 3.12+, a [Vapi account](https://dashboard.vapi.ai) with a configured assistant.

```bash
# 1. Clone
git clone https://github.com/sud1209/assessment-voice-bot.git
cd ai-voice-bot

# 2. Set up environment variables
cp .env.example .env
# Edit .env and fill in your VAPI_PUBLIC_KEY and ASSISTANT_ID

# 3. Install dependencies
pip install -r requirements.txt
# or, if you have uv:
uv sync

# 4. Run
python main.py

# 5. Open in browser
open http://localhost:8000
```

The server starts on port 8000 by default. Set `PORT` in `.env` to override.

**Getting Vapi credentials:**
1. Create an account at [dashboard.vapi.ai](https://dashboard.vapi.ai)
2. Create an assistant and copy its ID → `ASSISTANT_ID`
3. Go to Account → API Keys and copy your public key → `VAPI_PUBLIC_KEY`

---

## Running Tests

```bash
pytest
# or with uv:
uv run pytest
```

Tests cover all three API endpoints, including startup failure when environment variables are missing.

---

## Docker

```bash
# Build
docker build -t ai-voice-bot .

# Run (reads credentials from .env)
docker run -p 8000:8000 --env-file .env ai-voice-bot
```

Works on any Docker-compatible platform: Render, Fly.io, Railway, or a plain VPS. Set `VAPI_PUBLIC_KEY` and `ASSISTANT_ID` as environment variables on your platform.

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serves the frontend (index.html) |
| `/health` | GET | Health check — returns `{"status": "ok", "config_loaded": true, "version": "1.0.0"}` |
| `/api/config` | GET | Returns Vapi public key and assistant ID for the browser SDK |

---

## Tech Stack

| Tool | Role |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com) | Async Python web framework — minimal overhead, automatic OpenAPI docs |
| [Vapi AI](https://vapi.ai) | Managed voice AI SDK — handles STT, LLM routing, and TTS in one call |
| [UV](https://docs.astral.sh/uv/) | Fast Python package manager with reproducible lockfile |
| [Uvicorn](https://www.uvicorn.org) | ASGI server for running FastAPI |
| Vanilla JS | No build step, no bundler — fast browser load, easy to read |

---

## License

MIT
