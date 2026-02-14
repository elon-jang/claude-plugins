#!/usr/bin/env python3
"""Statistics for LinkedIn posts collection."""

import json
from collections import Counter
from pathlib import Path

import frontmatter

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_PATH = PROJECT_ROOT / "data" / "posts"


def get_all_posts() -> list[dict]:
    """Load all posts with metadata."""
    posts = []
    for md_file in sorted(POSTS_PATH.glob("*.md")):
        try:
            post = frontmatter.load(md_file)
            posts.append({
                "file": str(md_file),
                "filename": md_file.name,
                "metadata": dict(post.metadata),
                "content_length": len(post.content),
            })
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
    return posts


def get_stats() -> dict:
    """Generate comprehensive statistics."""
    posts = get_all_posts()

    if not posts:
        return {"total": 0, "message": "No posts found"}

    # Basic stats
    total = len(posts)

    # Tag distribution
    all_tags = []
    for p in posts:
        tags = p["metadata"].get("tags", [])
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except:
                tags = [tags] if tags else []
        all_tags.extend(tags)

    tag_counts = Counter(all_tags)
    posts_with_tags = sum(1 for p in posts if p["metadata"].get("tags"))

    # Author distribution
    authors = [p["metadata"].get("author", "") for p in posts]
    authors = [a for a in authors if a]  # Filter empty
    author_counts = Counter(authors)
    posts_with_author = len(authors)

    # URL coverage
    posts_with_url = sum(1 for p in posts if p["metadata"].get("url"))

    # Published date coverage
    posts_with_published_date = sum(1 for p in posts if p["metadata"].get("published_date"))

    # Date distribution
    dates = [p["metadata"].get("date", "") for p in posts]
    dates = [d for d in dates if d]
    date_counts = Counter(dates)

    # Content length stats
    lengths = [p["content_length"] for p in posts]
    avg_length = sum(lengths) // len(lengths) if lengths else 0

    return {
        "total": total,
        "tags": {
            "unique_count": len(tag_counts),
            "total_usage": len(all_tags),
            "posts_with_tags": posts_with_tags,
            "coverage_pct": round(posts_with_tags / total * 100, 1),
            "top_10": tag_counts.most_common(10),
        },
        "authors": {
            "unique_count": len(author_counts),
            "posts_with_author": posts_with_author,
            "coverage_pct": round(posts_with_author / total * 100, 1),
            "top_5": author_counts.most_common(5),
        },
        "urls": {
            "posts_with_url": posts_with_url,
            "coverage_pct": round(posts_with_url / total * 100, 1),
        },
        "published_dates": {
            "posts_with_published_date": posts_with_published_date,
            "coverage_pct": round(posts_with_published_date / total * 100, 1),
        },
        "dates": {
            "unique_dates": len(date_counts),
            "date_distribution": date_counts.most_common(10),
        },
        "content": {
            "avg_length": avg_length,
            "min_length": min(lengths) if lengths else 0,
            "max_length": max(lengths) if lengths else 0,
        },
    }


def format_stats(stats: dict) -> str:
    """Format statistics for display."""
    if stats.get("total", 0) == 0:
        return "No posts found."

    lines = []
    lines.append(f"## LinkedIn Posts 통계\n")
    lines.append(f"**총 {stats['total']}개 글**\n")

    # Tags
    lines.append("### 태그")
    t = stats["tags"]
    lines.append(f"- 고유 태그: {t['unique_count']}개")
    lines.append(f"- 태그 있는 글: {t['posts_with_tags']}개 ({t['coverage_pct']}%)")
    if t["top_10"]:
        lines.append("- Top 10:")
        for tag, count in t["top_10"]:
            lines.append(f"  - `{tag}`: {count}")
    lines.append("")

    # Authors
    lines.append("### 작성자")
    a = stats["authors"]
    lines.append(f"- 고유 작성자: {a['unique_count']}명")
    lines.append(f"- 작성자 있는 글: {a['posts_with_author']}개 ({a['coverage_pct']}%)")
    if a["top_5"]:
        lines.append("- Top 5:")
        for author, count in a["top_5"]:
            lines.append(f"  - {author}: {count}")
    lines.append("")

    # URLs
    lines.append("### URL")
    u = stats["urls"]
    lines.append(f"- URL 있는 글: {u['posts_with_url']}개 ({u['coverage_pct']}%)")
    lines.append("")

    # Published dates
    lines.append("### 게시일")
    pd = stats["published_dates"]
    lines.append(f"- 게시일 있는 글: {pd['posts_with_published_date']}개 ({pd['coverage_pct']}%)")
    lines.append("")

    # Content
    lines.append("### 컨텐츠 길이")
    c = stats["content"]
    lines.append(f"- 평균: {c['avg_length']:,}자")
    lines.append(f"- 최소: {c['min_length']:,}자")
    lines.append(f"- 최대: {c['max_length']:,}자")

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="LinkedIn posts statistics")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    stats = get_stats()

    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        print(format_stats(stats))


if __name__ == "__main__":
    main()
