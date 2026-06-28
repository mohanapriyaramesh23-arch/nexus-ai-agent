import os
print("[GRAPH.PY] Starting graph.py compilation...")
from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import analyze_query_node, execute_tool_node, synthesize_response_node

print("[GRAPH.PY] Initializing StateGraph workflow structure...")
workflow = StateGraph(AgentState)

# Define our standardized architectural graph nodes
workflow.add_node("tool_selector", analyze_query_node)
workflow.add_node("execute_tools", execute_tool_node)
workflow.add_node("synthesizer", synthesize_response_node)

# Construct the sequential execution links
workflow.set_entry_point("tool_selector")
workflow.add_edge("tool_selector", "execute_tools")
workflow.add_edge("execute_tools", "synthesizer")
workflow.add_edge("synthesizer", END)

# Compile the final validated agent structure
nexus_agent = workflow.compile()
print("[GRAPH.PY] Day 15 multi-source graph compiled successfully!")