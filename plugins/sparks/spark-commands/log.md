# Daily Log - Append Episode

하루 단위로 에피소드를 누적하는 데일리 로그. 짧은 메모나 작업 기록을 가볍게 남긴다.

## Options

- `--style=diary|bullet|devlog|narrative` - 스타일 오버라이드

## Style Presets

| Style | Description | Example |
|-------|-------------|---------|
| `diary` | 일기체 | "오늘 드디어 해결했다. 삽질 끝에..." |
| `bullet` | 간결 메모 | "- 항목1\n- 항목2\n- 항목3" |
| `devlog` | 개발 일지 | "**Problem**: X -> **Solution**: Y -> **Result**: Z" |
| `narrative` | 서술형 | "오늘의 작업은 블로그 기능 확장이었다. 먼저..." |

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

### 1. Determine Writing Style

**Parse `--style` argument** (if provided):
- `--style=diary` -> use `diary` style for this session only
- `--style=bullet` -> use `bullet` style
- `--style=devlog` -> use `devlog` style
- `--style=narrative` -> use `narrative` style

**If no `--style` argument**, read `.sparks/config.json`:
```bash
# Read log.defaultStyle from config
```

- If `log.defaultStyle` is set (not null) -> use that style
- If `log.defaultStyle` is null or missing -> go to Step 1b

#### Step 1b. Ask Style Preference (first-time only)

Use AskUserQuestion:

```json
{
  "questions": [
    {
      "question": "데일리 로그 기본 스타일을 선택하세요. 이후 --style 옵션으로 변경 가능합니다.",
      "header": "Style",
      "multiSelect": false,
      "options": [
        {"label": "diary", "description": "일기체 -- '오늘 드디어 해결했다...'"},
        {"label": "bullet", "description": "간결 메모 -- '- 항목1\\n- 항목2'"},
        {"label": "devlog", "description": "개발 일지 -- 'Problem -> Solution -> Result'"},
        {"label": "narrative", "description": "서술형 -- '오늘의 작업은...'"}
      ]
    }
  ]
}
```

**Save selection to config**: Read `.sparks/config.json`, set `log.defaultStyle` to chosen style, write back.

If `.sparks/config.json` doesn't have a `log` section, add it:
```json
{
  "log": {
    "defaultStyle": "<chosen>",
    "tags": ["daily"]
  }
}
```

### 2. Collect Episode Content

Use AskUserQuestion:

```json
{
  "questions": [
    {
      "question": "기록할 내용을 입력하세요.",
      "header": "Content",
      "multiSelect": false,
      "options": [
        {"label": "Enter content", "description": "오늘의 메모, 작업 기록, 생각 등"},
        {"label": "Skip", "description": "Not used"}
      ]
    }
  ]
}
```

If content is empty: "Error: Content is required."

### 3. Polish Content with Style

Claude rewrites the user's raw input according to the selected style:

- **diary**: 1인칭 일기체. 감정/느낌 포함. 자연스럽게.
- **bullet**: 핵심만 추린 글머리 기호 목록. 불필요한 수식어 제거.
- **devlog**: `**Problem**:` / `**Solution**:` / `**Result**:` 구조. 기술적 내용 강조.
- **narrative**: 3인칭 또는 관찰자 시점 서술. 맥락과 흐름 중심.

Keep the polished content concise -- a daily log episode should be short (3-10 lines).

### 4. Generate Episode

**Current time**: `HH:MM` format (24-hour)

**Episode title**: Claude generates a short title (5-15 characters) summarizing the content.

**Episode format**:
```markdown
## HH:MM - {episode title}

{polished content}
```

### 5. Write to Daily Log File

**Today's date**: `YYYY-MM-DD`

**Filename**: `blog/YYYY-MM-DD-daily-log.md`

**Check if file exists**: Use Glob `blog/YYYY-MM-DD-daily-log.md`

#### Case A: File does NOT exist -- Create new file

Use Write to create:

```markdown
---
title: "YYYY-MM-DD Daily Log"
date: "YYYY-MM-DD"
style: {style}
tags: [daily]
episodes: 1
---

# YYYY-MM-DD Daily Log

## HH:MM - {episode title}

{polished content}
```

#### Case B: File EXISTS -- Append episode

1. Read the existing file
2. Update frontmatter: increment `episodes` count by 1
3. Append new episode at the end of the file with a `---` separator before it

Use Edit to:
- Update `episodes: N` -> `episodes: N+1` in frontmatter
- Append at end of file:

```markdown

---

## HH:MM - {episode title}

{polished content}
```

### 6. Update README.md

**Read README.md** and find Blog section.

**Search patterns** (in order):
1. `<!-- spark-index:blog -->` - preferred anchor
2. `## Blog`
3. `### Blog`

**Check if today's daily log is already listed**: Search for `YYYY-MM-DD-daily-log.md` in README.

- If already listed -> **skip** README update (no duplicate entries)
- If NOT listed -> add entry (newest first, right after anchor comment):

```markdown
- [YYYY-MM-DD] [Daily Log](blog/YYYY-MM-DD-daily-log.md)
```

### 7. Git Operations

```bash
cd {REPO_ROOT} && \
git add blog/YYYY-MM-DD-daily-log.md README.md && \
git commit -m "log: YYYY-MM-DD episode - {episode title}" && \
git push origin {CURRENT_BRANCH}
```

### 8. Success Message

```
Daily log updated!

Repository: {REPO_ROOT}
File: blog/YYYY-MM-DD-daily-log.md
Style: {style}
Episode: #{episode_number} - {episode title}
```

## Error Handling

- **Not in Git repository**: Stop with error
- **Git push fails**: Show error, suggest manual push
- **Empty content**: Stop with error
- **Config file missing**: Proceed without config (ask style each time)
