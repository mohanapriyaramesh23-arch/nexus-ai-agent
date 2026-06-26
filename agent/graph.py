from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from agent.nodes import analyze_query_node, retrieve_documents_node, generate_answer_node

# Define our Shared State Object Structure
class AgentState(TypedDict):
    query: str                # The current user query
    history: str              # Formatted history strings
    chosen_sources: List[str] # List of chosen tool targets
    retrieved_context: str    # Search results payload text
    answer: str               # The finalized output string

def create_nexus_graph():
    """
    Assembles individual functional nodes into a coordinated StateGraph state machine.
    """
    # 1. Initialize the graph framework mapped onto our custom state structure
    builder = StateGraph(AgentState)
    
    # 2. Register our concrete processing nodes
    builder.add_node("query_analyzer", analyze_query_node)
    builder.add_node("document_retriever", retrieve_documents_node)
    builder.add_node("answer_generator", generate_answer_node)
    
    # 3. Construct direct operational execution paths (Edges)
    builder.add_edge(START, "query_analyzer")
    builder.add_edge("query_analyzer", "document_retriever")
    builder.add_edge("document_retriever", "answer_generator")
    builder.add_edge("answer_generator", END)
    
    # 4. Compile our structured graph map down into an executable binary state machine
    return builder.compile()

# Single access instance for our validation execution runner
nexus_agent_executor = create_nexus_graph()