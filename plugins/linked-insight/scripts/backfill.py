#!/usr/bin/env python3
"""Backfill and fix metadata for existing LinkedIn posts."""

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import frontmatter

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_PATH = PROJECT_ROOT / "data" / "posts"

# --- Tag backfill config ---

KEYWORD_TO_TAG = {
    "claude code": "claude-code", "클로드 코드": "claude-code",
    "claude": "claude-code",
    "바이브 코딩": "vibe-coding", "vibe coding": "vibe-coding",
    "에이전트": "ai-agent", "agent": "ai-agent",
    "mcp": "mcp",
    "스타트업": "startup", "startup": "startup",
    "해커톤": "hackathon", "hackathon": "hackathon",
    "플러그인": "plugin", "plugin": "plugin",
    "멀티 에이전트": "multi-agent", "multi-agent": "multi-agent",
    "터미널": "terminal", "terminal": "terminal",
    "productivity": "productivity", "생산성": "productivity",
    "linkedin": "linkedin", "링크드인": "linkedin",
    "코딩": "coding", "coding": "coding",
    "개발": "development", "development": "development",
    "커리어": "career", "career": "career",
    "ai tool": "ai-tools", "ai 도구": "ai-tools",
    "llm": "llm",
    "openai": "openai",
    "gemini": "gemini",
    "자동화": "automation", "automation": "automation",
    "글쓰기": "writing", "writing": "writing",
    "투자": "investment",
    "saas": "saas",
    "hook": "hook",
    "headless": "headless",
    "tmux": "terminal",
    "context7": "context7",
    "임베딩": "embedding",
    "검색": "search",
    "figma": "figma", "pencil": "pencil",
    "인터뷰": "interview",
    "학습": "learning",
    "notebooklm": "notebooklm", "노트북lm": "notebooklm",
    "구글": "google",
}

JUNK_TAGS = {
    "google_vignette", "utm_source", "utm_medium", "utm_campaign",
    "utm_term", "utm_content", "lipi", "lici", "rcm",
}

# Filename fixes: old_name -> new_name
FILENAME_FIXES = {
    " Figma 킬러앱 Pencil이 출시.md": "Figma 킬러앱 Pencil이 출시.md",
    "laude Code -> oh my opencode -> Pencil로 넘어갑니다.md": "Claude Code -> oh my opencode -> Pencil로 넘어갑니다.md",
}


def get_all_posts() -> list[dict]:
    """Load all posts with metadata and content."""
    posts = []
    for md_file in sorted(POSTS_PATH.glob("*.md")):
        try:
            post = frontmatter.load(md_file)
            posts.append({
                "file": md_file,
                "filename": md_file.name,
                "post": post,
                "metadata": dict(post.metadata),
                "content": post.content,
            })
        except Exception as e:
            print(f"  Error reading {md_file.name}: {e}", file=sys.stderr)
    return posts


def extract_tags_from_content(content: str, title: str = "") -> list[str]:
    """Extract tags from content using keyword matching."""
    text = (title + " " + content).lower()
    tag_scores: Counter = Counter()

    for keyword, tag in KEYWORD_TO_TAG.items():
        count = text.count(keyword.lower())
        if count > 0:
            tag_scores[tag] += count

    # Return top 3-5 tags
    top = tag_scores.most_common(5)
    if len(top) < 3:
        return [t for t, _ in top]  # Return even if < 3
    return [t for t, _ in top]


def fix_tags(post_data: dict, dry_run: bool) -> list[str]:
    """Fix empty/junk tags. Returns list of changes made."""
    changes = []
    post = post_data["post"]
    md_file: Path = post_data["file"]
    tags = post.metadata.get("tags", [])

    if isinstance(tags, str):
        try:
            import json
            tags = json.loads(tags)
        except Exception:
            tags = [tags] if tags else []

    # Remove junk tags
    original_tags = list(tags)
    cleaned_tags = [t for t in tags if t not in JUNK_TAGS]
    removed = set(original_tags) - set(cleaned_tags)
    if removed:
        changes.append(f"  Removed junk tags: {removed}")
        tags = cleaned_tags

    # Backfill empty tags
    if not tags:
        title = post.metadata.get("title", "")
        new_tags = extract_tags_from_content(post.content, title)
        if new_tags:
            changes.append(f"  Added tags: {new_tags}")
            tags = new_tags
        else:
            changes.append(f"  WARNING: Could not generate tags")

    if changes and not dry_run:
        post.metadata["tags"] = tags
        md_file.write_text(frontmatter.dumps(post), encoding="utf-8")

    return changes


def fix_dates(post_data: dict, dry_run: bool) -> list[str]:
    """Fix 2025-01/02 dates to 2026."""
    changes = []
    post = post_data["post"]
    md_file: Path = post_data["file"]
    date_str = str(post.metadata.get("date", ""))

    if re.match(r"^2025-0[12]-\d{2}$", date_str):
        new_date = "2026" + date_str[4:]
        changes.append(f"  Date: {date_str} → {new_date}")
        if not dry_run:
            post.metadata["date"] = new_date
            md_file.write_text(frontmatter.dumps(post), encoding="utf-8")

    return changes


