"""
GitHub Copilot CLI Adapter

Imperative Shell: Subprocess calls isolated here.
"""

import os
import subprocess
from domain import ModelConfig, Result, Success, Failure


class CopilotCLIAdapter:
    """
    Adapter for GitHub Copilot CLI.
    
    Explicit Boundaries: Isolates CLI-specific logic.
    Error Handling Design: Subprocess errors become Result types.
    """
    
    def call(self, prompt: str, config: ModelConfig) -> Result:
        """
        Call Copilot CLI.
        
        Local Reasoning: All parameters explicit.
        Naming as Design: Clear this invokes external CLI.
        """
        # Try new copilot CLI first, fall back to gh extension
        # The standalone CLI has auth issues with PATs in CI (see: github/copilot-cli#355)
        # So we use gh copilot extension which works better with GITHUB_TOKEN
        system_note = (
            "Provide a direct final answer only. Do not list options. "
            "You cannot edit files; this is a read-only sandbox."
        )

        cmd_cli = [
            "copilot",
            "-p", system_note + "\n\n" + prompt,
            "--model", config.model_name,
            "--silent",
            "--yolo",
            "--deny-tool", "write"
        ]
        
        cmd_gh = [
            "gh", "copilot", "suggest",
            "--target", "shell",
            prompt
        ]
        
        try:
            # Pass environment variables including GITHUB_TOKEN
            env = os.environ.copy()
            
            # If gh copilot not available, try standalone copilot CLI
            result = subprocess.run(
                cmd_cli,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=300,
                env=env,
                input="\n"  # Auto-select first option
            )
            
            # Try gh copilot extension (better for CI with PATs)
            if result.returncode != 0 and "gh: unknown command" in result.stderr:
                result = subprocess.run(
                    cmd_gh,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    timeout=300,
                    env=env
                )
            
            if result.returncode != 0:
                stderr = result.stderr.strip()
                stdout = result.stdout.strip()
                error_msg = stderr or stdout or "Unknown error"
                return Failure(
                    f"Copilot CLI failed (rc={result.returncode}): {error_msg}",
                    {"returncode": result.returncode, "stderr": stderr, "stdout": stdout}
                )
            
            return Success(result.stdout.strip())
        
        except subprocess.TimeoutExpired:
            return Failure(
                "Copilot CLI timeout after 300 seconds",
                {"timeout": 300}
            )
        except FileNotFoundError:
            return Failure(
                "Copilot CLI not found",
                {"hint": "Install with: npm install -g @githubnext/github-copilot-cli"}
            )
        except Exception as e:
            return Failure(
                f"Copilot CLI error",
                {"error": str(e), "type": type(e).__name__}
            )
    
    def is_available(self, config: ModelConfig) -> bool:
        """
        Check if Copilot CLI is available.
        
        Simple availability check.
        """
        try:
            result = subprocess.run(
                ["copilot", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
