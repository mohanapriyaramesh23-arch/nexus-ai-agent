from typing import Dict, Any
from google import genai
from google.genai import types
from retrieval.hybrid_retriever import hybrid_search
from retrieval.reranker import rerank_candidates

def analyze_query_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 1: Evaluates the user query using Gemini to determine the required search targets.
    Built extensibly so new tools can be added later without refactoring.
    """
    print("\n--- [NODE] Entering analyze_query_node ---")
    query = state.get("query", "")
    
    system_instruction = (
        "You are an routing analyzer for an AI agent ecosystem. Your job is to classify "
        "which information sources are absolutely required to answer a user's question.\n\n"
        "AVAILABLE SOURCES:\n"
        "- 'local_docs': Use this for questions regarding system architectures, enterprise "
        "specifications, engineering chapters, manuals, and technical internal metrics.\n\n"
        "STRICT COMPLIANCE:\n"
        "Return ONLY one of these exact strings matching your choice: ['local_docs']. "
        "Do not wrap your answer in markdown formatting or add any punctuation."
    )
    
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Determine source routing for query: {query}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0
            )
        )
        # Parse output safely into an extensible list matching our target design
        decision = response.text.strip().lower()
        chosen_sources = ["local_docs"] if "local_docs" in decision else ["local_docs"]
    except Exception as e:
        print(f"[WARNING] Query Analyzer failed: {e}. Defaulting to local_docs.")
        chosen_sources = ["local_docs"]

    print(f"[ANALYZER DECISION] Selected Routing Sources: {chosen_sources}")
    return {"chosen_sources": chosen_sources}


def retrieve_documents_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 2: Executes our Day 8 high-precision retrieval pipeline using the state's query.
    """
    print("\n--- [NODE] Entering retrieve_documents_node ---")
    query = state.get("query", "")
    
    print(f"[RETRIEVAL] Passing query down to Day 8 Stage-1 Hybrid Engine...")
    # Trigger Stage-1 (Vector + BM25 Fusion RRF)
    candidates = hybrid_search(query, limit=5)
    
    print(f"[RETRIEVAL] Passing shortlist down to Day 8 Stage-2 Reranker Engine...")
    # Trigger Stage-2 (Precise structural sequence re-scoring matcher)
    reranked_results = rerank_candidates(query, candidates)
    
    # Consolidate text chunks into a clean text block context payload
    context_blocks = []
    for rank, item in enumerate(reranked_results, start=1):
        chunk_text = item.get("chunk_text") or item.get("text") or item.get("page_content") or ""
        context_blocks.append(f"[Document Chunk {rank}]: {chunk_text}")
        
    retrieved_context = "\n\n".join(context_blocks)
    return {"retrieved_context": retrieved_context}


def generate_answer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Node 3: Synthesizes the final answer using the retrieved context or conversational logs.
    """
    print("\n--- [NODE] Entering generate_answer_node ---")
    query = state.get("query", "")
    context = state.get("retrieved_context", "No context retrieved.")
    history = state.get("history", "No prior conversation history.")
    
    system_instruction = (
        "You are the core Nexus system assistant. Your task is to provide a complete, technical, "
        "and accurate answer to the user's current question using the provided context blocks and history.\n"
        "If the context completely answers the question, prioritize it explicitly."
    )
    
    prompt = f"""
Conversation History:
{history}

Retrieved Reference Context:
{context}

Current Active User Question: {query}

Please output your refined technical answer:"""

    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3
        )
    )
    
    return {"answer": response.text.strip()}