def fix_filenames(dry_run: bool) -> list[str]:
    """Fix known bad filenames."""
    changes = []
    for old_name, new_name in FILENAME_FIXES.items():
        old_path = POSTS_PATH / old_name
        new_path = POSTS_PATH / new_name
        if old_path.exists():
            changes.append(f"  Rename: '{old_name}' → '{new_name}'")
            if not dry_run:
                old_path.rename(new_path)
        elif new_path.exists():
            changes.append(f"  Already fixed: '{new_name}'")
    return changes


def report_empty_authors(posts: list[dict]) -> list[str]:
    """Report posts with empty author field."""
    empty = [p for p in posts if not p["metadata"].get("author")]
    if not empty:
        return ["  All posts have authors."]
    lines = [f"  {len(empty)} posts with empty author:"]
    for p in empty:
        lines.append(f"    - {p['filename']}")
    return lines


def report_empty_urls(posts: list[dict]) -> list[str]:
    """Report posts with empty URL field."""
    empty = [p for p in posts if not p["metadata"].get("url")]
    if not empty:
        return ["  All posts have URLs."]
    lines = [f"  {len(empty)} posts with empty URL:"]
    for p in empty:
        lines.append(f"    - {p['filename']}")
    return lines


def report_duplicate_urls(posts: list[dict]) -> list[str]:
    """Report posts sharing the same URL."""
    url_map: dict[str, list[str]] = defaultdict(list)
    for p in posts:
        url = p["metadata"].get("url", "")
        if url:
            url_map[url].append(p["filename"])

    dupes = {url: files for url, files in url_map.items() if len(files) > 1}
    if not dupes:
        return ["  No duplicate URLs found."]

    lines = [f"  {len(dupes)} duplicate URL(s):"]
    for url, files in dupes.items():
        lines.append(f"    URL: {url}")
        for f in files:
            lines.append(f"      - {f}")
    return lines


def run_backfill(mode: str):
    """Run backfill in specified mode: dry-run, apply, or report."""
    posts = get_all_posts()
    print(f"Loaded {len(posts)} posts.\n")

    if mode == "report":
        print("=== Empty Authors (manual fix needed) ===")
        for line in report_empty_authors(posts):
            print(line)
        print()

        print("=== Empty URLs (manual fix needed) ===")
        for line in report_empty_urls(posts):
            print(line)
        print()

        print("=== Duplicate URLs ===")
        for line in report_duplicate_urls(posts):
            print(line)
        return

    dry_run = mode == "dry-run"
    tag_prefix = "[DRY RUN] " if dry_run else ""

    # 1. Fix filenames first
    print(f"=== {tag_prefix}Filename Fixes ===")
    fname_changes = fix_filenames(dry_run)
    if fname_changes:
        for line in fname_changes:
            print(line)
    else:
        print("  No filename fixes needed.")
    print()

    # Reload posts after filename fixes (paths may have changed)
    if not dry_run and fname_changes:
        posts = get_all_posts()

    # 2. Fix dates
    print(f"=== {tag_prefix}Date Fixes ===")
    date_count = 0
    for p in posts:
        changes = fix_dates(p, dry_run)
        if changes:
            date_count += 1
            print(f"  {p['filename']}")
            for line in changes:
                print(line)
    if date_count == 0:
        print("  No date fixes needed.")
    else:
        print(f"  Total: {date_count} files")
    print()

    # 3. Fix tags (empty + junk)
    print(f"=== {tag_prefix}Tag Fixes ===")
    tag_count = 0
    for p in posts:
        changes = fix_tags(p, dry_run)
        if changes:
            tag_count += 1
            print(f"  {p['filename']}")
            for line in changes:
                print(f"  {line}")
    if tag_count == 0:
        print("  No tag fixes needed.")
    else:
        print(f"  Total: {tag_count} files")
    print()

    # 4. Always show report section
    print("=== Report (manual fix needed) ===")
    print()
    print("--- Empty Authors ---")
    # Reload for accurate report after fixes
    if not dry_run:
        posts = get_all_posts()
    for line in report_empty_authors(posts):
        print(line)
    print()
    print("--- Empty URLs ---")
    for line in report_empty_urls(posts):
        print(line)
    print()
    print("--- Duplicate URLs ---")
    for line in report_duplicate_urls(posts):
        print(line)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Backfill and fix post metadata")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    group.add_argument("--apply", action="store_true", help="Apply auto-fixes")
    group.add_argument("--report", action="store_true", help="Show manual-fix report only")

    args = parser.parse_args()

    if args.dry_run:
        run_backfill("dry-run")
    elif args.apply:
        run_backfill("apply")
    elif args.report:
        run_backfill("report")


if __name__ == "__main__":
    main()
