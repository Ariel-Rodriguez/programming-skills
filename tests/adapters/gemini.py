"""
Gemini CLI Adapter

Imperative Shell: Subprocess calls isolated here.
"""

import subprocess
from domain import ModelConfig, Result, Success, Failure


class GeminiCLIAdapter:
    """
    Adapter for Google Gemini CLI.

    Explicit Boundaries: Isolates CLI-specific logic.
    Error Handling Design: Subprocess errors become Result types.
    """

    def call(self, prompt: str, config: ModelConfig) -> Result:
        """
        Call Gemini CLI.

        Local Reasoning: All parameters explicit.
        Naming as Design: Clear this invokes external CLI.
        """
        cmd = [
            "gemini",
            "--model", config.model_name,
            "--prompt", prompt
        ]

        import tempfile
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=600,
                    cwd=tmpdir,  # ISOLATION
                )

            if result.returncode != 0:
                stderr = result.stderr.strip()
                stdout = result.stdout.strip()
                error_msg = stderr or stdout or "Unknown error"
                return Failure(
                    f"Gemini CLI failed (rc={result.returncode}): {error_msg}",
                    {"returncode": result.returncode, "stderr": stderr, "stdout": stdout},
                )

            return Success(result.stdout.strip())

        except subprocess.TimeoutExpired:
            return Failure(
                "Gemini CLI timeout after 600 seconds",
                {"timeout": 600},
            )
        except FileNotFoundError:
            return Failure(
                "Gemini CLI not found",
                {"hint": "Install with: bun add -g @google/gemini-cli"},
            )
        except Exception as e:
            return Failure(
                "Gemini CLI error",
                {"error": str(e), "type": type(e).__name__},
            )

    def is_available(self, config: ModelConfig) -> bool:
        """
        Check if Gemini CLI is available.
        """
        try:
            result = subprocess.run(
                ["gemini", "--version"],
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False
