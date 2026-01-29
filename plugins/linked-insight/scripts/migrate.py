#!/usr/bin/env python3
"""Migrate existing markdown files to the new format with frontmatter and embeddings."""

import hashlib
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import frontmatter
import yaml

# Add scripts directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from embed import get_document_embedding
from index import add_document, get_collection, save_metadata_cache, load_metadata_cache

PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_PATH = PROJECT_ROOT / "source"
POSTS_PATH = PROJECT_ROOT / "data" / "posts"


def extract_metadata_from_content(content: str, filename: str) -> dict:
    """
    Extract metadata from markdown content.

    Args:
        content: Raw markdown content
        filename: Original filename

    Returns:
        Dictionary with extracted metadata
    """
    lines = content.strip().split("\n")

    # Extract title from first line or filename
    title = lines[0].strip() if lines else filename
    # Remove leading emoji and formatting
    title = re.sub(r"^[🏗️📌🎯💡✨🔥⚡️🚀]+\s*", "", title)
    title = title[:100]  # Limit title length

    # Extract hashtags/tags from content
    tags = re.findall(r"#(\w+)", content)
    tags = list(set(tags))[:10]  # Dedupe and limit

    # Extract URLs
    urls = re.findall(r"https?://[^\s\)\]]+", content)
    url = urls[0] if urls else ""

    # Try to detect author (patterns like "by Author" or "Author:")
    author = ""
    author_patterns = [
        r"by\s+([가-힣A-Za-z\s]+)",
        r"작성자[:\s]+([가-힣A-Za-z\s]+)",
    ]
    for pattern in author_patterns:
        match = re.search(pattern, content)
        if match:
            author = match.group(1).strip()
            break

    # Use file modification time as date fallback
    return {
        "title": title,
        "author": author,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "url": url,
        "tags": tags,
    }


def generate_ai_notes(content: str, tags: list) -> str:
    """Generate AI notes section (simple heuristic-based summary)."""
    lines = content.strip().split("\n")

    # Simple extractive summary: first meaningful paragraph
    summary_lines = []
    for line in lines[1:6]:  # Skip title, take up to 5 lines
        line = line.strip()
        if line and not line.startswith("#") and len(line) > 20:
            summary_lines.append(line)
            if len(" ".join(summary_lines)) > 150:
                break

    summary = " ".join(summary_lines)[:200]
    if len(summary) > 190:
        summary = summary[:190] + "..."

    tags_str = ", ".join(tags) if tags else "general"

    return f"""---
## AI Notes
- **Summary**: {summary}
- **Topics**: {tags_str}
"""


def migrate_file(
    source_file: Path,
    dry_run: bool = False,
    skip_embedding: bool = False,
) -> Optional[dict]:
    """
    Migrate a single markdown file.

    Args:
        source_file: Path to source file
        dry_run: If True, don't write files or update DB
        skip_embedding: If True, skip embedding generation

    Returns:
        Migration result dict or None if failed
    """
    try:
        # Read source file
        with open(source_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if already has frontmatter
        if content.startswith("---"):
            post = frontmatter.loads(content)
            metadata = dict(post.metadata)
            body = post.content
        else:
            # Extract metadata from content
            metadata = extract_metadata_from_content(content, source_file.stem)
            body = content

        # Generate embedding ID
        content_hash = hashlib.md5(body.encode()).hexdigest()[:8]
        embedding_id = f"{source_file.stem[:20]}-{content_hash}"
        metadata["embedding_id"] = embedding_id

        # Create post with frontmatter
        post = frontmatter.Post(body, **metadata)

        # Add AI notes if not present
        if "## AI Notes" not in body and "## AI 노트" not in body:
            ai_notes = generate_ai_notes(body, metadata.get("tags", []))
            post.content = body + "\n" + ai_notes

        if not dry_run:
            # Save to posts directory
            POSTS_PATH.mkdir(parents=True, exist_ok=True)
            dest_file = POSTS_PATH / source_file.name
            with open(dest_file, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))

            # Generate embedding and store in ChromaDB
            if not skip_embedding:
                embedding_content = f"{metadata.get('title', '')}\n{body}"
                add_document(
                    content=embedding_content,
                    metadata=metadata,
                    doc_id=embedding_id,
                )
                # Rate limiting for Gemini API (15 RPM for free tier)
                time.sleep(4.5)

        return {
            "source": str(source_file),
            "dest": str(POSTS_PATH / source_file.name),
            "embedding_id": embedding_id,
            "metadata": metadata,
        }

    except Exception as e:
        print(f"Error migrating {source_file}: {e}")
        return None


def migrate_all(
    dry_run: bool = False,
    skip_embedding: bool = False,
) -> list[dict]:
    """
    Migrate all markdown files from source to posts.

    Args:
        dry_run: If True, don't write files or update DB
        skip_embedding: If True, skip embedding generation

    Returns:
        List of migration results
    """
    results = []
    source_files = list(SOURCE_PATH.glob("*.md"))

    print(f"Found {len(source_files)} files to migrate")
    print(f"Dry run: {dry_run}, Skip embedding: {skip_embedding}")
    print("-" * 40)

    for i, source_file in enumerate(source_files):
        print(f"[{i+1}/{len(source_files)}] Migrating: {source_file.name}")
        result = migrate_file(source_file, dry_run, skip_embedding)
        if result:
            results.append(result)
            print(f"  -> {result['embedding_id']}")
        else:
            print(f"  -> FAILED")

    # Save metadata cache
    if not dry_run:
        metadata_cache = {r["embedding_id"]: r["metadata"] for r in results}
        save_metadata_cache(metadata_cache)

    print("-" * 40)
    print(f"Migrated {len(results)}/{len(source_files)} files")

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Migrate markdown files")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without making changes",
    )
    parser.add_argument(
        "--skip-embedding",
        action="store_true",
        help="Skip embedding generation (faster for testing)",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Migrate single file",
    )

    args = parser.parse_args()

    if args.file:
        source_file = Path(args.file)
        if not source_file.exists():
            source_file = SOURCE_PATH / args.file
        result = migrate_file(source_file, args.dry_run, args.skip_embedding)
        if result:
            print(f"Migrated: {result['embedding_id']}")
    else:
        migrate_all(args.dry_run, args.skip_embedding)


if __name__ == "__main__":
    main()
