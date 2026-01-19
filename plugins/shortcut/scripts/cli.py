"""CLI interface for Shortcut Master."""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

from scripts.repo_manager import RepositoryManager
from scripts.parser import parse_all_shortcuts, get_categories
from scripts.search import SearchEngine
from scripts.learning import LearningSystem
from scripts.integrity import IntegrityManager
from scripts.formatter import format_all_shortcuts
from scripts.utils import find_repo_root, normalize_shortcut


console = Console()


def cmd_init(args):
    """Initialize a new shortcut repository."""
    repo_path = Path(args.repo_path or Path.cwd() / 'shortcuts').expanduser()

    if repo_path.exists() and any(repo_path.iterdir()):
        console.print(f"[yellow]Directory {repo_path} already exists and is not empty.[/yellow]")
        return

    try:
        repo_manager = RepositoryManager(repo_path)
        repo_manager.initialize()
        console.print(f"\n[green]✓ Initialized shortcut repository at {repo_path}[/green]\n")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")


def cmd_add(args):
    """Add a new shortcut interactively."""
    repo_path = find_repo_root()
    if not repo_path:
        console.print("[red]저장소가 초기화되지 않았습니다. /shortcut init을 먼저 실행하세요.[/red]")
        return

    repo_manager = RepositoryManager(repo_path)

    # Get app list for autocomplete
    apps = repo_manager.get_app_list()

    # Prompt for app
    console.print("\n[bold]Add New Shortcut[/bold]\n")

    if apps:
        console.print(f"Existing apps: {', '.join(apps)}")

    app_name = Prompt.ask("App")

    # Get existing categories for autocomplete
    shortcuts_by_app = parse_all_shortcuts(repo_path)
    categories = []
    if app_name in shortcuts_by_app:
        categories = get_categories(shortcuts_by_app[app_name])

    if categories:
        console.print(f"Existing categories: {', '.join(categories)}")

    category = Prompt.ask("Category")

    # Get shortcut and normalize
    shortcut_raw = Prompt.ask("Shortcut")
    shortcut_normalized = normalize_shortcut(shortcut_raw)

    if shortcut_raw != shortcut_normalized:
        console.print(f"[dim]Normalized: {shortcut_normalized}[/dim]")

    description = Prompt.ask("Description")

    # Check for duplicates
    integrity_manager = IntegrityManager(repo_manager)
    if integrity_manager.check_duplicate(app_name, shortcut_normalized):
        console.print(f"\n[red]Error: 이미 존재하는 단축키입니다.[/red]\n")
        return

    # Add to file
    shortcuts_file = repo_path / f"{app_name}_shortcuts.md"

    # Create file if it doesn't exist
    if not shortcuts_file.exists():
        shortcuts_file.write_text(f"# {app_name.capitalize()} Shortcuts\n\n## {category}\n\n| Shortcut | Description | Category |\n|----------|-------------|----------|\n")

    # Append shortcut
    with open(shortcuts_file, 'a') as f:
        f.write(f"| {shortcut_normalized} | {description} | {category} |\n")

    # Format file
    format_all_shortcuts(repo_path)

    # Git commit
    try:
        repo = repo_manager.get_repo()
        if repo:
            repo.index.add([str(shortcuts_file.relative_to(repo_path))])
            repo.index.commit(f"Add shortcut: {shortcut_normalized}")
            console.print(f"\n[green]✓ Added to {app_name}_shortcuts.md[/green]")
            console.print(f"[green]✓ Committed: Add shortcut: {shortcut_normalized}[/green]\n")
    except Exception as e:
        console.print(f"\n[green]✓ Added to {app_name}_shortcuts.md[/green]")
        console.print(f"[yellow]Warning: Git commit failed: {e}[/yellow]\n")


def cmd_search(args):
    """Search shortcuts."""
    repo_path = find_repo_root()
    if not repo_path:
        console.print("[red]저장소가 초기화되지 않았습니다.[/red]")
        return

    search_engine = SearchEngine(repo_path)
    results = search_engine.search(
        args.query,
        app_filter=args.app,
        section_filter=args.section
    )
    search_engine.display_results(results, args.query)


def cmd_learn(args):
    """Start learning session."""
    repo_path = find_repo_root()
    if not repo_path:
        console.print("[red]저장소가 초기화되지 않았습니다.[/red]")
        return

    repo_manager = RepositoryManager(repo_path)

    # Clean orphaned progress first
    integrity_manager = IntegrityManager(repo_manager)
    orphaned = integrity_manager.clean_orphaned_progress()
    if orphaned > 0:
        console.print(f"[dim]Cleaned {orphaned} orphaned progress entries.[/dim]")

    learning_system = LearningSystem(repo_manager)
    learning_system.start_session(
        app_name=args.app,
        mode=args.mode,
        review_all=args.all
    )


