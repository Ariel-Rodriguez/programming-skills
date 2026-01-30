"""
Adapters Layer - External System Implementations

Imperative Shell: Side effects isolated here.
Explicit Boundaries: Adapters connect domain to infrastructure.
"""

from .filesystem import RealFileSystem
from .ollama import OllamaAdapter
from .copilot import CopilotCLIAdapter

__all__ = [
    "RealFileSystem",
    "OllamaAdapter",
    "CopilotCLIAdapter",
]
