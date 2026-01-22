"""CLI interface for Shortcut Master."""

import sys
import argparse
import re
from pathlib import Path
from datetime import date
from rich.console import Console
from rich.prompt import Prompt

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from scripts.repo_manager import RepositoryManager
from scripts.parser import parse_all_shortcuts, get_categories
from scripts.search import SearchEngine
from scripts.learning import LearningSystem
from scripts.integrity import IntegrityManager
from scripts.formatter import format_all_shortcuts
from scripts.utils import find_repo_root, normalize_shortcut


console = Console()

# App icons mapping
APP_ICONS = {
    'claude': '🤖', 'claude-desktop': '🤖',
    'gmail': '📧',
    'safari': '🧭',
    'slack': '💬',
    'vscode': '📝', 'vs-code': '📝', 'vs code': '📝',
    'chrome': '🌐',
    'figma': '🎨',
    'notion': '📓',
    'terminal': '💻',
    'finder': '📁',
    'arc': '🌈',
}

# Modifier key mappings for conversion
MODIFIER_MAP = {
    'cmd': '⌘', 'command': '⌘', '⌘': '⌘',
    'opt': '⌥', 'option': '⌥', 'alt': '⌥', '⌥': '⌥',
    'ctrl': '⌃', 'control': '⌃', '⌃': '⌃',
    'shift': '⇧', '⇧': '⇧',
}

SPECIAL_KEYS = {
    'enter': '↵', 'return': '↵', '↵': '↵',
    'delete': '⌫', 'backspace': '⌫', '⌫': '⌫',
    'tab': 'Tab',
    'esc': 'Esc', 'escape': 'Esc',
    'space': 'Space',
    'up': '↑', '↑': '↑',
    'down': '↓', '↓': '↓',
    'left': '←', '←': '←',
    'right': '→', '→': '→',
}


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


def cmd_cheatsheet(args):
    """Generate A4 printable cheat sheet HTML."""
    repo_path = find_repo_root()
    if not repo_path:
        console.print("[red]저장소가 초기화되지 않았습니다.[/red]")
        return

    # Determine output path
    output_path = Path(args.output or repo_path / 'cheatsheet.html').expanduser()

    # Load shortcuts from YAML or Markdown files
    apps_data = _load_all_shortcuts(repo_path)

    if not apps_data:
        console.print("[yellow]단축키 파일이 없습니다.[/yellow]")
        return

    # Generate HTML
    html_content = _generate_cheatsheet_html(apps_data, repo_path)

    # Write to file
    output_path.write_text(html_content, encoding='utf-8')
    console.print(f"\n[green]✓ Cheat sheet generated: {output_path}[/green]")

    # Open in browser if requested
    if not args.no_open:
        import subprocess
        try:
            subprocess.run(['open', str(output_path)], check=True)
            console.print("[dim]Opened in browser[/dim]\n")
        except Exception:
            console.print(f"[dim]Open with: open {output_path}[/dim]\n")


def _load_all_shortcuts(repo_path: Path) -> dict:
    """Load shortcuts from YAML or Markdown files."""
    apps_data = {}

    # Try YAML files first (shortcuts/*.yaml)
    yaml_dir = repo_path / 'shortcuts'
    if yaml_dir.exists() and HAS_YAML:
        for yaml_file in sorted(yaml_dir.glob('*.yaml')):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'app' in data:
                        app_name = data['app']
                        apps_data[app_name] = data.get('shortcuts', [])
            except Exception:
                continue

    # Also try root level YAML files
    for yaml_file in sorted(repo_path.glob('*.yaml')):
        if yaml_file.name.startswith('.'):
            continue
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data and 'app' in data:
                    app_name = data['app']
                    if app_name not in apps_data:
                        apps_data[app_name] = data.get('shortcuts', [])
        except Exception:
            continue

    # Fallback to Markdown files if no YAML found
    if not apps_data:
        try:
            shortcuts_by_app = parse_all_shortcuts(repo_path)
            for app_name, shortcuts in shortcuts_by_app.items():
                # Convert to YAML-like structure
                sections = {}
                for s in shortcuts:
                    section = s.section or s.category or 'General'
                    if section not in sections:
                        sections[section] = []
                    sections[section].append({
                        'shortcut': s.shortcut,
                        'description': s.description
                    })
                apps_data[app_name] = [
                    {'section': name, 'items': items}
                    for name, items in sections.items()
                ]
        except Exception:
            pass

    return apps_data


def _shortcut_to_keys_html(shortcut: str) -> str:
    """Convert shortcut string to HTML key elements."""
    # Already has symbols
    if any(sym in shortcut for sym in ['⌘', '⌥', '⌃', '⇧']):
        return _symbols_to_html(shortcut)

    # Parse text format (Cmd+Shift+P)
    return _text_to_html(shortcut)


