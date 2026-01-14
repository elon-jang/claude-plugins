# add-prompt Plugin

Claude Code plugin for adding new AI prompts to the prompts repository and automatically pushing to Github.

## Features

- Interactive prompt creation workflow
- Automatic file naming (title → kebab-case)
- Alphabetically sorted README updates
- Automatic git commit and push
- Duplicate filename handling

## Installation

### Local Development

```bash
cc --plugin-dir ~/elon/ai/claude-code/add-prompt
```

### Project Installation

Copy this plugin to your project's `.claude-plugin/` directory:

```bash
cp -r ~/elon/ai/claude-code/add-prompt /path/to/prompts/.claude-plugin/
```

## Usage

Run the command in the prompts repository:

```
/add-prompt
```

The plugin will guide you through:

1. **Category selection**: Choose `infrastructure` or `development`
2. **Prompt title**: Enter a descriptive title
3. **Prompt description**: One-line description for README
4. **Prompt content**: Full markdown content

The plugin will then:
- Create `.md` file in the appropriate category folder
- Update README.md with alphabetically sorted entry
- Commit changes with message: `Add new prompt: {title}`
- Push to Github

## Requirements

- Git repository initialized
- Remote `origin` configured
- Working in `/Users/elon/elon/ai/prompts` repository

## Error Handling

- **Duplicate filename**: Automatically appends `-2`, `-3`, etc.
- **Git push failure**: Shows error message but keeps created files

## Example

```
User: /add-prompt
Claude: [Asks for category]
User: infrastructure
Claude: [Asks for title]
User: AWS EC2 Management
Claude: [Asks for description]
User: AWS EC2 instance start/stop/status commands
Claude: [Asks for content]
User: [Pastes full prompt content]
Claude: ✅ Created infrastructure/aws-ec2-management.md
         ✅ Updated README.md
         ✅ Committed and pushed to Github
```

## Commands

- `/add-prompt` - Add new prompt to repository

## License

MIT
