import os
import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_qdrant_client() -> QdrantClient:
    """Initializes and returns a Qdrant client using credentials from environment variables."""
    host = os.getenv("QDRANT_HOST")
    api_key = os.getenv("QDRANT_API_KEY")
    
    if not host or not api_key:
        raise ValueError("[ERROR] Missing QDRANT_HOST or QDRANT_API_KEY inside environment configuration.")
        
    return QdrantClient(url=host, api_key=api_key)

def ensure_collection_exists(client: QdrantClient, collection_name: str = "nexus_documents"):
    """
    Checks if the Qdrant collection exists. If it does not, creates it safely once.
    This guarantees no existing collection data is ever deleted or overwritten.
    """
    # Check if collection already exists in Qdrant Cloud
    if client.collection_exists(collection_name):
        print(f"[INFO] Collection '{collection_name}' already exists. Proceeding safely without modifications.")
        return

    print(f"[INFO] Collection '{collection_name}' not found. Initializing a new one...")
    
    # Create the collection with Gemini's native 3072 dimensions and Cosine similarity
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=3072, 
            distance=Distance.COSINE
        )
    )
    print(f"[INFO] Collection '{collection_name}' successfully created.")

def generate_deterministic_uuid(text: str, source_file: str) -> str:
    """Generates a stable, reproducible UUID string based on text content and source metadata."""
    unique_string = f"{source_file}::{text}"
    # Using uuid.uuid5 creates an identical ID whenever the same file and text are evaluated
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, unique_string))

def embed_and_store_chunks(documents: List[Document], collection_name: str = "nexus_documents") -> Dict[str, int]:
    """
    Accepts chunked documents, filters out elements already present in Qdrant,
    generates vector embeddings for new items, and batch-upserts them.
    """
    if not documents:
        print("[INFO] No document chunks provided for storage mapping.")
        return {"stored": 0, "skipped": 0}

    client = get_qdrant_client()
    ensure_collection_exists(client, collection_name)
    
    # Initialize Google Gemini Embedding Engine
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    new_points = []
    skipped_count = 0

    print("[INFO] Evaluating chunks against storage cluster for duplicate filtering...")
    
    for doc in documents:
        text_content = doc.page_content
        source_file = doc.metadata.get("source", "unknown_source")
        
        # Generate a stable ID for this chunk
        point_id = generate_deterministic_uuid(text_content, source_file)
        
        # Check if this precise point is already indexed in our Qdrant collection
        try:
            # retrieve handles point checking by looking up its specific unique ID
            existing_points = client.retrieve(collection_name=collection_name, ids=[point_id])
            if existing_points:
                skipped_count += 1
                continue
        except Exception:
            # If a network check fails or collection is being polled for the first time, safely assume new point
            pass

        # If it's a completely new chunk, prepare it for generation
        new_points.append({
            "id": point_id,
            "text": text_content,
            "metadata": doc.metadata
        })

    # If all items were detected as duplicates, exit early without making heavy API calls
    if not new_points:
        print(f"[INFO] Storage sync completed. All {len(documents)} chunks already exist in database.")
        return {"stored": 0, "skipped": skipped_count}

    print(f"[INFO] Generating vector matrices for {len(new_points)} fresh text chunks...")
    
    # Extract just the raw text lists to feed into Gemini's batch embedder
    texts_to_embed = [point["text"] for point in new_points]
    generated_vectors = embeddings_model.embed_documents(texts_to_embed)
    
    # Construct Qdrant point objects for batch uploading
    points_to_upsert = []
    for idx, point in enumerate(new_points):
        # We store the original chunk text inside the payload dictionary under 'page_content' 
        # so we can easily read and display it to the user during future search lookups
        payload = {
            "page_content": point["text"],
            **point["metadata"]
        }
        
        points_to_upsert.append(
            PointStruct(
                id=point["id"],
                vector=generated_vectors[idx],
                payload=payload
            )
        )

    print(f"[INFO] Streamlining batch upsert payload ({len(points_to_upsert)} points) to Qdrant Cloud...")
    client.upsert(
        collection_name=collection_name,
        points=points_to_upsert
    )
    
    print("[INFO] Synchronization successfully finalized.")
    return {"stored": len(points_to_upsert), "skipped": skipped_count}