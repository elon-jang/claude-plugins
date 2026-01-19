---
name: add
description: 단축키를 대화형으로 추가합니다
argument-hint: ""
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
  - Edit
---

# Add Shortcut

단축키를 대화형으로 추가합니다.

## Usage

```bash
/shortcut:add
```

## Workflow

1. AskUserQuestion으로 정보 수집:
   - App 이름 (vscode, chrome, figma 등)
   - Category (Editing, Navigation, View 등)
   - Shortcut (Cmd+D, Ctrl+Shift+P 등)
   - Description (설명)

2. 단축키 표기법 자동 정규화:
   - `cmd+d` → `Cmd+D`
   - `command+shift+p` → `Cmd+Shift+P`

3. 중복 검사 후 Markdown 테이블에 추가

4. Git 자동 커밋

## Notes

- 단축키 표기법은 자동으로 정규화됩니다
- 카테고리는 기존 카테고리에서 자동완성 제공
- 중복 단축키는 자동으로 거부됩니다

## Implementation

Python CLI를 실행합니다:

```bash
cd {plugin_path} && python -m scripts.cli add
```
