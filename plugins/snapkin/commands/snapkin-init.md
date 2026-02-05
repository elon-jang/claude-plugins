---
name: snapkin-init
description: Generate the 2 Snapkin base documents (Napkin Stack) at project root
argument-hint: ""
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - AskUserQuestion
---

# Snapkin Init

Initialize the 2 Napkin Stack documents for a project.

## Placeholders

Templates use the following placeholders. Only these are valid — no other `{{...}}` patterns exist in templates.

| Placeholder | Source | Fallback |
|-------------|--------|----------|
| `{{PROJECT_NAME}}` | Package file `name` field, or directory name | Directory name |
| `{{LANGUAGE}}` | Detect from file extensions (`.ts`→TypeScript, `.py`→Python, etc.) | `Unknown` |
| `{{INSTALL_COMMAND}}` | Package scripts (`npm install`, `pip install -e .`, `cargo build`, etc.) | `# TODO: add install command` |
| `{{RUN_COMMAND}}` | Package scripts (`npm start`, `python main.py`, `cargo run`, etc.) | `# TODO: add run command` |
| `{{TEST_COMMAND}}` | Package scripts (`npm test`, `pytest`, `cargo test`, etc.) | `# TODO: add test command` |
| `{{FILE_STRUCTURE}}` | `ls` output of project root, formatted as tree | Raw `ls` output |
| `{{DATE}}` | Current date | `YYYY-MM-DD` format |

## Execution Steps

### Step 1: Git Check

Check if git is initialized in the project root. Git is a prerequisite for the `/snapkin:snapkin` commit phase, so verify it first.

If git is NOT initialized, ask:
```
AskUserQuestion(
    questions=[{
        "question": "Git is not initialized. Initialize a git repository? (Required for /snapkin:snapkin commit phase)",
        "header": "Git init",
        "multiSelect": false,
        "options": [
            {"label": "Yes", "description": "Run git init now"},
            {"label": "No", "description": "Skip — /snapkin:snapkin commit will be unavailable"}
        ]
    }]
)
```

If "Yes", run `git init` in the project root.

**`.gitignore` check**: After git init (or if git already existed), check if `.gitignore` exists. If not, ask:
```
AskUserQuestion(
    questions=[{
        "question": ".gitignore not found. Create a default one?",
        "header": ".gitignore",
        "multiSelect": false,
        "options": [
            {"label": "Yes", "description": "Generate .gitignore based on detected project language"},
            {"label": "No", "description": "Skip"}
        ]
    }]
)
```

If "Yes", generate a `.gitignore` appropriate for the detected language (Node → `node_modules/`, Python → `__pycache__/`, etc.). Always include these common entries:
```
.env
.DS_Store
*.log
```

### Step 2: Check for Existing Files

Check if the 2 Napkin Stack files already exist at the project root:
- `CLAUDE.md`
- `LESSONS.md`

**If both files exist**, offer a bulk action first:
```
AskUserQuestion(
    questions=[{
        "question": "Both Napkin Stack files already exist. What should I do?",
        "header": "Re-init",
        "multiSelect": false,
        "options": [
            {"label": "Skip all", "description": "Keep all existing files unchanged"},
            {"label": "Overwrite all", "description": "Replace all files with fresh templates"},
            {"label": "Choose per file", "description": "Decide individually for each file"},
            {"label": "Cancel", "description": "Abort initialization entirely"}
        ]
    }]
)
```

- **Skip all** → mark both as skipped, proceed to early exit (Step 2a)
- **Overwrite all** → mark both for overwrite, proceed to Step 3
- **Choose per file** → fall through to per-file questions below
- **Cancel** → abort immediately

**If SOME files exist** (or user chose "Choose per file"), batch existing files into a single `AskUserQuestion` call.

