"""Repository management for Shortcut Master."""

import json
from pathlib import Path
from typing import Optional
import git

from scripts.utils import get_app_name_from_file


class RepositoryManager:
    """Manages shortcut repository initialization and operations."""

    def __init__(self, repo_path: Path):
        """
        Initialize repository manager.

        Args:
            repo_path: Path to repository root
        """
        self.repo_path = repo_path
        self.config_dir = repo_path / '.shortcut-master'
        self.config_file = self.config_dir / 'config.json'
        self.progress_file = self.config_dir / 'learning-progress.json'
        self.gitignore_file = repo_path / '.gitignore'

    def initialize(self) -> None:
        """
        Initialize a new shortcut repository.

        Creates:
        - .shortcut-master/ directory
        - config.json
        - learning-progress.json
        - .gitignore
        - README.md
        - Git repository
        """
        # Create directories
        self.repo_path.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)

        # Create config.json
        default_config = {
            "version": "1.0.0",
            "apps": [],
            "settings": {
                "boxIntervals": {
                    "box1": 1,
                    "box2": 3,
                    "box3": 7
                },
                "quizSize": 10,
                "defaultLearningMode": "flash"
            }
        }

        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)

        # Create empty learning-progress.json
        with open(self.progress_file, 'w') as f:
            json.dump({}, f, indent=2)

        # Create .gitignore
        gitignore_content = """# Learning progress is local only
.shortcut-master/learning-progress.json

# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/

# OS
.DS_Store
Thumbs.db
"""
        with open(self.gitignore_file, 'w') as f:
            f.write(gitignore_content)

        # Create README.md
        readme_content = """# My Shortcuts

Personal keyboard shortcut collection managed with [Shortcut Master](https://github.com/elon-jang/claude-plugins/tree/master/plugins/shortcut-master).

## Apps

(Add apps with `/shortcut add`)

## Usage

```bash
# Search shortcuts
/shortcut search "comment"

# Learn shortcuts
/shortcut learn vscode

# View statistics
/shortcut stats
```
"""
        readme_file = self.repo_path / 'README.md'
        with open(readme_file, 'w') as f:
            f.write(readme_content)

        # Initialize git repository
        try:
            repo = git.Repo.init(self.repo_path)
            repo.index.add([
                '.shortcut-master/config.json',
                '.gitignore',
                'README.md'
            ])
            repo.index.commit("Initial commit: Initialize shortcut repository")
        except Exception as e:
            raise RuntimeError(f"Git 저장소 초기화 실패: {e}")

    def load_config(self) -> dict:
        """Load repository configuration."""
        if not self.config_file.exists():
            raise FileNotFoundError("저장소가 초기화되지 않았습니다. /shortcut init을 먼저 실행하세요.")

        with open(self.config_file) as f:
            return json.load(f)

    def save_config(self, config: dict) -> None:
        """Save repository configuration."""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def load_progress(self) -> dict:
        """Load learning progress data."""
        if not self.progress_file.exists():
            return {}

        with open(self.progress_file) as f:
            return json.load(f)

    def save_progress(self, progress: dict) -> None:
        """Save learning progress data."""
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)

    def get_app_list(self) -> list[str]:
        """
        Get list of apps by scanning for *_shortcuts.md files.

        Returns:
            List of app names
        """
        apps = []
        for file in self.repo_path.glob('*_shortcuts.md'):
            app_name = get_app_name_from_file(file)
            if app_name:
                apps.append(app_name)
        return sorted(apps)

    def rename_app(self, old_name: str, new_name: str) -> None:
        """
        Rename an app and update all related data.

        Args:
            old_name: Old app name
            new_name: New app name
        """
        old_file = self.repo_path / f'{old_name}_shortcuts.md'
        new_file = self.repo_path / f'{new_name}_shortcuts.md'

        if not old_file.exists():
            raise FileNotFoundError(f"{old_name}_shortcuts.md 파일이 존재하지 않습니다.")

        if new_file.exists():
            raise FileExistsError(f"{new_name}_shortcuts.md 파일이 이미 존재합니다.")

        # Rename file
        old_file.rename(new_file)

        # Update learning progress keys
        progress = self.load_progress()
        updated_progress = {}

        for key, value in progress.items():
            if key.startswith(f'{old_name}:'):
                new_key = key.replace(f'{old_name}:', f'{new_name}:', 1)
                updated_progress[new_key] = value
            else:
                updated_progress[key] = value

        self.save_progress(updated_progress)

        # Update config apps list
        config = self.load_config()
        if old_name in config['apps']:
            config['apps'].remove(old_name)
        if new_name not in config['apps']:
            config['apps'].append(new_name)
            config['apps'].sort()
        self.save_config(config)

        # Git commit
        try:
            repo = git.Repo(self.repo_path)
            repo.index.add([
                str(new_file.relative_to(self.repo_path)),
                '.shortcut-master/config.json'
            ])
            repo.index.commit(f"Rename app: {old_name} → {new_name}")
        except Exception:
            pass  # Git operations are optional

    def get_repo(self) -> Optional[git.Repo]:
        """Get git repository object if available."""
        try:
            return git.Repo(self.repo_path)
        except Exception:
            return None
