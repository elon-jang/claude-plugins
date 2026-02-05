---
name: snapkin
description: Full session parallel cleanup - 2 agents update 2 project docs and commit
argument-hint: "[quick [message]] | [review]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Task
  - AskUserQuestion
---

# Snapkin — Full Session Sync

Run the complete 4-Phase multi-agent session wrap-up. 2 parallel agents update 2 project documents, then commit.

## Mode Selection

Parse the command arguments:

| Invocation | Mode | Behavior |
|------------|------|----------|
| `/snapkin` | Full | 4-phase workflow (기본) |
| `/snapkin quick` | Quick | Phase 1 최소 → Phase 4 커밋 |
| `/snapkin quick <message>` | Quick+Message | Phase 1 최소 → 메시지로 커밋 |
| `/snapkin review` | Full+Review | 4-phase + 커밋 전 사용자 확인 |

### Quick Mode Workflow

`quick` 인자 감지 시 아래 워크플로우를 실행하고, Phase 1~4를 건너뛴다.

#### Quick Phase 1: Minimal Dispatch

1. 베이스라인 탐지 + git diff (기존과 동일)
2. CLAUDE.md만 읽기 (LESSONS.md 건너뜀)
3. diff --stat에서 1줄 요약 자동 생성

#### Quick Phase 2: SKIP

에이전트 호출 없음.

#### Quick Phase 3: Session Context 직접 업데이트

Edit 도구로 CLAUDE.md의 Session Context 마커 사이만 업데이트:
- `Last Sync` 날짜를 오늘로
- `Session` 설명을 quick 메시지 또는 자동 요약으로
- `Active Work`을 git diff --stat 기반 간략 요약으로
- 나머지 하위 섹션(Blockers, Next Entry Point, Recent Changes, Key Files)은 변경하지 않음

#### Quick Phase 4: Commit

```bash
git add CLAUDE.md
git commit -m "docs: snapkin quick sync (YYYY-MM-DD) - [message or auto-summary]"
```

#### Quick Report

```markdown
## Snapkin Quick Sync Complete

**Date**: YYYY-MM-DD
**Commit**: [hash]
**Mode**: Quick

Session Context 업데이트됨. 전체 레슨 추출은 `/snapkin`을 사용하세요.
```

> Quick 모드 완료 후 나머지 Phase는 실행하지 않는다.

---

## Phase 1: Dispatch (Data Collection)

### Step 1.1: Collect Git Data

Run these commands to understand what changed this session:

**Step A: Find session baseline** — locate the last snapkin sync commit to diff against the full session, not just the last commit:

```bash
git log --oneline --grep="snapkin.*sync" -1 --format="%H"
```

**Step B: Diff from baseline**

- If a snapkin sync commit was found (`$BASE`):
  ```bash
  git diff $BASE --stat
  git diff $BASE
  git log --oneline $BASE..HEAD
  ```
- If no snapkin sync commit exists (first run), fall back to:
  ```bash
  git diff HEAD~5 --stat 2>/dev/null || git diff --cached --stat
  git diff HEAD~5 2>/dev/null || git diff
  git log --oneline --all
  ```

### Step 1.2: Read Existing Napkin Stack

