# Sparks Plugin - Developer Guide

## Overview

지식과 인사이트를 Github에 저장하고, 3가지 학습 모드(소크라틱 대화, 플래시카드, 연결 탐색)를 통해 학습하는 플러그인

## Architecture

```
plugins/sparks/
├── .claude-plugin/plugin.json    # 플러그인 메타데이터
├── commands/
│   └── spark.md                  # 단일 파일 (라우터 + 모든 서브커맨드)
├── scripts/
│   └── build-blog.mjs            # MD→HTML 블로그 빌드 스크립트
├── templates/
│   ├── knowledge_template.md     # 지식 파일 템플릿
│   └── repo_init/                # 저장소 초기화 템플릿
├── package.json                  # 빌드 의존성 (marked, gray-matter)
├── CLAUDE.md
└── README.md
```

## Command

### `/spark <subcommand> [options]` - 통합 명령

단일 `/spark` 명령으로 모든 기능에 접근. 서브커맨드로 분기.

| 서브커맨드 | 설명 | 옵션 |
|-----------|------|------|
| `add` | 지식/인사이트 저장 | |
| `blog` | 블로그 글 저장/조회/수정 | `list`, `update`, `--publish`, `--style=<style>` |
| `log` | 데일리 로그 에피소드 | `--style=diary\|bullet\|devlog\|narrative` |
| `learn` | 학습 (3가지 모드) | `--mode=socratic\|flashcard\|connect --category=<name>` |
| `search` | 검색 | `<keyword> --tag=<tag> --category=<cat>` |
| `list` | 목록 조회 | `--category=<name> --stats --due` |
| `stats` | 학습 통계 대시보드 | |
| `publish` | 블로그 HTML 빌드 + Cloudflare 배포 | `--all`, `<filename>` |
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

# 블로그 배포 테스트
/spark publish --all
/spark publish 2026-02-23-특정글.md
/spark publish  # 인터랙티브
```

## Related Files

- `plugins/add-prompt/commands/add-prompt.md` - 커맨드 패턴 참조
- `plugins/shortcut-master/scripts/learning.py` - Leitner Box 로직 참조

---

<!-- SNAPKIN:SESSION_CONTEXT_START -->
## Session Context

> Current state snapshot. Fully rewritten each session sync.

### Last Sync

- **Date**: 2026-02-15
- **Session**: Sparks 플러그인 명령 통합 - 8개 개별 파일을 spark.md로 병합

### Active Work

- **완료**: 8개 개별 command 파일을 단일 spark.md로 통합
- **완료**: CLAUDE.md 대폭 간소화 (129줄 → 133줄, 구조 개선)
- **완료**: plugin.json 버전 업데이트 (1.0.0 → 1.1.0)

### Blockers

No blockers.

### Next Entry Point

- **[P1/M]** `/spark` 명령 실제 테스트 및 서브커맨드 동작 검증 — `commands/spark.md:1` (done: 모든 서브커맨드 정상 동작)
- **[P2/S]** README.md 업데이트 — 통합 명령 구조 반영
- **[P3/L]** 학습 모드 3가지 구현 완성도 검증

### Recent Changes

- `commands/spark.md` — 8개 서브커맨드를 단일 파일에 통합 (라우터 패턴)
- `CLAUDE.md` — 개발자 가이드 구조 개선, 테스트 섹션 추가
- `plugin.json` — 버전 1.1.0으로 업데이트

### Key Files

- `commands/spark.md` — 모든 서브커맨드 통합 라우터
- `templates/knowledge_template.md` — 지식 파일 템플릿
- `templates/repo_init/` — 저장소 초기화 템플릿

<!-- SNAPKIN:SESSION_CONTEXT_END -->
