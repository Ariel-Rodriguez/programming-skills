"""
FileSystem Port - Interface for file operations

Explicit Boundaries: Isolates filesystem from domain logic.
"""

from pathlib import Path
from typing import Protocol
from domain import Result


class FileSystemPort(Protocol):
    """
    Port for filesystem operations.
    
    Explicit Boundaries Adapters: Domain depends on this interface.
    Local Reasoning: All filesystem ops visible here.
    """
    
    def read_text(self, path: Path, encoding: str = 'utf-8') -> Result:
        """
        Read file content as text.
        
        Error Handling Design: Returns Result instead of raising exceptions.
        
        Args:
            path: File path to read
            encoding: Text encoding
            
        Returns:
            Success(content) or Failure(error_message)
        """
        ...
    
    def write_text(self, path: Path, content: str, encoding: str = 'utf-8') -> Result:
        """
        Write text content to file.
        
        Args:
            path: File path to write
            content: Text content
            encoding: Text encoding
            
        Returns:
            Success(None) or Failure(error_message)
        """
        ...
    
    def exists(self, path: Path) -> bool:
        """Check if path exists"""
        ...
    
    def is_dir(self, path: Path) -> bool:
        """Check if path is a directory"""
        ...
    
    def is_file(self, path: Path) -> bool:
        """Check if path is a file"""
        ...
    
    def list_dir(self, path: Path) -> list[Path]:
        """
        List directory contents.
        
        Returns empty list if path doesn't exist or isn't a directory.
        """
        ...
    
    def mkdir(self, path: Path, parents: bool = True) -> Result:
        """
        Create directory.
        
        Args:
            path: Directory path to create
            parents: Create parent directories if needed
            
        Returns:
            Success(None) or Failure(error_message)
        """
        ...
