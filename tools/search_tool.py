from typing import Dict, Any
from langchain_community.tools import DuckDuckGoSearchRun

def search_general_web(query: str) -> Dict[str, Any]:
    """
    Executes a general live web search query using DuckDuckGo.
    Returns data matching the unified tool interface schema.
    """
    print(f"\n[SEARCH_TOOL] Forwarding keyword query to DuckDuckGo: '{query}'")
    
    try:
        # Initialize LangChain's built-in live query runner
        search_engine = DuckDuckGoSearchRun()
        raw_results = search_engine.run(query)
        
        if not raw_results or "No good DuckDuckGo Search Result found" in raw_results:
            return {
                "source_type": "search",
                "results": [{"content": f"No web search hits returned for query: '{query}'", "source_info": "Zero Matches"}]
            }
            
        return {
            "source_type": "search",
            "results": [{
                "content": raw_results.strip(),
                "source_info": "Live DuckDuckGo Search Output"
            }]
        }
        
    except Exception as e:
        print(f"[SEARCH_TOOL_ERROR] Query runner failed: {e}")
        return {
            "source_type": "search",
            "results": [{"content": f"Search engine connection dropped: {str(e)}", "source_info": "System Fault"}]
        }