# =====================================================================
# CRITICAL WINDOWS COMPLIANCE: PyPDFLoader imports must stay at the absolute 
# top before any google-genai libraries to prevent memory access faults.
# =====================================================================
from langchain_community.document_loaders import PyPDFLoader

import os
from typing import Dict, Any
from retrieval.hybrid_retriever import hybrid_search
from retrieval.reranker import rerank_candidates

def search_pdf_documents(query: str) -> Dict[str, Any]:
    """
    Wraps the Day 8 high-precision hybrid search and cross-encoder 
    reranking pipeline into a standardized, reusable tool interface.
    """
    print(f"\n[PDF_TOOL] Executing search wrapper for query: '{query}'")
    
    try:
        # Execute our Stage 1 hybrid retrieval fusion engine
        candidates = hybrid_search(query, limit=5)
        
        # Execute our Stage 2 deep cross-encoder re-scoring layer
        reranked_results = rerank_candidates(query, candidates)
        
        # Format the top matched segments into our unified tool envelope
        formatted_results = []
        for item in reranked_results:
            text = item.get("chunk_text") or item.get("text") or item.get("page_content") or ""
            metadata = item.get("metadata", {})
            page_num = metadata.get("page", "Unknown Page")
            
            formatted_results.append({
                "content": text.strip(),
                "source_info": f"Local Document Ref - Page {page_num}"
            })
            
        return {
            "source_type": "pdf",
            "results": formatted_results
        }
        
    except Exception as e:
        print(f"[PDF_TOOL_ERROR] Search pipeline failed: {e}")
        return {
            "source_type": "pdf",
            "results": [{"content": f"Error executing document search: {str(e)}", "source_info": "System Fault"}]
        }