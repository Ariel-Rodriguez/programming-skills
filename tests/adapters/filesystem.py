"""
Real FileSystem Adapter

Imperative Shell: IO operations isolated here.
"""

from pathlib import Path
from domain import Result, Success, Failure


class RealFileSystem:
    """
    Adapter for real filesystem operations.
    
    Explicit Boundaries Adapters: Implements FileSystemPort.
    Error Handling Design: Exceptions converted to Result types.
    """
    
    def read_text(self, path: Path, encoding: str = 'utf-8') -> Result:
        """Read file, return Result instead of raising exception"""
        try:
            content = path.read_text(encoding=encoding)
            return Success(content)
        except FileNotFoundError:
            return Failure(f"File not found: {path}", {"path": str(path)})
        except PermissionError:
            return Failure(f"Permission denied: {path}", {"path": str(path)})
        except Exception as e:
            return Failure(f"Failed to read {path}", {"error": str(e)})
    
    def write_text(self, path: Path, content: str, encoding: str = 'utf-8') -> Result:
        """Write file, return Result instead of raising exception"""
        try:
            path.write_text(content, encoding=encoding)
            return Success(None)
        except PermissionError:
            return Failure(f"Permission denied: {path}", {"path": str(path)})
        except Exception as e:
            return Failure(f"Failed to write {path}", {"error": str(e)})
    
    def exists(self, path: Path) -> bool:
        """Check existence without exceptions"""
        return path.exists()
    
    def is_dir(self, path: Path) -> bool:
        """Check if directory"""
        return path.is_dir()
    
    def is_file(self, path: Path) -> bool:
        """Check if file"""
        return path.is_file()
    
    def list_dir(self, path: Path) -> list[Path]:
        """
        List directory contents.
        Returns empty list on error instead of raising.
        """
        if not self.exists(path) or not self.is_dir(path):
            return []
        try:
            return list(path.iterdir())
        except PermissionError:
            return []
        except Exception:
            return []
    
    def mkdir(self, path: Path, parents: bool = True) -> Result:
        """Create directory, return Result"""
        try:
            path.mkdir(parents=parents, exist_ok=True)
            return Success(None)
        except PermissionError:
            return Failure(f"Permission denied: {path}", {"path": str(path)})
        except Exception as e:
            return Failure(f"Failed to create {path}", {"error": str(e)})
