---
name: shortcut-delete
description: 단축키를 삭제합니다
argument-hint: "<app_name> <shortcut>"
allowed-tools:
  - Bash
  - Read
  - Edit
---

# Delete Shortcut

단축키를 삭제합니다.

## Usage

```bash
/shortcut:shortcut-delete <app_name> <shortcut>
```

## Arguments

- `app_name` (required): 앱 이름
- `shortcut` (required): 삭제할 단축키 (정확히 입력)

## Example

```bash
/shortcut:shortcut-delete vscode "Cmd+D"
```

## Notes

- 삭제 후 Git 자동 커밋
- 학습 진도 데이터도 함께 삭제

## Implementation

Python CLI를 실행합니다:

```bash
cd {plugin_path} && python -m scripts.cli delete {app_name} {shortcut}
```
