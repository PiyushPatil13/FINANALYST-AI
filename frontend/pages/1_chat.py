import streamlit as st
import requests
import sys
import os
import uuid
from datetime import datetime

# ── PATH FIX MUST BE BEFORE APP IMPORT ──────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import apply_theme, render_sidebar, BASE_URL

# ── PAGE CONFIG ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Chat with PDF - FinAnalyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()
render_sidebar()

# ── SESSION STATE INITIALIZATION ─────────────────────────────────
if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

if "filename" not in st.session_state:
    st.session_state.filename = None

if "chunks" not in st.session_state:
    st.session_state.chunks = 0


# ── HELPERS ──────────────────────────────────────────────────────
def panel_header(tag, title):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
        <span style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#00d4ff;
                     background:rgba(0,212,255,0.08);border:1px solid rgba(0,212,255,0.18);
                     padding:2px 8px;border-radius:3px;letter-spacing:.08em;
                     text-transform:uppercase">{tag}</span>
        <span style="font-size:12px;color:#94a3b8">{title}</span>
    </div>
    """, unsafe_allow_html=True)

def safe_error(response):
    """Safely extract error message from response — won't crash on non-JSON."""
    try:
        return response.json().get("detail", "Unknown error")
    except Exception:
        return f"HTTP {response.status_code} — {response.text[:200]}"


# ── SIDEBAR SESSION PERSISTENCE ──────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
                color:#4a6080;letter-spacing:.1em;text-transform:uppercase;margin-bottom:8px">
        HISTORY MANAGEMENT
    </div>
    """, unsafe_allow_html=True)
    
    # 1. Instantiate completely new chat threads
    if st.button("➕ Start New Chat Thread", use_container_width=True):
        new_id = str(uuid.uuid4())
        timestamp_title = f"Report Chat ({datetime.now().strftime('%b %d - %H:%M')})"
        
        try:
            create_resp = requests.post(
                f"{BASE_URL}/api/chat/sessions/create", 
                json={"session_id": new_id, "title": timestamp_title}
            )
            if create_resp.status_code == 200:
                st.session_state.active_session_id = new_id
                st.session_state.chat_history = []
                st.session_state.file_uploaded = False
                st.session_state.filename = None
                st.session_state.chunks = 0
                st.rerun()
        except requests.exceptions.ConnectionError:
            st.sidebar.error("Database connection failure.")

    st.markdown("---")
    
    # 2. Render clickable history list pulled dynamically from SQLite
    try:
        sessions_resp = requests.get(f"{BASE_URL}/api/chat/sessions")
        if sessions_resp.status_code == 200:
            saved_threads = sessions_resp.json().get("sessions", [])
            
            for thread in saved_threads:
                is_active = (thread["id"] == st.session_state.active_session_id)
                btn_style = f"🔷 {thread['title']}" if is_active else f"📄 {thread['title']}"
                
                if st.button(btn_style, key=thread["id"], use_container_width=True):
                    st.session_state.active_session_id = thread["id"]
                    
                    # Unpack linked filenames handling variable schemas safely
                    linked_fn = thread.get("linked_filename") or thread.get("filename")
                    
                    if linked_fn and linked_fn != "None":
                        st.session_state.file_uploaded = True
                        st.session_state.filename = str(linked_fn)
                        st.session_state.chunks = thread.get("chunks", "Indexed")
                    else:
                        st.session_state.file_uploaded = False
                        st.session_state.filename = None
                        st.session_state.chunks = 0
                    
                    # Read corresponding message sequence block from backend storage
                    history_resp = requests.get(f"{BASE_URL}/api/chat/history/{thread['id']}")
                    if history_resp.status_code == 200:
                        raw_messages = history_resp.json().get("history", [])
                        
                        formatted_history = []
                        for i in range(0, len(raw_messages), 2):
                            if i + 1 < len(raw_messages):
                                sources_list = raw_messages[i+1].get("sources", [])
                                if isinstance(sources_list, str):
                                    sources_list = [s.strip() for s in sources_list.split(",") if s.strip()]

                                formatted_history.append({
                                    "question": raw_messages[i]["content"],
                                    "answer": raw_messages[i+1]["content"],
                                    "sources": sources_list
                                })
                        st.session_state.chat_history = formatted_history
                        st.rerun()
        else:
            st.sidebar.write("⚠️ History log unavailable")
    except Exception as e:
        pass


# ── PAGE HEADER ──────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:20px">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
                color:#4a6080;letter-spacing:.1em;text-transform:uppercase">
        SYS/CHAT
    </div>
    <h2 style="font-size:20px;font-weight:600;color:#e2e8f0;margin:2px 0 0">
        Chat with PDF
    </h2>
</div>
""", unsafe_allow_html=True)

