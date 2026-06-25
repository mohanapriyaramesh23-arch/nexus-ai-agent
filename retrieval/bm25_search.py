import os
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from qdrant_client import QdrantClient

def get_qdrant_client() -> QdrantClient:
    """
    Initializes and returns a Qdrant client using credentials from environment variables.
    Matches the exact connection pattern established in vector_search.py.
    """
    host = os.getenv("QDRANT_HOST")
    api_key = os.getenv("QDRANT_API_KEY")
    
    if not host or not api_key:
        raise ValueError("[ERROR] Missing QDRANT_HOST or QDRANT_API_KEY environment variables.")
        
    return QdrantClient(url=host, api_key=api_key)

def search_bm25(query_text: str, collection_name: str = "nexus_documents", limit: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieves all text chunks from Qdrant, builds an in-memory BM25 index,
    and returns keyword-matched results matching the vector search return shape.
    """
    client = get_qdrant_client()
    
    # 1. Handle missing/empty collection edge case gracefully
    try:
        if not client.collection_exists(collection_name):
            print(f"[WARN] Collection '{collection_name}' not found.")
            return []
    except Exception:
        # Fallback handling to ensure it never crashes the agent pipeline
        return []
        
    # 2. Retrieve all stored points from Qdrant to build local index
    # We set a large limit to grab all chunks in this small-scale system
    try:
        response, _ = client.scroll(
            collection_name=collection_name,
            with_payload=True,
            with_vectors=False,
            limit=1000
        )
    except Exception as e:
        print(f"[ERROR] Failed to retrieve points from Qdrant: {str(e)}")
        return []

    if not response:
        return []

    # 3. Extract text content and build parallel tracking lists
    corpus_tokens = []
    chunk_registry = []
    
    for point in response:
        payload = point.payload if point.payload else {}
        
        # Pull text from page_content (handles the Day 4/5 upload schema)
        text_content = payload.get("page_content")
        
        # Gracefully track chunks missing the key due to legacy debug runs
        if not text_content:
            text_content = "[No content text field recovered]"
            
        metadata = {k: v for k, v in payload.items() if k != "page_content"}
        
        # Tokenize the chunk text (split into lowercased words) for BM25
        tokens = text_content.lower().split()
        corpus_tokens.append(tokens)
        
        # Save original data for scoring reconstruction
        chunk_registry.append({
            "chunk_text": text_content,
            "metadata": metadata
        })

    if not corpus_tokens:
        return []

    # 4. Initialize the rank-bm25 index in memory
    bm25 = BM25Okapi(corpus_tokens)
    
    # Tokenize the incoming user query
    query_tokens = query_text.lower().split()
    
    # Compute raw BM25 keyword scores across all documents
    bm25_scores = bm25.get_scores(query_tokens)
    
    # 5. Pair scores with chunks, filter out non-matches, and sort by highest score
    scored_results = []
    for idx, score in enumerate(bm25_scores):
        if score > 0.0:  # Only include chunks that matched at least one word
            chunk_data = chunk_registry[idx]
            scored_results.append({
                "chunk_text": chunk_data["chunk_text"],
                "score": float(score),
                "metadata": chunk_data["metadata"]
            })
            
    # Sort descending by BM25 score
    scored_results.sort(key=lambda x: x["score"], reverse=True)
    
    # Return up to requested limit
    return scored_results[:limit]