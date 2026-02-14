---
name: shortcut-delete
description: 단축키를 YAML에서 삭제합니다
argument-hint: "<app_name> <shortcut>"
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Edit
---

# Delete Shortcut

YAML 파일에서 단축키를 삭제합니다.

## Constants

```
REPO_ROOT = ~/elon/ai/shortcut
YAML_DIR  = $REPO_ROOT/shortcuts
```

## Usage

```
/shortcut:shortcut-delete <app_name> <shortcut>
```

인자 없이 실행하면 대화형으로 앱과 단축키를 선택합니다.

## Workflow

### 1. 대상 확인

**인자가 있는 경우**: `app_name`으로 YAML 파일을 찾고, `shortcut`과 일치하는 항목 검색.

**인자가 없는 경우**: AskUserQuestion으로 앱 선택 → 해당 앱의 단축키 목록 표시 → 삭제 대상 선택.

### 2. YAML 파일에서 삭제

Read the YAML file, find the matching item, and remove it using Edit tool.

해당 item 엔트리(shortcut + description 두 줄)를 삭제합니다.

**Section이 비게 되면**: section 전체(section name + items 헤더 포함)를 삭제합니다.

### 3. Git Operations

```bash
cd "$REPO_ROOT" && \
git add shortcuts/{app-id}.yaml && \
git commit -m "Remove shortcut: {App} - {Shortcut}" && \
git push
```

### 4. Success Message

```
Deleted: {App} - {Shortcut} ({Description})
Committed and pushed.
```

## Example

```
/shortcut:shortcut-delete chrome "Cmd+Y"

→ shortcuts/chrome.yaml에서 "Cmd+Y" 항목 삭제
→ Committed: "Remove shortcut: Chrome - Cmd+Y"
```

## Error Handling

- **앱 not found**: "'{app_name}'에 해당하는 YAML 파일이 없습니다"
- **단축키 not found**: "'{shortcut}'을 찾을 수 없습니다. 기존 단축키 목록:" + 목록 표시
