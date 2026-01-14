---
name: add-prompt
description: Add a new AI prompt to the repository and push to Github
argument-hint: ""
allowed-tools:
  - AskUserQuestion
  - Glob
  - Read
  - Write
  - Edit
  - Bash
---

# Add Prompt to Repository

Add a new AI prompt to the current Git repository, update README.md, and automatically commit and push to Github.

## Workflow

Execute the following steps in order:

### 0. Detect Repository Configuration

**Detect Git repository root**:
```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
```

If the command fails (not a Git repository):
- Display error: "Error: Not in a Git repository. Please run this command from within a Git repository."
- Stop execution

**Detect available categories**:
```bash
cd "$REPO_ROOT"
CATEGORIES=$(find . -maxdepth 1 -type d ! -name '.*' ! -name '_*' -exec basename {} \; | grep -v "^\\.$" | sort)
```

This finds all top-level directories (excluding hidden and underscore-prefixed directories).

If no directories found:
- Use default categories: ["general"]

**Detect current branch**:
```bash
CURRENT_BRANCH=$(git branch --show-current)
```

### 1. Collect Information

Use AskUserQuestion tool to gather all required information in a single call with 4 questions.

**IMPORTANT**: Dynamically build the category options from the detected categories in Step 0.

For each detected category directory, create an option:
```json
{
  "label": "{CategoryName}",
  "description": "Add to {category}/ directory"
}
```

Example question structure (with dynamically detected categories):
```json
{
  "questions": [
    {
      "question": "Which category should this prompt belong to?",
      "header": "Category",
      "multiSelect": false,
      "options": [
        // Dynamically generated from detected categories
        // Example if categories are: infrastructure, development, templates
        {
          "label": "infrastructure",
          "description": "Add to infrastructure/ directory"
        },
        {
          "label": "development",
          "description": "Add to development/ directory"
        },
        {
          "label": "templates",
          "description": "Add to templates/ directory"
        }
      ]
    },
    {
      "question": "What is the title of this prompt?",
      "header": "Title",
      "multiSelect": false,
      "options": [
        {
          "label": "Enter custom title",
          "description": "Type a descriptive title for the prompt"
        },
        {
          "label": "Skip",
          "description": "Not used"
        }
      ]
    },
    {
      "question": "Provide a one-line description for the README",
      "header": "Description",
      "multiSelect": false,
      "options": [
        {
          "label": "Enter custom description",
          "description": "Brief description (one line)"
        },
        {
          "label": "Skip",
          "description": "Not used"
        }
      ]
    },
    {
      "question": "Paste the full prompt content (markdown format)",
      "header": "Content",
      "multiSelect": false,
      "options": [
        {
          "label": "Enter custom content",
          "description": "Full markdown content of the prompt"
        },
        {
          "label": "Skip",
          "description": "Not used"
        }
      ]
    }
  ]
}
```

**Important**:
- Call AskUserQuestion once with all 4 questions
- User will select "Other" option to enter custom text for title, description, and content
- Extract answers from the response
- Category answer will be one of the detected directory names (lowercase)
- Title, Description, and Content will be user's custom input text

### 2. Generate Filename

Convert the title to kebab-case filename:
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters (keep only a-z, 0-9, hyphens)
- Ensure it ends with `.md`

Example: "AWS EC2 Management" → `aws-ec2-management.md`

### 3. Check for Duplicate Filenames

Use Glob to check if the file already exists in the target category folder:

```
Pattern: {category}/{filename}.md
```

If the file exists:
- Append `-2` to the filename
- If that exists, try `-3`, `-4`, etc.
- Continue until finding an available filename

Example:
- `aws-ec2-management.md` exists
- Try `aws-ec2-management-2.md`
- If that exists, try `aws-ec2-management-3.md`

### 4. Create Prompt File

Use Write to create the prompt file:

**Path**: `{REPO_ROOT}/{category}/{filename}.md`
**Content**: The prompt content provided by the user (exactly as entered)

Where `{REPO_ROOT}` is the Git repository root detected in Step 0.

### 5. Update README.md

Read the current README.md:

```
Path: {REPO_ROOT}/README.md
```

**Find the appropriate category section**:

Search for a section header matching the category. Try these patterns in order:
1. `## {Category}` (exact match, case-insensitive)
2. `## {Category} (...)` (with description in parentheses)
3. `### {Category}` (h3 header)

Example patterns for category "infrastructure":
- `## Infrastructure`
- `## infrastructure`
- `## Infrastructure (인프라 관리)`
- `### Infrastructure`

