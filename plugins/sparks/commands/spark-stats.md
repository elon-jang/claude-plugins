---
name: spark-stats
description: Display learning statistics dashboard with progress overview
argument-hint: ""
allowed-tools:
  - Glob
  - Read
  - Bash
---

# Learning Statistics Dashboard

Display comprehensive learning statistics including item counts, confidence distribution, review status, and due items.

## Workflow

### 0. Detect Repository Configuration

**Detect Git repository root**:
```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
```

If fails: "Error: Not in a Git repository."

**Check for Sparks repository**:
```bash
ls "$REPO_ROOT/.sparks/config.json" 2>/dev/null
```

If not found, show warning but continue with defaults.

### 1. Gather Knowledge Files

**Find all knowledge files**:
```bash
find "$REPO_ROOT" -type f -name "*.md" \
  -not -path "*/.git/*" \
  -not -path "*/.sparks/*" \
  -not -path "*/blog/*" \
  -not -name "README.md"
```

### 2. Parse Each Knowledge File

For each `.md` file found:

1. Read YAML frontmatter (between `---` markers)
2. Extract fields:
   - `category`: Category name
   - `confidence`: 1-5 scale (default: 3)
   - `review_count`: Number of reviews (default: 0)
   - `last_reviewed`: ISO date or null
   - `tags`: Array of tags
   - `created`: Creation date

### 3. Calculate Statistics

**Category Distribution**:
```
Count items per category:
- concepts: N items
- insights: N items
- skills: N items
- til: N items
```

**Confidence Distribution**:
```
Group by confidence level:
- Level 1 (Needs work): N items
- Level 2 (Learning): N items
- Level 3 (Understood): N items
- Level 4 (Confident): N items
- Level 5 (Mastered): N items
```

**Review Status**:
```
- Never reviewed: N items
- Reviewed 1-2 times: N items
- Reviewed 3-5 times: N items
- Reviewed 6+ times: N items
```

**Due for Review** (based on Leitner intervals):
```
Leitner intervals: [1, 3, 7, 14, 30] days

For each item:
- Get review_count (determines box: 0→box1, 1→box2, etc.)
- Get last_reviewed date
- Calculate days_since_review
- If days_since_review >= interval[box], item is due
```

**Tag Cloud** (top 10 most used tags):
```
Count tag occurrences across all items
Sort by frequency, show top 10
```

### 4. Display Dashboard

Output formatted statistics:

```
📊 Sparks Learning Dashboard
============================

📁 Repository: {REPO_ROOT}
📅 Generated: {current_date}

📚 Total Knowledge Items: {total_count}

┌─────────────────────────────────────┐
│ 📂 BY CATEGORY                      │
├─────────────────────────────────────┤
│ concepts   ████████░░░░░░  12 (30%) │
│ insights   ██████░░░░░░░░   8 (20%) │
│ skills     ██████████░░░░  15 (38%) │
│ til        ██░░░░░░░░░░░░   5 (12%) │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🎯 CONFIDENCE LEVELS                │
├─────────────────────────────────────┤
│ ⭐          Needs work     3 items  │
│ ⭐⭐        Learning       8 items  │
│ ⭐⭐⭐      Understood    15 items  │
│ ⭐⭐⭐⭐    Confident     10 items  │
│ ⭐⭐⭐⭐⭐  Mastered       4 items  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 📖 REVIEW STATUS                    │
├─────────────────────────────────────┤
│ Never reviewed:     12 items        │
│ Reviewed 1-2x:       8 items        │
│ Reviewed 3-5x:      15 items        │
│ Reviewed 6+x:        5 items        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ ⏰ DUE FOR REVIEW                   │
├─────────────────────────────────────┤
│ Overdue:            5 items         │
│ Due today:          3 items         │
│ Due this week:      8 items         │
└─────────────────────────────────────┘

🏷️ Top Tags: python (8), debugging (6), api (5), react (4), testing (3)

💡 Tips:
- Run `/spark-learn` to start reviewing due items
- Run `/spark-list --due` to see items due for review
```

### 5. Optional: Blog Statistics

If `blog/` directory exists:

```
┌─────────────────────────────────────┐
│ ✍️ BLOG POSTS                       │
├─────────────────────────────────────┤
│ Total posts:        15              │
│ Linked to knowledge: 8 (53%)        │
│ This month:          3              │
└─────────────────────────────────────┘
```

## Output Modes

### Default (Summary)
Shows the full dashboard above.

### Compact Mode (if terminal width < 80)
```
📊 Sparks Stats | 40 items | 5 due | 12 unreviewed
Categories: concepts(12) insights(8) skills(15) til(5)
Confidence: ⭐3 ⭐⭐8 ⭐⭐⭐15 ⭐⭐⭐⭐10 ⭐⭐⭐⭐⭐4
```

## Error Handling

- **Not in Git repository**: Stop with error
- **No knowledge files found**: Show "No knowledge items yet. Run /spark-add to get started!"
- **Missing frontmatter**: Skip file, count as "unparseable"
- **Invalid dates**: Treat as never reviewed

## Example

```
User: /spark-stats

📊 Sparks Learning Dashboard
============================

📁 Repository: /Users/user/my-sparks
📅 Generated: 2026-01-19

📚 Total Knowledge Items: 2

┌─────────────────────────────────────┐
│ 📂 BY CATEGORY                      │
├─────────────────────────────────────┤
│ insights   ██████████████   1 (50%) │
│ til        ██████████████   1 (50%) │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🎯 CONFIDENCE LEVELS                │
├─────────────────────────────────────┤
│ ⭐⭐⭐      Understood     2 items  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 📖 REVIEW STATUS                    │
├─────────────────────────────────────┤
│ Never reviewed:      2 items        │
└─────────────────────────────────────┘

⏰ Due for review: 2 items (all new items)

🏷️ Top Tags: 해외주식 (1), 증여 (1), 절세 (1)

💡 Run `/spark-learn` to start your first review session!
```
