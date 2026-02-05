#!/usr/bin/env python3
"""Delete LinkedIn posts from both file system and ChromaDB."""

import sys
from pathlib import Path

import frontmatter

# Add scripts directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from index import get_collection, delete_document

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_PATH = PROJECT_ROOT / "data" / "posts"


def list_posts() -> list[dict]:
    """List all posts with basic info."""
    posts = []
    for i, md_file in enumerate(sorted(POSTS_PATH.glob("*.md")), 1):
        try:
            post = frontmatter.load(md_file)
            posts.append({
                "index": i,
                "file": md_file,
                "filename": md_file.name,
                "title": post.get("title", md_file.stem)[:50],
                "embedding_id": post.get("embedding_id", ""),
                "date": post.get("date", ""),
            })
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
    return posts


def delete_post(filename: str, dry_run: bool = False) -> dict:
    """
    Delete a post from both file system and ChromaDB.

    Args:
        filename: Filename or partial match
        dry_run: If True, don't actually delete

    Returns:
        Result dict with status
    """
    # Find matching file
    matches = []
    for md_file in POSTS_PATH.glob("*.md"):
        if filename in md_file.name or filename == md_file.stem:
            matches.append(md_file)

    if not matches:
        return {"success": False, "error": f"No file matching '{filename}'"}

    if len(matches) > 1:
        return {
            "success": False,
            "error": f"Multiple matches: {[m.name for m in matches]}",
            "matches": [m.name for m in matches],
        }

    target_file = matches[0]

    # Load to get embedding_id
    try:
        post = frontmatter.load(target_file)
        embedding_id = post.get("embedding_id")
    except Exception as e:
        return {"success": False, "error": f"Error reading file: {e}"}

    result = {
        "file": str(target_file),
        "filename": target_file.name,
        "embedding_id": embedding_id,
        "dry_run": dry_run,
    }

    if dry_run:
        result["message"] = "Would delete (dry run)"
        return result

    # Delete from ChromaDB
    if embedding_id:
        try:
            delete_document(embedding_id)
            result["chromadb_deleted"] = True
        except Exception as e:
            result["chromadb_error"] = str(e)
            result["chromadb_deleted"] = False
    else:
        result["chromadb_deleted"] = False
        result["chromadb_note"] = "No embedding_id found"

    # Delete file
    try:
        target_file.unlink()
        result["file_deleted"] = True
        result["success"] = True
    except Exception as e:
        result["file_error"] = str(e)
        result["file_deleted"] = False
        result["success"] = False

    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Delete LinkedIn posts")
    parser.add_argument("filename", nargs="?", help="Filename to delete")
    parser.add_argument("--list", "-l", action="store_true", help="List all posts")
    parser.add_argument("--dry-run", action="store_true", help="Preview without deleting")
    parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")

    args = parser.parse_args()

    if args.list or not args.filename:
        posts = list_posts()
        if not posts:
            print("No posts found.")
            return

        print(f"Found {len(posts)} posts:\n")
        for p in posts:
            print(f"{p['index']:3}. {p['filename'][:40]:<40} ({p['date']})")
        return

    # Confirm deletion
    if not args.force and not args.dry_run:
        confirm = input(f"Delete '{args.filename}'? [y/N]: ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return

    result = delete_post(args.filename, args.dry_run)

    if result.get("success"):
        print(f"✓ Deleted: {result['filename']}")
        if result.get("chromadb_deleted"):
            print(f"  - ChromaDB: removed ({result['embedding_id']})")
        else:
            print(f"  - ChromaDB: {result.get('chromadb_note', 'not removed')}")
    elif result.get("dry_run"):
        print(f"[DRY RUN] Would delete: {result['filename']}")
        print(f"  - embedding_id: {result.get('embedding_id', 'none')}")
    else:
        print(f"✗ Error: {result.get('error', 'Unknown error')}")
        if result.get("matches"):
            print("  Matches:")
            for m in result["matches"]:
                print(f"    - {m}")


if __name__ == "__main__":
    main()
