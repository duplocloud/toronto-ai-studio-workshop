from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import json
import traceback
from common.agent_utilties import get_agent_response, get_bedrock_claude_3_5, get_conversation_history
from strands import Agent, Bedrock
from common import Endpoint
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
        content = Endpoint.parse(payload)
        print(f"[CHAT PARSE] Extracted content: {content}")

        conversation_history = get_conversation_history(payload)

        session = boto3.Session( # If using temporary credentials
            region_name='us-east-2',
            profile_name='test10'  # Optional: Use a specific profile
        )

        bedrock_model = get_bedrock_claude_3_5(session)

        # Create echo response
        agent = Agent(
            name="HelpDesk Chat",
            description="A chatbot that can help with helpdesk issues",
            model=bedrock_model,
            messages=conversation_history
        )

        agent_response = agent.run(content)
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

