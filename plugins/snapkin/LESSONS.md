# LESSONS — Snapkin

> Session learnings and insights. Each entry is tagged with a category.

## Categories

| Tag | Meaning |
|-----|---------|
| `[Error-Fix]` | Bug encountered and how it was resolved |
| `[Decision]` | Architectural or design choice made |
| `[Insight]` | Non-obvious discovery about the codebase |
| `[Domain]` | Domain-specific knowledge learned |
| `[Prompt]` | Effective prompting patterns discovered |
| `[Future]` | Ideas or improvements to revisit later |

---

## 2026-02-05

- **[Decision]** Reduced Napkin Stack from 5 files to 2 core files (CLAUDE.md, LESSONS.md) — removed PLAN.md, CONTEXT.md, and README.template.md from agent ownership to simplify maintenance burden and reduce agent confusion.
- **[Decision]** Session context embedded in CLAUDE.md using HTML comment markers (SNAPKIN:SESSION_CONTEXT_START/END) instead of separate CONTEXT.md file — keeps temporal state co-located with rules while remaining invisible in rendered Markdown.
- **[Decision]** Made README.md read-only (user-controlled, not agent-written) — prevents agents from overwriting user documentation and establishes clear ownership boundary.
- **[Decision]** Removed Strategist agent entirely, consolidated responsibilities to Auditor and Historian — reduces from 3 agents to 2, simplifying the workflow and reducing coordination overhead.
- **[Decision]** Deleted snapkin-plan command along with PLAN.md — explicit plan tracking removed in favor of lightweight session-based workflow.
- **[Insight]** Agent file ownership is a critical boundary — strict write permissions (Auditor owns CLAUDE.md, Historian owns LESSONS.md) prevent conflicts and make the system more predictable.
- **[Insight]** Fewer files in the Napkin Stack reduces cognitive load for both agents and users — simpler mental model with just two auto-maintained files (CLAUDE.md, LESSONS.md).
- **[Error-Fix]** Claude Code subagent routing requires fully qualified names in `subagent_type` parameter — using short names like "historian" instead of "snapkin:historian" in commands/snapkin.md and skills/snapkin-workflow/SKILL.md breaks subagent dispatch.
- **[Decision]** Git diff baseline for snapkin command changed from `HEAD~1` to last snapkin sync commit detection — provides accurate view of all session work instead of just last commit, especially when multiple commits occur during session.
- **[Decision]** Session Context size capped at ~40 lines with max 10 items per list (Recent Changes, Key Files) — prevents unbounded growth in CLAUDE.md embedded context that could overwhelm agent prompts.
- **[Decision]** Added Key Files section to Session Context alongside Recent Changes — provides richer context for agents beyond just modified files, includes core documentation and templates.
- **[Error-Fix]** snapkin-lesson command was missing Write tool in allowed-tools — command could not actually write to LESSONS.md despite being its primary purpose.
- **[Decision]** Added routing table entry for removed /snapkin:plan and /snapkin-plan triggers in SKILL.md — provides migration guidance for users attempting to use deprecated command.
- **[Insight]** Claude Code plugin cache is located at `~/.claude/plugins/cache/<plugin-name>/` and must be manually cleared with `rm -rf` during development to see command/skill changes — cache clear only takes effect in new sessions since skill list loads at session start, not mid-session.
- **[Decision]** Snapkin v2: Added 3 execution modes (Full/Quick/Review) via command argument parsing — single command with mode dispatch provides better UX than multiple commands.
- **[Decision]** Validator agent uses haiku model instead of sonnet — read-only validation tasks (pattern matching, structure checks) don't need sonnet's reasoning depth, optimizes cost and latency.
- **[Decision]** Git baseline detection changed from exact string "snapkin session sync" to regex "snapkin.*sync" — catches both full and quick sync commits for accurate session diff.
- **[Decision]** P0-P3 priority tags added to Next Entry Point: P0 (blocking), P1 (critical), P2 (important), P3 (nice-to-have) — makes session handoff explicit with clear urgency levels.
- **[Insight]** Quick mode only updates temporal Session Context sections (Last Sync, Session, Active Work), preserving cumulative sections (Blockers, Next Entry Point) — temporal vs cumulative distinction enables fast checkpoints without losing cross-session state.
- **[Insight]** Read-only validation agent pattern: validator checks and reports, orchestrator fixes — Single Responsibility Principle for agents makes prompts simpler and debugging easier.
- **[Decision]** Review mode adds Phase 3.5 user confirmation between validator and snap-commit — displays summary with file changes, validation results, commit message preview, awaits y/n input before proceeding to Phase 4.
- **[Insight]** Mode dispatch pattern: parse all bash arguments at command start, detect keywords ("quick", "review"), set boolean flags, branch workflow before Phase 1 — enables single command with multiple execution paths.
- **[Decision]** Validator integrated as dedicated Phase 3 after parallel agents (Phase 2) and before commit (Phase 4) — separates security/structure validation from agent writing responsibilities, enables independent haiku model optimization.
- **[Insight]** Historian Deep Extraction section added to agent prompt — explicit instructions to capture failed attempts, process improvements, hard-to-find information that agents typically skip over during session analysis.
- **[Insight]** Automation Candidate Detection added to historian agent — scans for repetitive manual work patterns, recurring error fixes, workflow friction points and records them as [Future] automation suggestions.
- **[Decision]** Created docs/comparison-session-wrap.md as architectural reference — documents why Snapkin v2 differs from session-wrap predecessor (file ownership, embedded context, validator model), preserves design rationale for future maintainers.
