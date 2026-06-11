import sqlite3
import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "chat_history.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # ── CHANGE 1: Added file_path and chunks columns ──
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id      TEXT PRIMARY KEY,
            session_title   TEXT NOT NULL,
            linked_filename TEXT,
            file_path       TEXT,
            chunks          INTEGER DEFAULT 0,
            created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

    # ── CHANGE 2: Added sources column ──
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role       TEXT NOT NULL,
            content    TEXT NOT NULL,
            sources    TEXT DEFAULT '[]',
            timestamp  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
            ON DELETE CASCADE
        )''')

    conn.commit()
    conn.close()
    print("SQLite Database initialized.")


# ── CHANGE 3: Added sources parameter ──
def log_message(session_id: str, role: str, content: str, sources: list = []):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_messages (session_id, role, content, sources) VALUES (?, ?, ?, ?)",
        (session_id, role, content, json.dumps(sources))
    )
    conn.commit()
    conn.close()


# ── CHANGE 4: Returns sources in history ──
def fetch_session_history(session_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, sources FROM chat_messages WHERE session_id = ? ORDER BY timestamp ASC",
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "role": row["role"],
            "content": row["content"],
            "sources": json.loads(row["sources"]) if row["sources"] else []
        }
        for row in rows
    ]


# ── CHANGE 5: Returns file_path and chunks in sessions ──
def fetch_all_sessions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT session_id, session_title, linked_filename, file_path, chunks
        FROM chat_sessions
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id":              row["session_id"],
            "title":           row["session_title"],
            "linked_filename": row["linked_filename"],
            "file_path":       row["file_path"],
            "chunks":          row["chunks"] or 0
        }
        for row in rows
    ]


def save_session_document(session_id: str, filename: str, file_path: str, chunks: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE chat_sessions
        SET linked_filename = ?, file_path = ?, chunks = ?
        WHERE session_id = ?
    """, (filename, file_path, chunks, session_id))
    conn.commit()
    conn.close()


# ── CHANGE 6: Added create_session (was missing — caused AttributeError) ──
def create_session(session_id: str, title: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO chat_sessions (session_id, session_title) VALUES (?, ?)",
        (session_id, title)
    )
    conn.commit()
    conn.close()


# ── CHANGE 7: Added create_new_session as alias ──
# routes/chat.py calls db.create_new_session() so we need both names
def create_new_session(session_id: str, title: str):
    create_session(session_id, title)


def delete_session(session_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()