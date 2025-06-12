from typing import Dict, Any, List, Optional
import datetime
import subprocess
from strands.models.bedrock import BedrockModel


def parse_request_v1(
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
    
    response = {}
    # Extract the current message content
    current_content = payload.get("content", "")

    if current_content:
        response["content"] = current_content
    # Extract the past messages
    past_messages = payload.get("pastMessages", [])
    thread_id = payload.get("thread_id", "")
    tenant_id = payload.get("tenant_id", "")
    platform_context = payload.get("platform_context", {})
    data = payload.get("data", {})

    if data:
        response["cmds"] = data.get("cmds", [])
        response["executed_cmds"] = data.get("executed_cmds", [])
        response["url_configs"] = data.get("url_configs", [])
    
    return response

def create_response_v1(
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
                "pastMessages": payload.get("pastMessages", []),
                "Content": response_text,
                "terminalCommands": [],
                "thread_id": payload.get("thread_id", ""),
                "tenant_id": payload.get("tenant_id", ""),
                "agent_managed_memory": payload.get("agent_managed_memory", True),
                "platform_context": payload.get("platform_context", {}),
                "data": {
                    "response_type": "success",
                    "processed_at": datetime.datetime.utcnow().isoformat() + "Z",
                    "cmds": cmds or [],
                    "executed_cmds": executed_cmds or [],
                    "url_configs": url_configs or []
                },
                "id": None
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
    def parse(payload: Dict[str, Any]) -> str:
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
        url_configs: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized success response payload in the new format.
        
        Args:
            content: The main response content
            payload: The original request payload (for compatibility)
            cmds: Optional list of commands to propose (with execute: false)
            executed_cmds: Optional list of commands that were executed
            url_configs: Optional list of URL configurations for browser actions
        
        Returns:
            Standardized success response dictionary
        """
        return create_response_v1(content, payload, cmds, executed_cmds, url_configs)

    @staticmethod
    def get_platform_context(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract platform context from the last user message.
        
        Args:
            payload: The request payload dictionary
        
        Returns:
            Platform context dictionary or empty dict
        """
        if "messages" in payload and payload["messages"]:
            # Find the last user message with platform context
            for message in reversed(payload["messages"]):
                if (isinstance(message, dict) and 
                    message.get("role") == "user" and 
                    "platform_context" in message):
                    return message["platform_context"]
        
        # Fallback to old format
        return payload.get("platform_context", {})
    
    @staticmethod
    def get_user_commands(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract commands from the last message's data.
        
        Args:
            payload: The request payload dictionary
        
        Returns:
            List of command dictionaries
        """
        if "messages" in payload and payload["messages"]:
            last_message = payload["messages"][-1]
            if isinstance(last_message, dict) and "data" in last_message:
                data = last_message["data"]
                return data.get("cmds", [])
        
        return []
    
    @staticmethod
    def get_executed_commands(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract executed commands from the last message's data.
        
        Args:
            payload: The request payload dictionary
        
        Returns:
            List of executed command dictionaries
        """
        if "messages" in payload and payload["messages"]:
            last_message = payload["messages"][-1]
            if isinstance(last_message, dict) and "data" in last_message:
                data = last_message["data"]
                return data.get("executed_cmds", [])
        
        return []
    

    @staticmethod
    def error(
        error_message: str,
        payload: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None,
        error_type: str = "processing"
    ) -> Dict[str, Any]:
        """
        Create a standardized error response payload in the new format.
        
        Args:
            error_message: Human-readable error message
            payload: The original request payload (for compatibility)
            error: The exception that occurred (optional)
            error_type: Type of error for categorization
        
        Returns:
            Standardized error response dictionary
        """
        data = {
            "cmds": [],
            "executed_cmds": [],
            "url_configs": [],
            "error_type": error_type,
            "processed_at": datetime.datetime.utcnow().isoformat() + "Z"
        }
        
        if error:
            data["error"] = str(error)
        
        return {
            "role": "assistant",
            "content": error_message,
            "data": data
        }
    
    @staticmethod
    def propose_commands(
        content: str,
        commands: List[str],
        files: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Propose commands for user approval.
        
        Args:
            content: Explanation of what the commands will do
            commands: List of command strings to propose
            files: Optional list of files to create (each with file_path and file_content)
        
        Returns:
            Response with commands set to execute: false
        """
        cmds = []
        for command in commands:
            cmd_dict = {
                "command": command,
                "execute": False
            }
            if files:
                cmd_dict["files"] = files
            cmds.append(cmd_dict)
        
        return Endpoint.success(content, cmds=cmds)
    
    @staticmethod
    def share_executed_commands(
        content: str,
        executed_commands: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Share results of executed commands.
        
        Args:
            content: Analysis or explanation of the command results
            executed_commands: List of dicts with 'command' and 'output' keys
        
        Returns:
            Response with executed commands
        """
        return Endpoint.success(content, executed_cmds=executed_commands)
    
    @staticmethod
    def provide_urls(
        content: str,
        urls: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Provide URLs for browser actions.
        
        Args:
            content: Explanation of the URLs being provided
            urls: List of dicts with 'url' and 'description' keys
        
        Returns:
            Response with URL configurations
        """
        return Endpoint.success(content, url_configs=urls)
    
    @staticmethod
    def create_file_operation_command(
        command: str,
        files: List[Dict[str, str]],
        execute: bool = False
    ) -> Dict[str, Any]:
        """
        Create a command that includes file operations.
        
        Args:
            command: The command to execute
            files: List of files to create (each with file_path and file_content)
            execute: Whether the command should be executed immediately
        
        Returns:
            Command dictionary with file operations
        """
        return {
            "command": command,
            "execute": execute,
            "files": files
        }


def run_subprocess_command(command: str, shell=True, capture_stderr=True, text=True, timeout=None):
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


def get_agent_response(response: any) -> str:
    """
    Get the response from the agent
    """
    return response.message["content"][0]["text"] 


def get_conversation_history(payload: any) -> str:
    """
    Get the conversation history from the agent
    """
    past_messages = payload.get("pastMessages", [])
    messages = [{"role": message.role, "content": [{"text": message.content}]} for message in past_messages]

    return messages


def get_bedrock_claude_3_5(session: any) -> str:
    return BedrockModel(
            model="us.anthropic.claude-3-5-sonnet-20240620-v1:0",
            tools=[],
            workflow=[],
            boto_session=session
        )