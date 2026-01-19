---
name: spark-search
description: Search stored knowledge by keyword, tag, or category
argument-hint: "<keyword> [--tag=<tag>] [--category=<cat>]"
allowed-tools:
  - Glob
  - Read
  - Bash
---

# Spark Search - Knowledge Search

Search through stored knowledge items by keyword, tag, or category.

## Arguments

- `<keyword>` - Search term (searches title, content, tags)
- `--tag=<tag>` - Filter by specific tag
- `--category=<cat>` - Filter by category (concepts, insights, skills, til)

## Workflow

### 0. Detect Repository

```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
```

### 1. Parse Search Arguments

Extract:
- `keyword` - main search term
- `tag` - tag filter (optional)
- `category` - category filter (optional)

### 2. Find Knowledge Files

**If category specified**:
```bash
find {REPO_ROOT}/{category} -name "*.md" -type f | grep -v README
```

**If no category**:
```bash
find {REPO_ROOT} -path "*/.sparks" -prune -o -name "*.md" -type f -print | grep -v README
```

### 3. Search Each File

For each markdown file:

1. **Read file content**
2. **Parse YAML frontmatter**: Extract title, tags, category
3. **Match criteria**:
   - Keyword: Check if keyword appears in title, content, or tags (case-insensitive)
   - Tag filter: Check if tag exists in tags array
   - Category filter: Check if file is in category directory

### 4. Rank Results

**Scoring**:
- Title match: +10 points
- Tag match: +5 points per matching tag
- Content match: +1 point per occurrence (max 10)

Sort by score descending.

### 5. Display Results

```
🔍 Search Results for "{keyword}"

Found {count} items:

1. 📌 {title} ({category})
   Tags: {tags}
   Confidence: {confidence}/5 | Reviews: {review_count}
   Path: {category}/{filename}.md
   Match: {match_reason}

2. 📌 {title} ({category})
   ...

---
Use `/spark-learn --category={category}` to study these topics.
```

**If no results**:
```
🔍 No results found for "{keyword}"

Suggestions:
- Try different keywords
- Check spelling
- Use --tag or --category to filter
- Run `/spark-list` to see all items
```

## Examples

### Search by Keyword
```
/spark-search machine learning

🔍 Search Results for "machine learning"

Found 3 items:

1. 📌 Machine Learning Basics (concepts)
   Tags: ai, ml, neural-networks
   Confidence: 4/5 | Reviews: 5
   Path: concepts/machine-learning-basics.md
   Match: Title, Tags

2. 📌 Deep Learning Introduction (concepts)
   Tags: ai, ml, deep-learning
   Confidence: 3/5 | Reviews: 2
   Path: concepts/deep-learning-intro.md
   Match: Tags
```

### Search by Tag
```
/spark-search --tag=python

🔍 Search Results for tag "python"

Found 5 items:
...
```

### Search with Multiple Filters
```
/spark-search debugging --category=skills --tag=python

🔍 Search Results for "debugging" in skills (tag: python)

Found 2 items:
...
```

## Error Handling

- **Not in Git repository**: Show error message
- **No search term**: Show usage help
- **Invalid category**: Show available categories
