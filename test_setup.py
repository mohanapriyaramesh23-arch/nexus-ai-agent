# test_setup.py
# Verifies environment variables, library imports, and live Gemini API calls

print("Starting setup verification...")
print("=" * 50)

# Test 1 - Environment variables
print("\n[Test 1] Loading environment variables...")
from dotenv import load_dotenv
import os
load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
qdrant_host = os.getenv("QDRANT_HOST")
qdrant_key = os.getenv("QDRANT_API_KEY")
news_key = os.getenv("NEWS_API_KEY")

for name, value in [
    ("GEMINI_API_KEY", gemini_key),
    ("QDRANT_HOST", qdrant_host),
    ("QDRANT_API_KEY", qdrant_key),
    ("NEWS_API_KEY", news_key),
]:
    if value:
        print(f"[OK] {name} loaded - starts with: {value[:10]}...")
    else:
        print(f"[FAIL] {name} NOT found - check your .env file")

# Test 2 - Core imports
print("\n[Test 2] Testing core library imports...")

try:
    from langchain_community.document_loaders import PyPDFLoader
    print("[OK] PyPDFLoader imported successfully")
except Exception as e:
    print(f"[FAIL] PyPDFLoader failed: {e}")

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("[OK] ChatGoogleGenerativeAI imported successfully")
except Exception as e:
    print(f"[FAIL] ChatGoogleGenerativeAI failed: {e}")

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    print("[OK] GoogleGenerativeAIEmbeddings imported successfully")
except Exception as e:
    print(f"[FAIL] GoogleGenerativeAIEmbeddings failed: {e}")

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print("[OK] RecursiveCharacterTextSplitter imported successfully")
except Exception as e:
    print(f"[FAIL] RecursiveCharacterTextSplitter failed: {e}")

# Test 3 - Gemini text generation
print("\n[Test 3] Testing Gemini text generation...")
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=gemini_key
    )
    response = llm.invoke("Say exactly this: Hello from Nexus! Setup is working.")
    print(f"[OK] Gemini response received:")
    print(f"   {response.content}")
except Exception as e:
    print(f"[FAIL] Gemini text generation failed: {e}")

# Test 4 - Gemini embeddings
print("\n[Test 4] Testing Gemini embeddings...")
try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=gemini_key
    )
    test_embedding = embeddings.embed_query("This is a test sentence for Nexus")
    print(f"[OK] Embeddings working - vector length: {len(test_embedding)}")
    print(f"   First 5 values: {test_embedding[:5]}")
except Exception as e:
    print(f"[FAIL] Embeddings failed: {e}")

print("\n" + "=" * 50)
print("Setup verification complete!")
print("If all tests show [OK] - Day 1 is fully done")
print("=" * 50)