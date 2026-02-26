# Sparks Plugin - Developer Guide

## Overview

지식과 인사이트를 Github에 저장하고, 3가지 학습 모드(소크라틱 대화, 플래시카드, 연결 탐색)를 통해 학습하는 플러그인

## Architecture

```
plugins/sparks/
├── .claude-plugin/plugin.json    # 플러그인 메타데이터
├── commands/
│   └── spark.md                  # 전체 스펙 (라우터 + 모든 서브커맨드)
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
| `publish` | 블로그 HTML 빌드 + Cloudflare 배포 | `--all`, `--draft`, `<filename>`, `<filename>:private` |
| `init` | 저장소 초기화 | `[directory]` |

**Routing**: `spark.md`에 라우터 + 모든 서브커맨드 전체 스펙 포함. $ARGUMENTS 첫 단어로 분기.

**Allowed Tools:** AskUserQuestion, Glob, Read, Write, Edit, Bash

## Knowledge Repository Structure

사용자 지식 저장소 구조 (`/spark init`으로 생성):

```
my-sparks/
├── .sparks/
│   ├── config.json       # 저장소 설정 (publish, log 등)
│   ├── progress.json     # 학습 진행 (gitignore)
│   └── published.json    # 발행 manifest
├── concepts/             # 개념/이론
├── insights/             # 인사이트/깨달음
├── skills/               # 실용 기술
├── til/                  # Today I Learned
├── blog/                 # 블로그 글 + 데일리 로그
├── .gitignore
└── README.md
```

Knowledge file format과 카테고리 상세는 `commands/spark.md` 참조.

## Testing

```bash
/spark blog                        # 블로그 저장
/spark add                         # 지식 저장
/spark learn --mode=flashcard      # 학습
/spark log                         # 데일리 로그
/spark stats                       # 통계
/spark publish 특정글.md            # 특정 글 배포
/spark publish --all               # 전체 배포
/spark publish --draft             # 저장 없이 배포
```

## Related Files

- `plugins/add-prompt/commands/add-prompt.md` - 커맨드 패턴 참조
- `plugins/shortcut/scripts/learning.py` - Leitner Box 로직 참조

---

<!-- SNAPKIN:SESSION_CONTEXT_START -->
## Session Context

> Current state snapshot. Fully rewritten each session sync.

### Last Sync

- **Date**: 2026-02-25
- **Session**: publish 플로우 개선 + CLAUDE.md 정리

### Active Work

- **완료**: publish 플로우 개선 (manifest 자동 처리, git commit 단계 추가, 접근 제어 확인)
- **완료**: CLAUDE.md 중복 제거 및 최신화

### Blockers

No blockers.

### Next Entry Point

- **[P2/S]** README.md 업데이트 — 통합 명령 구조 반영
- **[P3/L]** 학습 모드 3가지 구현 완성도 검증

### Recent Changes

- `commands/spark.md` — publish 플로우 3가지 개선 (manifest 자동화, git commit, 접근 제어)
- `CLAUDE.md` — 중복 제거, 오래된 정보 수정, Session Context 최신화

### Key Files

- `commands/spark.md` — 모든 서브커맨드 전체 스펙
- `scripts/build-blog.mjs` — 블로그 빌드 (manifest 자동 관리)
- `templates/knowledge_template.md` — 지식 파일 템플릿

<!-- SNAPKIN:SESSION_CONTEXT_END -->
