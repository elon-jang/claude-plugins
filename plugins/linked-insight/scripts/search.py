#!/usr/bin/env python3
"""Hybrid search (keyword + semantic) for LinkedIn posts."""

import argparse
import re
from pathlib import Path
from typing import Optional

import frontmatter

from index import search_semantic, get_all_documents

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_PATH = PROJECT_ROOT / "data" / "posts"


def search_keyword(query: str, n_results: int = 10) -> list[dict]:
    """
    Keyword search through markdown files.

    Args:
        query: Search query (space-separated terms)
        n_results: Maximum number of results

    Returns:
        List of matching documents with score
    """
    results = []
    terms = query.lower().split()

    for md_file in POSTS_PATH.glob("*.md"):
        try:
            post = frontmatter.load(md_file)
            content = post.content.lower()
            title = post.get("title", "").lower()
            tags = post.get("tags", [])
            if isinstance(tags, str):
                tags = [tags]
            tags_str = " ".join(tags).lower()

            # Calculate match score
            score = 0
            full_text = f"{title} {content} {tags_str}"

            for term in terms:
                # Count occurrences
                count = full_text.count(term)
                if count > 0:
                    score += count
                    # Bonus for title match
                    if term in title:
                        score += 5
                    # Bonus for tag match
                    if term in tags_str:
                        score += 3

            if score > 0:
                results.append({
                    "id": post.get("embedding_id", md_file.stem),
                    "document": post.content,
                    "metadata": dict(post.metadata),
                    "score": score,
                    "file": str(md_file),
                })
        except Exception as e:
            print(f"Error reading {md_file}: {e}")

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:n_results]


def reciprocal_rank_fusion(
    keyword_results: list[dict],
    semantic_results: list[dict],
    k: int = 60,
) -> list[dict]:
    """
    Combine keyword and semantic results using Reciprocal Rank Fusion (RRF).

    Args:
        keyword_results: Results from keyword search
        semantic_results: Results from semantic search
        k: RRF constant (default 60)

    Returns:
        Combined and re-ranked results
    """
    scores = {}
    docs = {}

    # Score from keyword results
    for rank, result in enumerate(keyword_results):
        doc_id = result["id"]
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
        docs[doc_id] = result

    # Score from semantic results
    for rank, result in enumerate(semantic_results):
        doc_id = result["id"]
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
        if doc_id not in docs:
            docs[doc_id] = result

    # Sort by combined score
    ranked_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

    results = []
    for doc_id in ranked_ids:
        doc = docs[doc_id]
        doc["rrf_score"] = scores[doc_id]
        results.append(doc)

    return results


def search_hybrid(
    query: str,
    n_results: int = 5,
    mode: str = "hybrid",
) -> list[dict]:
    """
    Hybrid search combining keyword and semantic search.

    Args:
        query: Search query
        n_results: Number of results to return
        mode: "keyword", "semantic", or "hybrid"

    Returns:
        List of search results
    """
    if mode == "keyword":
        return search_keyword(query, n_results)
    elif mode == "semantic":
        return search_semantic(query, n_results)
    else:  # hybrid
        keyword_results = search_keyword(query, n_results * 2)
        semantic_results = search_semantic(query, n_results * 2)
        return reciprocal_rank_fusion(keyword_results, semantic_results)[:n_results]


def format_results(results: list[dict], verbose: bool = False) -> str:
    """Format search results for display."""
    if not results:
        return "No results found."

    lines = []
    for i, result in enumerate(results, 1):
        meta = result.get("metadata", {})
        title = meta.get("title", "Untitled")
        author = meta.get("author", "Unknown")
        date = meta.get("date", "")
        tags = meta.get("tags", [])
        if isinstance(tags, str):
            try:
                import json
                tags = json.loads(tags)
            except:
                tags = [tags]

        # Score info
        score_info = ""
        if "rrf_score" in result:
            score_info = f" (RRF: {result['rrf_score']:.4f})"
        elif "distance" in result:
            score_info = f" (distance: {result['distance']:.4f})"
        elif "score" in result:
            score_info = f" (score: {result['score']})"

        lines.append(f"\n{i}. **{title}**{score_info}")
        lines.append(f"   Author: {author} | Date: {date}")
        if tags:
            lines.append(f"   Tags: {', '.join(tags)}")

        if verbose:
            # Show preview
            preview = result.get("document", "")[:200]
            if len(result.get("document", "")) > 200:
                preview += "..."
            lines.append(f"   Preview: {preview}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search LinkedIn posts")
    parser.add_argument("query", nargs="+", help="Search query")
    parser.add_argument(
        "--mode", "-m",
        choices=["keyword", "semantic", "hybrid"],
        default="hybrid",
        help="Search mode (default: hybrid)",
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=5,
        help="Number of results (default: 5)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show document preview",
    )

    args = parser.parse_args()
    query = " ".join(args.query)

    print(f"Searching for: {query}")
    print(f"Mode: {args.mode}")
    print("-" * 40)

    results = search_hybrid(query, args.limit, args.mode)
    print(format_results(results, args.verbose))


if __name__ == "__main__":
    main()
