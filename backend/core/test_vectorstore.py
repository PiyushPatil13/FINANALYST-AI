from backend.utils.pdf_loader import PDFLoader
from backend.core.vectorstore import VectorStoreManager
import os

def test_full_ingestion():

    # ── 1. Load and Split ──
    loader = PDFLoader()

    # Use path relative to project root — no hardcoding
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    test_file = os.path.join(base_dir, "backend", "utils", "HDFCBank-Analyst-Apr18-2026-vF.pdf")

    if not os.path.exists(test_file):
        print(f"[ERROR] PDF not found at: {test_file}")
        return

    print(f"[INFO] Loading PDF: {test_file}")
    docs = loader.load_and_split(test_file)
    print(f"[INFO] Total chunks created: {len(docs)}")

    # ── 2. Store in ChromaDB ──
    print("\n[INFO] Storing chunks in ChromaDB...")
    store = VectorStoreManager()
    store.clear()              # Clear old data before adding new
    store.add_documents(docs)
    print(f"[INFO] Vectorstore ready. Total docs: {store.vector_db._collection.count()}")

    # ── 3. Test Search ──
    print("\n--- Testing Search ---")
    query = "What was discussed in the HDFC Q4 earnings call?"
    results = store.search(query, k=5)

    if results:
        print(f"[OK] Found {len(results)} relevant chunks.")
        print(f"\nTop Result Preview:\n{results[0].page_content[:300]}...")
    else:
        print("[WARN] No results found — check if PDF was indexed correctly.")


if __name__ == "__main__":
    test_full_ingestion()