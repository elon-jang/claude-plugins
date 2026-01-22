---
name: shortcut-cheatsheet
description: A4 인쇄용 Cheat Sheet HTML을 생성합니다
argument-hint: "[output_path] [--mode simple|progress|interactive]"
allowed-tools:
  - Bash
  - Read
  - Write
---

# Generate Cheat Sheet

A4 한 장 분량의 인쇄용 Cheat Sheet HTML 파일을 생성합니다.

## Usage

```bash
/shortcut:shortcut-cheatsheet [output_path] [--mode MODE]
```

## Arguments

- `output_path` (optional): 출력 파일 경로. 기본값: `./cheatsheet.html`
- `--mode MODE` (optional): 체크박스 모드 선택
  - `simple` (기본값): 체크박스 없음
  - `progress`: 학습 진행상황 기반 체크박스 (읽기 전용)
    - ✓ = Box 3 (마스터)
    - △ = Box 2 (진행 중)
    - □ = Box 1 또는 미학습
  - `interactive`: 직접 체크 가능 (브라우저 localStorage 저장)

## Output

- A4 사이즈에 최적화된 HTML 파일
- 앱별로 그룹화된 단축키
- 개별 키캡 스타일로 가독성 높은 디자인
- 인쇄 시 배경색 포함 옵션
- (progress/interactive 모드) 체크박스 및 진행률 표시

## Example

```bash
# 기본 (체크박스 없음)
/shortcut:shortcut-cheatsheet

# 학습 진행상황 표시
/shortcut:shortcut-cheatsheet --mode progress

# 직접 체크 가능 (브라우저용)
/shortcut:shortcut-cheatsheet ~/Desktop/shortcuts.html --mode interactive
```

## Implementation

Python CLI를 실행합니다:

```bash
cd {repo_path} && python -m scripts.cli cheatsheet [output_path] --mode [MODE]
```

생성 후 브라우저에서 열기:

```bash
open [output_path]
```
