import re

def clean_text(text:str) -> str:
    # clean raw financial text before senting to finbert model
    if not text or not text.strip():
        return ""
    
    # Remove URL's
    text = re.sub(r'http\S+|www\S+','',text)

    # Remove speaker labels 
    text = re.sub(r'^[A-Z][a-zA-Z\s]+:\s*','',text,flags=re.MULTILINE)

    # Remove the content in brackets
    text = re.sub(r'\[.*?]','',text)

    # Remove special charaters
    text = re.sub(r'\[^a-zA-Z0-9\s%$.,\-]','',text)

    # Remove extra whitespace
    text = re.sub(r'\s+','',text).strip()

    return text

def clean_bulk(texts:list[str]) -> list[str]:
    return [clean_text(t) for t in texts]

def split_into_paragraphs(text:str) -> list[str]:
    paragraphs = text.split('\n\n')
    cleaned = [clean_text(p) for p in paragraphs]
    return [p for p in cleaned if len(p) > 30]

def truncate(text: str, max_chars: int = 512) -> str:
    """Truncate text to FinBERT's token limit."""
    return text[:max_chars]

