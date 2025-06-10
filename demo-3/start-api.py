#!/usr/bin/env python3

import uvicorn
from main import app

if __name__ == "__main__":
    print("[STARTUP] Starting AWS Workshop API server (Demo 3) on port 8001...")
    print("[STARTUP] Health endpoint: http://localhost:8001/health")
    print("[STARTUP] Chat endpoint: http://localhost:8001/chat")
    print("[STARTUP] API docs: http://localhost:8001/docs")
    print("[STARTUP] Alternative API docs: http://localhost:8001/redoc")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8001, 
        reload=True,
        log_level="info"
    ) 