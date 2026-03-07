import os
import logging
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sud-voice-bot")

load_dotenv()
app = FastAPI(title="Sud Rathi AI Voice Bot Server")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Path: {request.url.path} | Latency: {process_time:.4f}s")
    return response


current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sud-voice-bot", "version": "1.0.0"}

@app.get("/api/config")
async def get_config():
    pub_key = os.getenv("VAPI_PUBLIC_KEY")
    ast_id = os.getenv("ASSISTANT_ID")
    
    if not pub_key or not ast_id:
        logger.error("Configuration keys missing in environment variables")
        raise HTTPException(status_code=500, detail="Server configuration error")
        
    logger.info("Session configuration requested and served")
    return {
        "publicKey": pub_key,
        "assistantId": ast_id
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