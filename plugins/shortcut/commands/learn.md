---
name: learn
description: Leitner Box 학습 세션을 시작합니다
argument-hint: "[app_name] [--mode=flash|quick|typing] [--all]"
allowed-tools:
  - Bash
  - Read
---

# Learn Shortcuts

Leitner Box 알고리즘으로 학습 세션을 시작합니다.

## Usage

```bash
/shortcut:learn [app_name] [--mode=flash|quick|typing] [--all]
```

## Arguments

- `app_name` (optional): 특정 앱만 학습. 없으면 전체.
- `--mode` (optional): 학습 모드
  - `flash` (기본): 플래시카드 방식 (Enter → y/n → Enter)
  - `quick`: 빠른 학습 (Enter → 1/2)
  - `typing`: 실제 단축키 입력 (동시 누름만 지원)
- `--all`: 모든 카드 강제 복습 (Leitner 스케줄 무시)

## Leitner Box System

- Box 1: 매일 복습
- Box 2: 3일마다 복습
- Box 3: 7일마다 복습

정답 시 다음 박스로 이동, 오답 시 Box 1로 이동.

## Examples

```bash
/shortcut:learn vscode
/shortcut:learn vscode --mode=quick
/shortcut:learn vscode --all
/shortcut:learn --mode=typing
```

## Implementation

Python CLI를 실행합니다:

```bash
cd {plugin_path} && python -m scripts.cli learn {app_name} {options}
```
