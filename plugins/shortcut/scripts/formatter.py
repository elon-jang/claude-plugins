"""Markdown table formatter for shortcuts files."""

from pathlib import Path
from tabulate import tabulate


class ShortcutFormatter:
    """Formats Markdown shortcuts files."""

    def __init__(self, file_path: Path):
        """
        Initialize formatter.

        Args:
            file_path: Path to shortcuts file
        """
        self.file_path = file_path

    def format(self) -> None:
        """
        Format the shortcuts file with aligned tables.

        Reads the file, formats all tables, and writes back.
        """
        if not self.file_path.exists():
            return

        content = self.file_path.read_text()
        formatted = self._format_content(content)
        self.file_path.write_text(formatted)

    def _format_content(self, content: str) -> str:
        """
        Format content by aligning Markdown tables.

        Args:
            content: File content

        Returns:
            Formatted content
        """
        lines = content.split('\n')
        result = []
        current_table = []
        in_table = False

        for line in lines:
            stripped = line.strip()

            # Start of table (header with |)
            if '|' in stripped and ('Shortcut' in stripped or 'Description' in stripped):
                in_table = True
                current_table = [stripped]
                continue

            # Table separator or row
            if in_table and '|' in stripped:
                current_table.append(stripped)
                continue

            # End of table
            if in_table and (not stripped or not '|' in stripped):
                # Format accumulated table
                if len(current_table) > 2:  # Header + separator + at least 1 row
                    formatted_table = self._format_table(current_table)
                    result.extend(formatted_table)
                else:
                    result.extend(current_table)

                current_table = []
                in_table = False

            # Regular line (not part of table)
            if not in_table:
                result.append(line)

        # Handle table at end of file
        if current_table and len(current_table) > 2:
            formatted_table = self._format_table(current_table)
            result.extend(formatted_table)
        elif current_table:
            result.extend(current_table)

        return '\n'.join(result)

    def _format_table(self, table_lines: list[str]) -> list[str]:
        """
        Format a Markdown table using tabulate.

        Args:
            table_lines: List of table lines (header, separator, rows)

        Returns:
            Formatted table lines
        """
        if len(table_lines) < 3:
            return table_lines

        # Parse header
        header_line = table_lines[0]
        headers = [h.strip() for h in header_line.split('|') if h.strip()]

        # Parse rows (skip separator at index 1)
        rows = []
        for line in table_lines[2:]:
            cells = [c.strip() for c in line.split('|') if c.strip()]
            if len(cells) == len(headers):
                rows.append(cells)

        # Format with tabulate
        if rows:
            formatted = tabulate(rows, headers=headers, tablefmt='github')
            return formatted.split('\n')

        return table_lines


def format_all_shortcuts(repo_path: Path) -> None:
    """
    Format all shortcuts files in repository.

    Args:
        repo_path: Path to repository root
    """
    for file in repo_path.glob('*_shortcuts.md'):
        formatter = ShortcutFormatter(file)
        formatter.format()
