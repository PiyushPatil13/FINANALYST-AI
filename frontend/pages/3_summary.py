import streamlit as st
import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import apply_theme, render_sidebar, BASE_URL

st.set_page_config(
    page_title="Stock Summary - FinAnalyst",
    page_icon="📈",
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
        <span style="font-size:18px;color:#94a3b8">{title}</span>
    </div>
    """, unsafe_allow_html=True)


# ── PAGE HEADER ──────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:20px">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
                color:#4a6080;letter-spacing:.1em;text-transform:uppercase">
        SYS/STOCK
    </div>
    <h2 style="font-size:30px;font-weight:600;color:#e2e8f0;margin:2px 0 0">
        Stock Summary
    </h2>
</div>
""", unsafe_allow_html=True)


# ── TICKER INPUT ─────────────────────────────────────────────────
panel_header("YFINANCE . LIVE","STOCK LOOKUP")

col_input,col_btn = st.columns([3,1])

with col_input:
    ticker = st.text_input(
        label = "Ticket",
        placeholder="e.g. AAPL, TSLA, HDFCBANK.NS, RELIANCE.NS",
        label_visibility="collapsed"
    )

with col_btn:
    fetch_btn = st.button("⚡ Fetch + Analyze", use_container_width=True)


st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#2a4060;
            text-transform:uppercase;letter-spacing:.1em;margin:10px 0 6px">
    Quick select
