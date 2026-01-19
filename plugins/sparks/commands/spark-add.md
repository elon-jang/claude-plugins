---
name: spark-add
description: Add knowledge/insight to the repository and push to Github
argument-hint: ""
allowed-tools:
  - AskUserQuestion
  - Glob
  - Read
  - Write
  - Edit
  - Bash
---

# Add Knowledge to Sparks Repository

Add a new knowledge item to the current Git repository, auto-generate Q&A, update README.md, and automatically commit and push to Github.

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

Default categories if none found: `["concepts", "insights", "skills", "til"]`

**Detect current branch**:
```bash
CURRENT_BRANCH=$(git branch --show-current)
```

### 1. Collect Information (First Call)

Use AskUserQuestion to gather basic information (4 questions max):

```json
{
  "questions": [
    {
      "question": "Which category should this knowledge belong to?",
      "header": "Category",
      "multiSelect": false,
      "options": [
        {"label": "concepts", "description": "이론, 원리, 개념"},
        {"label": "insights", "description": "경험에서 얻은 깨달음"},
        {"label": "skills", "description": "실용 기술, How-to"},
        {"label": "til", "description": "Today I Learned (오늘 배운 것)"}
      ]
    },
    {
      "question": "What is the title of this knowledge?",
      "header": "Title",
      "multiSelect": false,
      "options": [
        {"label": "Enter custom title", "description": "Type a descriptive title"},
        {"label": "Skip", "description": "Not used"}
      ]
    },
    {
      "question": "Enter tags (comma-separated, e.g., python, debugging, api)",
      "header": "Tags",
      "multiSelect": false,
      "options": [
        {"label": "Enter custom tags", "description": "Comma-separated tags"},
        {"label": "Skip", "description": "No tags"}
      ]
    },
    {
      "question": "What is the source of this knowledge? (optional)",
      "header": "Source",
      "multiSelect": false,
      "options": [
        {"label": "Enter source", "description": "Book, course, experience, etc."},
        {"label": "Skip", "description": "No source"}
      ]
    }
  ]
}
```

### 2. Collect Content (Second Call)

```json
{
  "questions": [
    {
      "question": "Enter the main content/summary of this knowledge",
      "header": "Content",
      "multiSelect": false,
      "options": [
        {"label": "Enter content", "description": "Main knowledge content"},
        {"label": "Skip", "description": "Not used"}
      ]
    },
    {
      "question": "Enter key points (one per line, or comma-separated)",
      "header": "Key Points",
      "multiSelect": false,
      "options": [
        {"label": "Enter key points", "description": "Important takeaways"},
        {"label": "Skip", "description": "No key points"}
      ]
    }
  ]
}
```

### 3. Auto-Generate Q&A

Based on the content and key points, Claude generates 2-3 Q&A pairs:

**Q&A Generation Guidelines**:
- Generate questions that test understanding, not just recall
- Include "Why" and "How" questions
- Make answers concise but complete

**Confirm with user**:
```json
{
  "questions": [
    {
      "question": "I generated these Q&A pairs for flashcard learning. Are they okay?\n\n{generated_qa}\n\nSelect 'Accept' or provide your own.",
      "header": "Q&A Confirm",
      "multiSelect": false,
      "options": [
        {"label": "Accept generated Q&A", "description": "Use the auto-generated questions"},
        {"label": "Enter custom Q&A", "description": "Provide your own Q&A pairs"}
      ]
    }
  ]
}
```

### 4. Generate Filename and UUID

**UUID**: Generate a unique identifier (use timestamp-based format)
```
Format: {timestamp}-{random} e.g., 20260119-a1b2c3
```

**Filename**: Convert title to kebab-case
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters (keep only a-z, 0-9, hyphens)
- Ensure it ends with `.md`

Example: "Machine Learning Basics" → `machine-learning-basics.md`

### 5. Check for Duplicate Filenames

Use Glob to check if file exists:
```
Pattern: {category}/{filename}.md
```

If exists, append `-2`, `-3`, etc.

### 6. Create Knowledge File

**Path**: `{REPO_ROOT}/{category}/{filename}.md`

**Content Template**:
```markdown
---
id: "{uuid}"
title: "{title}"
category: "{category}"
tags: [{tags_array}]
created: "{iso_timestamp}"
source: "{source}"
confidence: 3
connections: []
review_count: 0
last_reviewed: null
---

# {title}

## Summary

{content}

## Key Points

{key_points_as_bullets}

## Questions

{qa_pairs}

## My Understanding

<!-- Add your own understanding here -->
```

### 7. Update README.md

Read `{REPO_ROOT}/README.md` and find the category section.

**Section patterns to search**:
1. `## {Category}` (exact match)
2. `### {Category}`
3. `<!-- spark-index:{category} -->`

**Add entry in alphabetical order**:
```markdown
- `{category}/{filename}.md` - {title}
```

If section not found, create it.

### 8. Git Operations

```bash
cd {REPO_ROOT} && \
git add {category}/{filename}.md README.md && \
git commit -m "Add knowledge: {title}" && \
git push origin {CURRENT_BRANCH}
```

### 9. Success Message

```
✅ Knowledge added successfully!

Repository: {REPO_ROOT}
Created: {category}/{filename}.md
Title: {title}
Tags: {tags}
Q&A pairs: {count}

Ready for learning with /spark-learn
```

## Error Handling

- **Not in Git repository**: Stop with error message
- **Git push fails**: Show error, suggest manual push
- **File creation fails**: Stop execution
- **No categories**: Use default categories and create directories

## Example

```
User: /spark-add

Category: insights
Title: Code Review Best Practices
Tags: code-review, collaboration, quality
Source: Team experience
Content: Effective code review improves code quality and knowledge sharing...
Key Points:
- Review logic, not style
- Ask questions instead of making demands
- Limit review size to 400 lines

Generated Q&A:
- Q: Why should you ask questions instead of making demands in code review?
- A: Questions encourage discussion and learning, while demands can create defensiveness.

Result:
- Created: insights/code-review-best-practices.md
- Updated README.md
- Committed and pushed
```
