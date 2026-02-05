# CLAUDE.md — Snapkin

## Code Style

- Language: Markdown / Shell (Claude Code Plugin)
- Formatting: Standard Markdown

## Conventions

- Agent definitions go in `agents/` as `.md` files
- Commands go in `commands/` as `.md` files
- Skills go in `skills/` as subdirectories with templates
- Each agent has strict file ownership — no cross-writes
- `README.md` is read-only — not auto-written by any agent

## Execution Modes

| Mode | Command | Behavior |
|------|---------|----------|
| **Full** | `/snapkin` | 4-phase workflow: dispatch → parallel agents → validator → commit |
| **Quick** | `/snapkin quick [msg]` | Session Context only, no agents, fast commit |
| **Review** | `/snapkin review` | Full workflow + user confirmation before commit |

See `commands/snapkin.md` for detailed mode specifications.

## Agent Architecture

| Agent | Owns | Model | Responsibility |
|-------|------|-------|----------------|
| **historian** | LESSONS.md | Sonnet | Extract lessons, categorize, detect automation candidates |
| **auditor** | CLAUDE.md | Sonnet | Update conventions, rewrite Session Context with P0-P3 priorities |
| **validator** | (read-only) | Haiku | Security scan, structure validation, duplicate detection, size limits |

## Important Rules

- Never commit secrets, API keys, or credentials
- Always run tests before committing
- Document variable names only, never actual values
- Session Context section in CLAUDE.md is fully rewritten each sync, not appended
- Plugin cache at `~/.claude/plugins/cache/snapkin/` must be cleared manually during development
- Cache clear only takes effect in new sessions (skill list loaded at session start)
- Next Entry Point uses P0-P3 priority tags: P0 (blocking), P1 (critical), P2 (important), P3 (nice-to-have)
- At least 1 Next Entry Point required, max 5 entries, highest priority first

## File Structure

```
snapkin/
├── .claude-plugin/
│   ├── plugin.json         # Claude Code plugin metadata
│   └── marketplace.json    # Marketplace submission metadata
├── .gitignore              # Git ignore patterns
├── README.md               # User-facing project documentation (read-only)
├── CLAUDE.md               # Code conventions + session context
├── LESSONS.md              # Session learnings, categorized insights
├── agents/
│   ├── auditor.md          # CLAUDE.md owner (conventions + session context)
│   ├── historian.md        # LESSONS.md owner
│   └── validator.md        # Read-only validator (Phase 3)
├── commands/
│   ├── snapkin.md          # Full session wrap-up command
│   ├── snapkin-init.md     # Initialize Napkin Stack
│   └── snapkin-lesson.md   # Quick lesson entry
├── docs/
│   └── comparison-session-wrap.md  # Architecture comparison with session-wrap
└── skills/
    └── snapkin-workflow/
        ├── SKILL.md        # Intent routing, workflow documentation
        └── templates/
            ├── CLAUDE.template.md   # Template for CLAUDE.md initialization
            └── LESSONS.template.md  # Template for LESSONS.md initialization
```

## Dependencies

- Claude Code CLI
- Git (for snap-commit phase)

## Development

```bash
# Install
git clone https://github.com/elon-jang/snapkin.git

# Run
claude  # /snapkin:* commands auto-activate

# Test
# Manual testing via Claude Code CLI

# Clear plugin cache during development (requires new session to take effect)
rm -rf ~/.claude/plugins/cache/snapkin/
```

<!-- SNAPKIN:SESSION_CONTEXT_START -->
## Session Context

> Current state snapshot. Fully rewritten each session sync by the auditor agent.

### Last Sync

- **Date**: 2026-02-05
- **Session**: Quick mode test

### Active Work

- Testing Quick mode workflow — no file changes since last full sync
- Validating `/snapkin quick "message"` execution path

### Blockers

No blockers.

### Next Entry Point

- **[P2]** Test Snapkin v2 in real session — validate Quick mode, Review mode, validator Phase 3 — `/snapkin quick "test run"`
- **[P2]** Verify P0-P3 priority format in Next Entry Point output — `agents/auditor.md:L100-120`
- **[P3]** Document blog post comparing wrap vs snapkin approach — `docs/blog-wrap-vs-snapkin.md` (currently untracked)
- **[P3]** Consider marketplace submission after v2 stabilization

### Recent Changes

- `agents/validator.md` — New read-only validator agent (security, structure, dedup, size)
- `agents/historian.md` — Added Deep Extraction + Automation Candidate Detection
- `agents/auditor.md` — P0-P3 priority format for Next Entry Point
- `commands/snapkin.md` — Mode dispatch (Full/Quick/Review), 4-phase workflow
- `docs/comparison-session-wrap.md` — Architecture comparison document
- `skills/snapkin-workflow/SKILL.md` — Updated workflow diagrams
- `templates/CLAUDE.template.md` — P3 tag format example
- `README.md` — Added cache-clearing note to Development section
- `LESSONS.md` — Session wrap lessons (in progress)

### Key Files

```
commands/snapkin.md              — Mode dispatch + 4-phase orchestration
agents/validator.md              — Phase 3 validator (security, structure, dedup)
agents/auditor.md                — CLAUDE.md owner with P0-P3 priorities
agents/historian.md              — LESSONS.md owner with deep extraction
skills/snapkin-workflow/SKILL.md — Intent routing + workflow documentation
docs/comparison-session-wrap.md  — Architecture comparison with session-wrap
CLAUDE.md                        — Conventions + session context
```
<!-- SNAPKIN:SESSION_CONTEXT_END -->
