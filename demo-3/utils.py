import json
import os
import shutil
import tempfile
from typing import Dict, Any, List, Optional
import datetime
import subprocess
from strands.models.bedrock import BedrockModel


def parse_request_v1(
        payload: Dict[str, Any],
        ) -> Dict[str, Any]:
    """
    Parse the incoming chat payload and convert it to the format expected by HumanInLoop.
    
    Args:
        payload: The incoming JSON payload from the REST API
        
    Returns:
        List of message dictionaries in the format expected by HumanInLoop
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    
    response = {}
    # Extract the current message content
    current_content = payload.get("content", "")

    if current_content:
        response["content"] = current_content
    # Extract the past messages
    past_messages = payload.get("pastMessages", [])
    response["messages"] = past_messages
    response["thread_id"] = payload.get("thread_id", "")
    response["tenant_id"] = payload.get("tenant_id", "")
    response["id"] = payload.get("id", "")
    response["platform_context"] = payload.get("platform_context", {})
    data = payload.get("data", {})

    if data:
        response["past_messages_count"] = len(past_messages)
        response["cmds"] = [transform_v1_command_to_v2_format(cmd) for cmd in (data.get("Cmds", []) or [])]
        response["executed_cmds"] = [transform_v1_command_to_v2_format(cmd) for cmd in (data.get("executedCmds", []) or [])]

        response["url_configs"] = data.get("url_configs", [])
    
    return response

def transform_v2_command_to_v1_format(command_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a command dictionary from the old format to the new format.
    
    Args:
        command_dict: Dictionary containing command information in the format:
            {
                "command": str,
                "execute": bool,
                "files": List[Dict[str, str]]
            }
            
    Returns:
        Dictionary in the new format:
            {
                "Command": str,
                "Output": str,
                "execute": bool
            }
    """
    return {
        "Command": command_dict.get("command", ""),
        "Output": command_dict.get("output", ""),
        "files": command_dict.get("files", []),
        "execute": command_dict.get("execute", False)
    }

