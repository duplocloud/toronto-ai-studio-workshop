import os
import shutil
import tempfile
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import json
import traceback
from utils import run_subprocess_command, Endpoint

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
        request = Endpoint.parse(payload)
        response_text = ""
        executed_commands = []
        cmds = []

        commands = request.get("cmds", [])
        if len(commands) > 0:
            executed_commands = []
            for command in commands:
                print(f"[CHAT EXECUTE COMMAND] Command: {json.dumps(command, indent=2)}")
                command_text = command.get("command", "")
                execute = command.get("execute", False)
                files = command.get("files", [])

                if execute:
                    temp_dir = tempfile.mkdtemp()
                    try:


                        for file_info in files:
                            file_path = file_info.get("file_path")
                            file_content = file_info.get("file_content")
                            
                            if not file_path or file_content is None:
                                continue
                                
                            # Create full path within the temp directory
                            full_path = os.path.join(temp_dir, file_path)
                                
                            # Create directory structure if it doesn't exist
                            dir_path = os.path.dirname(full_path)
                            if dir_path and not os.path.exists(dir_path):
                                os.makedirs(dir_path)
                                
                            # Write the file
                            with open(full_path, 'w') as f:
                                f.write(file_content)
                                    
                            command_text = f"cd {temp_dir} && {command_text}"
                            response = run_subprocess_command(command_text, cwd=temp_dir)
                            # Add the response to the payload
                            command["output"] = response.get("stdout", "") # json.dumps(response, indent=2)
                            print(f"[CHAT EXECUTE COMMAND] Response: {json.dumps(response, indent=2)}")

                            executed_commands.append(command)
                    except Exception as e:
                        print(f"[CHAT EXECUTE COMMAND] Error: {e}")
                        command["output"] = f"Error: {e}"
                    finally:
                        # Clean up the temporary directory
                        shutil.rmtree(temp_dir)
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
                        "file_content": "Hello, world!dsfasddf"
                    }
                ]
            })

           # tmp1
           # cds into tmp1
           # create a file called sample.txt with the content "Hello, world!"
           # when in the tmp1 directory, runs the command "cat sample.txt"
           # when it's done, it should return the content of the file and delete the tmp1

           

        return Endpoint.success(
            content=response_text,
            payload=payload,
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
