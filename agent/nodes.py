import os
import re
from typing import List
print("[NODES.PY] Top of nodes.py reached. Importing dependencies...")
from agent.state import AgentState

print("[NODES.PY] Loading multi-source tool extensions...")
from tools.pdf_tool import query_hybrid_knowledgebase
from tools.youtube_tool import get_youtube_transcript
from tools.web_scraper_tool import scrape_web_page
from tools.news_tool import fetch_live_news
from tools.search_tool import search_general_web

print("[NODES.PY] Setting up isolated local environment routing configurations...")

def _multi_tool_heuristic_router(query: str) -> List[str]:
    """
    Day 16 Multi-Tool Router: Scans user intent and maps it to target tools.
    """
    q = query.lower()
    chosen_tools = []
    
    if any(keyword in q for keyword in ["architecture", "layer", "reranker", "pdf", "document", "specification"]):
        chosen_tools.append("pdf")
    if any(keyword in q for keyword in ["youtube", "youtu.be", "video", "transcript", "subtitle"]):
        chosen_tools.append("youtube")
    if any(keyword in q for keyword in ["http", "https", "scrape", "link", "webpage"]):
        chosen_tools.append("web")
    if any(keyword in q for keyword in ["news", "headline", "breaking", "current event"]):
        chosen_tools.append("news")
        
    # Default fallback to general search if no specific tags match
    if not chosen_tools or any(keyword in q for keyword in ["weather", "search", "lookup", "who is", "what is"]):
        chosen_tools.append("search")
        
    return list(dict.fromkeys(chosen_tools))

def analyze_query_node(state: AgentState) -> dict:
    """Tool Selector Node."""
    query_to_analyze = state.get("rewritten_query") or state.get("query")
    print(f"\n[NODE: TOOL SELECTOR] Routing analysis for query: '{query_to_analyze}'")
    selected_list = _multi_tool_heuristic_router(query_to_analyze)
    print(f"[NODE: TOOL SELECTOR DECISION] Mapped intent targets to tool sequence: {selected_list}")
    return {"selected_tools": selected_list}

def execute_tool_node(state: AgentState) -> dict:
    """
    Action Router Node: Sequentially invokes chosen tools. 
    Guarantees isolation so a single tool crash won't bring down the entire graph runtime.
    """
    tools_to_run = state.get("selected_tools", ["search"])
    query = state.get("rewritten_query") or state.get("query")
    
    print(f"[NODE: EXECUTE TOOL] Processing channel loop for: {tools_to_run}")
    aggregated_results = []
    
    for tool in tools_to_run:
        print(f" -> Active Channel: Launching execution wrapper for '{tool}'...")
        try:
            raw_results = []
            
            # --- Simulated Failure Hooks for Testing Part A ---
            if "FAIL_NEWS" in query and tool == "news":
                raise RuntimeError("Simulated News Wire Connection Timeout (504 Gateway error)")
            if "FAIL_PDF" in query and tool == "pdf":
                raise KeyError("Simulated Database Authentication Failure (401 Unauthorized)")
            
            # --- Normal Production Execution Paths ---
            if tool == "pdf":
                tool_output = query_hybrid_knowledgebase(query)
                raw_results = tool_output.get("results", [])
            elif tool == "youtube":
                tool_output = get_youtube_transcript(query)
                raw_results = tool_output.get("results", [])
            elif tool == "web":
                tool_output = scrape_web_page(query)
                raw_results = tool_output.get("results", [])
            elif tool == "news":
                tool_output = fetch_live_news(query)
                raw_results = tool_output.get("results", [])
            else:  # search
                tool_output = search_general_web(query)
                raw_results = tool_output.get("results", [])
                
            print(f" -> Channel Success: Collected {len(raw_results)} records from '{tool}'.")
            aggregated_results.extend(raw_results)
            
        except Exception as e:
            print(f" ❌ [CHANNEL FAILURE] '{tool}' encountered an execution anomaly: {str(e)}")
            # Inject a failure context indicator payload instead of letting the program crash
            aggregated_results.append({
                "content": f"ERROR: Component tool source execution failed due to: {str(e)}",
                "source_info": f"FAILED_TOOL:{tool.upper()}"
            })
            
    return {"tool_raw_results": aggregated_results}

def synthesize_response_node(state: AgentState) -> dict:
    """
    Multi-Source Response Synthesizer Node: Blends successful outputs 
    and appends explicit system notices for failed tool nodes.
    """
    query = state.get("query")
    tools_used = state.get("selected_tools", [])
    payloads = state.get("tool_raw_results", [])
    
    print(f"[NODE: SYNTHESIZER] Blending data layers from tools {tools_used}")
    
    # Check for systemic empty results
    if not payloads:
        return {"final_answer": "I was unable to aggregate any context documents to formulate an answer."}
        
    constructed_answer = f"According to the multi-source coordination matrix, I verified information across the target channels.\n\n"
    
    # Group regular tool contents vs failed tool streams
    failed_tools = [p.get("content") for p in payloads if "FAILED_TOOL:" in p.get("source_info", "")]
    pdf_records = [p for p in payloads if "Local Document" in p.get("source_info", "")]
    youtube_records = [p for p in payloads if "YouTube" in p.get("source_info", "") or "Video" in p.get("source_info", "")]
    news_records = [p for p in payloads if "News" in p.get("source_info", "") and "FAILED_TOOL" not in p.get("source_info")]
    search_records = [p for p in payloads if "DuckDuckGo" in p.get("source_info", "") or "Search" in p.get("source_info", "")]
    
    # 1. Append valid source contents
    if pdf_records:
        constructed_answer += "### 📄 Internal Documentation Findings:\n"
        for p in pdf_records:
            constructed_answer += f"- **[{p.get('source_info')}]**: {p.get('content')}\n"
        constructed_answer += "\n"
        
    if youtube_records:
        constructed_answer += "### 🎥 Video Analytics Summary:\n"
        for p in youtube_records:
            constructed_answer += f"- **[{p.get('source_info')}]**: {p.get('content')}\n"
        constructed_answer += "\n"
        
    if news_records:
        constructed_answer += "### 📰 Live News Wire Updates:\n"
        for p in news_records:
            constructed_answer += f"- **[{p.get('source_info')}]**: {p.get('content')}\n"
        constructed_answer += "\n"
        
    if search_records:
        constructed_answer += "### 🌐 Live Web Search Telemetry:\n"
        for p in search_records:
            constructed_answer += f"- **[{p.get('source_info')}]**: {p.get('content')}\n"
        constructed_answer += "\n"
        
    # 2. Append explicit service disruption alerts for any failed components
    if failed_tools:
        constructed_answer += "### ⚠️ System Component Disruption Notices:\n"
        for err_msg in failed_tools:
            constructed_answer += f"- {err_msg}\n"
            
    return {"final_answer": constructed_answer}