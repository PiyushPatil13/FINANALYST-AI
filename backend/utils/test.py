# from backend.utils.yfinance_loader import YFinanceLoader
# import json

# def test_ticker_data(symbol="NVDA"):
#     print(f"--- Testing YFinanceLoader for: {symbol} ---")
#     loader = YFinanceLoader(symbol)
    
#     # 1. Test Summary Data
#     print("\n[1] Fetching Ticker Summary...")
#     summary = loader.get_ticker_summary()
#     print(json.dumps(summary, indent=2))

#     # 3. Test Financial Statements (Markdown conversion)
#     print("\n[3] Fetching Financial Statements...")
#     financials = loader.get_financial_statements()
#     # Print just the first 200 characters to verify it's a string/table
#     print(f"Data Preview:\n{financials[:200]}...")

# if __name__ == "__main__":
#     # Test with a high-volume stock to ensure news exists
#     test_ticker_data("AAPL")

from backend.utils.pdf_loader import PDFLoader

def test_langchain_pdf():
    pdf_processor = PDFLoader()
    # Ensure you have a test file in this directory
    test_file = r"C:\Users\Lenovo\OneDrive\Desktop\AI FINANCIAL ANALYST\backend\utils\HDFCBank-Analyst-Apr18-2026-vF.pdf"
    documents = pdf_processor.load_and_split(test_file)
    
    print(f"Total Chunks Created: {len(documents)}")
    print(f"Sample Metadata: {documents[0].metadata}")
    print(f"Sample Content Preview: {documents[0].page_content[:200]}...")

if __name__ == "__main__":
    test_langchain_pdf()