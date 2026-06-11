from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from backend.core.rag_pipeline import RAGPipeline
from backend.utils import database as db
from backend.utils.pdf_loader import PDFLoader
import shutil
from backend.utils.database import save_session_document
import os

router = APIRouter()

# Instantiate the pipeline and loader once at startup
rag = RAGPipeline()
pdf_loader = PDFLoader()

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── REQUEST/RESPONSE SCHEMAS ───────────────────────────────────

class SessionCreateSchema(BaseModel):
    session_id : str
    title : str

class NewMessageSchema(BaseModel):
    session_id : str
    user_query : str

class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks: int

class AskRequest(BaseModel):
    question: str
    session_id: str = "default"

class AskResponse(BaseModel):
    answer: str
    sources: list[str]


# ── HISTORY & SESSION ENDPOINTS ──────────────────────────────────

@router.get("/sessions")
def list_all_sessions():
    # FIXED: Correctly calls fetch_all_sessions() to pull the historic session rows
    return {"sessions": db.fetch_all_sessions()}

@router.get("/history/{session_id}")
def get_session_history_log(session_id: str):
    return {"history": db.fetch_session_history(session_id)}

@router.post("/sessions/create")
def instantiate_session(payload: SessionCreateSchema):
    db.create_new_session(payload.session_id, payload.title)
    return {"status": "success"}


# ── MAIN CHAT MIGRATION ROUTE ────────────────────────────────────

@router.post("/query")
def handle_rag_chat_turn(payload: NewMessageSchema):
    if not payload.user_query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # ── FIX: Ensure the session parent record exists before adding messages ──
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        # Check if the session exists
        cursor.execute("SELECT 1 FROM chat_sessions WHERE session_id = ?", (payload.session_id,))
        exists = cursor.fetchone()
        
        # If it doesn't exist, create it dynamically right now
        if not exists:
            # Generate a clean title from the start of the query
            fallback_title = f"Chat: {payload.user_query[:25]}..." if len(payload.user_query) > 25 else f"Chat: {payload.user_query}"
            cursor.execute(
                "INSERT INTO chat_sessions (session_id, session_title) VALUES (?, ?)",
                (payload.session_id, fallback_title)
            )
            conn.commit()
            
        conn.close()
    except Exception as e:
        print(f"⚠️ Parent session validation check failed: {str(e)}")

    # 1. Log the incoming user query to SQLite (This will now pass safely!)
    db.log_message(payload.session_id, "user", payload.user_query)
    
    # 2. Get past short-term conversational turns out of SQLite
    past_conversational_context = db.fetch_session_history(payload.session_id)
    
    # 3. Process RAG search and generation using your instantiated `rag` object
    try:
        result = rag.ask(
            question=payload.user_query,
            session_id=payload.session_id
        )
        
        ai_response_string = result["answer"]
        sources = result.get("sources", [])

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG Pipeline Error: {str(e)}")
    
    # 4. Log the final generated response back to SQLite
    db.log_message(payload.session_id, "assistant", ai_response_string)
    
    return {
        "response": ai_response_string,
        "sources": sources
    }
# ── DOCUMENT INGESTION ENDPOINTS ─────────────────────────
@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), session_id: str = "default"):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported.")

    # Save PDF to disk
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Chunk and index
    docs = pdf_loader.load_and_split(file_path)
    rag.store.add_documents(docs)
    rag.chain = None
    rag.build_chain()

    # Save to database
    abs_file_path = os.path.abspath(file_path)
    save_session_document(
        session_id=session_id,
        filename=file.filename,
        file_path=abs_file_path,
        chunks=len(docs)
    )

    # Also update linked_filename in chat_sessions
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE chat_sessions SET linked_filename = ? WHERE session_id = ?",
            (file.filename, session_id)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database link failed: {str(e)}")

    # Get all stored files
    stored_files = rag.store.get_stored_files()

    # ← ONE return at the end
    return {
        "message": f"'{file.filename}' added to knowledge base.",
        "filename": file.filename,
        "chunks": len(docs),
        "total_files": len(stored_files),
        "all_files": stored_files
    }


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        result = rag.ask(
            question=request.question,
            session_id=request.session_id
        )
        return AskResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status():
    return {
        "document_loaded": not rag.store.is_empty(),
        "chain_ready": rag.chain is not None
    }


@router.get("/files")
async def get_loaded_files():
    return {
        "files": rag.store.get_stored_files(),
        "total": len(rag.store.get_stored_files())
    }