def _symbols_to_html(shortcut: str) -> str:
    """Convert symbol-based shortcut to HTML."""
    keys_html = []
    i = 0
    chars = list(shortcut)

    while i < len(chars):
        char = chars[i]

        # Modifier symbols
        if char in ['⌘', '⌥', '⌃', '⇧']:
            keys_html.append(f'<span class="key modifier">{char}</span>')
            i += 1
        # Arrow keys
        elif char in ['↑', '↓', '←', '→', '↵', '⌫']:
            keys_html.append(f'<span class="key">{char}</span>')
            i += 1
        # Regular characters (skip + and spaces)
        elif char not in ['+', ' ', '-']:
            # Check for multi-char keys (Esc, Tab, etc.)
            remaining = ''.join(chars[i:])
            found_special = False
            for key_name, display in SPECIAL_KEYS.items():
                if remaining.lower().startswith(key_name):
                    css_class = 'key wide' if len(display) > 2 else 'key'
                    keys_html.append(f'<span class="{css_class}">{display}</span>')
                    i += len(key_name)
                    found_special = True
                    break
            if not found_special:
                keys_html.append(f'<span class="key">{char.upper()}</span>')
                i += 1
        else:
            i += 1

    return '<div class="keys">' + ''.join(keys_html) + '</div>'


def _text_to_html(shortcut: str) -> str:
    """Convert text-based shortcut (Cmd+P) to HTML."""
    keys_html = []

    # Split by + or spaces
    parts = re.split(r'[+\s]+', shortcut)

    for part in parts:
        part_lower = part.lower().strip()
        if not part_lower:
            continue

        # Check modifiers
        if part_lower in MODIFIER_MAP:
            symbol = MODIFIER_MAP[part_lower]
            keys_html.append(f'<span class="key modifier">{symbol}</span>')
        # Check special keys
        elif part_lower in SPECIAL_KEYS:
            display = SPECIAL_KEYS[part_lower]
            css_class = 'key wide' if len(display) > 2 else 'key'
            keys_html.append(f'<span class="{css_class}">{display}</span>')
        # Regular key
        else:
            # Handle ranges like 1~9 or 1-9
            if re.match(r'\d[~\-]\d', part):
                keys_html.append(f'<span class="key wide">{part}</span>')
            else:
                keys_html.append(f'<span class="key">{part.upper()}</span>')

    return '<div class="keys">' + ''.join(keys_html) + '</div>'


def _generate_cheatsheet_html(apps_data: dict, repo_path: Path) -> str:
    """Generate complete cheat sheet HTML."""
    # Load template
    template_path = Path(__file__).parent.parent / 'templates' / 'cheatsheet_template.html'

    if template_path.exists():
        template = template_path.read_text(encoding='utf-8')
    else:
        # Fallback minimal template
        template = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Shortcuts</title></head>
<body><div class="container">{{apps_html}}</div></body></html>"""

    # Generate apps HTML
    apps_html = []
    total_count = 0

    for app_name, sections in apps_data.items():
        app_key = app_name.lower().replace(' ', '-')
        icon = APP_ICONS.get(app_key, '📱')

        app_html = f'    <div class="app" data-app="{app_key}">\n'
        app_html += f'      <div class="app-header">\n'
        app_html += f'        <span class="app-icon">{icon}</span>\n'
        app_html += f'        <span class="app-name">{app_name}</span>\n'
        app_html += f'      </div>\n'

        for section in sections:
            section_name = section.get('section', 'General')
            items = section.get('items', [])

            if not items:
                continue

            app_html += f'      <div class="section">\n'
            app_html += f'        <div class="section-name">{section_name}</div>\n'

            for item in items:
                shortcut = item.get('shortcut', '')
                desc = item.get('description', '')

                if not shortcut:
                    continue

                keys_html = _shortcut_to_keys_html(shortcut)
                app_html += f'        <div class="shortcut-row">\n'
                app_html += f'          {keys_html}\n'
                app_html += f'          <span class="desc">{desc}</span>\n'
                app_html += f'        </div>\n'
                total_count += 1

            app_html += f'      </div>\n'

        app_html += f'    </div>\n'
        apps_html.append(app_html)

    # Fill template
    html = template.replace('{{apps_html}}', '\n'.join(apps_html))
    html = html.replace('{{total_count}}', str(total_count))
    html = html.replace('{{app_count}}', str(len(apps_data)))
    html = html.replace('{{date}}', date.today().isoformat())

    return html


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

    # cheatsheet
    parser_cheatsheet = subparsers.add_parser('cheatsheet', help='Generate A4 cheat sheet HTML')
    parser_cheatsheet.add_argument('output', nargs='?', help='Output file path')
    parser_cheatsheet.add_argument('--no-open', action='store_true', help='Do not open in browser')
    parser_cheatsheet.set_defaults(func=cmd_cheatsheet)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
