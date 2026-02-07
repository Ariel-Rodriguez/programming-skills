"""
Adapters Layer - External System Implementations

Imperative Shell: Side effects isolated here.
Explicit Boundaries: Adapters connect domain to infrastructure.
"""

from .filesystem import RealFileSystem
from .ollama import OllamaAdapter
from .copilot import CopilotCLIAdapter
from .codex import CodexCLIAdapter
from .gemini import GeminiCLIAdapter

__all__ = [
    "OllamaAdapter",
    "CopilotCLIAdapter",
    "CodexCLIAdapter",
    "RealFileSystem",
    "GeminiCLIAdapter",
]
