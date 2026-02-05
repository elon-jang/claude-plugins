---
name: snapkin-lesson
description: Immediately add one lesson entry to LESSONS.md
argument-hint: "[category] <lesson text>"
allowed-tools:
  - Read
  - Write
  - Edit
---

# Snapkin Lesson

Quickly add a single lesson entry to LESSONS.md without running the full multi-agent workflow.

## Argument Format

```
/snapkin:snapkin-lesson [category] <lesson text>
```

**Examples:**
- `/snapkin:snapkin-lesson [Error-Fix] useEffect cleanup must return void, not Promise`
- `/snapkin:snapkin-lesson Always validate env vars at startup, not at first use`

## Execution Steps

### Step 1: Parse Input

Extract from the argument:
- **Category tag**: One of `[Error-Fix]`, `[Decision]`, `[Insight]`, `[Domain]`, `[Prompt]`, `[Future]`
- **Lesson text**: The remaining text after the tag

If no category tag is provided, **auto-infer** the most appropriate category from the lesson content:
- Error/bug/fix related → `[Error-Fix]`
- Choice/picked/chose/decided → `[Decision]`
- Discovered/found/realized/turns out → `[Insight]`
- Domain concept/business rule → `[Domain]`
- Prompt/Claude/AI/LLM → `[Prompt]`
- TODO/later/future/idea/should → `[Future]`

### Step 2: Read LESSONS.md

Read `LESSONS.md` from the project root.

If the file doesn't exist, inform the user to run `/snapkin:snapkin-init` first.

### Step 3: Duplicate Check

Search the existing LESSONS.md for similar content. Check for:
- Exact substring match of the lesson text
- Semantically similar entries (same topic, same conclusion)

If a duplicate is found, inform the user and do **not** add it.

### Step 4: Find or Create Date Section

Look for a section header matching today's date: `## YYYY-MM-DD`

- If the section **exists**: Append the new entry at the end of that section
- If the section **does not exist**: Create a new `## YYYY-MM-DD` section at the top of the log (after the categories table and `---` separator)

### Step 5: Add Entry

Add the lesson in this format:

```markdown
- **[Category]** Lesson text here
```

Use the Edit tool to insert the entry.

### Step 6: Confirm

Output:

```
Added to LESSONS.md:
- **[Category]** Lesson text

Section: ## YYYY-MM-DD
```
