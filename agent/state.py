from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    """
    Main state vector tracking the multi-tool routing and synthesis pipeline.
    """
    query: str                         # Original raw user input string
    rewritten_query: str               # Optimized or cleaned query string (optional)
    selected_tools: List[str]          # Day 15: Array of all tools chosen for parallel/sequential execution
    tool_raw_results: List[Dict[str, Any]] # Consolidated repository of all pulled source context records
    final_answer: str                  # Ultimate synthesized anchored output answer string