---
name: shortcut-add
description: 단축키를 대화형으로 추가하고 README.md를 자동 업데이트합니다
argument-hint: ""
allowed-tools:
  - AskUserQuestion
  - Glob
  - Bash
  - Read
  - Write
  - Edit
---

# Add Shortcut

단축키를 대화형으로 추가하고 README.md를 자동 업데이트합니다.

## Workflow

Execute the following steps in order:

### 0. Detect Repository Configuration

**Detect Git repository root**:
```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
```

If the command fails (not a Git repository):
- Display error: "Error: Not in a Git repository. Please run `/shortcut:init` first."
- Stop execution

**Detect current branch**:
```bash
CURRENT_BRANCH=$(git branch --show-current)
```

**Detect existing apps**:
```bash
ls "$REPO_ROOT"/*_shortcuts.md 2>/dev/null | sed 's/_shortcuts.md$//' | xargs -n1 basename
```

### 1. Collect Information

Use AskUserQuestion to gather all required information:

**First AskUserQuestion call** (4 questions):

```json
{
  "questions": [
    {
      "question": "Which application is this shortcut for?",
      "header": "App",
      "multiSelect": false,
      "options": [
        {"label": "vscode", "description": "Visual Studio Code"},
        {"label": "chrome", "description": "Google Chrome"},
        {"label": "figma", "description": "Figma Design"},
        {"label": "Enter custom app", "description": "Type app name"}
      ]
    },
    {
      "question": "Which category does this shortcut belong to?",
      "header": "Category",
      "multiSelect": false,
      "options": [
        {"label": "Editing", "description": "Text editing, selection"},
        {"label": "Navigation", "description": "Moving around, jumping"},
        {"label": "View", "description": "UI, panels, zoom"},
        {"label": "Enter custom category", "description": "Type category name"}
      ]
    },
    {
      "question": "What is the keyboard shortcut? (e.g., cmd+d, ctrl+shift+p)",
      "header": "Shortcut",
      "multiSelect": false,
      "options": [
        {"label": "Enter shortcut", "description": "Type the keyboard shortcut"},
        {"label": "Skip", "description": "Not used"}
      ]
    },
    {
      "question": "What does this shortcut do?",
      "header": "Description",
      "multiSelect": false,
      "options": [
        {"label": "Enter description", "description": "Brief description of the action"},
        {"label": "Skip", "description": "Not used"}
      ]
    }
  ]
}
```

**Important**:
- If existing apps detected, dynamically add them to App options
- If existing categories found in the target app file, add them to Category options

### 2. Normalize Shortcut Notation

Convert shortcut to standard format:

| Input | Output |
|-------|--------|
| `cmd+d` | `Cmd+D` |
| `command+shift+p` | `Cmd+Shift+P` |
| `ctrl+alt+del` | `Ctrl+Alt+Del` |
| `option+shift+f` | `Opt+Shift+F` |

**Normalization rules**:
- `cmd`, `command` → `Cmd`
- `ctrl`, `control` → `Ctrl`
- `opt`, `option`, `alt` → `Opt`
- `shift` → `Shift`
- All letters uppercase
- Join with `+`

### 3. Check for Duplicates

Read target file `{REPO_ROOT}/{app}_shortcuts.md` if exists.

Search for the normalized shortcut in the table.

If duplicate found:
- Display error: "Error: Shortcut `{shortcut}` already exists for {app}."
- Show existing entry
- Stop execution

### 4. Add Shortcut to File

**If file doesn't exist**, create `{REPO_ROOT}/{app}_shortcuts.md`:

```markdown
# {App} Shortcuts

## {Category}

| Shortcut | Description |
|----------|-------------|
| {shortcut} | {description} |
```

**If file exists**, find or create the category section and add the row:

```markdown
| {shortcut} | {description} |
```

**Sorting**: Add entries alphabetically within each category.

### 5. Update README.md

**Scan all shortcut files**:
```bash
ls "$REPO_ROOT"/*_shortcuts.md
```

**For each file**:
1. Extract app name from filename
2. Count total shortcuts (table rows excluding header)
3. Get file modification date
4. Extract Top 5 shortcuts (first 5 from first category)

**Generate README.md content**:

```markdown
# My Shortcuts

애플리케이션 단축키 모음입니다.

## Summary

| App | Shortcuts | Last Updated |
|-----|-----------|--------------|
| [vscode](./vscode_shortcuts.md) | 25 | 2026-01-19 |
| [chrome](./chrome_shortcuts.md) | 12 | 2026-01-18 |

**Total**: 37 shortcuts across 2 apps

## Quick Reference

### vscode

| Shortcut | Description |
|----------|-------------|
| Cmd+D | Select next occurrence |
| Cmd+Shift+P | Command palette |
| Cmd+P | Quick open file |
| Cmd+B | Toggle sidebar |
| Cmd+` | Toggle terminal |

[View all vscode shortcuts →](./vscode_shortcuts.md)

### chrome

| Shortcut | Description |
|----------|-------------|
| Cmd+T | New tab |
| Cmd+W | Close tab |
| Cmd+L | Focus address bar |
| Cmd+Shift+T | Reopen closed tab |
| Cmd+Option+I | Developer tools |

[View all chrome shortcuts →](./chrome_shortcuts.md)
```

**Write to** `{REPO_ROOT}/README.md`

### 6. Git Operations

```bash
cd "$REPO_ROOT" && \
git add {app}_shortcuts.md README.md && \
git commit -m "Add shortcut: {app} - {shortcut}" && \
git push origin "$CURRENT_BRANCH"
```

### 7. Success Message

```
✅ Shortcut added successfully!

App: {app}
Category: {category}
Shortcut: {shortcut}
Description: {description}

Files updated:
- {app}_shortcuts.md
- README.md

Committed and pushed to origin/{branch}
```

## Error Handling

- **Not in Git repository**: Display error, suggest `/shortcut:init`
- **Duplicate shortcut**: Display existing entry, stop execution
- **Git push fails**: Show error, files are saved locally
- **File permission error**: Display error, stop execution

## Example

```
User: /shortcut:add

App: vscode
Category: Editing
Shortcut: cmd+d
Description: Select next occurrence

Result:
- Added to vscode_shortcuts.md
- Updated README.md (25 shortcuts, Top 5 shown)
- Committed: "Add shortcut: vscode - Cmd+D"
- Pushed to origin/main
```