If no matching section found:
- Create a new section at the end of README:
  ```markdown
  ## {Category}

  - `{category}/{filename}.md` - {description}
  ```

**Add the new entry in alphabetical order** within that section:

**Format**: `` - `{category}/{filename}.md` - {description} ``

**Alphabetical sorting**:
- Compare filenames (not titles)
- Insert at the correct position to maintain alphabetical order
- Example ordering:
  ```
  - `infrastructure/aws-ec2-management.md` - ...
  - `infrastructure/tencent-vm-start.md` - ...
  - `infrastructure/tencent-vm-status.md` - ...
  ```

Use Edit to update README.md with the new entry inserted at the correct position.

### 6. Git Operations

Change to the repository directory and execute git commands:

```bash
cd {REPO_ROOT} && \
git add {category}/{filename}.md README.md && \
git commit -m "Add new prompt: {title}" && \
git push origin {CURRENT_BRANCH}
```

Where:
- `{REPO_ROOT}` is the Git repository root detected in Step 0
- `{CURRENT_BRANCH}` is the current branch detected in Step 0

**Important**:
- Use the actual title (not filename) in the commit message
- Include both the new prompt file and README.md in the commit
- Push to the current branch (not hardcoded main/master)

### 7. Error Handling

**If not in a Git repository** (Step 0):
- Display error: "Error: Not in a Git repository. Please run this command from within a Git repository."
- Stop execution

**If git push fails**:
- Display the error message to the user
- Inform that the file and README updates were created successfully
- Suggest manual push: `cd {REPO_ROOT} && git push origin {CURRENT_BRANCH}`
- Do NOT attempt to rollback the file creation

**If file creation fails**:
- Display error and stop execution
- Do not proceed to README update or git operations

**If no categories detected** (Step 0):
- Use "general" as the default category
- Create the directory if it doesn't exist

### 8. Success Message

After successful completion, display:

```
✅ Prompt added successfully!

Repository: {REPO_ROOT}
Created: {category}/{filename}.md
Updated: README.md
Committed: "Add new prompt: {title}"
Pushed: origin/{CURRENT_BRANCH}

The new prompt is now available in the repository.
```

## Examples

### Example 1: With Detected Categories

```
User runs from ~/my-prompts repository
Repository structure:
  infrastructure/
  development/
  templates/

User: /add-prompt

Detected categories: infrastructure, development, templates
Selected category: infrastructure
Title: AWS EC2 Management
Description: AWS EC2 instance start/stop/status commands
Content: [Full markdown content]

Result:
- Detected repo: ~/my-prompts
- Created: infrastructure/aws-ec2-management.md
- Updated README with alphabetically sorted entry
- Committed and pushed to current branch (main)
```

### Example 2: Auto-Create Section in README

```
User: /add-prompt

Category: templates (new section not in README)
Title: Project Template
Description: Standard project structure template
Content: [Full markdown content]

Result:
- Created: templates/project-template.md
- Added new "## Templates" section in README
- Committed and pushed
```

### Example 3: Duplicate Filename

```
User: /add-prompt

Category: infrastructure
Title: Tencent VM Start
[File infrastructure/tencent-vm-start.md already exists]

Result:
- Created: infrastructure/tencent-vm-start-2.md
- Updated README accordingly
- Committed and pushed
```

## Important Notes

- **Must run from within a Git repository** - Command will fail if not in a Git repository
- **Automatically detects repository root** using `git rev-parse --show-toplevel`
- **Automatically detects categories** from top-level directories
- **Automatically detects current Git branch** for pushing
- Maintain alphabetical sorting in README
- Category names are case-sensitive (use lowercase in directory names)
- Preserve existing README formatting
- Do NOT modify other sections of README
- Commit message format: "Add new prompt: {exact title}"
- If README section doesn't exist, creates it automatically

## Expected Repository Structure

The plugin works with any Git repository that has a category-based structure:

```
{repository}/
├── README.md              # Required: Will be updated with new entries
├── {category1}/          # Auto-detected category directories
│   ├── prompt1.md
│   └── prompt2.md
├── {category2}/
│   └── prompt3.md
└── {category3}/
    └── prompt4.md
```

Example structures:

**Structure 1: Simple categories**
```
my-prompts/
├── README.md
├── infrastructure/
├── development/
└── templates/
```

**Structure 2: Hierarchical**
```
ai-library/
├── README.md
├── prompts/
├── templates/
├── guides/
└── examples/
```

The plugin adapts to any directory structure automatically.
