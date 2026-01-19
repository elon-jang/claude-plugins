---
name: shortcut-stats
description: 학습 통계를 표시합니다
argument-hint: "[app_name]"
allowed-tools:
  - Bash
  - Read
---

# Shortcut Statistics

학습 통계를 표시합니다.

## Usage

```bash
/shortcut:stats [app_name]
```

## Arguments

- `app_name` (optional): 특정 앱 통계만 표시. 없으면 전체.

## Output

- Box 분포 (Box 1/2/3 카드 수)
- 전체 정답률
- 가장 어려운 단축키 Top 5

## Examples

```bash
/shortcut:stats
/shortcut:stats vscode
```

## Implementation

Python CLI를 실행합니다:

```bash
cd {plugin_path} && python -m scripts.cli stats {app_name}
```
