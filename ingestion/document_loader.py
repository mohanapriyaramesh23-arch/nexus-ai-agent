import os
from typing import List
from langchain_core.documents import Document

# WINDOWS CRITICAL RULE: Always import PyPDFLoader BEFORE any langchain_google_genai modules if present
from langchain_community.document_loaders import PyPDFLoader, TextLoader

def load_document(file_path: str) -> List[Document]:
    """
    Loads a document from a given file path based on its extension.
    Supports .pdf and .txt files.
    """
    # 1. Extract the file extension and convert it to lowercase FIRST (Requirement #7)
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()
    
    # 2. Check if the extension is supported before looking for the file
    if extension not in ['.pdf', '.txt']:
        raise ValueError(f"Error: Unsupported file extension '{extension}'. Only .pdf and .txt are allowed.")
        
    # 3. If the extension IS supported, now check if the file actually exists on the laptop
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: The file at '{file_path}' does not exist.")
    
    # 4. Select the appropriate LangChain loader based on extension
    if extension == '.pdf':
        print(f"[INFO] Detected PDF file. Initializing PyPDFLoader for: {file_path}")
        loader = PyPDFLoader(file_path)
        return loader.load()
        
    elif extension == '.txt':
        print(f"[INFO] Detected Text file. Initializing TextLoader for: {file_path}")
        loader = TextLoader(file_path, encoding='utf-8')
        return loader.load()