"""
Orphan Branch Manager - Adapter for Git Operations

Handles operations on the benchmark-history orphan branch.
Encapsulates git operations behind a clean interface.
"""

import subprocess
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass(frozen=True)
class GitResult:
    """Result of a git operation."""
    success: bool
    message: str
    output: Optional[str] = None


class OrphanBranchManager:
    """
    Manages operations on the benchmark-history orphan branch.

    This adapter encapsulates git operations, making them testable
    and easy to modify if git strategy changes.
    """

    def __init__(self, repo_path: Path, branch_name: str = "benchmark-history"):
        """
        Initialize the manager.

        Args:
            repo_path: Path to the git repository
            branch_name: Name of the orphan branch to use
        """
        self.repo_path = repo_path
        self.branch_name = branch_name

    def _run_git(self, *args: str) -> GitResult:
        """
        Run a git command.

        Args:
            *args: Git command arguments

        Returns:
            GitResult with success status and output
        """
        try:
            result = subprocess.run(
                ["git"] + list(args),
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return GitResult(
                    success=True,
                    message="Command succeeded",
                    output=result.stdout.strip() if result.stdout else None
                )
            else:
                return GitResult(
                    success=False,
                    message=result.stderr.strip() if result.stderr else "Command failed"
                )
        except Exception as e:
            return GitResult(
                success=False,
                message=str(e)
            )

    def branch_exists(self) -> bool:
        """
        Check if the orphan branch exists.

        Returns:
            True if branch exists, False otherwise
        """
        result = self._run_git("show-ref", "--verify", f"refs/heads/{self.branch_name}")
        return result.success

    def create_orphan_branch(self) -> GitResult:
        """
        Create the orphan branch.

        Returns:
            GitResult with success status
        """
        if self.branch_exists():
            return GitResult(
                success=False,
                message=f"Branch '{self.branch_name}' already exists"
            )

        result = self._run_git("checkout", "--orphan", self.branch_name)
        if result.success:
            # Remove all files to start fresh
            self._run_git("rm", "-rf", ".")
            # Create initial commit
            self._run_git("commit", "--allow-empty", "-m", f"Initial {self.branch_name} commit")

        return result

    def checkout_branch(self) -> GitResult:
        """
        Checkout the orphan branch.

        Returns:
            GitResult with success status
        """
        if not self.branch_exists():
            return self.create_orphan_branch()

        return self._run_git("checkout", self.branch_name)

    def copy_files_to_branch(self, source_dir: Path, dest_dir: Optional[str] = None) -> GitResult:
        """
        Copy files from source to the branch.

        Args:
            source_dir: Source directory to copy from
            dest_dir: Destination directory relative to repo root

        Returns:
            GitResult with success status
        """
        dest = self.repo_path / (dest_dir or "")
        dest.mkdir(parents=True, exist_ok=True)

        try:
            import shutil
            if dest_dir:
                shutil.copytree(source_dir, dest, dirs_exist_ok=True)
                return GitResult(success=True, message=f"Copied files to {dest}")

            for item in source_dir.iterdir():
                target = dest / item.name
                if item.is_dir():
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.copytree(item, target)
                else:
                    shutil.copy2(item, target)

            return GitResult(success=True, message=f"Copied files to {dest}")
        except Exception as e:
            return GitResult(success=False, message=str(e))

    def add_all_files(self) -> GitResult:
        """
        Add all files in the repo to staging.

        Returns:
            GitResult with success status
        """
        return self._run_git("add", ".")

    def commit(self, message: str) -> GitResult:
        """
        Commit staged changes.

        Args:
            message: Commit message

        Returns:
            GitResult with success status
        """
        return self._run_git("commit", "-m", message)

    def push(self, remote: str = "origin") -> GitResult:
        """
        Push the branch to remote.

        Args:
            remote: Remote repository name

        Returns:
            GitResult with success status
        """
        return self._run_git("push", "-f", remote, self.branch_name)

    def reset_hard(self) -> GitResult:
        """
        Reset branch to clean state (delete all changes).

        Returns:
            GitResult with success status
        """
        return self._run_git("reset", "--hard", "HEAD")

    def clean_untracked(self) -> GitResult:
        """
        Remove untracked files.

        Returns:
            GitResult with success status
        """
        return self._run_git("clean", "-fd")

    def get_branch_status(self) -> Tuple[str, str]:
        """
        Get current branch status.

        Returns:
            Tuple of (branch_name, commit_hash)
        """
        branch_result = self._run_git("rev-parse", "--abbrev-ref", "HEAD")
        commit_result = self._run_git("rev-parse", "HEAD")

        branch = branch_result.output or "unknown"
        commit = commit_result.output or "unknown"

        return branch, commit


def manage_benchmark_branch(
    repo_path: Path,
    docs_dir: Path,
    branch_name: str = "benchmark-history"
) -> bool:
    """
    Convenience function: Manage the benchmark branch end-to-end.

    This is the main entry point for most use cases.

    Args:
        repo_path: Path to the git repository
        docs_dir: Path to the docs directory to push
        branch_name: Name of the orphan branch

    Returns:
        True if successful, False otherwise
    """
    manager = OrphanBranchManager(repo_path, branch_name)

    print(f"Managing orphan branch: {branch_name}")

    # Checkout branch (create if needed)
    result = manager.checkout_branch()
    if not result.success:
        print(f"Error checking out branch: {result.message}")
        return False
    print(f"Checked out branch: {branch_name}")

    # Clean branch (remove tracked + untracked)
    result = manager._run_git("rm", "-rf", ".")
    if not result.success:
        print(f"Warning: Could not remove tracked files: {result.message}")

    result = manager.clean_untracked()
    if not result.success:
        print(f"Warning: Could not clean untracked files: {result.message}")

    # Copy output to branch (if exists)
    if docs_dir.exists():
        result = manager.copy_files_to_branch(docs_dir)
        if not result.success:
            print(f"Error copying files: {result.message}")
            return False
        print(f"Copied output to branch")
    else:
        print(f"Warning: output directory does not exist: {docs_dir}")
        print("Creating minimal output structure...")
        # Create a minimal output folder with a README
        docs_dir.mkdir(parents=True, exist_ok=True)
        (docs_dir / "README.md").write_text("# Benchmark Data\n\nThis branch contains benchmark results for the programming skills project.\n")
        result = manager.copy_files_to_branch(docs_dir)
        if not result.success:
            print(f"Error copying files: {result.message}")
            return False
        print(f"Copied output to branch")

    # Add and commit
    result = manager.add_all_files()
    if not result.success:
        print(f"Error adding files: {result.message}")
        return False

    result = manager.commit("Update benchmark data")
    if not result.success:
        # Check if nothing to commit
        status_result = manager._run_git("status", "--porcelain")
        if not status_result.output:
            print("No changes to commit")
            return True
        print(f"Error committing: {result.message}")
        return False
    print("Committed changes")

    # Push to remote
    result = manager.push()
    if not result.success:
        print(f"Error pushing: {result.message}")
        return False
    print("Pushed to remote")

    return True


if __name__ == "__main__":
    import sys

    repo_path = Path(__file__).parent.parent
    docs_dir = repo_path / "docs"
    branch_name = "benchmark-history"

    success = manage_benchmark_branch(repo_path, docs_dir, branch_name)
    sys.exit(0 if success else 1)
