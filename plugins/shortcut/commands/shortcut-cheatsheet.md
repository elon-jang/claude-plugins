---
name: shortcut-cheatsheet
description: A4 인쇄용 Cheat Sheet HTML을 생성합니다
argument-hint: "[output_path]"
allowed-tools:
  - Bash
  - Read
  - Write
---

# Generate Cheat Sheet

A4 한 장 분량의 인쇄용 Cheat Sheet HTML 파일을 생성합니다.

## Usage

```bash
/shortcut:shortcut-cheatsheet [output_path]
```

## Arguments

- `output_path` (optional): 출력 파일 경로. 기본값: `./cheatsheet.html`

## Output

- A4 사이즈에 최적화된 HTML 파일
- 앱별로 그룹화된 단축키
- 개별 키캡 스타일로 가독성 높은 디자인
- 인쇄 시 배경색 포함 옵션

## Example

```bash
# 기본 경로에 생성
/shortcut:shortcut-cheatsheet

# 특정 경로에 생성
/shortcut:shortcut-cheatsheet ~/Desktop/shortcuts.html
```

## Implementation

Python CLI를 실행합니다:

```bash
cd {repo_path} && python -m scripts.cli cheatsheet [output_path]
```

생성 후 브라우저에서 열기:

```bash
open [output_path]
```
