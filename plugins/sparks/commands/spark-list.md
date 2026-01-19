---
name: spark-list
description: List knowledge items by category with statistics
argument-hint: "[--category=<name>] [--stats] [--due]"
allowed-tools:
  - Glob
  - Read
  - Bash
---

# Spark List - Knowledge Inventory

List all knowledge items organized by category with optional statistics.

## Arguments

- `--category=<name>` - Show only specific category
- `--stats` - Include learning statistics (confidence, reviews, box)
- `--due` - Show only items due for review

## Workflow

### 0. Detect Repository

```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
```

### 1. Find All Knowledge Files

```bash
find {REPO_ROOT} -path "*/.sparks" -prune -o -name "*.md" -type f -print | grep -v README
```

### 2. Parse Each File

For each file:
- Extract YAML frontmatter
- Get: title, category, tags, confidence, review_count, last_reviewed

### 3. Load Progress (if --stats or --due)

```
Path: {REPO_ROOT}/.sparks/progress.json
```

### 4. Display List

**Basic List**:
```
📚 Sparks Knowledge Base

## Concepts (3 items)
- machine-learning-basics.md - Machine Learning Basics
- deep-learning-intro.md - Deep Learning Introduction
- design-patterns.md - Design Patterns Overview

## Insights (2 items)
- code-review-lessons.md - Code Review Lessons Learned
- debugging-mindset.md - The Debugging Mindset

## Skills (4 items)
- git-advanced.md - Advanced Git Techniques
- python-debugging.md - Python Debugging Tips
- vim-shortcuts.md - Essential Vim Shortcuts
- docker-basics.md - Docker Basics

## TIL (1 item)
- 2026-01-19-plugin-structure.md - Claude Plugin Structure

---
Total: 10 items across 4 categories
```

**With Stats (--stats)**:
```
📚 Sparks Knowledge Base (with stats)

## Concepts (3 items)
| File | Title | Confidence | Reviews | Box | Last Review |
|------|-------|------------|---------|-----|-------------|
| machine-learning-basics.md | Machine Learning Basics | ⭐⭐⭐⭐ | 5 | 3 | 2 days ago |
| deep-learning-intro.md | Deep Learning Introduction | ⭐⭐⭐ | 2 | 2 | 5 days ago |
| design-patterns.md | Design Patterns Overview | ⭐⭐ | 0 | 1 | Never |

## Insights (2 items)
...

---
📊 Summary:
- Total items: 10
- Average confidence: 3.2/5
- Items reviewed: 7
- Items due for review: 3
```

**Due Items Only (--due)**:
```
📅 Items Due for Review

1. 📌 Design Patterns Overview (concepts)
   Box 1 - Due: Today
   Last reviewed: Never

2. 📌 Deep Learning Introduction (concepts)
   Box 2 - Due: Yesterday
   Last reviewed: 5 days ago

3. 📌 Docker Basics (skills)
   Box 1 - Due: 2 days ago
   Last reviewed: 3 days ago

---
3 items due. Run `/spark-learn --mode=flashcard` to review.
```

**Single Category (--category=concepts)**:
```
📚 Category: Concepts

3 items:

1. machine-learning-basics.md
   Title: Machine Learning Basics
   Tags: ai, ml, neural-networks
   Created: 2026-01-15

2. deep-learning-intro.md
   Title: Deep Learning Introduction
   Tags: ai, ml, deep-learning
   Created: 2026-01-16

3. design-patterns.md
   Title: Design Patterns Overview
   Tags: software, architecture, patterns
   Created: 2026-01-17
```

## Examples

```bash
# List all items
/spark-list

# List with statistics
/spark-list --stats

# List only due items
/spark-list --due

# List specific category
/spark-list --category=skills

# Combine flags
/spark-list --category=concepts --stats
```

## Error Handling

- **No knowledge items**: "No knowledge items found. Run `/spark-add` to add your first item."
- **Invalid category**: "Category '{name}' not found. Available: concepts, insights, skills, til"
- **No progress file**: Create empty stats (all items in box 1)
