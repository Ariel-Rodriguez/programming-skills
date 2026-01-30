"""
Ports Layer - Interface Definitions

Explicit Boundaries Adapters: Domain depends on interfaces, not implementations.
Local Reasoning: Interfaces document what operations are available.
"""

from .filesystem import FileSystemPort
from .model import ModelPort

__all__ = [
    "FileSystemPort",
    "ModelPort",
]
