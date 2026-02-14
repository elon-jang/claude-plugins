#!/usr/bin/env python3
"""Gemini embedding wrapper for LinkedIn posts."""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

MODEL_NAME = "gemini-embedding-001"


def _get_client():
    """Get Gemini client (lazy initialization)."""
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable not set")

    from google import genai
    return genai.Client(api_key=GOOGLE_API_KEY)


def get_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    """
    Generate embedding for text using Gemini.

    Args:
        text: Text to embed
        task_type: One of RETRIEVAL_DOCUMENT, RETRIEVAL_QUERY, SEMANTIC_SIMILARITY

    Returns:
        List of floats representing the embedding vector
    """
    client = _get_client()

    # Map task types
    from google.genai import types
    task_map = {
        "RETRIEVAL_DOCUMENT": "RETRIEVAL_DOCUMENT",
        "RETRIEVAL_QUERY": "RETRIEVAL_QUERY",
        "SEMANTIC_SIMILARITY": "SEMANTIC_SIMILARITY",
    }

    result = client.models.embed_content(
        model=MODEL_NAME,
        contents=text,
        config=types.EmbedContentConfig(task_type=task_map.get(task_type, task_type)),
    )
    return result.embeddings[0].values


def get_query_embedding(query: str) -> list[float]:
    """Generate embedding optimized for query/retrieval."""
    return get_embedding(query, task_type="RETRIEVAL_QUERY")


def get_document_embedding(document: str) -> list[float]:
    """Generate embedding optimized for document storage."""
    return get_embedding(document, task_type="RETRIEVAL_DOCUMENT")


def batch_embed(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """
    Generate embeddings for multiple texts.

    Note: Gemini API has rate limits (15 RPM for free tier).
    For large batches, consider adding delays.
    """
    embeddings = []
    for text in texts:
        embedding = get_embedding(text, task_type)
        embeddings.append(embedding)
    return embeddings


if __name__ == "__main__":
    # Test embedding
    test_text = "Claude Code는 AI 코딩 도구입니다."
    try:
        embedding = get_document_embedding(test_text)
        print(f"Embedding dimension: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure GOOGLE_API_KEY is set in your environment.")
