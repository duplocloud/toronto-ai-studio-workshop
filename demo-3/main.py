from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import json
import traceback
from utils import get_agent_response,  get_conversation_history, Endpoint, run_command, run_command_simple
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
    Chat endpoint that handles both regular messages and command responses.
    """
    try:
        # Define the system prompt as a variable
        system_prompt = """You are an coder who only responds in a specific JSON structure.
Your response must be only a valid JSON object, nothing else!! And with the following structure:
{
  "content": "Your response message here",
  "data": {
    "cmds": [
      {
        "command": "bash command here",
        "execute": false
      }
    ]
  }
}

Rules:
1. Always respond with valid JSON!!! In the exact structure shown above
2. The "content" field should contain your response message
3. The "data.cmds" array should contain command objects with "command" and "execute" fields
4. The "command" field should contain a valid bash command
5. The "execute" field should be a boolean (true/false)
6. Do not include any text outside the JSON structure
7. Do not include any placeholders in the commands
8. Only include a SINGLE COMMAND. 
9. Do not EXPLAIN the command, just return the command.

## Example:
### User Prompt:
    Generate the command to list the files in the current directory.

### JSON Response:
    {
    "content": "Here is the command to list the files in the current directory.",
    "data": {
        "cmds": [
        {
            "command": "ls -l",
            "execute": false
        }
        ]
    }
    }
"""
        # Log the incoming request to console for Docker
        print(f"[CHAT REQUEST] Received payload: {json.dumps(payload, indent=2)}")
        
        # Parse content from the payload using the utility method
        request = Endpoint.parse(payload)
        content = request.get("content", "")
        cmds = request.get("cmds", [])
        print(f"[CHAT REQUEST] Content: {content}")

        # Check if this is a command response
        if len(cmds) > 0:
            # This is a command response, process it
            print(f"[CHAT RESPONSE] Executing commands: {cmds}")
            executed_commands = run_commands(cmds)
            print(f"[CHAT RESPONSE] Executed commands: {executed_commands}")
            return Endpoint.success(
                content="Command executed successfully",
                payload=payload,
                executed_cmds=executed_commands
            )

        # For regular messages, proceed with the LLM call
        conversation_history = get_conversation_history(request)

        session = boto3.Session(
            region_name='us-east-2',
            profile_name='test10'
        )

        bedrock_model = BedrockModel(
            model="us.amazon.nova-lite-v1:0",
            system_prompt=system_prompt,
            temperature=0.1,
            tools=[],
            workflow=[],
            boto_session=session
        )

        # Create echo response
        agent = Agent(
            model=bedrock_model,
            messages=conversation_history
        )

        agent_response = agent(content)
        ai_response = get_agent_response(agent_response)
        print(f"[CHAT RESPONSE] AI Response: {ai_response}")

        # Second LLM call to parse the first command
        parse_prompt = f"""You are a command parser. Your task is to extract ONLY the first bash command from the previous AI response.
You must respond in this exact JSON structure:
{{  
    "command": "the first command from the previous response"
}} 

Rules:
1. Only return the command string, nothing else
2. If there are no commands, return an empty string
3. Do not include any explanations or additional text
4. The response must be valid JSON

## Previous AI Response:
{ai_response}
"""

        bedrock_model = BedrockModel(
            model="us.amazon.nova-lite-v1:0",
            system_prompt=system_prompt,
            temperature=0.1,
            tools=[],
            workflow=[],
            boto_session=session
        )

        # Create a new agent for parsing
        parse_agent = Agent(
            model=bedrock_model,
        )

        # Get the parsed command
        parse_response = parse_agent(parse_prompt)
        parsed_command = json.loads(get_agent_response(parse_response))
        print(f"[PARSE RESPONSE] Parsed command: {parsed_command}")

        cmds.append({
            "command": parsed_command["command"],
            "execute": False
        })

        
        # Return the command response
        return Endpoint.success(
            content="Do you want to execute the command?",
            cmds=cmds,
            payload=payload
        )
        
    except Exception as e:
        # Log error details to console for Docker debugging
        error_details = traceback.format_exc()
        print(f"[CHAT ERROR] Exception occurred: {str(e)}")
        print(f"[CHAT ERROR] Full traceback:\n{error_details}")
        print(f"[CHAT ERROR] Original payload: {json.dumps(payload, indent=2) if payload else 'None'}")
        
        # Return error response with 500 status
        raise HTTPException(status_code=500, detail=error_details)
    
def run_commands(commands):
    executed_commands = []
                
    for command in commands:
        command_text = command.get("command", "")
        execute = command.get("execute", False)

        if execute:
            run_command_simple(executed_commands, command, command_text)
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