import os
import pprint
from typing import Dict, Any
from retrieval.hybrid_retriever import hybrid_search
from retrieval.reranker import rerank_candidates

def query_hybrid_knowledgebase(query: str) -> Dict[str, Any]:
    """
    Day 16 Diagnostic Interface for Local PDF Knowledgebase Document queries.
    Prints the raw inner data shape of the first result object to catch parsing bugs.
    """
    print(f"[PDF_TOOL] Executing search wrapper for query: '{query}'")
    
    raw_nodes = hybrid_search(query, limit=5)
    
    # DIAGNOSTIC PRINT: If we got items back, dump the exact data structure of the first item
    if raw_nodes:
        print("\n=======================================================")
        print("🔍 RAW RETRIEVED OBJECT SHAPE FROM HYBRID_SEARCH:")
        print("=======================================================")
        pprint.pprint(raw_nodes[0])
        print("=======================================================\n")
    else:
        print("\n⚠️ [PDF_TOOL ALERT] hybrid_search returned an empty list! No records retrieved.\n")
        
    reranked_nodes = rerank_candidates(query, raw_nodes)
    
    results_list = []
    for node in reranked_nodes:
        page_num = node.get("metadata", {}).get("page", "Unknown")
        results_list.append({
            "content": node.get("text", ""),
            "source_info": f"Local Document Ref - Page {page_num}"
        })
        
    return {
        "source_type": "pdf",
        "results": results_list
    }