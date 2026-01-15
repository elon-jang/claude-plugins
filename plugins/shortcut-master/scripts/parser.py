"""Markdown table parser for shortcut files."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from scripts.utils import normalize_shortcut, get_app_name_from_file


@dataclass
class Shortcut:
    """Represents a single shortcut entry."""
    app: str
    shortcut: str
    description: str
    category: str
    section: Optional[str] = None
    line_number: int = 0


class ShortcutParser:
    """Parses Markdown shortcut files."""

    def __init__(self, file_path: Path):
        """
        Initialize parser.

        Args:
            file_path: Path to *_shortcuts.md file
        """
        self.file_path = file_path
        self.app_name = get_app_name_from_file(file_path)

        if not self.app_name:
            raise ValueError(f"Invalid shortcuts file name: {file_path.name}")

    def parse(self) -> list[Shortcut]:
        """
        Parse shortcuts file.

        Returns:
            List of Shortcut objects

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"{self.file_path.name} 파일이 존재하지 않습니다.")

        content = self.file_path.read_text()

        if not content.strip():
            raise ValueError(f"{self.file_path.name} 파일이 비어 있습니다.")

        shortcuts = []
        current_section = None
        in_table = False
        header_found = False

        for line_num, line in enumerate(content.split('\n'), 1):
            stripped = line.strip()

            # Section header (## Editing)
            if stripped.startswith('##'):
                current_section = stripped.lstrip('#').strip()
                in_table = False
                header_found = False
                continue

            # Table header (| Shortcut | Description | Category |)
            if '|' in stripped and 'Shortcut' in stripped:
                # Validate header
                if not self._is_valid_header(stripped):
                    raise ValueError(
                        f"{self.file_path.name}:{line_num} - 테이블 형식 오류. "
                        f"필수 컬럼: Shortcut, Description, Category"
                    )
                in_table = True
                header_found = True
                continue

            # Table separator (|----------|-------------|----------|)
            if in_table and re.match(r'\|[\s\-\|]+\|', stripped):
                continue

            # Table row
            if in_table and '|' in stripped:
                try:
                    shortcut = self._parse_row(stripped, current_section, line_num)
                    if shortcut:
                        shortcuts.append(shortcut)
                except ValueError as e:
                    raise ValueError(f"{self.file_path.name}:{line_num} - {e}")

            # Empty line or non-table content
            elif stripped == '' or not stripped.startswith('|'):
                if in_table and not stripped:
                    in_table = False
                continue

        if not shortcuts:
            raise ValueError(f"{self.file_path.name} - 단축키가 없습니다.")

        return shortcuts

    def _is_valid_header(self, line: str) -> bool:
        """
        Check if table header contains required columns.

        Args:
            line: Header line

        Returns:
            True if valid
        """
        required_cols = ['Shortcut', 'Description', 'Category']
        return all(col in line for col in required_cols)

    def _parse_row(self, line: str, section: Optional[str], line_num: int) -> Optional[Shortcut]:
        """
        Parse a single table row.

        Args:
            line: Table row line
            section: Current section name
            line_num: Line number for error reporting

        Returns:
            Shortcut object or None if empty row

        Raises:
            ValueError: If row format is invalid
        """
        # Split by | and clean
        parts = [p.strip() for p in line.split('|')]

        # Remove empty first/last elements (from leading/trailing |)
        if parts and parts[0] == '':
            parts = parts[1:]
        if parts and parts[-1] == '':
            parts = parts[:-1]

        # Need at least 3 columns
        if len(parts) < 3:
            raise ValueError(f"파이프(|) 누락 - 3개 컬럼 필요 (Shortcut, Description, Category)")

        shortcut_raw = parts[0].strip()
        description = parts[1].strip()
        category = parts[2].strip()

        # Skip empty rows
        if not shortcut_raw or not description or not category:
            return None

        # Normalize shortcut notation
        shortcut_normalized = normalize_shortcut(shortcut_raw)

        return Shortcut(
            app=self.app_name,
            shortcut=shortcut_normalized,
            description=description,
            category=category,
            section=section,
            line_number=line_num
        )


def parse_all_shortcuts(repo_path: Path) -> dict[str, list[Shortcut]]:
    """
    Parse all shortcut files in repository.

    Args:
        repo_path: Path to repository root

    Returns:
        Dict mapping app name to list of shortcuts
    """
    shortcuts_by_app = {}

    for file in sorted(repo_path.glob('*_shortcuts.md')):
        try:
            parser = ShortcutParser(file)
            shortcuts = parser.parse()
            app_name = parser.app_name
            shortcuts_by_app[app_name] = shortcuts
        except ValueError:
            # Skip invalid files
            continue

    return shortcuts_by_app


def get_categories(shortcuts: list[Shortcut]) -> list[str]:
    """
    Extract unique categories from shortcuts.

    Args:
        shortcuts: List of shortcuts

    Returns:
        Sorted list of unique categories
    """
    categories = set(s.category for s in shortcuts if s.category)
    return sorted(categories)


def get_sections(shortcuts: list[Shortcut]) -> list[str]:
    """
    Extract unique sections from shortcuts.

    Args:
        shortcuts: List of shortcuts

    Returns:
        Sorted list of unique sections
    """
    sections = set(s.section for s in shortcuts if s.section)
    return sorted(sections)
