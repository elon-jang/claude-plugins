"""Data integrity management for shortcut-master."""

from pathlib import Path
from typing import Set

from scripts.parser import parse_all_shortcuts
from scripts.repo_manager import RepositoryManager


class IntegrityManager:
    """Manages data integrity between shortcuts files and learning progress."""

    def __init__(self, repo_manager: RepositoryManager):
        """
        Initialize integrity manager.

        Args:
            repo_manager: Repository manager instance
        """
        self.repo_manager = repo_manager

    def clean_orphaned_progress(self) -> int:
        """
        Remove learning progress for shortcuts that no longer exist in files.

        This is called automatically when learning session starts.

        Returns:
            Number of orphaned entries removed
        """
        # Parse all shortcuts from files
        shortcuts_by_app = parse_all_shortcuts(self.repo_manager.repo_path)

        # Build set of valid keys (app:shortcut)
        valid_keys: Set[str] = set()
        for app_name, shortcuts in shortcuts_by_app.items():
            for shortcut in shortcuts:
                key = f"{app_name}:{shortcut.shortcut}"
                valid_keys.add(key)

        # Load learning progress
        progress = self.repo_manager.load_progress()

        # Find orphaned keys
        orphaned_keys = set(progress.keys()) - valid_keys

        # Remove orphaned entries
        if orphaned_keys:
            for key in orphaned_keys:
                del progress[key]

            self.repo_manager.save_progress(progress)

        return len(orphaned_keys)

    def check_duplicate(self, app_name: str, shortcut: str) -> bool:
        """
        Check if a shortcut already exists in the app's file.

        Args:
            app_name: App name
            shortcut: Shortcut notation (already normalized)

        Returns:
            True if duplicate exists
        """
        shortcuts_by_app = parse_all_shortcuts(self.repo_manager.repo_path)

        if app_name not in shortcuts_by_app:
            return False

        for s in shortcuts_by_app[app_name]:
            if s.shortcut == shortcut:
                return True

        return False

    def get_stats(self) -> dict:
        """
        Get integrity statistics.

        Returns:
            Dict with stats about data consistency
        """
        shortcuts_by_app = parse_all_shortcuts(self.repo_manager.repo_path)
        progress = self.repo_manager.load_progress()

        # Count shortcuts in files
        total_shortcuts = sum(len(shortcuts) for shortcuts in shortcuts_by_app.values())

        # Count entries in progress
        total_progress_entries = len(progress)

        # Count orphaned (progress but no file)
        valid_keys = set()
        for app_name, shortcuts in shortcuts_by_app.items():
            for shortcut in shortcuts:
                key = f"{app_name}:{shortcut.shortcut}"
                valid_keys.add(key)

        orphaned_count = len(set(progress.keys()) - valid_keys)

        # Count not-yet-learned (file but no progress)
        not_learned_count = len(valid_keys - set(progress.keys()))

        return {
            "total_shortcuts": total_shortcuts,
            "total_progress_entries": total_progress_entries,
            "orphaned_entries": orphaned_count,
            "not_yet_learned": not_learned_count,
            "apps": len(shortcuts_by_app)
        }
