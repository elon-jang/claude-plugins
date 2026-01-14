# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Claude Code plugin that automates adding new AI prompts to any Git repository. The plugin handles interactive prompt collection, file creation, README updates, and automatic git commit/push operations.

**Key Features**:
- **Repository-agnostic**: Works with any Git repository (auto-detects root)
- **Dynamic categories**: Auto-detects categories from directory structure
- **Auto-branching**: Pushes to current Git branch automatically
- **Flexible README**: Adapts to different README section formats

## Plugin Architecture

**Plugin Structure**:
- `.claude-plugin/plugin.json` - Plugin metadata (name, version, description)
- `commands/add-prompt.md` - Command definition with workflow instructions
- `README.md` - User-facing documentation

**Command Definition Format** (`commands/add-prompt.md`):
- YAML frontmatter defines command metadata:
  - `name`: Command name (invoked as `/add-prompt`)
  - `description`: Brief description shown in help
  - `argument-hint`: Optional argument syntax hint
  - `allowed-tools`: List of Claude Code tools the command can use
- Markdown body contains detailed workflow instructions that Claude follows

**Target Repository**: Auto-detects the Git repository where the user runs the command (uses `git rev-parse --show-toplevel`)

## Command Workflow

The `/add-prompt` command follows this sequence:

0. **Auto-detect repository configuration**:
   - Git repository root: `git rev-parse --show-toplevel`
   - Available categories: Scan top-level directories
   - Current branch: `git branch --show-current`
1. **Single AskUserQuestion call** with dynamically generated category options
2. **Filename generation**: Convert title to kebab-case (e.g., "AWS EC2" → `aws-ec2-management.md`)
3. **Duplicate handling**: Check for existing files, append `-2`, `-3`, etc. if needed
4. **File creation**: Write prompt to `{REPO_ROOT}/{category}/{filename}.md`
5. **README update**: Insert alphabetically sorted entry (auto-creates section if missing)
6. **Git operations**: `git add`, `git commit`, `git push origin {CURRENT_BRANCH}`

**Critical Implementation Details**:
- Must be run from within a Git repository
- Categories are auto-detected from directory structure (not hardcoded)
- README entries must be alphabetically sorted by filename (not title)
- README sections are detected flexibly (supports multiple formats and languages)
- Exact commit message format: `"Add new prompt: {title}"` (uses title, not filename)
- Pushes to current branch (not hardcoded main/master)

## Testing the Plugin

**Local Development**:
```bash
# Test plugin loading
cc --plugin-dir ~/elon/ai/claude-code/claude-plugins/plugins/add-prompt

# Or from marketplace
/plugin install add-prompt@ai-plugins
```

**Integration Testing**:
```bash
# Create test repository
mkdir test-prompts && cd test-prompts
git init
mkdir infrastructure development
echo "# Test Prompts" > README.md
git add . && git commit -m "Initial commit"

# Inside Claude Code session
/add-prompt
```

**Test Cases**:
- Test with different directory structures
- Test with duplicate filenames (should append `-2`)
- Test README alphabetical insertion
- Test auto-creating new README sections
- Test with different Git branches
- Test git push failures (graceful error handling)
- Test non-Git directory (should fail gracefully)

## Plugin Development Notes

**Allowed Tools** (defined in command frontmatter):
- `AskUserQuestion` - Interactive user input collection
- `Glob` - File existence checks
- `Read` - Reading README.md for updates
- `Write` - Creating new prompt files
- `Edit` - Updating README.md
- `Bash` - Git operations

**Key Constraints**:
- **Must run from within a Git repository** (fails if not in Git repo)
- **Requires README.md** in repository root (creates sections if missing)
- Must preserve existing README formatting
- Must maintain alphabetical order in README
- Git push failures should not rollback file creation
- Category directories must exist (or use default "general" category)

## Marketplace Registration

To register this plugin in the Claude Code marketplace (`elon-jang/claude-plugins`):

### 1. Prepare Plugin for Marketplace

Ensure the plugin follows the required structure:

```
add-prompt/
├── .claude-plugin/
│   └── plugin.json          # Plugin metadata
├── commands/
│   └── add-prompt.md        # Command definition
├── README.md                # User documentation
└── CLAUDE.md                # Developer documentation
```

### 2. Add to Marketplace Repository

**Directory Structure**:
```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json     # Marketplace config
└── plugins/
    └── add-prompt/          # Copy entire plugin here
        ├── .claude-plugin/
        │   └── plugin.json
        ├── commands/
        │   └── add-prompt.md
        ├── README.md
        └── CLAUDE.md
```

**Update marketplace.json**:
```json
{
  "name": "ai-plugins",
  "owner": {
    "name": "Elon",
    "email": "contact@elon.dev"
  },
  "description": "A collection of Claude Code plugins for AI-Native Product Items",
  "version": "1.0.0",
  "plugins": [
    {
      "source": "./plugins/add-prompt",
      "description": "Add new AI prompts to repository and push to Github",
      "keywords": ["prompts", "workflow", "git", "automation"]
    }
  ]
}
```

### 3. Update plugin.json

Ensure `.claude-plugin/plugin.json` contains complete metadata:

```json
{
  "name": "add-prompt",
  "version": "0.1.0",
  "description": "Add new AI prompts to the prompts repository and push to Github",
  "author": {
    "name": "Elon"
  },
  "keywords": ["prompts", "workflow", "git", "automation"],
  "repository": "https://github.com/elon-jang/claude-plugins",
  "license": "MIT",
  "homepage": "https://github.com/elon-jang/claude-plugins/tree/main/plugins/add-prompt"
}
```

### 4. Installation from Marketplace

**Add marketplace**:
```bash
/plugin marketplace add elon-jang/claude-plugins
```

**Install plugin**:
```bash
/plugin install add-prompt@ai-plugins
```

**Use plugin**:
```bash
/add-prompt
```

### 5. Marketplace Requirements

- **plugin.json**: Complete metadata including name, version, description, author, keywords
- **README.md**: User-facing documentation with usage examples
- **Command files**: Properly formatted with YAML frontmatter and markdown instructions
- **Keywords**: Searchable tags for plugin discovery
- **License**: MIT license recommended for open source plugins
