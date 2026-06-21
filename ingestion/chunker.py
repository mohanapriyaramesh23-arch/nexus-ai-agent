from typing import List
from langchain_core.documents import Document
# Correct import path as per strict tech guidelines
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Takes a list of LangChain Document objects and splits them into smaller
    chunks using RecursiveCharacterTextSplitter.
    """
    # Edge case handling: If the input list is empty, return an empty list back safely
    if not documents:
        print("[INFO] Empty document list passed. Returning an empty chunk list.")
        return []

    # Initialize the text splitter with required parameters
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    # split_documents automatically preserves metadata from the original documents
    chunks = splitter.split_documents(documents)
    
    print(f"[INFO] Successfully split {len(documents)} original document(s) into {len(chunks)} text chunks.")
    return chunks