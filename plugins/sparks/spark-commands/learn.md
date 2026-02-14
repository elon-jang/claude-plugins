# Spark Learn - Interactive Knowledge Learning

Start an interactive learning session using one of three modes: Socratic dialogue, Flashcard quiz, or Connection exploration.

## Options

- `--mode=socratic` - Socratic dialogue (Why/How questions)
- `--mode=flashcard` - Flashcard quiz (Leitner 5-box system)
- `--mode=connect` - Connection exploration (relate knowledge items)
- `--category=<name>` - Filter by category (concepts, insights, skills, til)
- `--all` - Include all items regardless of due date

If no mode specified, prompt user to select.

## Workflow

### 0. Detect Repository and Parse Arguments

```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
```

Parse command arguments for mode and category.

### 1. Select Learning Mode (if not specified)

```json
{
  "questions": [
    {
      "question": "Which learning mode would you like to use?",
      "header": "Learning Mode",
      "multiSelect": false,
      "options": [
        {"label": "Socratic", "description": "Claude asks Why/How questions to deepen understanding"},
        {"label": "Flashcard", "description": "Q&A quiz with spaced repetition (Leitner box)"},
        {"label": "Connect", "description": "Explore relationships between knowledge items"}
      ]
    }
  ]
}
```

### 2. Load Knowledge Items

**Find all knowledge files**:
```bash
find {REPO_ROOT}/{category} -name "*.md" -type f 2>/dev/null | grep -v README
```

**Read and parse each file**:
- Extract YAML frontmatter (id, title, category, tags, confidence, review_count, last_reviewed)
- Extract Questions section for flashcard mode

**Load progress file** (if exists):
```
Path: {REPO_ROOT}/.sparks/progress.json
```

---

## Mode: Socratic Dialogue

### Socratic Workflow

1. **Select item**: Choose item with low confidence or not recently reviewed
2. **Display context**: Show title and summary
3. **Progressive questioning**:

**Level 1 (Basic Understanding)**:
```json
{
  "questions": [
    {
      "question": "Topic: {title}\n\nCan you explain this concept in your own words?",
      "header": "Level 1: Explain",
      "multiSelect": false,
      "options": [
        {"label": "Enter my explanation", "description": "Explain in your own words"},
        {"label": "I need a hint", "description": "Get a guiding question"},
        {"label": "Skip", "description": "Move to next topic"}
      ]
    }
  ]
}
```

**Level 2 (Why)**:
```
"Why is {key_concept} important?"
```

**Level 3 (How)**:
```
"How would you apply {concept} in practice?"
```

**Level 4 (Edge Cases)**:
```
"What happens when {edge_case}?"
```

**Level 5 (Connections)**:
```
"How does this relate to {related_concept}?"
```

4. **Evaluate response**: Claude analyzes the answer and provides feedback
5. **Update confidence**: Adjust confidence score based on performance
6. **Record progress**: Update last_reviewed and review_count

### Socratic Evaluation

Claude evaluates user's response:
- **Strong**: Move to next level, increase confidence
- **Partial**: Provide hint, retry same level
- **Weak**: Provide explanation, stay at level

---

## Mode: Flashcard Quiz

### Leitner 5-Box System

| Box | Review Interval |
|-----|-----------------|
| 1   | 1 day           |
| 2   | 3 days          |
| 3   | 7 days          |
| 4   | 14 days         |
| 5   | 30 days         |

### Flashcard Workflow

1. **Select due cards**: Filter items where `last_reviewed + interval < today`
2. **For each card**:

**Show Question**:
```
Flashcard ({current}/{total})
Category: {category}
Box: {box_number}

Q: {question}

[Press Enter to reveal answer]
```

**Reveal Answer**:
```
A: {answer}

---
How did you do?
```

```json
{
  "questions": [
    {
      "question": "Did you answer correctly?",
      "header": "Self-Assess",
      "multiSelect": false,
      "options": [
        {"label": "Correct", "description": "Move to next box"},
        {"label": "Incorrect", "description": "Move back to box 1"},
        {"label": "Skip", "description": "Skip this card"}
      ]
    }
  ]
}
```

3. **Update box position**:
   - Correct: Move to next box (max 5)
   - Incorrect: Move back to box 1
4. **Update progress.json**

### Session Summary

```
Flashcard Session Complete!

Cards reviewed: {total}
Correct: {correct} ({percentage}%)
Incorrect: {incorrect}

Box distribution:
- Box 1: {count} items
- Box 2: {count} items
- Box 3: {count} items
- Box 4: {count} items
- Box 5: {count} items

Next review: {next_due_date}
```

---

## Mode: Connection Exploration

### Connection Workflow

1. **Select starting item**: User selects or random selection
2. **Analyze for connections**: Find items with:
   - Overlapping tags (Jaccard similarity > 0.3)
   - Similar category
   - Mentioned in connections array

3. **Suggest connections**:
```
Connection Explorer

Current: {title}

I found potential connections:

1. {related_title_1}
   - Shared tags: {common_tags}
   - Relationship: May be related

2. {related_title_2}
   - Same category
   - Relationship: Similar concept

Would you like to explore any of these?
```

4. **Explore relationship**:
```json
{
  "questions": [
    {
      "question": "How do you see '{item_a}' and '{item_b}' relating?",
      "header": "Relationship",
      "multiSelect": false,
      "options": [
        {"label": "Prerequisite", "description": "A is required to understand B"},
        {"label": "Builds on", "description": "B extends or deepens A"},
        {"label": "Contrasts", "description": "Different approaches to same problem"},
        {"label": "Synthesizes", "description": "Combining creates new insight"}
      ]
    }
  ]
}
```

5. **Create new insight** (if synthesis selected):
```json
{
  "questions": [
    {
      "question": "Would you like to capture this new insight as a knowledge item?",
      "header": "New Insight",
      "multiSelect": false,
      "options": [
        {"label": "Yes, create new item", "description": "Opens /spark add with context"},
        {"label": "No, just save connection", "description": "Only update connection links"}
      ]
    }
  ]
}
```

6. **Update connections**: Add connection to both items' frontmatter

---

## Progress File Format

**Path**: `{REPO_ROOT}/.sparks/progress.json`

```json
{
  "{item_id}": {
    "box": 2,
    "lastReviewed": "2026-01-18T15:00:00",
    "correctCount": 5,
    "incorrectCount": 1,
    "socraticDepth": 3,
    "connectionsMade": ["other-item-id"]
  }
}
```

## Error Handling

- **No knowledge items**: Suggest running `/spark add` first
- **No due cards**: Show message "No cards due for review. Use --all to review anyway."
- **Progress file missing**: Create empty progress.json
- **Invalid mode**: Show mode selection prompt
