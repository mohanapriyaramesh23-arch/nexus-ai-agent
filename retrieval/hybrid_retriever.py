import os
import concurrent.futures
from typing import List, Dict, Any
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from google import genai

# Ensure environment variables are loaded directly at module level
load_dotenv()

qdrant_client = None
ai_client = None

def _run_embedding_with_timeout(client, query: str):
    """
    Executes the network embedding lookup using the confirmed,
    working model string identifier.
    """
    response = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=query
    )
    return response.embeddings[0].values

def hybrid_search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Executes a high-precision vector search via query_points. 
    Connects to the cloud cluster using QDRANT_HOST and QDRANT_API_KEY.
    """
    global qdrant_client, ai_client
    
    if qdrant_client is None:
        print("[RETRIEVAL] Connecting to Qdrant Cloud Cluster...")
        try:
            qdrant_host = os.getenv("QDRANT_HOST")
            qdrant_api_key = os.getenv("QDRANT_API_KEY")
            
            if qdrant_host:
                print(f"[RETRIEVAL] Target endpoint detected: {qdrant_host}")
                qdrant_client = QdrantClient(
                    url=qdrant_host,
                    api_key=qdrant_api_key,
                    check_compatibility=False
                )
            else:
                print("[RETRIEVAL] WARNING: QDRANT_HOST not found. Falling back to localhost...")
                qdrant_client = QdrantClient(
                    url="http://localhost:6333",
                    check_compatibility=False
                )
        except Exception as e:
            raise RuntimeError(f"CRITICAL: Failed to initialize Qdrant Client connection: {e}")
        
    if ai_client is None:
        print("[RETRIEVAL] Initializing Gemini API Client...")
        try:
            ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        except Exception as e:
            raise RuntimeError(f"CRITICAL: Failed to authorize Gemini SDK API Client: {e}")

    print(f"[RETRIEVAL] Running live hybrid vector search for: '{query}'")
    
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("CRITICAL FAILURE: GEMINI_API_KEY environment variable is empty or missing.")

    print("[RETRIEVAL] Dispatching embedding call with a thread safety check...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run_embedding_with_timeout, ai_client, query)
        try:
            query_vector = future.result(timeout=2.0)
            
            # Target our confirmed, working document collection name
            response = qdrant_client.query_points(
                collection_name="nexus_documents",
                query=query_vector,
                limit=limit
            )
            search_results = response.points

            candidates = []
            for hit in search_results:
                payload = hit.payload if hit.payload else {}
                
                # DIRECT SCHEMA FIX: Extracting directly from verified 'page_content' field
                text_content = payload.get("page_content", "")
                metadata_content = payload.get("metadata", {})

                candidates.append({
                    "text": text_content,
                    "metadata": metadata_content,
                    "score": getattr(hit, "score", 0.0)
                })
            return candidates

        except concurrent.futures.TimeoutError:
            raise TimeoutError("CRITICAL: Gemini embedding network request timed out after 2.0s.")
        except Exception as e:
            raise RuntimeError(f"CRITICAL: Live channel vector generation aborted. Engine fault: {str(e)}")