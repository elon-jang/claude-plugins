---
name: init
description: 새 단축키 저장소를 초기화합니다
argument-hint: "[repo_path]"
allowed-tools:
  - Bash
  - Write
---

# Initialize Shortcut Repository

새 단축키 저장소를 초기화합니다.

## Usage

```bash
/shortcut:init [repo_path]
```

## Arguments

- `repo_path` (optional): 저장소 경로. 기본값은 현재 디렉토리.

## Workflow

1. 저장소 경로 확인 (인자 없으면 현재 디렉토리)
2. `.shortcut-master/` 디렉토리 생성
3. `learning-progress.json` 초기화
4. Git 저장소 초기화 (없으면)
5. `.gitignore`에 학습 진도 파일 추가

## Example

```bash
/shortcut:init ~/my-shortcuts
```

## Implementation

Python CLI를 실행합니다:

```bash
cd {plugin_path} && python -m scripts.cli init {repo_path}
```
