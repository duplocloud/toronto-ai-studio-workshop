
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
        response_text = ""
        executed_commands = []
        commands_executed = False
        cmds = []

        commands = request.get("cmds", [])
        if len(commands) > 0:

            executed_commands = []
            for command in commands:

                command_text = command.get("command", "")
                execute = command.get("execute", False)
                files = command.get("files", [])

                if execute:
                    commands_executed = True
                    run_command(executed_commands, command, command_text, files)
                else:
                    cmds.append(command)
        else:
            response_text = "Would like to list the files in the current directory?"
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
        
        if commands_executed:
            response_text = "Here are the results of the commands."

          
        return Endpoint.success(
            content=response_text,
            payload=request,
            cmds=cmds,
            executed_cmds=executed_commands,
            url_configs=[]
        )
        
    except Exception as e:
        
        # Return error response with 500 status
        raise HTTPException(status_code=500, detail=traceback.format_exc())


if __name__ == "__main__":

        uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,     # set True for auto-reload in dev
        log_level="info",
    )
