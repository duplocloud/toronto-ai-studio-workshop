from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import json
import traceback
from utils import Endpoint

app = FastAPI(title="AWS Workshop API", version="0.1.0")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    print("[HEALTH] Health check requested")
    return {"status": "healthy", "service": "aws-workshop-api"}

@app.post("/chat")
async def chat(payload: Dict[str, Any] = Body(...)):
    """
    Simple echo endpoint that returns what the user sends.
    Accepts a message payload and echoes it back in the original complex format.
    """
    try:
        
        print(f"[CHAT REQUEST] Received payload: {json.dumps(payload, indent=2)}")

        # Parse content from the payload using the utility method
        message = Endpoint.parse(payload)
        content = message.get("content", "")

        print(f"Extracted content: {content}")
        
        # Create echo response
        echo_response = f"You said: {content}"
        
        # Use the Endpoint.success utility function
        response_payload = Endpoint.success(
            content=echo_response,
            payload=payload
        )
        
        # Log successful response to console for Docker
        print(f"[CHAT SUCCESS] Echoing back: {echo_response}")
        
        return response_payload
        
    except Exception as e:
        # Log error details to console for Docker debugging
        error_details = traceback.format_exc()
        print(f"[CHAT ERROR] Exception occurred: {str(e)}")
        print(f"[CHAT ERROR] Full traceback:\n{error_details}")
        print(f"[CHAT ERROR] Original payload: {json.dumps(payload, indent=2) if payload else 'None'}")
        
        # Create error response using utility function
        error_message = f"Error processing your request: {str(e)}"
        error_response = Endpoint.error(
            error_message=error_message,
            payload=payload,
            error=e,
            error_type=type(e).__name__
        )
        
        # Log the error response to console for Docker
        print(f"[CHAT ERROR RESPONSE] Sending error response: {json.dumps(error_response, indent=2)}")
        
        # Return error response with 500 status
        raise HTTPException(status_code=500, detail=error_response)

if __name__ == "__main__":

        uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,     # set True for auto-reload in dev
        log_level="info",
    )