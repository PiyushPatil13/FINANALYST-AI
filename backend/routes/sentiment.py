from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.ml.sentiment import analyze_sentiment,analyze_bulk

router = APIRouter()

# ── RESPONSE MODELS ──────────────────────────────────────────────

class SentimentRequest(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    label: str       # positive / negative / neutral
    score: float     # confidence 0 to 1
    text_preview: str


# ── ENDPOINTS ────────────────────────────────────────────────────

@router.post("/analyze", response_model=SentimentResponse)
async def analyze(request: SentimentRequest):
    """Analyze sentiment of financial text using FinBERT."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    if len(request.text) < 10:
        raise HTTPException(status_code=400, detail="Text too short.")

    result = analyze_sentiment(request.text)
    return SentimentResponse(**result)


@router.post("/bulk-analyze")
async def bulk_analyze(texts: list[str]):
    """Analyze sentiment for multiple paragraphs at once."""
    if not texts:
        raise HTTPException(status_code=400, detail="No texts provided.")

    if len(texts) > 20:
        raise HTTPException(status_code=400, detail="Max 20 texts per request.")

    results = analyze_bulk(texts)
    return {"results": results, "total": len(results)}