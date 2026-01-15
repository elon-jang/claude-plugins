"""Learning system with Leitner Box algorithm."""

from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import random

from rich.console import Console
from rich.prompt import Prompt, Confirm

from scripts.parser import parse_all_shortcuts, Shortcut
from scripts.repo_manager import RepositoryManager
from scripts.utils import is_due_for_review, format_date_relative, get_next_review_date


@dataclass
class LearningCard:
    """Represents a shortcut in the learning system."""
    shortcut: Shortcut
    box: int
    last_reviewed: str
    correct_count: int
    incorrect_count: int
    added_date: str


@dataclass
class SessionStats:
    """Statistics for a learning session."""
    total_questions: int
    correct: int
    incorrect: int
    skipped: int
    box_changes: dict  # e.g., {"1->2": 5, "2->1": 2}


class LearningSystem:
    """Manages learning sessions with Leitner Box algorithm."""

    def __init__(self, repo_manager: RepositoryManager):
        """
        Initialize learning system.

        Args:
            repo_manager: Repository manager instance
        """
        self.repo_manager = repo_manager
        self.console = Console()
        self.config = repo_manager.load_config()
        self.intervals = self.config['settings']['boxIntervals']
        self.quiz_size = self.config['settings']['quizSize']

    def start_session(
        self,
        app_name: Optional[str] = None,
        mode: str = 'flash',
        review_all: bool = False
    ) -> None:
        """
        Start a learning session.

        Args:
            app_name: Filter by app (None = all apps)
            mode: Learning mode ('flash', 'quick', 'typing')
            review_all: If True, review all cards regardless of schedule
        """
        # Get cards to review
        cards = self._get_due_cards(app_name, review_all)

        if not cards:
            next_date = self._get_next_review_date(app_name)
            if next_date:
                self.console.print(
                    f"\n[yellow]오늘 복습할 카드가 없습니다. "
                    f"다음 복습: {format_date_relative(next_date)}[/yellow]\n"
                )
            else:
                self.console.print(
                    "\n[yellow]학습할 단축키가 없습니다. /shortcut add로 추가하세요.[/yellow]\n"
                )
            return

        # Limit quiz size
        if len(cards) > self.quiz_size:
            cards = cards[:self.quiz_size]
        elif len(cards) < self.quiz_size:
            self.console.print(
                f"\n[dim]오늘은 {len(cards)}문제로 진행합니다.[/dim]\n"
            )

        # Shuffle cards
        random.shuffle(cards)

        # Show session header
        self._show_session_header(app_name or "All Apps", mode, cards)

        # Run session based on mode
        if mode == 'flash':
            stats = self._run_flash_mode(cards)
        elif mode == 'quick':
            stats = self._run_quick_mode(cards)
        elif mode == 'typing':
            stats = self._run_typing_mode(cards)
        else:
            self.console.print(f"[red]Unknown mode: {mode}[/red]")
            return

        # Save progress
        self._save_session_progress(cards)

        # Show final stats
        self._show_session_stats(stats)

    def _get_due_cards(self, app_name: Optional[str], review_all: bool) -> list[LearningCard]:
        """Get cards due for review."""
        shortcuts_by_app = parse_all_shortcuts(self.repo_manager.repo_path)
        progress = self.repo_manager.load_progress()

        cards = []

        for app, shortcuts in shortcuts_by_app.items():
            if app_name and app != app_name:
                continue

            for shortcut in shortcuts:
                key = f"{app}:{shortcut.shortcut}"

                # Get or create progress entry
                if key in progress:
                    p = progress[key]
                    card = LearningCard(
                        shortcut=shortcut,
                        box=p['box'],
                        last_reviewed=p['lastReviewed'],
                        correct_count=p['correctCount'],
                        incorrect_count=p['incorrectCount'],
                        added_date=p['addedDate']
                    )

                    # Check if due
                    if review_all or is_due_for_review(p['lastReviewed'], p['box'], self.intervals):
                        cards.append(card)
                else:
                    # New card (not yet learned)
                    if review_all:
                        now_iso = datetime.now().isoformat()
                        card = LearningCard(
                            shortcut=shortcut,
                            box=1,
                            last_reviewed=now_iso,
                            correct_count=0,
                            incorrect_count=0,
                            added_date=now_iso
                        )
                        cards.append(card)

        # Sort by box (Box 1 first), then by incorrect_count (struggling cards first)
        cards.sort(key=lambda c: (c.box, -c.incorrect_count))

        return cards

    def _get_next_review_date(self, app_name: Optional[str]) -> Optional[datetime]:
        """Get the earliest next review date."""
        progress = self.repo_manager.load_progress()

        if not progress:
            return None

        next_dates = []
        for key, p in progress.items():
            if app_name:
                if not key.startswith(f"{app_name}:"):
                    continue

            next_date = get_next_review_date(p['lastReviewed'], p['box'], self.intervals)
            next_dates.append(next_date)

        return min(next_dates) if next_dates else None

    def _show_session_header(self, app_name: str, mode: str, cards: list[LearningCard]) -> None:
        """Show session header with box distribution."""
        box_counts = {1: 0, 2: 0, 3: 0}
        for card in cards:
            box_counts[card.box] = box_counts.get(card.box, 0) + 1

        mode_display = {
            'flash': 'Flash',
            'quick': 'Quick',
            'typing': 'Typing'
        }.get(mode, mode)

        self.console.print(f"\n[bold]=== Learning Mode: {app_name} ({mode_display}) ===[/bold]")
        self.console.print(
            f"Box 1: {box_counts[1]} cards | "
            f"Box 2: {box_counts[2]} cards | "
            f"Box 3: {box_counts[3]} cards\n"
        )

    def _run_flash_mode(self, cards: list[LearningCard]) -> SessionStats:
        """Run flash card mode."""
        stats = SessionStats(
            total_questions=len(cards),
            correct=0,
            incorrect=0,
            skipped=0,
            box_changes={}
        )

        for i, card in enumerate(cards, 1):
            self.console.print(f"\n[bold][Question {i}/{len(cards)}] Box {card.box}[/bold]")
            self.console.print("What does this shortcut do?\n")
            self.console.print(f"  [cyan]{card.shortcut.shortcut}[/cyan]\n")

            input("[dim][Press Enter to reveal answer][/dim]")

            # Show answer
            self.console.print("\n[bold]=== Answer ===[/bold]\n")
            self.console.print(f"  [cyan]{card.shortcut.shortcut}[/cyan]\n")
            self.console.print(f"  → [green]{card.shortcut.description}[/green]\n")
            self.console.print(f"  Category: {card.shortcut.category}")
            if card.shortcut.section:
                self.console.print(f"  Section: {card.shortcut.section}")

            # Get user response
            self.console.print("\nDid you remember correctly?")
            response = Prompt.ask(
                "  [y] Yes  [n] No  [s] Skip",
                choices=['y', 'n', 's'],
                default='y'
            )

            # Update card
            if response == 'y':
                stats.correct += 1
                old_box = card.box
                card.box = min(card.box + 1, 3)
                card.correct_count += 1
                if old_box != card.box:
                    key = f"{old_box}->{card.box}"
                    stats.box_changes[key] = stats.box_changes.get(key, 0) + 1
                    self.console.print(f"[green][Box {old_box} → Box {card.box}] ✓[/green]")
            elif response == 'n':
                stats.incorrect += 1
                old_box = card.box
                card.box = 1
                card.incorrect_count += 1
                if old_box != card.box:
                    key = f"{old_box}->{card.box}"
                    stats.box_changes[key] = stats.box_changes.get(key, 0) + 1
                    self.console.print(f"[red][Box {old_box} → Box 1] ✗[/red]")
                else:
                    self.console.print("[yellow][Stays in Box 1][/yellow]")
            else:  # skip
                stats.skipped += 1
                self.console.print("[dim][Skipped][/dim]")

            card.last_reviewed = datetime.now().isoformat()

        return stats

    def _run_quick_mode(self, cards: list[LearningCard]) -> SessionStats:
        """Run quick mode (no jump allowed)."""
        stats = SessionStats(
            total_questions=len(cards),
            correct=0,
            incorrect=0,
            skipped=0,
            box_changes={}
        )

        for i, card in enumerate(cards, 1):
            self.console.print(f"\n[bold][Question {i}/{len(cards)}] Box {card.box}[/bold]")
            self.console.print("What does this shortcut do?\n")
            self.console.print(f"  [cyan]{card.shortcut.shortcut}[/cyan]\n")

            input("[dim][Press Enter to reveal answer][/dim]")

            # Show answer
            self.console.print(f"\n  [cyan]{card.shortcut.shortcut}[/cyan] → {card.shortcut.description}\n")

            # Get difficulty rating
            self.console.print("How well did you know it?")
            response = Prompt.ask(
                "  [1] Didn't know  [2] Got it",
                choices=['1', '2'],
                default='2'
            )

            # Update card (no jump, only gradual progression)
            if response == '2':
                stats.correct += 1
                old_box = card.box
                card.box = min(card.box + 1, 3)
                card.correct_count += 1
                if old_box != card.box:
                    key = f"{old_box}->{card.box}"
                    stats.box_changes[key] = stats.box_changes.get(key, 0) + 1
            else:
                stats.incorrect += 1
                old_box = card.box
                card.box = 1
                card.incorrect_count += 1
                if old_box != card.box:
                    key = f"{old_box}->{card.box}"
                    stats.box_changes[key] = stats.box_changes.get(key, 0) + 1

            card.last_reviewed = datetime.now().isoformat()

        return stats

    def _run_typing_mode(self, cards: list[LearningCard]) -> SessionStats:
        """Run typing mode (keyboard input detection)."""
        self.console.print("[yellow]Typing mode: Only simultaneous key presses supported (e.g., Cmd+Shift+P)[/yellow]")
        self.console.print("[yellow]Multi-key sequences (e.g., Cmd+K → Cmd+S) are not supported.[/yellow]\n")

        # For now, fallback to flash mode
        # TODO: Implement actual keyboard detection with pynput
        return self._run_flash_mode(cards)

    def _save_session_progress(self, cards: list[LearningCard]) -> None:
        """Save learning progress after session."""
        progress = self.repo_manager.load_progress()

        for card in cards:
            key = f"{card.shortcut.app}:{card.shortcut.shortcut}"
            progress[key] = {
                "box": card.box,
                "lastReviewed": card.last_reviewed,
                "correctCount": card.correct_count,
                "incorrectCount": card.incorrect_count,
                "addedDate": card.added_date
            }

        self.repo_manager.save_progress(progress)

    def _show_session_stats(self, stats: SessionStats) -> None:
        """Show final session statistics."""
        self.console.print("\n[bold]=== Learning Session Complete ===[/bold]\n")

        # Accuracy
        total_answered = stats.correct + stats.incorrect
        if total_answered > 0:
            accuracy = (stats.correct / total_answered) * 100
            self.console.print(f"Today's Progress:")
            self.console.print(f"  Correct: {stats.correct}/{total_answered} ({accuracy:.0f}%)")
            if stats.incorrect > 0:
                self.console.print(f"  Incorrect: {stats.incorrect}/{total_answered}")
            if stats.skipped > 0:
                self.console.print(f"  Skipped: {stats.skipped}")
            self.console.print()

        # Box changes
        if stats.box_changes:
            self.console.print("Box Changes:")
            for change, count in sorted(stats.box_changes.items()):
                if '->' in change and count > 0:
                    from_box, to_box = change.split('->')
                    direction = "↑" if int(to_box) > int(from_box) else "↓"
                    self.console.print(f"  Box {change}: {count} shortcuts {direction}")
            self.console.print()

        self.console.print("[green]Great work! Keep practicing.[/green]\n")
