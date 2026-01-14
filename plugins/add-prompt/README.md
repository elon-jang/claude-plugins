# add-prompt Plugin

Claude Code plugin for adding new AI prompts to any Git repository and automatically pushing to Github.

## Features

- **Repository-agnostic**: Works with any Git repository
- **Auto-detection**: Automatically detects repository root, categories, and current branch
- **Interactive workflow**: Guided prompt creation with category selection
- **Smart file naming**: Automatic kebab-case conversion with duplicate handling
- **README management**: Alphabetically sorted updates with auto-section creation
- **Git automation**: Automatic commit and push to current branch
- **Flexible structure**: Adapts to any directory structure and README format

## Installation

### From Marketplace (Recommended)

```bash
# Add marketplace
/plugin marketplace add elon-jang/claude-plugins

# Install plugin
/plugin install add-prompt@ai-plugins
```

### Local Development

```bash
cc --plugin-dir ~/elon/ai/claude-code/claude-plugins/plugins/add-prompt
```

## Usage

Navigate to any Git repository with category directories and run:

```
/add-prompt
```

The plugin will:
1. **Auto-detect** your repository structure and available categories
2. **Guide you** through an interactive workflow:
   - **Category selection**: Choose from detected categories
   - **Prompt title**: Enter a descriptive title
   - **Prompt description**: One-line description for README
   - **Prompt content**: Full markdown content
3. **Automatically**:
   - Create `.md` file in the selected category folder
   - Update README.md with alphabetically sorted entry
   - Commit changes with message: `Add new prompt: {title}`
   - Push to your current Git branch

## Requirements

- **Git repository**: Must be run from within a Git repository
- **README.md**: Repository should have a README.md file
- **Category directories**: At least one top-level directory for organizing prompts
- **Remote configured**: Git remote `origin` for pushing

## Error Handling

- **Not in Git repository**: Fails with clear error message
- **Duplicate filename**: Automatically appends `-2`, `-3`, etc.
- **Missing README section**: Automatically creates new section
- **Git push failure**: Shows error message but keeps created files

## Example

```bash
# Navigate to your prompts repository
cd ~/my-prompts

# Repository structure:
#   infrastructure/
#   development/
#   templates/

# Run the plugin
cc
> /add-prompt

# Plugin auto-detects:
#   - Repository: ~/my-prompts
#   - Categories: infrastructure, development, templates
#   - Current branch: main

# Interactive workflow:
Claude: [Shows detected categories]
User: Selects "infrastructure"
User: Title: "AWS EC2 Management"
User: Description: "AWS EC2 instance start/stop/status commands"
User: Content: [Pastes full prompt content]

Claude: ✅ Prompt added successfully!
        Repository: ~/my-prompts
        Created: infrastructure/aws-ec2-management.md
        Updated: README.md
        Committed: "Add new prompt: AWS EC2 Management"
        Pushed: origin/main
```

## Commands

- `/add-prompt` - Add new prompt to repository

## License

MIT
