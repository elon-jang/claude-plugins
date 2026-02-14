# Sparks Plugin - Developer Guide

## Overview

지식과 인사이트를 Github에 저장하고, 3가지 학습 모드(소크라틱 대화, 플래시카드, 연결 탐색)를 통해 학습하는 플러그인

## Architecture

```
plugins/sparks/
├── .claude-plugin/plugin.json    # 플러그인 메타데이터
├── commands/
│   └── spark.md                  # 단일 파일 (라우터 + 모든 서브커맨드)
├── templates/
│   ├── knowledge_template.md     # 지식 파일 템플릿
│   └── repo_init/                # 저장소 초기화 템플릿
├── CLAUDE.md
└── README.md
```

## Command

### `/spark <subcommand> [options]` - 통합 명령

단일 `/spark` 명령으로 모든 기능에 접근. 서브커맨드로 분기.

| 서브커맨드 | 설명 | 옵션 |
|-----------|------|------|
| `add` | 지식/인사이트 저장 | |
| `blog` | 블로그 글 저장/조회/수정 | `list`, `update` |
| `log` | 데일리 로그 에피소드 | `--style=diary\|bullet\|devlog\|narrative` |
| `learn` | 학습 (3가지 모드) | `--mode=socratic\|flashcard\|connect --category=<name>` |
| `search` | 검색 | `<keyword> --tag=<tag> --category=<cat>` |
| `list` | 목록 조회 | `--category=<name> --stats --due` |
| `stats` | 학습 통계 대시보드 | |
| `init` | 저장소 초기화 | `[directory]` |

**Routing**: `spark.md` 단일 파일에 라우터 + 모든 서브커맨드가 요약 수준으로 포함됨. $ARGUMENTS 첫 단어로 분기.

**Allowed Tools:** AskUserQuestion, Glob, Read, Write, Edit, Bash

## Knowledge File Format

```yaml
---
id: "uuid"
title: "제목"
category: "concepts"
tags: ["tag1", "tag2"]
created: "2026-01-19T10:30:00"
source: "출처 (선택)"
blog_link: "blog/2026-01-19-title.md"  # 블로그 연결 시 (선택)
confidence: 3           # 1-5 (자기 평가)
connections: ["related-id"]
review_count: 0
last_reviewed: null
---

# 제목

## Summary
핵심 요약

## Key Points
- 포인트 1
- 포인트 2

## Questions
- Q: 질문
- A: 답변

## My Understanding
나만의 이해/설명
```

## Knowledge Repository Structure

사용자 지식 저장소 권장 구조:

```
my-sparks/
├── .sparks/
│   ├── config.json       # 저장소 설정
│   └── progress.json     # 학습 진행 (gitignore)
├── concepts/             # 개념/이론
├── insights/             # 인사이트/깨달음
├── skills/               # 실용 기술
├── til/                  # Today I Learned
├── blog/                 # 블로그 글 (원문) + 데일리 로그
├── .gitignore
└── README.md
```

### Categories

| 카테고리 | 용도 | 예시 |
|---------|------|------|
| `concepts` | 이론, 원리, 개념 | ML 기초, 디자인 패턴 |
| `insights` | 경험에서 얻은 깨달음 | 코드리뷰 교훈, 실패 복기 |
| `skills` | 실용 기술, How-to | Git 명령어, 단축키 |
| `til` | 오늘 배운 것 | 일일 학습 기록 |
| `blog` | 블로그 글 원문 + 데일리 로그 | 기술 블로그, 회고 글, 일일 기록 |

## Testing

```bash
# 플러그인 디렉토리에서 테스트
cd plugins/sparks

# 블로그 저장 테스트
/spark blog

# 지식 저장 테스트 (블로그 연결 포함)
/spark add

# 학습 테스트
/spark learn --mode=flashcard
/spark learn --mode=socratic
/spark learn --mode=connect

# 데일리 로그 테스트
/spark log
/spark log --style=bullet

# 통계 대시보드 테스트
/spark stats
```

## Related Files

- `plugins/add-prompt/commands/add-prompt.md` - 커맨드 패턴 참조
- `plugins/shortcut-master/scripts/learning.py` - Leitner Box 로직 참조