</div>
""", unsafe_allow_html=True)

quick_cols = st.columns(6)
quick_tickers = ["AAPL", "TSLA", "GOOGL", "HDFCBANK.NS", "RELIANCE.NS", "INFY.NS"]

for col, qt in zip(quick_cols,quick_tickers):
    with col:
        if st.button(qt, use_container_width=True):
            st.session_state.selected_ticker = qt
            st.rerun()

if "selected_ticker" in st.session_state and not ticker:
    ticker = st.session_state.selected_ticker

st.markdown("<br>",unsafe_allow_html=True)


# FETCH AND DISPLAY THE STOCK
if (fetch_btn or "selected_ticker" in st.session_state) and ticker:
    with st.spinner(f"fetching live data of {ticker.upper()}..."):
        try:
            response = requests.post(
                f"{BASE_URL}/api/summary/stock",
                json = {"ticker":ticker.strip()}
            )

            if response.status_code == 200:
                data = response.json()
                stock = data["market_data"]

                if "selected_ticker" in st.session_state:
                    del st.session_state.selected_ticker

                st.markdown(f"""
                <div style="background:#0a0f1a;border:1px solid rgba(0,212,255,0.15);
                            border-radius:10px;padding:20px;position:relative;
                            overflow:hidden;margin-bottom:14px">
                    <div style="position:absolute;top:0;left:0;right:0;height:1px;
                                background:linear-gradient(90deg,transparent,#00d4ff,transparent);
                                opacity:.4"></div>
                    <div style="display:flex;justify-content:space-between;align-items:flex-start">
                        <div>
                            <div style="font-size:18px;font-weight:600;color:#e2e8f0;
                                        margin-bottom:4px">{stock.get('name', 'N/A')}</div>
                            <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                                        color:#00d4ff">{stock.get('ticker', '')} · {stock.get('sector', 'N/A')}</div>
                        </div>
                        <div style="text-align:right">
                            <div style="font-family:'JetBrains Mono',monospace;font-size:26px;
                                        font-weight:600;color:#00d4ff">
                                {stock.get('current_price', 'N/A')}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # METRICS
                m1,m2,m3,m4 = st.columns(4)

                def fmt_market_cap(val):
                    try:
                        val = float(val)
                        if val >= 1e12:
                            return f"₹{val/1e12:.2f}T"
                        elif val >= 1e9:
                            return f"₹{val/1e9:.2f}B"
                        else:
                            return f"₹{val:,.0f}"
                    except Exception:
                        return str(val)
                    
                with m1:
                    st.metric("Market Cap", fmt_market_cap(stock.get("market_cap","N/A")))
                with m2:
                    pe = stock.get("pe_ratio","N/A")
                    st.metric("PE Ratio",f"{pe:.1f}x" if isinstance(pe,float) else str(pe))
                with m3:
                    st.metric("52w High",f"₹{stock.get("52w_high","N/A")}")
                with m4:
                    st.metric("52w Low", f"₹{stock.get('52w_low', 'N/A')}")
                
                st.markdown("<br>", unsafe_allow_html=True)
 
                col_left, col_right = st.columns([1.2, 1])
 
                with col_left:
                    # ── AI SUMMARY ───────────────────────────────
                    panel_header("GEMINI · AI ANALYST", "Generated summary")
                    st.markdown(f"""
                    <div style="background:#0a0f1a;border-left:2px solid #00d4ff;
                                border-radius:0 8px 8px 0;padding:14px 16px;
                                font-size:13px;color:#94a3b8;line-height:1.8">
                        {data.get('ai_summary', 'Summary not available.')}
                    </div>
                    """, unsafe_allow_html=True)
 
                with col_right:
                    # ── BUSINESS SUMMARY ─────────────────────────
                    panel_header("COMPANY", "Business overview")
                    business = stock.get("summary", "N/A")
                    if business and business != "N/A":
                        # Truncate to 300 chars
                        truncated = business[:300] + "..." if len(business) > 300 else business
                        st.markdown(f"""
                        <div style="background:#0a0f1a;border:1px solid rgba(0,212,255,0.1);
                                    border-radius:8px;padding:14px;font-size:12px;
                                    color:#64748b;line-height:1.7">
                            {truncated}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style="background:#0a0f1a;border:1px solid rgba(0,212,255,0.1);
                                    border-radius:8px;padding:14px;font-size:12px;color:#4a6080">
                            Business summary not available for this ticker.
                        </div>
                        """, unsafe_allow_html=True)
 
                st.markdown("<br>", unsafe_allow_html=True)
 
                # ── PRICE HISTORY CHART ───────────────────────────
                panel_header("PRICE HISTORY", "Historical closing prices")

                period_col, _ = st.columns([1, 3])
                with period_col:
                    period = st.selectbox(
                        "Period",
                        ["1mo", "3mo", "6mo", "1y", "2y"],
                        index=3,
                        label_visibility="collapsed"
                    )

                # ← Call OHLC endpoint instead of importing backend directly
                ohlc_response = requests.get(
                    f"{BASE_URL}/api/summary/stock/ohlc/{ticker.strip()}",
                    params={"period": period}
                )

                if ohlc_response.status_code == 200:
                    ohlc_data = ohlc_response.json().get("ohlc", [])

                    if ohlc_data:
                        import pandas as pd
                        import plotly.graph_objects as go

                        df = pd.DataFrame(ohlc_data)
                        df["date"] = pd.to_datetime(df["date"])

                        fig = go.Figure(data=go.Candlestick(
                            x=df["date"],
                            open=df["open"],
                            high=df["high"],
                            low=df["low"],
                            close=df["close"],
                            increasing_line_color="#34d399",  # green candles
                            decreasing_line_color="#f87171",  # red candles
                        ))

                        fig.update_layout(
                            paper_bgcolor="#070b12",
                            plot_bgcolor="#0a0f1a",
                            font=dict(color="#94a3b8", family="JetBrains Mono"),
                            xaxis=dict(
                                gridcolor="rgba(0,212,255,0.08)",
                                showgrid=True,
                                rangeslider=dict(visible=False),  # hide range slider
                                color="#4a6080"
                            ),
                            yaxis=dict(
                                gridcolor="rgba(0,212,255,0.08)",
                                showgrid=True,
                                color="#4a6080",
                                side="right"
                            ),
                            margin=dict(l=0, r=0, t=20, b=0),
                            height=350,
                        )

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No historical data available.")

                elif ohlc_response.status_code == 404:
                    st.warning("OHLC data not available for this ticker.")
                else:
                    st.error("Failed to fetch price history.")
            else:
                try:
                    detail = response.json().get("detail", "Unknown error")
                except Exception:
                    detail = f"HTTP {response.status_code}"
                st.error(f"Failed to fetch stock data: {detail}")
 
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to FastAPI. Is uvicorn running?")
 
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
 
elif fetch_btn and not ticker:
    st.warning("Please enter a ticker symbol.")
