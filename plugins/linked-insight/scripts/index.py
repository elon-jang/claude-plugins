#!/usr/bin/env python3
"""ChromaDB index management for LinkedIn posts."""

import json
import os
import uuid
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings

from embed import get_document_embedding, get_query_embedding

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
CHROMA_PATH = PROJECT_ROOT / "data" / "chroma"
METADATA_PATH = PROJECT_ROOT / "data" / "metadata.json"

# Collection name
COLLECTION_NAME = "linkedin_posts"


def get_client() -> chromadb.PersistentClient:
    """Get ChromaDB persistent client."""
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(CHROMA_PATH),
        settings=Settings(anonymized_telemetry=False),
    )


def get_collection(client: Optional[chromadb.PersistentClient] = None) -> chromadb.Collection:
    """Get or create the LinkedIn posts collection."""
    if client is None:
        client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "LinkedIn posts with Gemini embeddings"},
    )


def add_document(
    content: str,
    metadata: dict,
    doc_id: Optional[str] = None,
) -> str:
    """
    Add a document to the collection.

    Args:
        content: Document text content
        metadata: Document metadata (author, date, tags, etc.)
        doc_id: Optional document ID (generated if not provided)

    Returns:
        Document ID
    """
    collection = get_collection()

    if doc_id is None:
        doc_id = str(uuid.uuid4())

    # Generate embedding
    embedding = get_document_embedding(content)

    # Ensure metadata values are valid types for ChromaDB
    clean_metadata = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)):
            clean_metadata[key] = value
        elif isinstance(value, list):
            clean_metadata[key] = json.dumps(value)  # Store lists as JSON strings
        elif value is None:
            clean_metadata[key] = ""
        else:
            clean_metadata[key] = str(value)

    collection.add(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[content],
        metadatas=[clean_metadata],
    )

    return doc_id


def update_document(
    doc_id: str,
    content: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> None:
    """Update an existing document."""
    collection = get_collection()

    update_kwargs = {"ids": [doc_id]}

    if content is not None:
        embedding = get_document_embedding(content)
        update_kwargs["embeddings"] = [embedding]
        update_kwargs["documents"] = [content]

    if metadata is not None:
        clean_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                clean_metadata[key] = value
            elif isinstance(value, list):
                clean_metadata[key] = json.dumps(value)
            elif value is None:
                clean_metadata[key] = ""
            else:
                clean_metadata[key] = str(value)
        update_kwargs["metadatas"] = [clean_metadata]

    collection.update(**update_kwargs)


def delete_document(doc_id: str) -> None:
    """Delete a document from the collection."""
    collection = get_collection()
    collection.delete(ids=[doc_id])


def search_semantic(
    query: str,
    n_results: int = 5,
) -> list[dict]:
    """
    Semantic search using embeddings.

    Args:
        query: Search query
        n_results: Number of results to return

    Returns:
        List of results with document, metadata, and distance
    """
    collection = get_collection()

    query_embedding = get_query_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    # Format results
    formatted = []
    for i in range(len(results["ids"][0])):
        metadata = results["metadatas"][0][i]
        # Parse JSON-encoded lists back
        for key, value in metadata.items():
            if isinstance(value, str) and value.startswith("["):
                try:
                    metadata[key] = json.loads(value)
                except json.JSONDecodeError:
                    pass

        formatted.append({
            "id": results["ids"][0][i],
            "document": results["documents"][0][i],
            "metadata": metadata,
            "distance": results["distances"][0][i],
        })

    return formatted


def get_all_documents() -> list[dict]:
    """Get all documents in the collection."""
    collection = get_collection()
    results = collection.get(include=["documents", "metadatas"])

    formatted = []
    for i in range(len(results["ids"])):
        metadata = results["metadatas"][i]
        for key, value in metadata.items():
            if isinstance(value, str) and value.startswith("["):
                try:
                    metadata[key] = json.loads(value)
                except json.JSONDecodeError:
                    pass

        formatted.append({
            "id": results["ids"][i],
            "document": results["documents"][i],
            "metadata": metadata,
        })

    return formatted


def get_document_count() -> int:
    """Get number of documents in collection."""
    collection = get_collection()
    return collection.count()


def save_metadata_cache(metadata: dict) -> None:
    """Save metadata to JSON cache file."""
    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def load_metadata_cache() -> dict:
    """Load metadata from JSON cache file."""
    if not METADATA_PATH.exists():
        return {}
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    # Test connection
    client = get_client()
    collection = get_collection(client)
    print(f"Collection: {collection.name}")
    print(f"Document count: {collection.count()}")
