from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.routes import chat, sentiment, summary
from backend.utils.database import init_db
from dotenv import load_dotenv

load_dotenv()

# The lifespan context manager replaces the deprecated @app.on_event("startup")
# It handles initializing your SQLite chat database tables right when the server spins up.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the SQLite database tables
    try:
        init_db()
        print("📁 Chat history database initialized successfully.")
    except Exception as e:
        print(f"❌ Error initializing chat database: {e}")
    
    yield
    # Shutdown logic (if any) can go here

# APP SETUP
app = FastAPI(
    title="AI Financial Analyst API",
    description="RAG Based financial document analyst with sentiment scoring and session history",
    version='1.0.0',
    lifespan=lifespan
)

# CORS MIDDLEWARE
# It helps the Streamlit frontend talk to the FastAPI app without the browser blocking requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ROUTES
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(sentiment.router, prefix="/api/sentiment", tags=["Sentiment"])
app.include_router(summary.router, prefix="/api/summary", tags=["Summary"])

@app.get("/")
def health_check():
    return {
        "status": "AI app is running",
        "version": "1.0.0",
        "docs": "Visit /docs for the interactive API documentation"
    }