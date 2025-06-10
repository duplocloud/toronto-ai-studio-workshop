from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import json
import traceback
import sys
import os

from common.command_utilties import run_subprocess_command

# Add the parent directory to the Python path to access the common module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import Endpoint

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
        
        # Parse content from the payload using the utility method
        content = Endpoint.parse(payload)

        print(f"[CHAT PARSE] Extracted content: {content}")

        ## Get last message from the payload.
        user_commands = Endpoint.get_user_commands(payload)
        
        if len(user_commands) > 0:

            executed_commands = []

            # Execute the command
            for command in user_commands:
                running_command = command["command"]
                can_execute = command["execute"]

                if can_execute:
                    response = run_subprocess_command(payload, running_command)
                    executed_commands.append({
                        "command": running_command,
                        "output": response
                    })

                print(f"[CHAT EXECUTE COMMAND] Response: {response}")
                # Add the response to the payload
                payload["messages"].append(response)
                # Add the command to the payload
                payload["messages"].append()
                
        else:
            # Send a greeting
            # responde with "Would like to execute this command? And supply a command to create a file on the file system."
            # It needs the user to approval to execute the command.

        # If the last message is a command, we need to execute it.
        print(f"[CHAT LAST MESSAGE] Last message: {last_message}")
        
        
        # Create echo response

        # When the user says "clear", the we clear the chat history, and send back a greeting.
        if content == "clear":
            # Clear the chat history
            # Send back a greeting
            echo_response = Endpoint.clear_chat(payload)
        elif content == "command":
            # Send a command to the user
            echo_response = Endpoint.send_command(payload)
        elif content == "file":
            # Send a file to the user
            echo_response = Endpoint.send_file(payload)
        else:
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

