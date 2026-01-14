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

Add a new AI prompt to the prompts repository (`/Users/elon/elon/ai/prompts`), update README.md, and automatically commit and push to Github.

## Workflow

Execute the following steps in order:

### 1. Collect Information

Use AskUserQuestion tool to gather all required information in a single call with 4 questions:

```json
{
  "questions": [
    {
      "question": "Which category should this prompt belong to?",
      "header": "Category",
      "multiSelect": false,
      "options": [
        {
          "label": "Infrastructure",
          "description": "Infrastructure management (VM, cloud, servers)"
        },
        {
          "label": "Development",
          "description": "Development workflows (SPEC, code review, testing)"
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
- Category answer will be "Infrastructure" or "Development"
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

**Path**: `/Users/elon/elon/ai/prompts/{category}/{filename}.md`
**Content**: The prompt content provided by the user (exactly as entered)

### 5. Update README.md

Read the current README.md:

```
Path: /Users/elon/elon/ai/prompts/README.md
```

Find the appropriate category section:
- For "Infrastructure": Find the `## Infrastructure (인프라 관리)` section
- For "Development": Find the `## Development (개발)` section

Add the new entry in **alphabetical order** within that section:

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

Change to the prompts repository directory and execute git commands:

```bash
cd /Users/elon/elon/ai/prompts && \
git add {category}/{filename}.md README.md && \
git commit -m "Add new prompt: {title}" && \
git push
```

**Important**:
- Use the actual title (not filename) in the commit message
- Include both the new prompt file and README.md in the commit

### 7. Error Handling

**If git push fails**:
- Display the error message to the user
- Inform that the file and README updates were created successfully
- Suggest manual push: `cd /Users/elon/elon/ai/prompts && git push`
- Do NOT attempt to rollback the file creation

**If file creation fails**:
- Display error and stop execution
- Do not proceed to README update or git operations

### 8. Success Message

After successful completion, display:

```
✅ Prompt added successfully!

Created: {category}/{filename}.md
Updated: README.md
Committed: "Add new prompt: {title}"
Pushed: origin/main

The new prompt is now available in the repository.
```

## Examples

### Example 1: Infrastructure Prompt

```
User: /add-prompt

Category: Infrastructure
Title: AWS EC2 Management
Description: AWS EC2 instance start/stop/status commands
Content: [Full markdown content]

Result:
- Created: infrastructure/aws-ec2-management.md
- Updated README with alphabetically sorted entry
- Committed and pushed
```

### Example 2: Development Prompt

```
User: /add-prompt

Category: Development
Title: Code Review Checklist
Description: Comprehensive code review guidelines
Content: [Full markdown content]

Result:
- Created: development/code-review-checklist.md
- Updated README with alphabetically sorted entry
- Committed and pushed
```

### Example 3: Duplicate Filename

```
User: /add-prompt

Category: Infrastructure
Title: Tencent VM Start
[File infrastructure/tencent-vm-start.md already exists]

Result:
- Created: infrastructure/tencent-vm-start-2.md
- Updated README accordingly
- Committed and pushed
```

## Important Notes

- Always work in the `/Users/elon/elon/ai/prompts` directory
- Maintain alphabetical sorting in README
- Use exact category names: "infrastructure" or "development" (lowercase in paths)
- Preserve existing README formatting
- Do NOT modify other sections of README
- Commit message format: "Add new prompt: {exact title}"

## Repository Structure Reference

```
/Users/elon/elon/ai/prompts/
├── README.md
├── CLAUDE.md
├── infrastructure/
│   ├── tencent-vm-start.md
│   ├── tencent-vm-stop.md
│   ├── tencent-vm-status.md
│   └── tencent-vm-manage.md
└── development/
    ├── spec-interview.md
    └── plan-mode-setting.md
```
