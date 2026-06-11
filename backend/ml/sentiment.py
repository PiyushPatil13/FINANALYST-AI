from transformers import pipeline, BertTokenizer, BertForSequenceClassification
import torch

_model = None
_tokenizer = None

# FinBERT label mapping — this is the key fix
LABEL_MAP = {
    "LABEL_0": "positive",
    "LABEL_1": "negative", 
    "LABEL_2": "neutral",
    # Also handle if it returns text directly
    "positive": "positive",
    "negative": "negative",
    "neutral": "neutral"
}

def get_sentiment_pipeline():
    global _model, _tokenizer

    if _model is None:
        print("[FinBERT] Loading model...")
        _tokenizer = BertTokenizer.from_pretrained("ProsusAI/finbert")
        _model = BertForSequenceClassification.from_pretrained("ProsusAI/finbert")
        _model.eval()
        print("[FinBERT] Model loaded successfully.")

    return _tokenizer, _model


def analyze_sentiment(text: str) -> dict:
    tokenizer, model = get_sentiment_pipeline()

    # Clean and truncate
    from backend.ml.preprocess import clean_text
    cleaned = clean_text(text)[:512]

    inputs = tokenizer(
        cleaned,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True
    )

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.softmax(outputs.logits, dim=-1)[0]

    # FinBERT order: positive=0, negative=1, neutral=2
    scores = {
        "positive": probs[0].item(),
        "negative": probs[1].item(),
        "neutral":  probs[2].item()
    }

    # Get highest scoring label
    best_label = max(scores, key=scores.get)
    best_score = scores[best_label]

    return {
        "label": best_label,
        "score": round(best_score, 4),
        "text_preview": cleaned[:200] + "..." if len(cleaned) > 200 else cleaned
    }


def analyze_bulk(texts: list[str]) -> list[dict]:
    return [analyze_sentiment(t) for t in texts]