---
name: shortcut-add
description: 단축키를 대화형으로 추가합니다 (YAML 기반, 웹앱 자동 동기화)
argument-hint: ""
allowed-tools:
  - AskUserQuestion
  - Glob
  - Bash
  - Read
  - Write
  - Edit
---

# Add Shortcut

단축키를 YAML 파일에 대화형으로 추가합니다. 추가 즉시 Shortcut Pro 웹앱에 자동 반영됩니다.

## Constants

```
REPO_ROOT = ~/elon/ai/shortcut
YAML_DIR  = $REPO_ROOT/shortcuts
```

## Workflow

### 0. Detect Repository & Existing Data

**YAML 디렉토리 존재 확인**:
```bash
ls "$YAML_DIR"/*.yaml
```

**기존 앱 목록 추출**: YAML 파일명에서 앱 이름을 파싱 (각 파일 첫 줄의 `app:` 값).

**기존 섹션 추출**: 사용자가 앱을 선택하면 해당 YAML의 `section:` 값들을 수집.

### 1. Collect Information

Use AskUserQuestion to gather all required information:

**First AskUserQuestion** (2 questions):

```json
{
  "questions": [
    {
      "question": "Which application is this shortcut for?",
      "header": "App",
      "multiSelect": false,
      "options": [
        // 기존 앱들을 YAML에서 읽어 동적으로 생성
        // 예: {"label": "Chrome", "description": "15 shortcuts"},
        // 항상 마지막에:
        {"label": "New app", "description": "새 앱 추가"}
      ]
    },
    {
      "question": "Which section does this shortcut belong to?",
      "header": "Section",
      "multiSelect": false,
      "options": [
        // 선택된 앱의 기존 섹션들을 동적으로 표시
        // 예: {"label": "Navigation", "description": "existing section"},
        {"label": "New section", "description": "새 섹션 추가"}
      ]
    }
  ]
}
```

**Second AskUserQuestion** (2 questions):

```json
{
  "questions": [
    {
      "question": "What is the keyboard shortcut? (e.g., cmd+d, ctrl+shift+p)",
      "header": "Shortcut",
      "multiSelect": false,
      "options": [
        {"label": "Enter shortcut", "description": "Type the keyboard shortcut"}
      ]
    },
    {
      "question": "What does this shortcut do?",
      "header": "Description",
      "multiSelect": false,
      "options": [
        {"label": "Enter description", "description": "Brief description of the action"}
      ]
    }
  ]
}
```

### 2. Normalize Shortcut Notation

| Input | Output |
|-------|--------|
| `cmd+d` | `Cmd+D` |
| `command+shift+p` | `Cmd+Shift+P` |
| `ctrl+alt+del` | `Ctrl+Alt+Del` |
| `option+shift+f` | `Opt+Shift+F` |

**Normalization rules**:
- `cmd`, `command` → `Cmd`
- `ctrl`, `control` → `Ctrl`
- `opt`, `option`, `alt` → `Opt`
- `shift` → `Shift`
- All letters uppercase
- Join with `+`

### 3. Check for Duplicates

Read target YAML file. Search all items for matching shortcut.

If duplicate found:
- Display: "이미 존재하는 단축키입니다: `{shortcut}` → {description}"
- Stop execution

### 4. Add Shortcut to YAML File

**If YAML file doesn't exist** (new app), create `$YAML_DIR/{app-id}.yaml`:

```yaml
app: {App Name}
shortcuts:
  - section: {Section}
    items:
      - shortcut: {Normalized Shortcut}
        description: {Description}
```

`app-id`는 앱 이름을 소문자 kebab-case로 변환 (예: `VS Code` → `vscode`, `Claude Desktop` → `claude-desktop`).

**If YAML file exists**, find the target section:

- **Section exists**: 해당 section의 `items` 배열 끝에 추가
- **Section doesn't exist**: `shortcuts` 배열 끝에 새 section 추가

```yaml
      - shortcut: {Normalized Shortcut}
        description: {Description}
```

### 5. Git Operations

```bash
cd "$REPO_ROOT" && \
git add shortcuts/{app-id}.yaml && \
git commit -m "Add shortcut: {App} - {Shortcut} ({Description})" && \
git push
```

### 6. Success Message

```
Added successfully!

App: {App}
Section: {Section}
Shortcut: {Shortcut}
Description: {Description}

File: shortcuts/{app-id}.yaml
Committed and pushed.

웹앱(Shortcut Pro)에서 dev 서버 실행 중이면 자동으로 반영됩니다.
```

## Error Handling

- **YAML 디렉토리 없음**: "shortcuts/ 디렉토리를 찾을 수 없습니다"
- **중복 단축키**: 기존 항목 표시, 실행 중지
- **Git push 실패**: "로컬에 저장되었습니다. 수동으로 push해주세요."

## Example

```
User: /shortcut:shortcut-add

→ App: Notion (10 shortcuts)
→ Section: Editing
→ Shortcut: cmd+shift+l
→ Description: Toggle bulleted list

Result:
- shortcuts/notion.yaml 업데이트
- Committed: "Add shortcut: Notion - Cmd+Shift+L (Toggle bulleted list)"
- 웹앱 자동 반영
```
