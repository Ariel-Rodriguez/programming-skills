"""
Model Port - Interface for AI model invocation

Explicit Boundaries: Isolates AI providers from domain logic.
"""

from typing import Protocol
from domain import ModelConfig, Result


class ModelPort(Protocol):
    """
    Port for AI model invocation.
    
    Explicit Boundaries Adapters: Domain doesn't know about Ollama or Copilot.
    Naming as Design: Clear what this port provides.
    """
    
    def call(self, prompt: str, config: ModelConfig) -> Result:
        """
        Call AI model with prompt.
        
        Error Handling Design: Returns Result for explicit error handling.
        Local Reasoning: All parameters explicit.
        
        Args:
            prompt: Input prompt for the model
            config: Model configuration
            
        Returns:
            Success(response_text) or Failure(error_message)
        """
        ...
    
    def is_available(self, config: ModelConfig) -> bool:
        """
        Check if model service is available.
        
        Args:
            config: Model configuration
            
        Returns:
            True if service is reachable, False otherwise
        """
        ...
