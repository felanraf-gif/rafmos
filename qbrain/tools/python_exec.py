from .base_tool import BaseTool, ToolResult
import subprocess
import sys


class PythonExecTool(BaseTool):
    name = "python_exec"
    description = "Execute Python code safely"
    parameters = {
        "code": {"type": "string", "description": "Python code to execute"},
        "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30},
    }
    
    def execute(self, code: str, timeout: int = 30) -> ToolResult:
        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            output = result.stdout
            if result.stderr:
                output += "\n--- STDERR ---\n" + result.stderr
            
            return ToolResult(success=True, data={
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            })
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Execution timeout")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
