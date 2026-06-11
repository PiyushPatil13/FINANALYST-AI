import streamlit as st
import requests

st.set_page_config(
    page_title="FinAnalyst AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_URL = "http://localhost:8000"

def apply_theme():
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css"/>
    <style>
    .stApp { background-color: #070b12 !important; color: #e2e8f0 !important; font-family: 'Space Grotesk', sans-serif !important; }
    [data-testid="stSidebar"], section[data-testid="stSidebar"] > div { background-color: #0a0f1a !important; border-right: 1px solid rgba(0,212,255,0.15) !important; }
    [data-testid="stSidebar"] * { color: #94a3b8 !important; font-family: 'Space Grotesk', sans-serif !important; }
    div.stButton > button { background: rgba(0,212,255,0.06) !important; border: 1px solid rgba(0,212,255,0.3) !important; color: #00d4ff !important; border-radius: 6px !important; font-family: 'JetBrains Mono', monospace !important; font-size: 11px !important; letter-spacing: 0.06em !important; transition: all 0.2s !important; }
    div.stButton > button:hover { background: rgba(0,212,255,0.12) !important; border-color: #00d4ff !important; }
    .stTextInput input, .stTextArea textarea { background-color: #0d1220 !important; border: 1px solid rgba(0,212,255,0.15) !important; color: #e2e8f0 !important; border-radius: 6px !important; font-family: 'Space Grotesk', sans-serif !important; }
    .stTextInput input:focus, .stTextArea textarea:focus { border-color: rgba(0,212,255,0.5) !important; box-shadow: 0 0 0 1px rgba(0,212,255,0.2) !important; }
    [data-testid="stFileUploader"] { background: rgba(0,212,255,0.03) !important; border: 1px dashed rgba(0,212,255,0.3) !important; border-radius: 8px !important; }
    [data-testid="stMetric"] { background: #0d1220 !important; border: 1px solid rgba(0,212,255,0.15) !important; border-radius: 8px !important; padding: 14px !important; }
    [data-testid="stMetricLabel"] > div { font-family: 'JetBrains Mono', monospace !important; font-size: 9px !important; color: #4a6080 !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; }
    [data-testid="stMetricValue"] > div { color: #00d4ff !important; font-family: 'JetBrains Mono', monospace !important; font-size: 22px !important; }
    h1, h2, h3 { color: #e2e8f0 !important; font-family: 'Space Grotesk', sans-serif !important; }
    [data-testid="stChatMessage"] { background: #0d1220 !important; border: 1px solid rgba(0,212,255,0.12) !important; border-radius: 8px !important; }
    section[data-testid="stMain"] { background-color: #070b12 !important; }
    .main .block-container { padding-top: 1rem !important; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header[data-testid="stHeader"] { background: transparent !important; }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding:8px 4px 18px;border-bottom:1px solid rgba(0,212,255,0.12);margin-bottom:14px">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                <div style="width:30px;height:30px;background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.3);border-radius:7px;display:flex;align-items:center;justify-content:center;flex-shrink:0">
                    <i class="ti ti-chart-line" style="font-size:16px;color:#00d4ff"></i>
                </div>
                <div>
                    <div style="font-size:13px;font-weight:600;color:#00d4ff;letter-spacing:.08em;line-height:1.2">FINANALYST</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:8px;color:#2a4060;letter-spacing:.06em">AI CORE · v1.0.0</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:8px;color:#2a4060;text-transform:uppercase;letter-spacing:.12em;padding:2px 4px 8px">Navigation</div>', unsafe_allow_html=True)
        st.page_link("app.py",               label="  Home")
        st.page_link("pages/1_chat.py",      label="  Chat with PDF")
        st.page_link("pages/2_sentiment.py", label="  Sentiment")
        st.page_link("pages/3_summary.py",   label="  Stock Summary")

        st.markdown("<br>", unsafe_allow_html=True)
        st.divider()

        st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:8px;color:#2a4060;text-transform:uppercase;letter-spacing:.12em;padding:2px 4px 8px">System</div>', unsafe_allow_html=True)

        try:
            res = requests.get(f"{BASE_URL}/", timeout=2)
            api_ok = res.status_code == 200
        except:
            api_ok = False

        try:
            res2 = requests.get(f"{BASE_URL}/api/chat/status", timeout=2)
            doc_loaded = res2.json().get("document_loaded", False) if res2.status_code == 200 else False
        except:
            doc_loaded = False

        def status_row(label, ok, text):
            color = "#34d399" if ok else "#f87171"
            dot_bg = "rgba(52,211,153,0.15)" if ok else "rgba(248,113,113,0.15)"
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                        padding:7px 10px;background:#0d1220;border:1px solid rgba(0,212,255,0.1);
                        border-radius:6px;margin-bottom:6px">
                <span style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#4a6080">{label}</span>
                <div style="display:flex;align-items:center;gap:5px">
                    <div style="width:5px;height:5px;border-radius:50%;background:{color};box-shadow:0 0 4px {color}"></div>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:9px;color:{color}">{text}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        status_row("FastAPI", api_ok, "ONLINE" if api_ok else "OFFLINE")
        status_row("ChromaDB", doc_loaded, "LOADED" if doc_loaded else "EMPTY")
        status_row("FinBERT", True, "CACHED")
        status_row("Gemini", api_ok, "CONNECTED" if api_ok else "N/A")


apply_theme()
render_sidebar()

# ── HERO SECTION ─────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:52px 20px 44px">
    <div style="display:inline-block;font-family:'JetBrains Mono',monospace;font-size:10px;
                color:#00d4ff;background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.2);
                border-radius:20px;padding:4px 16px;letter-spacing:.12em;text-transform:uppercase;
                margin-bottom:20px">
        AI · FINANCE · ANALYTICS PLATFORM
    </div>
    <h1 style="font-size:42px;font-weight:600;color:#e2e8f0;letter-spacing:.04em;
               margin:0 0 4px;line-height:1.1">
        FINANALYST <span style="color:#00d4ff">AI</span>
    </h1>
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#2a4060;
                letter-spacing:.1em;margin-bottom:16px">
        ── POWERED BY GEMINI · LANGCHAIN · CHROMADB ──
    </div>
    <p style="font-size:14px;color:#64748b;max-width:480px;margin:0 auto;line-height:1.8">
        Query annual reports in natural language. Analyze earnings sentiment.<br/>
        Get AI-generated stock summaries from live market data.
    </p>
</div>
""", unsafe_allow_html=True)

# ── STATS ROW ─────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Model", "Gemini 3.5 Flash")
with c2:
    st.metric("Vector DB", "ChromaDB")
with c3:
    st.metric("Sentiment", "FinBERT")
with c4:
    st.metric("Market Data", "yfinance")

st.markdown("<br>", unsafe_allow_html=True)

# ── FEATURE CARDS ─────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

cards = [
    {
        "icon": "ti-message-2",
        "title": "Chat with PDF",
        "tags": "RAG · GEMINI · CHROMADB",
        "desc": "Upload 10-K filings and earnings transcripts. Ask questions in natural language and get answers with source page references.",
        "stat_label": "Retrieval",
        "stat_value": "Top-K chunks",
        "color": "#00d4ff"
    },
    {
        "icon": "ti-activity",
        "title": "Sentiment Analysis",
        "tags": "FINBERT · NLP · TRANSFORMERS",
        "desc": "Analyze earnings call transcripts using FinBERT — a BERT model fine-tuned specifically on financial language.",
        "stat_label": "Labels",
        "stat_value": "Pos · Neg · Neu",
        "color": "#34d399"
    },
    {
        "icon": "ti-chart-candle",
        "title": "Stock Summary",
        "tags": "YFINANCE · GEMINI · LIVE",
        "desc": "Fetch live market data for any ticker and get AI-generated analyst summaries covering valuation and sector context.",
        "stat_label": "Data",
        "stat_value": "Live market feed",
        "color": "#a78bfa"
    }
]

for col, card in zip([col1, col2, col3], cards):
    with col:
        st.markdown(f"""
        <div style="background:#0a0f1a;border:1px solid rgba(0,212,255,0.12);border-radius:10px;
                    padding:22px 20px;height:100%;position:relative;overflow:hidden;
                    transition:border-color 0.2s">
            <div style="position:absolute;top:0;left:0;right:0;height:1px;
                        background:linear-gradient(90deg,transparent,{card['color']},transparent);opacity:.4"></div>
            <div style="width:38px;height:38px;background:rgba(0,212,255,0.06);
                        border:1px solid rgba(0,212,255,0.2);border-radius:8px;
                        display:flex;align-items:center;justify-content:center;margin-bottom:14px">
                <i class="ti {card['icon']}" style="font-size:20px;color:{card['color']}"></i>
            </div>
            <div style="font-size:14px;font-weight:500;color:#e2e8f0;margin-bottom:6px">{card['title']}</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:8px;color:#2a4060;
                        text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px">{card['tags']}</div>
            <div style="font-size:12px;color:#64748b;line-height:1.7;margin-bottom:16px">{card['desc']}</div>
            <div style="border-top:1px solid rgba(0,212,255,0.08);padding-top:12px;
                        display:flex;justify-content:space-between;align-items:center">
                <span style="font-family:'JetBrains Mono',monospace;font-size:8px;color:#2a4060;
                             text-transform:uppercase;letter-spacing:.08em">{card['stat_label']}</span>
                <span style="font-family:'JetBrains Mono',monospace;font-size:9px;color:{card['color']}">{card['stat_value']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── HOW IT WORKS ─────────────────────────────────────────────────
st.markdown("""
<div style="margin:8px 0 20px">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#2a4060;
                text-transform:uppercase;letter-spacing:.12em;margin-bottom:6px">Architecture</div>
    <div style="font-size:16px;font-weight:500;color:#e2e8f0">How it works</div>
</div>
""", unsafe_allow_html=True)

steps = [
    ("01", "ti-upload", "Upload PDF", "10-K, annual report or earnings transcript uploaded and chunked into 1000-char segments"),
    ("02", "ti-database", "Vector Store", "Chunks embedded via Gemini and stored in ChromaDB for semantic retrieval"),
    ("03", "ti-search", "RAG Retrieval", "Top-K relevant chunks retrieved based on your question using cosine similarity"),
    ("04", "ti-robot", "Gemini Answer", "Retrieved context passed to Gemini 3.5 Flash with financial analyst prompt"),
]

cols = st.columns(4)
for col, (num, icon, title, desc) in zip(cols, steps):
    with col:
        st.markdown(f"""
        <div style="background:#0a0f1a;border:1px solid rgba(0,212,255,0.1);border-radius:8px;padding:16px 14px">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
                <span style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#2a4060">{num}</span>
                <i class="ti {icon}" style="font-size:16px;color:#00d4ff"></i>
            </div>
            <div style="font-size:12px;font-weight:500;color:#e2e8f0;margin-bottom:6px">{title}</div>
            <div style="font-size:11px;color:#4a6080;line-height:1.6">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;padding:20px;border-top:1px solid rgba(0,212,255,0.08)">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#1a2a3a;letter-spacing:.1em">
        FINANALYST AI · BUILT WITH LANGCHAIN · FASTAPI · STREAMLIT · CHROMADB
    </div>
</div>
""", unsafe_allow_html=True)