Read these files from the project root (note which ones don't exist yet):
- `CLAUDE.md`
- `LESSONS.md`

Also read `README.md` for context only (do NOT modify it).

### Step 1.3: Build Session Summary

From the git data, write a concise session summary:

```
Session Summary:
- Date: YYYY-MM-DD
- Work: [Main tasks performed — what was built/fixed/changed]
- Files changed: [Key files modified, created, or deleted]
- Key decisions: [Any architectural or design choices made]
```

This summary will be passed to both agents.

---

## Phase 2: Parallel Scribble (Agent Execution)

Launch both agents in a **single message** (2 Task tool calls) for true parallel execution.

**CRITICAL**: Both must be in the same message to run in parallel.

### Agent 1: Historian

```
Task(
    subagent_type="snapkin:historian",
    model="sonnet",
    description="Extract session lessons",
    prompt="""
You are the Historian agent for Snapkin. Update LESSONS.md based on this session.

## Git Diff
{git_diff}

## Session Summary
{session_summary}

## Current LESSONS.md
{current_lessons_md OR "File does not exist yet — create it with the standard template."}

Follow your agent instructions to:
1. Extract lessons from the diff and summary
2. Categorize each as [Error-Fix], [Decision], [Insight], [Domain], [Prompt], or [Future]
3. Check for duplicates against existing entries
4. Add new entries under today's date section (## YYYY-MM-DD)
5. Write the updates to LESSONS.md
"""
)
```

### Agent 2: Auditor

```
Task(
    subagent_type="snapkin:auditor",
    model="sonnet",
    description="Audit conventions and session context",
    prompt="""
You are the Auditor agent for Snapkin. Update CLAUDE.md based on this session.

## Git Diff
{git_diff}

## Session Summary
{session_summary}

## Current CLAUDE.md
{current_claude_md OR "File does not exist yet — create it with a basic structure including Session Context markers."}

Follow your agent instructions to:
1. Update CLAUDE.md conventions (above the SNAPKIN:SESSION_CONTEXT_START marker) with new conventions, dependencies, structure changes
2. Rewrite the Session Context section (between SNAPKIN:SESSION_CONTEXT_START and SNAPKIN:SESSION_CONTEXT_END markers) as a fresh snapshot
3. NEVER include actual secret values — variable names only
4. Remove any outdated information
"""
)
```

---

## Phase 3: Validate

### Step 3.1: Read Updated Files

auditor와 historian이 작성한 최신 CLAUDE.md, LESSONS.md를 읽는다.

### Step 3.2: Launch Validator

```
Task(
    subagent_type="snapkin:validator",
    model="haiku",
    description="Validate Napkin Stack files",
    prompt="""
You are the Validator agent. Check these files for issues.

## Current CLAUDE.md
{updated_claude_md}

## Current LESSONS.md
{updated_lessons_md}

Today's date: YYYY-MM-DD

Run all validation checks and report findings.
"""
)
```

### Step 3.3: Handle Results

- **All checks passed**: Phase 4로 진행 (또는 review 모드면 Phase 3.5)
- **Issues found**: 오케스트레이터가 Edit 도구로 수정
  - Security 이슈 → 민감 데이터를 `[REDACTED]` 또는 변수명으로 교체
  - Structure 이슈 → 누락된 섹션/마커 추가
  - Duplicate 이슈 → 덜 상세한 쪽 제거
  - Size 경고 → 리스트 요약 또는 축소

> **Fallback**: validator 에이전트 호출 실패 시, 인라인 검증 로직으로 폴백한다:
> - Security: Grep으로 `API[_-]?KEY`, `PASSWORD`, `sk-`, `ghp_`, `SECRET` 패턴 검색
> - Structure: SNAPKIN 마커 존재 여부 + 필수 하위 섹션 확인
> - Duplicates: LESSONS.md에서 유사 항목, CLAUDE.md 컨벤션 중복 수동 확인

---

## Phase 3.5: User Review (review 모드에서만 실행)

> `/snapkin review`로 호출된 경우에만 이 단계를 실행한다. 기본 모드에서는 Phase 4로 바로 진행.

### Step 3.5.1: 변경 요약 표시

```markdown
## Session Sync 요약 — 커밋 대기 중

### CLAUDE.md
- 컨벤션: [변경된 섹션 목록 또는 "변경 없음"]
- Session Context: [세션 초점]으로 재작성
- Next Entry Point: [P0-P3 요약]

### LESSONS.md
- 새 레슨: [N개 추가]
- 카테고리: [사용된 태그 목록]
```

### Step 3.5.2: 사용자 질문

```
AskUserQuestion(
    questions=[{
        "question": "어떻게 진행할까요?",
        "header": "Snapkin Sync",
        "multiSelect": false,
        "options": [
            {"label": "커밋 (Recommended)", "description": "CLAUDE.md, LESSONS.md를 스테이징하고 커밋"},
            {"label": "변경사항 확인", "description": "커밋 전에 전체 diff를 먼저 보여줌"},
            {"label": "커밋 건너뛰기", "description": "파일 변경은 유지하되 커밋하지 않음"}
        ]
    }]
)
```

### Step 3.5.3: 선택 처리

- **커밋**: Phase 4로 진행
- **변경사항 확인**: `git diff CLAUDE.md LESSONS.md` 실행 후, 다시 "커밋 / 건너뛰기" 선택
- **커밋 건너뛰기**: "변경사항이 파일에 저장되었습니다. 수동으로 커밋하려면: `git add CLAUDE.md LESSONS.md && git commit`" 표시 후 종료

---

## Phase 4: Snap-Commit

### Step 4.1: Stage Files

Only stage Napkin Stack files that exist and were modified:

```bash
git add CLAUDE.md LESSONS.md
```

### Step 4.2: Check for Changes

```bash
git diff --cached --stat
```

If no changes are staged, inform the user: "No documentation changes to commit."

### Step 4.3: Commit

Build a commit message from the session summary:

```bash
git commit -m "docs: snapkin session sync (YYYY-MM-DD) - [1-line summary of session work]"
```

### Step 4.4: Report

Display final summary:

```markdown
## Snapkin Session Sync Complete

**Date**: YYYY-MM-DD
**Commit**: [commit hash]

| File | Section | Status | Changes |
|------|---------|--------|---------|
| CLAUDE.md | Conventions | Updated / No changes | [brief description] |
| CLAUDE.md | Session Context | Rewritten | [session focus] |
| LESSONS.md | — | Updated / No changes | [N new lessons] |

**Next Entry Point**: [from CLAUDE.md Session Context]
```

---

## Error Handling

- If git is not initialized: Inform user, skip Phase 1 git commands and Phase 4 commit
- If no Napkin Stack files exist: Suggest running `/snapkin:snapkin-init` first
- If an agent fails: Report the failure, continue with the other agent's results
- If commit fails (pre-commit hook): Report the error, do NOT retry with `--no-verify`
