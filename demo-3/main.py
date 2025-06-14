from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import json
import traceback
from utils import get_agent_response,  get_bedrock_model, get_conversation_history, Endpoint
from strands import Agent
from strands.models.bedrock import BedrockModel
import boto3

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
        # Log the incoming request to console for Docker
        print(f"[CHAT REQUEST] Received payload: {json.dumps(payload, indent=2)}")
        
        # Parse content from the payload using the utility method
        request = Endpoint.parse(payload)
        content = request.get("content", "")
        print(f"[CHAT REQUEST] Content: {content}")

        conversation_history = get_conversation_history(request)

        session = boto3.Session( # If using temporary credentials
            region_name='us-east-2'
        )

        bedrock_model = BedrockModel(
            model="us.amazon.nova-lite-v1:0",
            tools=[],
            workflow=[],
            boto_session=session
        )

        #bedrock_model = get_bedrock_model(session)

        # Create echo response
        agent = Agent(
            model=bedrock_model,
            messages=conversation_history
        )

        agent_response = agent(content)
        ai_response = get_agent_response(agent_response)
        
        # Use the Endpoint.success utility function
        response_payload = Endpoint.success(
            content=ai_response,
            payload=payload
        )
        
        return response_payload
        
    except Exception as e:
        # Log error details to console for Docker debugging
        error_details = traceback.format_exc()
        print(f"[CHAT ERROR] Exception occurred: {str(e)}")
        print(f"[CHAT ERROR] Full traceback:\n{error_details}")
        print(f"[CHAT ERROR] Original payload: {json.dumps(payload, indent=2) if payload else 'None'}")
        
        # Create error response using utility function
        error_message = f"Error processing your request: {str(e)}"
        print(f"[CHAT ERROR] Error message: {error_message}")

        
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