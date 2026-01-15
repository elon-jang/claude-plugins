"""Utility functions for Shortcut Master."""

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


def normalize_shortcut(shortcut: str) -> str:
    """
    Normalize shortcut notation to standard format.

    Examples:
        cmd+d -> Cmd+D
        command+shift+p -> Cmd+Shift+P
        ctrl+alt+delete -> Ctrl+Alt+Delete

    Args:
        shortcut: Raw shortcut string

    Returns:
        Normalized shortcut in format: Cmd+Shift+P
    """
    # Mapping of common variations
    modifier_map = {
        'command': 'Cmd',
        'cmd': 'Cmd',
        'control': 'Ctrl',
        'ctrl': 'Ctrl',
        'option': 'Alt',
        'alt': 'Alt',
        'shift': 'Shift',
    }

    # Split by + and normalize each part
    parts = [p.strip() for p in shortcut.split('+')]
    normalized_parts = []

    for part in parts:
        part_lower = part.lower()
        if part_lower in modifier_map:
            normalized_parts.append(modifier_map[part_lower])
        else:
            # Capitalize regular keys
            normalized_parts.append(part.upper() if len(part) == 1 else part.capitalize())

    return '+'.join(normalized_parts)


def get_next_review_date(last_reviewed: str, box: int, intervals: dict) -> datetime:
    """
    Calculate next review date based on Leitner Box interval.

    Args:
        last_reviewed: ISO 8601 datetime string
        box: Box number (1, 2, or 3)
        intervals: Dict with box1, box2, box3 intervals in days

    Returns:
        Next review datetime
    """
    last_dt = datetime.fromisoformat(last_reviewed)
    interval_key = f'box{box}'
    interval_days = intervals.get(interval_key, 1)

    return last_dt + timedelta(days=interval_days)


def is_due_for_review(last_reviewed: str, box: int, intervals: dict) -> bool:
    """
    Check if a card is due for review today.

    Uses exact date matching: today >= lastReviewed + interval

    Args:
        last_reviewed: ISO 8601 datetime string
        box: Box number
        intervals: Box intervals config

    Returns:
        True if due today
    """
    next_review = get_next_review_date(last_reviewed, box, intervals)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    next_review_date = next_review.replace(hour=0, minute=0, second=0, microsecond=0)

    return today >= next_review_date


def find_repo_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find the shortcut repository root by looking for .shortcut-master directory.

    Args:
        start_path: Starting directory (defaults to cwd)

    Returns:
        Path to repo root, or None if not found
    """
    current = start_path or Path.cwd()

    # Check up to 10 parent directories
    for _ in range(10):
        if (current / '.shortcut-master').is_dir():
            return current

        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent

    return None


def get_app_name_from_file(file_path: Path) -> Optional[str]:
    """
    Extract app name from shortcuts file path.

    Examples:
        vscode_shortcuts.md -> vscode
        gmail_shortcuts.md -> gmail

    Args:
        file_path: Path to shortcuts file

    Returns:
        App name or None if invalid format
    """
    if not file_path.name.endswith('_shortcuts.md'):
        return None

    return file_path.name.replace('_shortcuts.md', '')


def format_date_relative(dt: datetime) -> str:
    """
    Format datetime as relative string.

    Examples:
        today -> "today"
        tomorrow -> "tomorrow"
        2026-01-18 -> "Jan 18"

    Args:
        dt: Datetime to format

    Returns:
        Relative date string
    """
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    dt_date = dt.replace(hour=0, minute=0, second=0, microsecond=0)

    diff = (dt_date - today).days

    if diff == 0:
        return "today"
    elif diff == 1:
        return "tomorrow"
    elif diff == -1:
        return "yesterday"
    elif 0 < diff < 7:
        return dt.strftime("%A")  # Day name
    else:
        return dt.strftime("%b %d")  # Jan 18
