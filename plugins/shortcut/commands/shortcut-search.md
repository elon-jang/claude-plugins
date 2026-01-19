---
name: shortcut-search
description: 키워드로 단축키를 검색합니다
argument-hint: "<keyword>"
allowed-tools:
  - Bash
  - Read
---

# Search Shortcuts

키워드로 단축키를 검색합니다.

## Usage

```bash
/shortcut:shortcut-search <keyword> [--section=<name>]
```

## Arguments

- `keyword` (required): 검색할 키워드
- `--section` (optional): 특정 섹션(카테고리)에서만 검색

## Examples

```bash
/shortcut:shortcut-search "comment"
/shortcut:shortcut-search "toggle" --section=Editing
/shortcut:shortcut-search "save"
```

## Implementation

Python CLI를 실행합니다:

```bash
cd {plugin_path} && python -m scripts.cli search {keyword} {options}
```
