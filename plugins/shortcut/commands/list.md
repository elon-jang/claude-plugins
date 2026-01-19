---
name: list
description: 등록된 앱 목록을 표시합니다
argument-hint: ""
allowed-tools:
  - Bash
  - Read
---

# List Apps

등록된 앱 목록을 표시합니다.

## Usage

```bash
/shortcut:list
```

## Output

- 앱 이름
- 단축키 개수
- 마지막 수정일

## Example

```bash
/shortcut:list
```

## Implementation

Python CLI를 실행합니다:

```bash
cd {plugin_path} && python -m scripts.cli list
```
