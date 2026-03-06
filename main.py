import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_index():
    # Use absolute path to avoid "where is the file?" confusion
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "static", "index.html")
    
    print(f">>> [SERVER] Attempting to serve: {file_path}")
    
    if not os.path.exists(file_path):
        return f"CRITICAL ERROR: File not found at {file_path}"

    with open(file_path, "r") as f:
        content = f.read()
    
    # Inject keys
    content = content.replace("REPLACE_WITH_PUBLIC_KEY", os.getenv("VAPI_PUBLIC_KEY", ""))
    content = content.replace("REPLACE_WITH_ASSISTANT_ID", os.getenv("ASSISTANT_ID", ""))
    
    return content

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)