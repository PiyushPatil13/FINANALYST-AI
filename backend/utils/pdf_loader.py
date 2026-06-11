from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

class PDFLoader:
    def __init__(self, chunk_size=1500, chunk_overlap=200):
        """
        Initializes the loader with LangChain's recommended splitting logic.
        Higher overlap (200) is better for conversational transcripts like earnings calls.
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""],
            add_start_index=True, # Useful for referencing exact locations in the PDF
        )

    def load_and_split(self, pdf_path):
        """
        Uses LangChain's PyPDFLoader to read the file and split it into 
        Document objects compatible with ChromaDB.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File not found: {pdf_path}")

        # 1. Load the PDF into LangChain Document objects (one per page)
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()

        # 2. Split the pages into smaller chunks
        docs = self.splitter.split_documents(pages)
        
        # 3. Add custom metadata (optional)
        # You can add the ticker or year here so the RAG can filter by them
        filename = os.path.basename(pdf_path)
        for doc in docs:
            doc.metadata["file_name"] = filename
            # Example: if file is 'AAPL_2025.pdf', metadata['ticker'] = 'AAPL'
            doc.metadata["ticker"] = filename.split('-')[0].upper()

        return docs