def cmd_stats(args):
    """Show learning statistics."""
    repo_path = find_repo_root()
    if not repo_path:
        console.print("[red]저장소가 초기화되지 않았습니다.[/red]")
        return

    repo_manager = RepositoryManager(repo_path)
    progress = repo_manager.load_progress()

    if not progress:
        console.print("\n[yellow]No learning data yet. Start with /shortcut learn[/yellow]\n")
        return

    # Filter by app if specified
    if args.app:
        progress = {k: v for k, v in progress.items() if k.startswith(f"{args.app}:")}

    if not progress:
        console.print(f"\n[yellow]No learning data for {args.app}[/yellow]\n")
        return

    # Calculate stats
    box_counts = {1: 0, 2: 0, 3: 0}
    total_correct = 0
    total_incorrect = 0
    difficult_shortcuts = []

    for key, p in progress.items():
        box_counts[p['box']] = box_counts.get(p['box'], 0) + 1
        total_correct += p['correctCount']
        total_incorrect += p['incorrectCount']
        if p['incorrectCount'] > 0:
            difficult_shortcuts.append((key, p['incorrectCount']))

    # Sort by incorrect count
    difficult_shortcuts.sort(key=lambda x: -x[1])

    # Display
    app_name = args.app or "All Apps"
    console.print(f"\n[bold]=== Learning Statistics: {app_name.capitalize()} ===[/bold]\n")

    console.print("Box Distribution:")
    console.print(f"  Box 1: {box_counts[1]} cards (review now)")
    console.print(f"  Box 2: {box_counts[2]} cards")
    console.print(f"  Box 3: {box_counts[3]} cards")
    console.print()

    if total_correct + total_incorrect > 0:
        accuracy = (total_correct / (total_correct + total_incorrect)) * 100
        console.print(f"Overall Accuracy: {accuracy:.1f}%")
        console.print(f"  Correct: {total_correct} / Incorrect: {total_incorrect}")
        console.print()

    if difficult_shortcuts:
        console.print("Most Difficult Shortcuts (Top 5):")
        for key, count in difficult_shortcuts[:5]:
            app, shortcut = key.split(':', 1)
            console.print(f"  {shortcut} - incorrectCount: {count}")
        console.print()


def cmd_list(args):
    """List all apps."""
    repo_path = find_repo_root()
    if not repo_path:
        console.print("[red]저장소가 초기화되지 않았습니다.[/red]")
        return

    repo_manager = RepositoryManager(repo_path)
    apps = repo_manager.get_app_list()

    if not apps:
        console.print("\n[yellow]No apps found. Add shortcuts with /shortcut add[/yellow]\n")
        return

    console.print("\n[bold]Apps:[/bold]")
    for app in apps:
        console.print(f"  - {app}")
    console.print()


def cmd_delete(args):
    """Delete a shortcut."""
    console.print(f"\n[red]Not implemented yet: delete {args.app} {args.shortcut}[/red]\n")


def cmd_rename(args):
    """Rename an app."""
    repo_path = find_repo_root()
    if not repo_path:
        console.print("[red]저장소가 초기화되지 않았습니다.[/red]")
        return

    repo_manager = RepositoryManager(repo_path)

    try:
        repo_manager.rename_app(args.old_name, args.new_name)
        console.print(f"\n[green]✓ Renamed {args.old_name} → {args.new_name}[/green]\n")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Shortcut Master - Manage and learn keyboard shortcuts',
        prog='shortcut'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # init
    parser_init = subparsers.add_parser('init', help='Initialize repository')
    parser_init.add_argument('repo_path', nargs='?', help='Repository path')
    parser_init.set_defaults(func=cmd_init)

    # add
    parser_add = subparsers.add_parser('add', help='Add new shortcut')
    parser_add.set_defaults(func=cmd_add)

    # search
    parser_search = subparsers.add_parser('search', help='Search shortcuts')
    parser_search.add_argument('query', help='Search query')
    parser_search.add_argument('--app', help='Filter by app')
    parser_search.add_argument('--section', help='Filter by section')
    parser_search.set_defaults(func=cmd_search)

    # learn
    parser_learn = subparsers.add_parser('learn', help='Start learning session')
    parser_learn.add_argument('app', nargs='?', help='App name')
    parser_learn.add_argument('--mode', choices=['flash', 'quick', 'typing'], default='flash')
    parser_learn.add_argument('--all', action='store_true', help='Review all cards')
    parser_learn.set_defaults(func=cmd_learn)

    # stats
    parser_stats = subparsers.add_parser('stats', help='Show statistics')
    parser_stats.add_argument('app', nargs='?', help='App name')
    parser_stats.set_defaults(func=cmd_stats)

    # list
    parser_list = subparsers.add_parser('list', help='List all apps')
    parser_list.set_defaults(func=cmd_list)

    # delete
    parser_delete = subparsers.add_parser('delete', help='Delete shortcut')
    parser_delete.add_argument('app', help='App name')
    parser_delete.add_argument('shortcut', help='Shortcut to delete')
    parser_delete.set_defaults(func=cmd_delete)

    # rename
    parser_rename = subparsers.add_parser('rename', help='Rename app')
    parser_rename.add_argument('old_name', help='Old app name')
    parser_rename.add_argument('new_name', help='New app name')
    parser_rename.set_defaults(func=cmd_rename)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
