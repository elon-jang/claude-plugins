---
name: snapkin-workflow
description: This skill should be used when the user asks to "정리해줘", "세션 마무리", "session wrap up", "update docs", "문서 정리", "레슨 기록", "교훈 남겨", "이거 기억해둬", "snapkin", "napkin", "프로젝트 초기화", "docs sync", "세션 종료"
version: 1.0.0
---

# Snapkin Workflow

Multi-Agent Session Management Protocol. Routes user intent to the appropriate command.

## Intent Routing

Analyze the user's request and route to the correct command:

| Intent | Route To | Examples |
|--------|----------|----------|
| Full session wrap-up | `/snapkin:snapkin` | "정리해줘", "세션 마무리", "session wrap up", "docs sync", "세션 종료" |
| Quick sync | `/snapkin:snapkin quick` | "빨리 정리", "quick wrap", "간단히 커밋" |
| Review before commit | `/snapkin:snapkin review` | "확인하고 커밋", "review wrap" |
| Project initialization | `/snapkin:snapkin-init` | "프로젝트 초기화", "snapkin init", "napkin stack 만들어" |
| Quick lesson | `/snapkin:snapkin-lesson` | "레슨 기록", "교훈 남겨", "이거 기억해둬" |
| Plan update (removed) | — | "계획 변경", "플랜 업데이트" → 제거됨. `[Future]` 태그로 `/snapkin:snapkin-lesson`에 기록하세요. |

## The Napkin Stack

2 project documents managed by 3 specialized agents:

```
┌─────────────────────────────────────────┐
│              Napkin Stack                │
├──────────┬──────────────────────────────┤
│ historian│          auditor             │
│          │                              │
│ LESSONS  │ CLAUDE.md                    │
│  .md     │ (conventions + session ctx)  │
├──────────┴──────────────────────────────┤
│ validator (read-only)                   │
│ 보안 + 구조 + 중복 + 사이즈 검사        │
└─────────────────────────────────────────┘
```

## Full Session Workflow (/snapkin:snapkin)

```
┌─────────────────────────────────────────────────────────┐
│  Mode Selection: /snapkin | /snapkin quick | /snapkin review │
├─────────────────────┬───────────────────────────────────┤
│  QUICK MODE         │  FULL MODE (기본) / REVIEW MODE   │
├─────────────────────┼───────────────────────────────────┤
│ P1: git diff 수집   │ P1: git diff + docs 읽기 + 요약   │
│     CLAUDE.md만 읽기│                                   │
├─────────────────────┼───────────────────────────────────┤
│ P2: 건너뜀          │ P2: Parallel Scribble             │
│                     │ ┌──────────┐  ┌──────────┐        │
│                     │ │historian │  │ auditor  │        │
│                     │ │LESSONS.md│  │CLAUDE.md │        │
│                     │ └──────────┘  └──────────┘        │
├─────────────────────┼───────────────────────────────────┤
│ P3: 오케스트레이터가│ P3: Validator (read-only)          │
│     Session Context │ 보안+구조+중복+사이즈 검사         │
│     직접 업데이트   │ 오케스트레이터가 이슈 수정         │
├─────────────────────┼───────────────────────────────────┤
│                     │ P3.5: User Review (review만)       │
│                     │ AskUserQuestion → 커밋/검토/건너뛰기│
├─────────────────────┼───────────────────────────────────┤
│ P4: Quick Commit    │ P4: Snap-Commit                   │
│ git add CLAUDE.md   │ git add CLAUDE.md LESSONS.md      │
└─────────────────────┴───────────────────────────────────┘
```

### Phase 2: Agent Invocation

Launch both agents in a **single message** for true parallel execution:

```
Task(
    subagent_type="snapkin:historian",
    model="sonnet",
    description="Extract session lessons",
    prompt="[git diff + session summary + current LESSONS.md]"
)

Task(
    subagent_type="snapkin:auditor",
    model="sonnet",
    description="Audit conventions and session context",
    prompt="[git diff + session summary + current CLAUDE.md]"
)
```

### Phase 3: Validation (Main Agent)

After both agents complete, the orchestrator performs:

1. **Security scan**: Grep for API keys, passwords, tokens, secrets, .env values
2. **Session Context structure**: Verify SNAPKIN markers and required sub-sections exist
3. **Dedup check**: Ensure no duplicate entries across files
4. **Fix any issues** found before committing

### Phase 4: Commit

```bash
git add CLAUDE.md LESSONS.md
git commit -m "docs: snapkin session sync (YYYY-MM-DD) - [Summary]"
```

## Quick Reference

| When | Use |
|------|-----|
| End of session | `/snapkin:snapkin` |
| Quick sync (no lessons) | `/snapkin:snapkin quick` or `/snapkin:snapkin quick "message"` |
| Review before commit | `/snapkin:snapkin review` |
| New project | `/snapkin:snapkin-init` |
| Learn something | `/snapkin:snapkin-lesson [tag] text` |
