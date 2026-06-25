from typing import List, Dict, Any
from retrieval.vector_search import search_vector_store
from retrieval.bm25_search import search_bm25
from retrieval.reranker import rerank_candidates  # Import Stage 2 component

def hybrid_search(query_text: str, collection_name: str = "nexus_documents", limit: int = 5) -> List[Dict[str, Any]]:
    """
    Executes a complete Two-Stage Retrieval Pipeline:
    Stage 1: Gathers and blends documents using Vector Search, BM25 Search, and RRF.
    Stage 2: Reranks the top candidate pool using a deep Cross-Encoder attention model.
    """
    # K constant buffer parameter (standard industry value to balance rank weights)
    K = 60
    
    # ==========================================
    # STAGE 1: HYBRID CANDIDATE GATHERING (RRF)
    # ==========================================
    
    # Use a small multiplier safety factor for candidate pulling
    candidate_limit = limit * 2
    
    try:
        vector_results = search_vector_store(query_text, collection_name=collection_name, limit=candidate_limit)
    except Exception:
        vector_results = []
        
    try:
        bm25_results = search_bm25(query_text, collection_name=collection_name, limit=candidate_limit)
    except Exception:
        bm25_results = []

    # Track combined items and compute aggregate RRF scores
    rrf_scores = {}      # Maps chunk_text -> calculated float score
    chunk_registry = {}  # Maps chunk_text -> original metadata

    # Process Vector List
    for rank, match in enumerate(vector_results, 1):
        text = match.get("chunk_text") or match.get("text") or match.get("page_content")
        if not text:
            continue
            
        if text not in rrf_scores:
            rrf_scores[text] = 0.0
            chunk_registry[text] = match.get("metadata", {})
            
        rrf_scores[text] += 1.0 / (rank + K)

    # Process BM25 List
    for rank, match in enumerate(bm25_results, 1):
        text = match.get("chunk_text") or match.get("text") or match.get("page_content")
        if not text:
            continue
            
        if text not in rrf_scores:
            rrf_scores[text] = 0.0
            chunk_registry[text] = match.get("metadata", {})
            
        rrf_scores[text] += 1.0 / (rank + K)

    # If neither search returned any results, exit early gracefully
    if not rrf_scores:
        return []

    # Convert the mapped registry into a structured candidates list
    candidates = []
    for text, score in rrf_scores.items():
        candidates.append({
            "chunk_text": text,
            "score": float(score),
            "metadata": chunk_registry[text]
        })

    # Pre-sort Stage 1 results by RRF score to prune down to an optimal shortlist
    candidates.sort(key=lambda x: x["score"], reverse=True)
    shortlist = candidates[:candidate_limit]

    # ==========================================
    # STAGE 2: CROSS-ENCODER RERANKING
    # ==========================================
    print(f"[INFO] Passing {len(shortlist)} candidates to Stage 2 Cross-Encoder Reranker...")
    reranked_results = rerank_candidates(query_text, shortlist)

    # Return up to the requested top limit, now fully optimized
    return reranked_results[:limit]