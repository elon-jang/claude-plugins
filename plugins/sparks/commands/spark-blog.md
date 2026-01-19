---
name: spark-blog
description: Save blog post to the repository and push to Github
argument-hint: ""
allowed-tools:
  - AskUserQuestion
  - Glob
  - Read
  - Write
  - Edit
  - Bash
---

# Add Blog Post to Sparks Repository

Save a blog post (original markdown) to the `blog/` directory, update README.md, and push to Github.

## Workflow

### 0. Detect Repository Configuration

**Detect Git repository root**:
```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
```

If fails: "Error: Not in a Git repository."

**Detect current branch**:
```bash
CURRENT_BRANCH=$(git branch --show-current)
```

**Ensure blog directory exists**:
```bash
mkdir -p "$REPO_ROOT/blog"
```

### 1. Collect Blog Information

Use AskUserQuestion:

```json
{
  "questions": [
    {
      "question": "What is the title of this blog post?",
      "header": "Title",
      "multiSelect": false,
      "options": [
        {"label": "Enter title", "description": "Blog post title"},
        {"label": "Skip", "description": "Not used"}
      ]
    },
    {
      "question": "Enter tags (comma-separated, optional)",
      "header": "Tags",
      "multiSelect": false,
      "options": [
        {"label": "Enter tags", "description": "Comma-separated tags"},
        {"label": "Skip", "description": "No tags"}
      ]
    }
  ]
}
```

### 2. Collect Blog Content

```json
{
  "questions": [
    {
      "question": "Enter the blog post content (markdown)",
      "header": "Content",
      "multiSelect": false,
      "options": [
        {"label": "Enter content", "description": "Full blog post in markdown"},
        {"label": "Skip", "description": "Not used"}
      ]
    }
  ]
}
```

### 3. Generate Filename

**Date**: Today's date in `YYYY-MM-DD` format

**Filename**: `{date}-{title-in-kebab-case}.md`
- Convert title to lowercase
- Replace spaces with hyphens
- Remove special characters (keep only a-z, 0-9, hyphens, Korean characters)

Example: "My First Post" → `2026-01-19-my-first-post.md`

### 4. Check for Duplicate

Use Glob: `blog/{date}-*.md`

If duplicate date+title exists, append `-2`, `-3`, etc.

### 5. Create Blog File

**Path**: `{REPO_ROOT}/blog/{filename}`

**Content**: Save as-is (user's original markdown)

If user provided tags, optionally prepend minimal frontmatter:
```yaml
---
title: "{title}"
date: "{date}"
tags: [{tags}]
---

{content}
```

Otherwise, just save the content with a `# {title}` header.

### 6. Update README.md

Find or create Blog section in README.md:

**Search patterns**:
1. `## Blog`
2. `### Blog`
3. `<!-- spark-index:blog -->`

**Add entry** (newest first):
```markdown
- [{date}] [{title}]({blog/filename})
```

### 7. Git Operations

```bash
cd {REPO_ROOT} && \
git add blog/{filename} README.md && \
git commit -m "Add blog: {title}" && \
git push origin {CURRENT_BRANCH}
```

### 8. Success Message

```
✅ Blog post saved!

Repository: {REPO_ROOT}
Created: blog/{filename}
Title: {title}

💡 To create a knowledge item from this blog, run:
   /spark-add (select "From blog post" as source)
```

## Error Handling

- **Not in Git repository**: Stop with error
- **Git push fails**: Show error, suggest manual push
- **Empty content**: Stop with error

## Example

```
User: /spark-blog

Title: Understanding React Hooks
Tags: react, hooks, frontend
Content:
# Understanding React Hooks

React Hooks are functions that let you use state...
(full content)

Result:
- Created: blog/2026-01-19-understanding-react-hooks.md
- Updated README.md
- Committed and pushed
```
