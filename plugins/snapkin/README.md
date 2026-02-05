# Snapkin

Multi-Agent Session Management Protocol — 2 parallel agents that sync session work into 2 project documents (the "Napkin Stack").

## The Napkin Stack

| Document | Purpose | Owner Agent |
|----------|---------|-------------|
| `CLAUDE.md` | Code conventions + session context snapshot | auditor |
| `LESSONS.md` | Session learnings, categorized insights | historian |

> `README.md` is read-only — not auto-written by any agent.

## Commands

| Command | Description |
|---------|-------------|
| `/snapkin:snapkin` | Full session wrap-up — 2 agents update both docs in parallel, then commit |
| `/snapkin:snapkin-init` | Initialize the 2 Napkin Stack documents for a new project |
| `/snapkin:snapkin-lesson [category] <text>` | Quickly add a lesson entry to LESSONS.md |

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Phase 1: Dispatch                                       │
│  Collect git diff, read existing docs, build summary     │
├──────────────────────────────────────────────────────────┤
│  Phase 2: Parallel Scribble                              │
│  ┌────────────┐  ┌──────────────────────────────┐        │
│  │ historian   │  │           auditor            │        │
│  │ LESSONS.md  │  │ CLAUDE.md (conventions +     │        │
│  │             │  │   session context)           │        │
│  └────────────┘  └──────────────────────────────┘        │
├──────────────────────────────────────────────────────────┤
│  Phase 3: Synthesize & Validate                          │
│  Security scan, session context check, dedup             │
├──────────────────────────────────────────────────────────┤
│  Phase 4: Snap-Commit                                    │
│  git add + commit with formatted message                 │
└──────────────────────────────────────────────────────────┘
```

## Lesson Categories

| Tag | Meaning |
|-----|---------|
| `[Error-Fix]` | Bug encountered and how it was resolved |
| `[Decision]` | Architectural or design choice made |
| `[Insight]` | Non-obvious discovery about the codebase |
| `[Domain]` | Domain-specific knowledge learned |
| `[Prompt]` | Effective prompting patterns discovered |
| `[Future]` | Ideas or improvements to revisit later |

## Installation

### 로컬 (개발/직접 사용)

이 저장소를 clone하고 해당 폴더에서 Claude Code를 실행하면 자동 인식됩니다.

```bash
git clone https://github.com/elon-jang/snapkin.git
cd snapkin
claude  # /snapkin:* 커맨드 자동 활성화
```

### 원격 (다른 사용자)

```bash
# Step 1: Add marketplace
/plugin marketplace add github:elon-jang/snapkin

# Step 2: Install plugin
/plugin install snapkin@snapkin
```

## Quick Start

1. `/snapkin:snapkin-init` — Generate the 2 base documents
2. Work on your project as usual
3. `/snapkin:snapkin` — Run full session wrap-up before ending

## Development

```bash
# After editing plugin files (agents, commands, skills), clear cache:
rm -rf ~/.claude/plugins/cache/snapkin/
# Then start a new Claude Code session for changes to take effect
```

## Design Principles

- **Strict file ownership**: Each agent only writes to its assigned files — no conflicts
- **Session Context section in CLAUDE.md is a snapshot**: Fully rewritten each sync, not appended
- **No secrets**: Agents document variable names only, never values
- **Parallel by default**: Both agents run simultaneously for speed
- **Validation in orchestrator**: Security and consistency checks run in the main agent, not a sub-agent
