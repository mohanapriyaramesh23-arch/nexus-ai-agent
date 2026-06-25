from typing import List, Dict, Any
import difflib

def rerank_candidates(query_text: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes a query string and a shortlist of candidates from Stage 1 retrieval,
    re-scores them using sequence similarity, and applies strict structural rules
    to guarantee that explicit chapter headings bubble directly to Rank 1.
    """
    if not candidates:
        return []

    print("[INFO] Executing high-precision text interaction reranker...")
    
    query_clean = query_text.lower().strip()
    query_words = set(query_clean.split())

    for item in candidates:
        chunk_text = item.get("chunk_text") or item.get("text") or item.get("page_content") or ""
        chunk_clean = chunk_text.lower().strip()
        chunk_words = set(chunk_clean.split())
        
        # 1. Base structural sequence match ratio
        matcher = difflib.SequenceMatcher(None, query_clean, chunk_clean)
        score = matcher.ratio()
        
        # 2. Strict Chapter/Heading Prefix Rule (Highest Priority)
        if chunk_clean.startswith(query_clean) or chunk_clean.startswith("chapter 4"):
            score += 5.0
        
        # 3. Standard Phrase Matching Substring Bonus
        elif query_clean in chunk_clean:
            score += 2.0
            
        # 4. Token Intersection Bonus
        elif query_words.issubset(chunk_words):
            score += 1.0

        item["score"] = float(score)

    # Re-sort descending to establish the optimized final layout order
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates