from fastapi import FastAPI, HTTPException, Body
from typing import Dict, Any
import uvicorn
import json
import traceback
from utils import get_conversation_history, Endpoint, run_command_simple
from strands import Agent
from strands.models.bedrock import BedrockModel
import boto3
import logging

app = FastAPI(title="AWS Workshop API", version="0.1.0")

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Unified system prompt for the agent (shared across all requests)
SYSTEM_PROMPT = """You are a JSON response bot. Your entire response MUST be valid JSON only.

RESPONSE FORMAT:
- Commands: {"content": "description", "data": {"cmds": [{"command": "bash_command", "execute": false}]}}
- General: {"content": "answer", "data": {}}

STRICT RULES:
1. RESPOND ONLY WITH JSON
2. NO TEXT BEFORE/AFTER JSON
3. NO EXPLANATIONS OUTSIDE JSON
4. NO MARKDOWN CODE BLOCKS
5. VALIDATE JSON BEFORE RESPONDING

EXAMPLES:
User: "list files" → {"content": "Command to list directory contents", "data": {"cmds": [{"command": "ls -la", "execute": false}]}}
User: "what is git?" → {"content": "Git is a distributed version control system for tracking changes in source code.", "data": {}}

IMPORTANT: Start your response with { and end with }. Nothing else."""

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def extract_json_from_response(response_text: str) -> str:
    """Return the JSON portion of a response string.

    The model occasionally adds prose or wraps the JSON in code fences. This helper
    attempts to locate and return the first valid JSON object it can find. If no
    JSON is found, the original text is returned so that downstream logic can
    handle the error gracefully.
    """
    response_text = response_text.strip()

    # Fast-path: string already looks like pure JSON
    if response_text.startswith("{") and response_text.endswith("}"):
        return response_text

    import re

    # Look for JSON surrounded by fenced code blocks
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
    if match:
        return match.group(1)

    # Fallback: first curly-brace section
    match = re.search(r"(\{.*?\})", response_text, re.DOTALL)
    if match:
        return match.group(1)

    return response_text

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {"status": "healthy", "service": "aws-workshop-api"}

@app.post("/chat")
async def chat(payload: Dict[str, Any] = Body(...)):
    """
    Unified chat endpoint that handles both command generation and general questions.
    Always returns JSON in the specified format.
    """
    try:
        # Use the shared system prompt
        system_prompt = SYSTEM_PROMPT

        # Log the incoming request
        logger.debug("Received payload: %s", json.dumps(payload, indent=2))
        
        # Parse content from the payload
        request = Endpoint.parse(payload)
        content = request.get("content", "")
        cmds = request.get("cmds", [])
        logger.debug("Content: %s", content)

        # Check if this is a command execution request
        if len(cmds) > 0:
            # This is a command response, process it
            logger.info("Executing commands: %s", cmds)
            executed_commands = run_commands(cmds)
            logger.info("Executed commands: %s", executed_commands)
            return Endpoint.success(
                content="Command executed successfully",
                payload=payload,
                executed_cmds=executed_commands
            )

        # For new messages, use the unified agent
        conversation_history = get_conversation_history(request)

        session = boto3.Session(region_name='us-east-2', profile_name='test10')

        # Create the unified agent
        bedrock_model = BedrockModel(
            model="anthropic.claude-3-5-sonnet-20240620-v1:0",
            temperature=0.1,
            tools=[],
            workflow=[],
            boto_session=session
        )

        agent = Agent(
            system_prompt=system_prompt,
            model=bedrock_model,
            messages=conversation_history
        )

        # Get unified response
        agent_response = agent(content)
        
        # Extract response - handle different Strands response formats
        try:
            if hasattr(agent_response, 'message') and agent_response.message:
                ai_response = agent_response.message["content"][0]["text"]
            elif hasattr(agent_response, 'messages') and agent_response.messages:
                ai_response = agent_response.messages[-1].content
            else:
                ai_response = str(agent_response)
        except (KeyError, IndexError, AttributeError) as e:
            logger.warning("Response extraction error: %s", e)
            ai_response = str(agent_response)
            
        logger.debug("AI Response: %s", ai_response)

        # Clean and parse the JSON response
        try:
            cleaned_response = extract_json_from_response(ai_response)
            
            parsed_response = json.loads(cleaned_response)
            response_content = parsed_response.get("content", "")
            response_data = parsed_response.get("data", {})
            
            # Check if this is a command response
            if "cmds" in response_data and response_data["cmds"]:
                # It's a command response - return it for user approval
                logger.info("Commands detected: %s", response_data["cmds"])
                return Endpoint.success(
                    content=response_content,
                    cmds=response_data["cmds"],
                    payload=payload
                )
            else:
                # It's a general response - return the content
                logger.info("General response - content: %s", response_content)
                return Endpoint.success(
                    content=response_content,
                    payload=payload
                )
                
        except json.JSONDecodeError as e:
            logger.error("Failed to parse AI response: %s", e)
            logger.debug("Raw response: %s", ai_response)
            
            # Fallback response
            return Endpoint.success(
                content="I apologize, but I encountered an error processing your request. Please try again.",
                payload=payload
            )
        
    except Exception as e:
        # Log error details
        error_details = traceback.format_exc()
        logger.error("Exception occurred: %s", e)
        logger.error("Full traceback:\n%s", error_details)
        logger.debug("Original payload: %s", json.dumps(payload, indent=2) if payload else 'None')
        
        # Return error response
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