For `CLAUDE.md`:
```
{
    "question": "CLAUDE.md already exists. What should I do?",
    "header": "CLAUDE.md",
    "multiSelect": false,
    "options": [
        {"label": "Skip", "description": "Keep existing file unchanged"},
        {"label": "Merge", "description": "Keep existing content and add missing template sections"},
        {"label": "Overwrite", "description": "Replace with Snapkin template"},
        {"label": "Cancel", "description": "Abort initialization entirely"}
    ]
}
```

For `LESSONS.md`:
```
{
    "question": "LESSONS.md already exists. What should I do?",
    "header": "LESSONS.md",
    "multiSelect": false,
    "options": [
        {"label": "Skip", "description": "Keep existing file unchanged"},
        {"label": "Overwrite", "description": "Replace with Snapkin template"},
        {"label": "Cancel", "description": "Abort initialization entirely"}
    ]
}
```

If **any** answer is "Cancel", abort the entire initialization immediately.

**Merge behavior** (CLAUDE.md only):
1. Read existing `CLAUDE.md` and identify its section headers (`## ...`)
2. Read the template and identify template section headers
3. Append any template sections that do NOT already exist in the file
4. Preserve all existing content unchanged
5. Always ensure the `<!-- SNAPKIN:SESSION_CONTEXT_START -->` and `<!-- SNAPKIN:SESSION_CONTEXT_END -->` markers exist

#### Step 2a: Early Exit Check

If **no files need to be created, overwritten, or merged** (all skipped):

```markdown
## Snapkin Init Complete

All files already exist — no changes made.

Next: Start working, then run `/snapkin:snapkin` to sync your session.
```

Append git status line if applicable (see Step 6 rules), then **stop execution**. Do NOT proceed to Steps 3–6.

### Step 3: Analyze Project Context

> Only runs if at least one file needs to be generated/overwritten/merged.

Gather project information to customize templates:

1. **Package metadata**: Read `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, or similar
2. **Language**: Detect primary language from file extensions
3. **File structure**: Run `ls` to understand top-level layout

Extract values for all placeholders defined in the **Placeholders** table above. Use the **Fallback** column for any value that cannot be detected.

### Step 4: Resolve Template Paths

Templates are located relative to **this command file's directory**:

```
<this-file>        = commands/snapkin-init.md
<plugin-root>      = ../                        (parent of commands/)
<templates-dir>    = ../skills/snapkin-workflow/templates/
```

Resolve the absolute path by finding this plugin's installation directory. Search in order:
1. Current working directory: `./skills/snapkin-workflow/templates/`
2. Plugin cache: `~/.claude/plugins/cache/snapkin/snapkin/*/skills/snapkin-workflow/templates/`

Template files:
- `CLAUDE.template.md`
- `LESSONS.template.md`

### Step 5: Generate Files

For each file that should be created (not skipped):
1. Read the corresponding template
2. Replace all `{{PLACEHOLDER}}` values with detected project data
3. Write the file to the project root

### Step 6: Validate & Summary

**Validate**: Check for unresolved placeholders:
```
Grep for '{{' in all generated files
```
If any `{{...}}` patterns remain, display a warning listing each file and the unresolved placeholders.

**Summary**:
```markdown
## Snapkin Init Complete

| File | Status |
|------|--------|
| CLAUDE.md | Created / Skipped / Overwritten / Merged |
| LESSONS.md | Created / Skipped / Overwritten |

Next: Start working, then run `/snapkin:snapkin` to sync your session.
```

**Git status lines** (append to summary as applicable):
- Git initialized this run → `Git repository initialized.`
- Git not found, user declined → `Warning: Git not initialized. /snapkin:snapkin commit phase will not work.`
- `.gitignore` created → `.gitignore created.`

## Important Notes

- Templates are starting points — agents will refine these documents over time
- Session Context section in CLAUDE.md will be fully rewritten on each `/snapkin:snapkin` run
- Never include actual secret values in any generated file
- All template placeholders must be listed in the Placeholders table — no undocumented placeholders allowed
