"""
Codex CLI Adapter

Imperative Shell: Subprocess calls isolated here.
"""

import subprocess
from domain import ModelConfig, Result, Success, Failure


class CodexCLIAdapter:
    """
    Adapter for Codex CLI.

    Explicit Boundaries: Isolates CLI-specific logic.
    Error Handling Design: Subprocess errors become Result types.
    """

    def call(self, prompt: str, config: ModelConfig) -> Result:
        """
        Call Codex CLI.

        Local Reasoning: All parameters explicit.
        Naming as Design: Clear this invokes external CLI.
        """
        system_note = (
            "Provide a direct final answer only. Do not list options. "
            "Do not claim to edit files; you are in a read-only sandbox."
        )

        cmd = [
            "codex",
            "exec",
            "--sandbox",
            "read-only",
            "--model",
            config.model_name,
            system_note + "\n\n" + prompt,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=600,
            )

            if result.returncode != 0:
                stderr = result.stderr.strip()
                stdout = result.stdout.strip()
                error_msg = stderr or stdout or "Unknown error"
                return Failure(
                    f"Codex CLI failed (rc={result.returncode}): {error_msg}",
                    {"returncode": result.returncode, "stderr": stderr, "stdout": stdout},
                )

            return Success(result.stdout.strip())

        except subprocess.TimeoutExpired:
            return Failure(
                "Codex CLI timeout after 600 seconds",
                {"timeout": 600},
            )
        except FileNotFoundError:
            return Failure(
                "Codex CLI not found",
                {"hint": "Install Codex CLI and sign in with ChatGPT"},
            )
        except Exception as e:
            return Failure(
                "Codex CLI error",
                {"error": str(e), "type": type(e).__name__},
            )

    def is_available(self, config: ModelConfig) -> bool:
        """
        Check if Codex CLI is available.
        """
        try:
            result = subprocess.run(
                ["codex", "--version"],
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False
