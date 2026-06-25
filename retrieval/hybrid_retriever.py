from typing import List, Dict, Any
from retrieval.vector_search import search_vector_store
from retrieval.bm25_search import search_bm25

def hybrid_search(query_text: str, collection_name: str = "nexus_documents", limit: int = 5) -> List[Dict[str, Any]]:
    """
    Executes both vector similarity search and BM25 keyword search, unifies them
    using Reciprocal Rank Fusion (RRF), and returns a single optimized list.
    """
    # K constant buffer parameter (standard industry value to balance rank weights)
    K = 60
    
    # 1. Gather results from both underlying retrieval mechanisms
    # We retrieve slightly more items (limit * 2) to ensure a robust overlap pool for ranking
    try:
        vector_results = search_vector_store(query_text, collection_name=collection_name, limit=limit * 2)
    except Exception:
        vector_results = []
        
    try:
        bm25_results = search_bm25(query_text, collection_name=collection_name, limit=limit * 2)
    except Exception:
        bm25_results = []

    # 2. Track combined items and compute aggregate RRF scores
    # We use chunk_text as our unique identifier string to cross-reference matches
    rrf_scores = {}      # Maps chunk_text -> calculated float score
    chunk_registry = {}  # Maps chunk_text -> original metadata and structural properties

    # Process Vector List
    for rank, match in enumerate(vector_results, 1):
        text = match.get("chunk_text")
        if not text:
            continue
            
        if text not in rrf_scores:
            rrf_scores[text] = 0.0
            chunk_registry[text] = match.get("metadata", {})
            
        rrf_scores[text] += 1.0 / (rank + K)

    # Process BM25 List
    for rank, match in enumerate(bm25_results, 1):
        text = match.get("chunk_text")
        if not text:
            continue
            
        if text not in rrf_scores:
            rrf_scores[text] = 0.0
            chunk_registry[text] = match.get("metadata", {})
            
        rrf_scores[text] += 1.0 / (rank + K)

    # 3. If neither search returned any results, exit gracefully with an empty list
    if not rrf_scores:
        return []

    # 4. Convert the mapped registry into a structured list of dictionaries
    fused_results = []
    for text, score in rrf_scores.items():
        fused_results.append({
            "chunk_text": text,
            "score": float(score),
            "metadata": chunk_registry[text]
        })

    # 5. Sort the unified results so that highest RRF scores sit at the top
    fused_results.sort(key=lambda x: x["score"], reverse=True)

    # Return up to the requested top limit
    return fused_results[:limit]