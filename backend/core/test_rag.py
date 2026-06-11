from backend.core.rag_pipeline import RAGPipeline
from backend.utils.pdf_loader import PDFLoader

# Load PDF
loader = PDFLoader()
docs = loader.load_and_split(r"C:\Users\Lenovo\OneDrive\Desktop\AI FINANCIAL ANALYST\backend\utils\HDFCBank-Analyst-Apr18-2026-vF.pdf")

# Build pipeline
rag = RAGPipeline()
rag.store.add_documents(docs)
rag.build_chain()

# Ask questions
r1 = rag.ask("What was HDFC Bank's credit growth in FY26?")
print(r1["answer"])
print(r1["sources"])

# Follow-up — memory makes "that" refer to net interest income
r2 = rag.ask("How did that change compared to last year?")
print(r2["answer"])

r3 = rag.ask("How does that compare to the system credit growth?")
print(r2['answer'])