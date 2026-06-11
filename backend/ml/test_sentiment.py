# test_sentiment.py — run from project root
from backend.ml.sentiment import analyze_sentiment, analyze_bulk

# ── TEST 1: Positive ─────────────────────────────────────────────
print("=" * 50)
print("TEST 1 — POSITIVE TEXT")
print("=" * 50)
r1 = analyze_sentiment(
    "Revenue grew 12% driven by strong retail demand and record customer acquisition."
)
print(f"Label: {r1['label']}")
print(f"Score: {r1['score']}")
print(f"Preview: {r1['text_preview']}")

# ── TEST 2: Negative ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("TEST 2 — NEGATIVE TEXT")
print("=" * 50)
r2 = analyze_sentiment(
    "NIM compression and rising credit costs led to a significant decline in profitability."
)
print(f"Label: {r2['label']}")
print(f"Score: {r2['score']}")
print(f"Preview: {r2['text_preview']}")

# ── TEST 3: Neutral ──────────────────────────────────────────────
print("\n" + "=" * 50)
print("TEST 3 — NEUTRAL TEXT")
print("=" * 50)
r3 = analyze_sentiment(
    "The bank held its quarterly earnings call on April 18, 2026."
)
print(f"Label: {r3['label']}")
print(f"Score: {r3['score']}")
print(f"Preview: {r3['text_preview']}")

# ── TEST 4: Bulk ─────────────────────────────────────────────────
print("\n" + "=" * 50)
print("TEST 4 — BULK ANALYSIS (3 texts at once)")
print("=" * 50)
bulk_results = analyze_bulk([
    "Record profits driven by strong loan growth and cost efficiencies.",
    "Gross NPA rose sharply due to stress in the retail segment.",
    "The board approved a dividend of Rs 22 per share for FY26."
])
for i, r in enumerate(bulk_results, 1):
    print(f"Text {i}: {r['label']} ({r['score']}) — {r['text_preview'][:60]}...")