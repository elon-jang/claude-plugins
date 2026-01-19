# Sparks Plugin - Developer Guide

## Overview

지식과 인사이트를 Github에 저장하고, 3가지 학습 모드(소크라틱 대화, 플래시카드, 연결 탐색)를 통해 학습하는 플러그인

## Architecture

```
plugins/sparks/
├── .claude-plugin/plugin.json    # 플러그인 메타데이터
├── commands/
│   ├── spark-add.md              # 지식 저장
│   ├── spark-blog.md             # 블로그 글 저장
│   ├── spark-learn.md            # 학습 (3가지 모드)
│   ├── spark-search.md           # 검색
│   ├── spark-list.md             # 목록 조회
│   └── spark-init.md             # 저장소 초기화
├── templates/
│   ├── knowledge_template.md     # 지식 파일 템플릿
│   └── repo_init/                # 저장소 초기화 템플릿
├── CLAUDE.md
└── README.md
```

## Commands

### `/spark-add` - 지식 저장

**Workflow:**
1. Git 저장소 감지 (`git rev-parse --show-toplevel`)
2. 블로그 글 존재 여부 확인 (`blog/` 디렉토리)
3. AskUserQuestion으로 입력 수집:
   - Category, Title, Tags, Source (블로그 링크 옵션 포함), Content
4. 블로그에서 가져올 경우: 블로그 글 선택 → `blog_link` 필드에 저장
5. Claude가 Q&A 자동 생성 → 사용자 확인
6. Markdown + YAML frontmatter 파일 생성
7. README.md 업데이트
8. Git add, commit, push

**Allowed Tools:** AskUserQuestion, Glob, Read, Write, Edit, Bash

### `/spark-blog` - 블로그 글 저장

**Workflow:**
1. Git 저장소 감지
2. AskUserQuestion으로 입력 수집:
   - Title, Tags (선택), Content
3. `blog/YYYY-MM-DD-title.md` 파일 생성 (원문 그대로)
4. README.md 업데이트 (Blog 섹션)
5. Git add, commit, push

**Allowed Tools:** AskUserQuestion, Glob, Read, Write, Edit, Bash

### `/spark-learn` - 학습 모드

**Arguments:**
```
--mode=socratic    소크라틱 대화 (Why/How 질문)
--mode=flashcard   플래시카드 퀴즈 (Leitner 5-box)
--mode=connect     연결 탐색 (관련 지식 연결)
--category=<name>  특정 카테고리만 학습
--all              모든 항목 대상
```

#### Socratic Mode
- Level 1: "이 개념을 자신의 말로 설명해보세요"
- Level 2: "왜 이것이 중요한가요?"
- Level 3: "실제로 어떻게 적용하나요?"
- Level 4: "예외 상황은 어떻게 처리하나요?"
- Level 5: "다른 개념과 어떻게 연결되나요?"

#### Flashcard Mode
- Leitner 5-box 알고리즘
- 복습 간격: 1일 → 3일 → 7일 → 14일 → 30일
- Q 표시 → 사용자 답변 → 정답 확인 → 자기 평가

#### Connect Mode
- 태그/키워드 기반 유사 항목 제안
- 관계 유형: prerequisite, alternative, synthesis
- 새 인사이트 도출 시 새 지식 항목 생성 제안

### `/spark-search` - 검색

**Arguments:**
```
<keyword>           키워드 검색
--tag=<tag>         태그 필터
--category=<name>   카테고리 필터
```

### `/spark-list` - 목록

**Arguments:**
```
--category=<name>   특정 카테고리만
--stats             통계 포함 (복습 횟수, confidence)
```

### `/spark-init` - 저장소 초기화

새 지식 저장소를 초기화. 템플릿 기반으로 디렉토리 구조와 설정 파일 생성.

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
├── blog/                 # 블로그 글 (원문)
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
| `blog` | 블로그 글 원문 | 기술 블로그, 회고 글 |

## Testing

```bash
# 플러그인 디렉토리에서 테스트
cd plugins/sparks

# 블로그 저장 테스트
/spark-blog

# 지식 저장 테스트 (블로그 연결 포함)
/spark-add

# 학습 테스트
/spark-learn --mode=flashcard
/spark-learn --mode=socratic
/spark-learn --mode=connect
```

## Related Files

- `plugins/add-prompt/commands/add-prompt.md` - 커맨드 패턴 참조
- `plugins/shortcut-master/scripts/learning.py` - Leitner Box 로직 참조