def transform_v1_command_to_v2_format(command_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a command dictionary from the new format back to the old format.
    
    Args:
        command_dict: Dictionary containing command information in the format:
            {
                "Command": str,
                "Output": str,
                "execute": bool
            }
            
    Returns:
        Dictionary in the old format:
            {
                "command": str,
                "execute": bool,
                "files": List[Dict[str, str]]
            }
    """
    return {
        "command": command_dict.get("Command", ""),
        "execute": command_dict.get("execute", False),
        "files": command_dict.get("files", [])
    }

def create_response_v1(
        response_text: str,
        payload: Optional[Dict[str, Any]] = None,
        cmds: Optional[List[Dict[str, Any]]] = None,
        executed_cmds: Optional[List[Dict[str, Any]]] = None,
        url_configs: Optional[List[Dict[str, Any]]] = None,
        browser_urls: Optional[List[Dict[str, Any]]] = None
        ) -> Dict[str, Any]:
    """
    Generate a chat response based on the payload.
    """
    # Transform commands if they exist
    transformed_cmds = [transform_v2_command_to_v1_format(cmd) for cmd in (cmds or [])]
    transformed_executed_cmds = [transform_v2_command_to_v1_format(cmd) for cmd in (executed_cmds or [])]

    return {
        "pastMessages": payload.get("pastMessages", []) if payload else [],
        "Content": response_text,
        "terminalCommands": [],
        "thread_id": payload.get("thread_id", ""),
        "tenant_id": payload.get("tenant_id", ""),
        "agent_managed_memory": payload.get("agent_managed_memory", True) if payload else True,
        "platform_context": payload.get("platform_context", {}) if payload else {},
        "data": {
            "response_type": "success",
            "processed_at": datetime.datetime.utcnow().isoformat() + "Z",
            "Cmds": transformed_cmds,
            "executedCmds": transformed_executed_cmds or [],
            "url_configs": url_configs or [],
            "browser_urls": browser_urls or []
        },
        "id": payload.get("id", "") 
    }


def parse_request_v2(
        payload: Dict[str, Any],
        ) -> str:
    """
    Parse the incoming chat payload and convert it to the format expected by HumanInLoop.
    
    Args:
        payload: The incoming JSON payload from the REST API
        
    Returns:
        List of message dictionaries in the format expected by HumanInLoop
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    # Extract the current message content
    if not payload.get("messages"):
            return ""
        
    last_message = payload["messages"][-1]

    return {
        "content": str(last_message["content"]),
        "cmds": payload.get("data", {}).get("cmds", []),
        "executed_cmds": payload.get("data", {}).get("executed_cmds", []),
        "url_configs": payload.get("data", {}).get("url_configs", [])
    }

def create_response_v2(
        response_text: str,
        payload: Optional[Dict[str, Any]] = None,
        cmds: Optional[List[Dict[str, Any]]] = None,
        executed_cmds: Optional[List[Dict[str, Any]]] = None,
        url_configs: Optional[List[Dict[str, Any]]] = None
        ) -> Dict[str, Any]:
    """
    Generate a chat response based on the payload.
    """
    return {
            "role": "assistant",
            "content": response_text,
            "data": {
                "cmds": cmds or [],
                "executed_cmds": executed_cmds or [],
                "url_configs": url_configs or []
            }
        }


class Endpoint:
    @staticmethod
    def parse(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and extract content from the last message.
        
        Args:
            payload: The request payload dictionary containing messages array
        
        Returns:
            Extracted content string from the last message
        """
        return parse_request_v1(payload)
    
    @staticmethod
    def success(
        content: str,
        payload: Optional[Dict[str, Any]] = None,
        cmds: Optional[List[Dict[str, Any]]] = None,
        executed_cmds: Optional[List[Dict[str, Any]]] = None,
        url_configs: Optional[List[Dict[str, Any]]] = None,
        browser_urls: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized success response payload in the new format.
        
        Args:
            content: The main response content
            payload: The original request payload (for compatibility)
            cmds: Optional list of commands to propose (with execute: false)
            executed_cmds: Optional list of commands that were executed
            url_configs: Optional list of URL configurations for browser actions
            browser_urls: Optional list of browser URLs to open
        Returns:
            Standardized success response dictionary
        """
        response = create_response_v1(content, payload, cmds, executed_cmds, url_configs, browser_urls)
        return response


def run_subprocess_command(command: str, shell=True, capture_stderr=True, text=True, timeout=None,cwd=None):
    """
    Run a subprocess command and capture all output.
    
    Args:
        payload: The original request payload (for compatibility)
        command (str or list): The command to run. Can be a string or list of arguments.
        shell (bool): Whether to run the command through the shell. Default is False.
        capture_stderr (bool): Whether to capture stderr along with stdout. Default is True.
        text (bool): Whether to return output as text (True) or bytes (False). Default is True.
        timeout (int): Maximum time in seconds to wait for command completion. Default is None (no timeout).
    
    Returns:
        dict: A dictionary containing:
            - 'stdout': Standard output from the command
            - 'stderr': Standard error from the command (if capture_stderr=True)
            - 'returncode': Exit code of the command
            - 'success': Boolean indicating if command succeeded (returncode == 0)
    
    Raises:
        subprocess.TimeoutExpired: If the command times out
        FileNotFoundError: If the command is not found
        subprocess.CalledProcessError: If there are other subprocess errors
    """
    try:
        # Run the command and capture output
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=text,
            timeout=timeout,
            cwd=cwd,
            check=False  # Don't raise exception on non-zero exit codes
        )
        
        return {
            'stdout': result.stdout,
            'stderr': result.stderr if capture_stderr else None,
            'returncode': result.returncode,
            'success': result.returncode == 0
        }
        
    except subprocess.TimeoutExpired as e:
        return {
            'stdout': e.stdout.decode('utf-8') if e.stdout and not text else e.stdout,
            'stderr': e.stderr.decode('utf-8') if e.stderr and not text else e.stderr,
            'returncode': None,
            'success': False,
            'error': f'Command timed out after {timeout} seconds'
        }
    except FileNotFoundError as e:
        return {
            'stdout': '',
            'stderr': f'Command not found: {e}',
            'returncode': -1,
            'success': False,
            'error': str(e)
        }
    except Exception as e:
        return {
            'stdout': '',
            'stderr': f'Unexpected error: {e}',
            'returncode': -1,
            'success': False,
            'error': str(e)
        }


def read_text_file(file_path, encoding='utf-8', strip_whitespace=False):
    """
    Read a text file and return its contents.
    
    Args:
        file_path (str): Path to the text file to read
        encoding (str): Text encoding to use when reading the file. Default is 'utf-8'
        strip_whitespace (bool): Whether to strip leading/trailing whitespace. Default is False
    
    Returns:
        dict: A dictionary containing:
            - 'content': The text content of the file
            - 'success': Boolean indicating if the file was read successfully
            - 'file_path': The path of the file that was read
            - 'error': Error message if reading failed (only present if success=False)
    """
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            content = file.read()
            
        if strip_whitespace:
            content = content.strip()
            
        return {
            'content': content,
            'success': True,
            'file_path': file_path
        }
        
    except FileNotFoundError:
        return {
            'content': '',
            'success': False,
            'file_path': file_path,
            'error': f'File not found: {file_path}'
        }
    except PermissionError:
        return {
            'content': '',
            'success': False,
            'file_path': file_path,
            'error': f'Permission denied: {file_path}'
        }
    except UnicodeDecodeError as e:
        return {
            'content': '',
            'success': False,
            'file_path': file_path,
            'error': f'Unicode decode error with encoding {encoding}: {e}'
        }
    except Exception as e:
        return {
            'content': '',
            'success': False,
            'file_path': file_path,
            'error': f'Unexpected error reading file: {e}'
        }


def get_bedrock_model(session: any) -> str:
    return BedrockModel(
            model="us.amazon.nova-lite-v1:0",
            tools=[],
            workflow=[],
            boto_session=session
        )

def run_command(executed_commands, command, command_text, files):
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

def run_command_simple(executed_commands, command, command_text):
    """
    Execute a command in the application root directory without file handling.
    
    Args:
        executed_commands: List to append the executed command to
        command: Command dictionary to update with output
        command_text: The actual command string to execute
    """
    try:
        # Execute command in application root directory
        response = run_subprocess_command(command_text)
        
        # Add the response to the command
        command["output"] = response.get("stdout", "")
        print(f"[CHAT EXECUTE COMMAND] Response: {json.dumps(response, indent=2)}")
        
        executed_commands.append(command)
    except Exception as e:
        print(f"[CHAT EXECUTE COMMAND] Error: {e}")
        command["output"] = f"Error: {e}"

def get_conversation_history(request: any) -> list[dict[str, Any]]:
    """
    Get the conversation history from the agent and convert it to the expected format.
    
    Args:
        request: Dictionary containing pastMessages with userMsg/agentResponse structure
        
    Returns:
        List of messages in the format [{"role": str, "content": [{"text": str}]}]
        Returns empty list if conversion fails
    """
    try:
        past_messages = request.get("pastMessages", [])
        messages = []
        
        for msg in past_messages:
            if "userMsg" in msg:
                messages.append({
                    "role": "user",
                    "content": [{"text": msg["userMsg"]["content"]}]
                })
            elif "agentResponse" in msg:
                messages.append({
                    "role": "assistant",
                    "content": [{"text": msg["agentResponse"]["content"]}]
                })
        
        return messages
    except Exception as e:
        print(f"Error converting conversation history: {str(e)}")
        return []

        
def get_agent_response(response: any) -> str:
    """
    Get the response from the agent
    """
    return response.message["content"][0]["text"] 