# ── UPLOAD SECTION ───────────────────────────────────────────────
with st.container():
    panel_header("INGEST · PDF", "Upload financial document")

    # Use a dynamic key based on active session to prevent uploader widget collisions
    uploader_key = f"pdf_uploader_{st.session_state.active_session_id or 'none'}"

    uploaded_file = st.file_uploader(
        label="Upload PDF",
        type=["pdf"],
        label_visibility="collapsed",
        key=uploader_key
    )

    if uploaded_file is not None:
        if uploaded_file.name != st.session_state.filename:
            with st.spinner("Chunking and indexing document..."):
                try:
                    # Ensure an active session ID exists before sending the file
                    if not st.session_state.active_session_id:
                        st.session_state.active_session_id = str(uuid.uuid4())
                        timestamp_title = f"Doc Chat: {uploaded_file.name[:20]}"
                        requests.post(
                            f"{BASE_URL}/api/chat/sessions/create", 
                            json={"session_id": st.session_state.active_session_id, "title": timestamp_title}
                        )

                    response = requests.post(
                        f"{BASE_URL}/api/chat/upload?session_id={st.session_state.active_session_id}",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    )

                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.file_uploaded = True
                        st.session_state.all_files = data.get("all_files",[])
                        
                        # ✅ FIXED: Do NOT reset st.session_state.chat_history here. 
                        # This allows the freshly indexed PDF context to bind to the existing conversation!
                        
                        st.toast(f"{uploaded_file.name} added - {data['total_files']}")
                        st.rerun()
                    else:
                        st.error(f"Upload failed: {safe_error(response)}")

                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to FastAPI. Make sure uvicorn is running on port 8000.")
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")
                       
# ── FILE STATUS BAR DISPLAY ──────────────────────────────────────
if st.session_state.file_uploaded and st.session_state.filename:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;background:#0d1220;
                border:1px solid rgba(0,212,255,0.38);border-radius:6px;
                padding:7px 12px;font-family:'JetBrains Mono',monospace;font-size:11px;
                margin:8px 0">
        <i class="ti ti-file-check" style="font-size:14px;color:#00d4ff"></i>
        <span style="color:#00d4ff">{st.session_state.filename}</span>
        <span style="color:#4a6080;margin-left:auto">
            {st.session_state.chunks} chunks · indexed in active session
        </span>
    </div>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css"/>
    """, unsafe_allow_html=True)

# ── LOADED FILES DISPLAY ─────────────────────────────────────────
try:
    files_resp = requests.get(f"{BASE_URL}/api/chat/files",timeout=2)
    if files_resp.status_code == 200:
        loaded_files = files_resp.json().get("files",[])

        if loaded_files:
            st.markdown(f"""
            <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
                        color:#2a4060;text-transform:uppercase;letter-spacing:.1em;
                        margin:10px 0 6px">
                {len(loaded_files)} document(s) in knowledge base
            </div>
            """, unsafe_allow_html=True)

            for fname in loaded_files:
                col_file,col_del = st.columns([5,1])
                with col_file:
                     st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:8px;background:#0d1220;
                                border:1px solid rgba(0,212,255,0.25);border-radius:6px;
                                padding:6px 12px;font-family:'JetBrains Mono',monospace;
                                font-size:11px">
                        <i class="ti ti-file-check" style="color:#00d4ff;font-size:13px"></i>
                        <span style="color:#00d4ff">{fname}</span>
                    </div>
                    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css"/>
                    """, unsafe_allow_html=True)
                with col_del:
                    if st.button("🗑",key=f"del_{fname}",help = f"Remove {fname}"):
                        del_resp = requests.delete(f"{BASE_URL}/api/chat/files/{fname}")
                        if del_resp.status_code == 200:
                            st.toast(f"{fname} removed")
                            st.rerun()
except Exception:
    pass
    
# ── CHAT SECTION RENDER WINDOW ───────────────────────────────────
st.markdown("<div style='margin-top:8px'>", unsafe_allow_html=True)
panel_header("RAG · GEMINI", "Document Q&A interface")

if st.session_state.active_session_id is None:
    st.info("💡 Please start a new session thread or load an existing one from the sidebar history to activate chat capabilities.")
else:
    for item in st.session_state.chat_history:
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"""
            <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#00d4ff">
                {item['question']}
            </div>
            """, unsafe_allow_html=True)

        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(f"""
            <div style="font-size:13px;color:#e2e8f0;line-height:1.6">
                {item['answer']}
            </div>
            """, unsafe_allow_html=True)

            if item.get("sources"):
                sources_html = "".join([
                    f'<span style="background:#070b12;border:1px solid rgba(0,212,255,0.18);'
                    f'border-radius:3px;padding:2px 7px;font-family:JetBrains Mono,monospace;'
                    f'font-size:9px;color:#4a6080;margin-right:4px">{s}</span>'
                    for s in item["sources"]
                ])
                st.markdown(f"<div style='margin-top:6px'>{sources_html}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# ── QUESTION INPUT CONTROLLERS ───────────────────────────────────
question = st.chat_input(
    placeholder="Query the document...",
    disabled=(st.session_state.active_session_id is None)
)

if question:
    greetings = ["hi", "hello", "hey", "sup", "what's up", "howdy"]
    if question.strip().lower() in greetings:
        st.session_state.chat_history.append({
            "question": question,
            "answer": "Hello! I'm FinAnalyst AI. Upload a financial document and ask me anything about it — revenue, risks, growth metrics, or any other details from the report.",
            "sources": []
        })
        st.rerun()

    elif not st.session_state.file_uploaded:
        st.warning("Please upload a PDF document first to run analytical inference queries.")
    else:
        with st.spinner("Processing RAG model evaluation..."):
            try:
                response = requests.post(
                    f"{BASE_URL}/api/chat/query",
                    json={
                        "user_query": question,
                        "session_id": st.session_state.active_session_id
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": data["response"],
                        "sources": data.get("sources", [])
                    })
                    st.rerun()
                elif response.status_code == 404:
                    st.error("No active context found. Please re-upload your PDF file.")
                else:
                    st.error(f"Error: {safe_error(response)}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to FastAPI. Is uvicorn running?")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")