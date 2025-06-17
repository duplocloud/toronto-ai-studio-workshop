from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import traceback
from utils import Endpoint, run_command

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
        request = Endpoint.parse(payload)
        request_text = request.get("content", "")

        response_text = ""
        executed_commands = []
        cmds = []
        url_configs = []
        browser_use = []

        if request_text == "":
            commands = request.get("cmds", [])

            if len(commands) > 0:
                response_text = "Here are the results of the commands."
                executed_commands = run_commands(commands)

        elif request_text == "command":
            response_text = "Do you want view the content of the file sample.txt?"
            cmds.append({
                "command": "cat sample.txt",
                "execute": False,
                "files": [
                    {
                        "file_path": "sample.txt",
                        "file_content": "Amazon rocks!"
                    }
                ]
            })
        
        elif request_text == "url":
            response_text = "Visit Duplo Cloud!"
            url_configs.append({
                "url": "https://duplocloud.com",
                "description": "Visit Duplo Cloud"
            })

        elif request_text == "browser":
            response_text = "Visit Duplo Cloud!"
            browser_use.append({
                    "action": "go_to_url",
                    "action_type": "navigate",
                    "href": "https://duplo.workshop05.duploworkshop.com/"
                })

        else:
            response_text = "How can I help you today? I can execute a command, or I can navigate to a URL, or I can open a browser, by typing 'command', 'url', or 'browser'"
          
        return Endpoint.success(
            content=response_text,
            payload=request,
            cmds=cmds,
            executed_cmds=executed_commands,
            url_configs=url_configs,
            browser_use=browser_use
        )
        
    except Exception as e:
        
        # Return error response with 500 status
        raise HTTPException(status_code=500, detail=traceback.format_exc())

def run_commands(commands):
    executed_commands = []
                
    for command in commands:
        command_text = command.get("command", "")
        execute = command.get("execute", False)
        files = command.get("files", [])

        if execute:
            run_command(executed_commands, command, command_text, files)
        else:
            executed_commands.append(command)
            
    return executed_commands


if __name__ == "__main__":

        uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,     # set True for auto-reload in dev
        log_level="info",
    )
