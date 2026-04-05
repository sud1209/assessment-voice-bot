import os
import json
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

# --- Structured JSON Logging ---
class JsonFormatter(logging.Formatter):
    def format(self, record):
        base = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
        }
        msg = record.getMessage()
        try:
            parsed = json.loads(msg)
            if isinstance(parsed, dict):
                base.update(parsed)
                return json.dumps(base)
        except (json.JSONDecodeError, TypeError):
            pass
        base["message"] = msg
        return json.dumps(base)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("sud-voice-bot")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.propagate = False

# --- Startup Validation ---
@asynccontextmanager
async def lifespan(_app: FastAPI):
    if not os.getenv("VAPI_PUBLIC_KEY") or not os.getenv("ASSISTANT_ID"):
        raise RuntimeError(
            "Missing required environment variables: VAPI_PUBLIC_KEY, ASSISTANT_ID. "
            "Copy .env.example to .env and fill in your Vapi credentials."
        )
    logger.info("Configuration validated. Server ready.")
    yield

app = FastAPI(title="Sud Rathi AI Voice Bot Server", lifespan=lifespan)

# --- Request Logging Middleware ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    latency_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(json.dumps({
        "path": request.url.path,
        "method": request.method,
        "status_code": response.status_code,
        "latency_ms": latency_ms,
    }))
    return response

current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "config_loaded": True,
        "version": "1.0.0",
    }

@app.get("/api/config")
async def get_config():
    logger.info("Config requested")
    return {
        "publicKey": os.getenv("VAPI_PUBLIC_KEY"),
        "assistantId": os.getenv("ASSISTANT_ID"),
    }

@app.get("/", response_class=HTMLResponse)
async def read_index():
    file_path = os.path.join(static_dir, "index.html")
    if not os.path.exists(file_path):
        logger.critical(f"Index file missing at {file_path}")
        return HTMLResponse(content="<h1>System Offline</h1>", status_code=500)
    with open(file_path, "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
