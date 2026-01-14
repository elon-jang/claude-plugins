# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Claude Code plugin that automates adding new AI prompts to the prompts repository (`/Users/elon/elon/ai/prompts`). The plugin handles interactive prompt collection, file creation, README updates, and automatic git commit/push operations.

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

**Target Repository**: All operations execute against `/Users/elon/elon/ai/prompts` (not this plugin repo)

## Command Workflow

The `/add-prompt` command follows this sequence:

1. **Single AskUserQuestion call** with 4 questions (category, title, description, content)
2. **Filename generation**: Convert title to kebab-case (e.g., "AWS EC2" → `aws-ec2-management.md`)
3. **Duplicate handling**: Check for existing files, append `-2`, `-3`, etc. if needed
4. **File creation**: Write prompt to `/Users/elon/elon/ai/prompts/{category}/{filename}.md`
5. **README update**: Insert alphabetically sorted entry in appropriate category section
6. **Git operations**: `git add`, `git commit -m "Add new prompt: {title}"`, `git push`

**Critical Implementation Details**:
- AskUserQuestion must collect all 4 inputs in one call (not separate calls)
- README entries must be alphabetically sorted by filename (not title)
- Category is "Infrastructure" or "Development" (user input), but paths use lowercase
- Exact commit message format: `"Add new prompt: {title}"` (uses title, not filename)
- Git commands must cd to `/Users/elon/elon/ai/prompts` first

## Testing the Plugin

**Local Development**:
```bash
# Test plugin loading
cc --plugin-dir ~/elon/ai/claude-code/add-prompt

# Inside Claude Code session
/add-prompt
```

**Integration Testing**:
- Test with duplicate filenames (should append `-2`)
- Test README alphabetical insertion
- Test both infrastructure and development categories
- Test git push failures (graceful error handling)

## Plugin Development Notes

**Allowed Tools** (defined in command frontmatter):
- `AskUserQuestion` - Interactive user input collection
- `Glob` - File existence checks
- `Read` - Reading README.md for updates
- `Write` - Creating new prompt files
- `Edit` - Updating README.md
- `Bash` - Git operations

**Key Constraints**:
- Plugin operates on a different repository (`/Users/elon/elon/ai/prompts`)
- Must preserve existing README formatting
- Must maintain alphabetical order in README
- Git push failures should not rollback file creation

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
  "name": "elon-hub",
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
/plugin install add-prompt@elon-hub
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
