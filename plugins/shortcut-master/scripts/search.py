"""Search engine for shortcuts."""

from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from fuzzywuzzy import fuzz
from rich.console import Console
from rich.table import Table

from scripts.parser import parse_all_shortcuts, Shortcut


@dataclass
class SearchResult:
    """Represents a search result."""
    shortcut: Shortcut
    score: int  # Relevance score (0-100)


class SearchEngine:
    """Searches shortcuts with fuzzy matching."""

    def __init__(self, repo_path: Path, fuzzy_threshold: int = 60):
        """
        Initialize search engine.

        Args:
            repo_path: Path to repository root
            fuzzy_threshold: Minimum fuzzy match score (0-100)
        """
        self.repo_path = repo_path
        self.fuzzy_threshold = fuzzy_threshold

    def search(
        self,
        query: str,
        app_filter: Optional[str] = None,
        section_filter: Optional[str] = None
    ) -> list[SearchResult]:
        """
        Search shortcuts.

        Args:
            query: Search query
            app_filter: Filter by app name (optional)
            section_filter: Filter by section name (optional)

        Returns:
            List of search results sorted by relevance
        """
        shortcuts_by_app = parse_all_shortcuts(self.repo_path)
        results = []

        for app_name, shortcuts in shortcuts_by_app.items():
            # Apply app filter
            if app_filter and app_name != app_filter:
                continue

            for shortcut in shortcuts:
                # Apply section filter
                if section_filter and shortcut.section != section_filter:
                    continue

                # Calculate relevance score
                score = self._calculate_score(query, shortcut)

                if score >= self.fuzzy_threshold:
                    results.append(SearchResult(shortcut, score))

        # Sort by score (descending), then by app name
        results.sort(key=lambda r: (-r.score, r.shortcut.app))

        return results

    def _calculate_score(self, query: str, shortcut: Shortcut) -> int:
        """
        Calculate relevance score for a shortcut.

        Checks:
        - App name
        - Description
        - Category
        - Section
        - Shortcut itself

        Args:
            query: Search query
            shortcut: Shortcut to score

        Returns:
            Score (0-100)
        """
        query_lower = query.lower()

        # Exact matches get highest score
        if query_lower in shortcut.description.lower():
            return 100
        if query_lower in shortcut.category.lower():
            return 95
        if shortcut.section and query_lower in shortcut.section.lower():
            return 90
        if query_lower in shortcut.app.lower():
            return 85

        # Fuzzy matching
        desc_score = fuzz.partial_ratio(query_lower, shortcut.description.lower())
        cat_score = fuzz.partial_ratio(query_lower, shortcut.category.lower())
        app_score = fuzz.partial_ratio(query_lower, shortcut.app.lower())

        section_score = 0
        if shortcut.section:
            section_score = fuzz.partial_ratio(query_lower, shortcut.section.lower())

        # Return highest score
        return max(desc_score, cat_score, app_score, section_score)

    def display_results(self, results: list[SearchResult], query: str) -> None:
        """
        Display search results in formatted output.

        Groups by app and shows results.

        Args:
            results: Search results
            query: Original query
        """
        console = Console()

        if not results:
            console.print(f"\n[yellow]No shortcuts found for '{query}'[/yellow]\n")
            return

        console.print(f"\n[bold]=== Search Results for '{query}' ===[/bold]\n")

        # Group by app
        by_app = {}
        for result in results:
            app = result.shortcut.app
            if app not in by_app:
                by_app[app] = []
            by_app[app].append(result)

        # Display each app's results
        for app in sorted(by_app.keys()):
            console.print(f"[bold cyan][{app.upper()}][/bold cyan]")

            for result in by_app[app]:
                s = result.shortcut
                console.print(
                    f"  {s.shortcut:<20} {s.description:<40} ({s.category})"
                )

            console.print()  # Blank line between apps

        # Summary
        total = len(results)
        apps_count = len(by_app)
        console.print(f"Found {total} shortcuts across {apps_count} app(s).\n")
