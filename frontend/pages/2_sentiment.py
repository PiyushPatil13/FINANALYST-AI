
import streamlit as st
import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import apply_theme, render_sidebar, BASE_URL

st.set_page_config(
    page_title="Sentiment Analysis - FinAnalyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
render_sidebar()


def panel_header(tag, title, color="#00d4ff"):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
        <span style="font-family:'JetBrains Mono',monospace;font-size:9px;color:{color};
                     background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.18);
                     padding:2px 8px;border-radius:3px;letter-spacing:.08em;
                     text-transform:uppercase">{tag}</span>
        <span style="font-size:12px;color:#94a3b8">{title}</span>
    </div>
    """, unsafe_allow_html=True)


def sentiment_badge(label, score):
    """Render a styled sentiment badge with confidence bar."""
    colors = {
        "positive": ("#34d399", "rgba(52,211,153,0.1)", "rgba(52,211,153,0.3)"),
        "negative": ("#f87171", "rgba(248,113,113,0.1)", "rgba(248,113,113,0.3)"),
        "neutral":  ("#fbbf24", "rgba(251,191,36,0.1)",  "rgba(251,191,36,0.3)")
    }
    label_lower = label.lower()
    text_color, bg_color, border_color = colors.get(label_lower, colors["neutral"])
    pct = int(score * 100)

    st.markdown(f"""
    <div style="background:#0d1220;border:1px solid rgba(0,212,255,0.12);
                border-radius:8px;padding:16px;margin-bottom:8px">
        <div style="display:flex;align-items:center;gap:14px">
            <span style="font-family:'JetBrains Mono',monospace;font-size:11px;
                         font-weight:500;padding:5px 14px;border-radius:4px;
                         letter-spacing:.06em;text-transform:uppercase;
                         background:{bg_color};color:{text_color};
                         border:1px solid {border_color}">{label.upper()}</span>
            <div style="flex:1">
                <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
                            color:#4a6080;margin-bottom:5px;text-transform:uppercase;
                            letter-spacing:.08em">Confidence — {pct}%</div>
                <div style="height:4px;background:rgba(255,255,255,.06);
                            border-radius:2px;overflow:hidden">
                    <div style="height:100%;width:{pct}%;border-radius:2px;
                                background:linear-gradient(90deg,#0099cc,{text_color})">
                    </div>
                </div>
            </div>
            <span style="font-family:'JetBrains Mono',monospace;font-size:22px;
                         font-weight:600;color:{text_color}">{pct}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── PAGE HEADER ──────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:20px">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
                color:#4a6080;letter-spacing:.1em;text-transform:uppercase">
        SYS/SENT
    </div>
    <h2 style="font-size:30px;font-weight:600;color:#e2e8f0;margin:2px 0 0">
        Sentiment Analysis
    </h2>
</div>
""", unsafe_allow_html=True)

# ── TWO COLUMN LAYOUT ────────────────────────────────────────────
col_left, col_right = st.columns([1.2, 1])

with col_left:
    # ── SINGLE ANALYSIS ─────────────────────────────────────────
    panel_header("FINBERT · NLP", "Single paragraph analysis")

    text_input = st.text_area(
        label="Text input",
        placeholder="Paste any earnings call paragraph or financial text here...",
        height=130,
        label_visibility="collapsed"
    )

    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        analyze_btn = st.button("⚡ Analyze", use_container_width=True)

    # Example texts
    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#2a4060;
                text-transform:uppercase;letter-spacing:.1em;margin:12px 0 6px">
        Quick examples
    </div>
    """, unsafe_allow_html=True)

    examples = {
        "📈 Positive": "Revenue grew 12% driven by strong retail demand and record customer acquisition across all segments.",
        "📉 Negative": "NIM compression and rising credit costs led to a significant decline in profitability this quarter.",
        "➖ Neutral":  "The board held its quarterly earnings call on April 18, 2026 to discuss financial results."
    }

    for label, text in examples.items():
        if st.button(label, use_container_width=True):
            st.session_state.example_text = text
            st.rerun()

    # Auto-fill example text
    if "example_text" in st.session_state and not text_input:
        text_input = st.session_state.example_text

    # ── SINGLE RESULT ────────────────────────────────────────────
    if analyze_btn and text_input.strip():
        with st.spinner("Running FinBERT inference..."):
            try:
                response = requests.post(
                    f"{BASE_URL}/api/sentiment/analyze",
                    json={"text": text_input}
                )
                if response.status_code == 200:
                    result = response.json()
                    st.markdown("<br>", unsafe_allow_html=True)
                    panel_header("OUTPUT", "Sentiment result")
                    sentiment_badge(result["label"], result["score"])

                    st.markdown(f"""
                    <div style="background:#0a0f1a;border-left:2px solid rgba(0,212,255,0.3);
                                border-radius:0 6px 6px 0;padding:10px 14px;margin-top:8px">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
                                    color:#2a4060;text-transform:uppercase;letter-spacing:.08em;
                                    margin-bottom:6px">Analyzed text preview</div>
                        <div style="font-size:12px;color:#64748b;line-height:1.6">
                            {result['text_preview']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                else:
                    try:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    except Exception:
                        st.error(f"HTTP {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to FastAPI. Is uvicorn running?")

    elif analyze_btn:
        st.warning("Please enter some text to analyze.")


with col_right:
    # ── BULK ANALYSIS ────────────────────────────────────────────
    panel_header("BATCH · MULTI", "Bulk paragraph analysis")

    bulk_input = st.text_area(
        label="Bulk input",
        placeholder="Paste multiple paragraphs separated by a blank line...\n\nEach paragraph will be analyzed separately.",
        height=160,
        label_visibility="collapsed"
    )

    bulk_btn = st.button("🔬 Analyze all", use_container_width=True)

    if bulk_btn and bulk_input.strip():
        # Split by blank line
        paragraphs = [p.strip() for p in bulk_input.split("\n\n") if p.strip()]

        if len(paragraphs) > 20:
            st.warning("Maximum 20 paragraphs at once.")
            paragraphs = paragraphs[:20]

        with st.spinner(f"Analyzing {len(paragraphs)} paragraphs..."):
            try:
                response = requests.post(
                    f"{BASE_URL}/api/sentiment/bulk-analyze",
                    json=paragraphs
                )

                if response.status_code == 200:
                    results = response.json()["results"]

                    st.markdown("<br>", unsafe_allow_html=True)
                    panel_header("BATCH OUTPUT", f"{len(results)} results")

                    # Summary counts
                    counts = {"positive": 0, "negative": 0, "neutral": 0}
                    for r in results:
                        counts[r["label"].lower()] = counts.get(r["label"].lower(), 0) + 1

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Positive", counts["positive"])
                    with c2:
                        st.metric("Negative", counts["negative"])
                    with c3:
                        st.metric("Neutral", counts["neutral"])

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Individual results
                    colors = {"positive": "#34d399", "negative": "#f87171", "neutral": "#fbbf24"}
                    for i, r in enumerate(results, 1):
                        color = colors.get(r["label"].lower(), "#fbbf24")
                        pct = int(r["score"] * 100)
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;justify-content:space-between;
                                    padding:8px 12px;background:#0d1220;
                                    border:1px solid rgba(0,212,255,0.1);
                                    border-radius:6px;margin-bottom:6px">
                            <div style="display:flex;align-items:center;gap:8px;flex:1;min-width:0">
                                <span style="font-family:'JetBrains Mono',monospace;font-size:9px;
                                             color:#2a4060;flex-shrink:0">#{i:02d}</span>
                                <span style="font-size:11px;color:#64748b;
                                             overflow:hidden;text-overflow:ellipsis;
                                             white-space:nowrap">{r['text_preview'][:60]}...</span>
                            </div>
                            <span style="font-family:'JetBrains Mono',monospace;font-size:9px;
                                         font-weight:500;padding:2px 10px;border-radius:3px;
                                         color:{color};background:rgba(0,0,0,0.3);
                                         flex-shrink:0;margin-left:8px">
                                {r['label'].upper()} · {pct}%
                            </span>
                        </div>
                        """, unsafe_allow_html=True)

                else:
                    st.error("Bulk analysis failed.")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to FastAPI. Is uvicorn running?")

    elif bulk_btn:
        st.warning("Please enter some text to analyze.")
