import os
from ingestion.document_loader import load_document

def run_test():
    print("--- STARTING DAY 2 INGESTION TEST ---")
    
    # Test 1: Testing the Text Loader (Success Case)
    txt_path = "sample.txt"
    if os.path.exists(txt_path):
        print(f"\n--- Testing Text File: {txt_path} ---")
        txt_docs = load_document(txt_path)
        print(f"Success! Returned {len(txt_docs)} Document object(s).")
    
    # Test 2: Testing the PDF Loader (Success Case)
    pdf_path = "sample.pdf"
    if os.path.exists(pdf_path):
        print(f"\n--- Testing PDF File: {pdf_path} ---")
        pdf_docs = load_document(pdf_path)
        print(f"Success! Returned {len(pdf_docs)} Document object(s).")

    print("\n--- STARTING ERROR HANDLING TESTS ---")

    # Test 3: Testing a Missing File (Requirement #7)
    print("\n--- Testing Missing File ---")
    try:
        load_document("this_file_does_not_exist.txt")
    except FileNotFoundError as e:
        print(f"Success! Caught expected error:\n  -> {e}")
    except Exception as e:
        print(f"FAILED: Caught wrong error type: {type(e).__name__}: {e}")

    # Test 4: Testing an Unsupported Extension (Requirement #7)
    print("\n--- Testing Unsupported Extension ---")
    # We will create a fake image file name just to test the extension check
    try:
        load_document("test_image.png")
    except ValueError as e:
        print(f"Success! Caught expected error:\n  -> {e}")
    except Exception as e:
        print(f"FAILED: Caught wrong error type: {type(e).__name__}: {e}")

if __name__ == "__main__":
    run_test()