import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_qdrant_client() -> QdrantClient:
    """Initializes and returns a Qdrant client using credentials from environment variables."""
    host = os.getenv("QDRANT_HOST")
    api_key = os.getenv("QDRANT_API_KEY")
    
    if not host or not api_key:
        raise ValueError("[ERROR] Missing QDRANT_HOST or QDRANT_API_KEY inside environment configuration.")
        
    return QdrantClient(url=host, api_key=api_key)

def search_vector_store(query_text: str, collection_name: str = "nexus_documents", limit: int = 5) -> List[Dict[str, Any]]:
    """
    Converts a raw string query into a vector embedding using Gemini,
    searches Qdrant, and returns a structured list of matching chunks with metadata.
    """
    if not query_text.strip():
        print("[WARNING] Empty search query received. Returning empty result matrix.")
        return []

    client = get_qdrant_client()

    # Graceful handling if the collection does not exist yet or is completely missing
    try:
        if not client.collection_exists(collection_name):
            print(f"[WARNING] Requested collection '{collection_name}' does not exist in Qdrant instance.")
            return []
    except Exception as e:
        print(f"[ERROR] Failed to communicate with Qdrant collection layers: {str(e)}")
        return []

    # Initialize the identical embedding engine used during Day 4 ingestion
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    try:
        # Convert text query into its matching 3072-dimension coordinate vector
        query_vector = embeddings_model.embed_query(query_text)
        
        # Execute similarity search in Qdrant using modern query_points interface
        search_results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit
        ).points
        
        structured_results = []
        for point in search_results:
            # Safely extract the original chunk text and structural fields we stored in the payload
            payload = point.payload if point.payload else {}
            chunk_text = payload.get("page_content", "[No content text field recovered]")
            
            # Reconstruct metadata dict by isolating fields that aren't page_content
            metadata = {k: v for k, v in payload.items() if k != "page_content"}
            
            structured_results.append({
                "chunk_text": chunk_text,
                "score": point.score,
                "metadata": metadata
            })
            
        return structured_results

    except Exception as e:
        print(f"[ERROR] Exception triggered during vector similarity lookup execution: {str(e)}")
        return []