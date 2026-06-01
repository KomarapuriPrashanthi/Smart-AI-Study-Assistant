import sqlite3
import os
from datetime import datetime

DB_PATH = "study.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        filetype TEXT,
        pages INTEGER DEFAULT 0,
        uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        document_name TEXT,
        score INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        taken_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS flashcards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        deck_name TEXT NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS summaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        document_id INTEGER,
        document_name TEXT,
        summary_text TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS study_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        activity TEXT,
        detail TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

def register_user(name, email, password):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)", (name, email, password))
        conn.commit()
        return True, "OK"
    except sqlite3.IntegrityError:
        return False, "Email already registered."
    finally:
        conn.close()

def login_user(email, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def save_document(user_id, filename, filepath, filetype, pages=0):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO documents (user_id,filename,filepath,filetype,pages) VALUES (?,?,?,?,?)",
              (user_id, filename, filepath, filetype, pages))
    conn.commit()
    doc_id = c.lastrowid
    conn.close()
    return doc_id

def get_documents(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM documents WHERE user_id=? ORDER BY uploaded_at DESC", (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def delete_document(doc_id, user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT filepath FROM documents WHERE id=? AND user_id=?", (doc_id, user_id))
    row = c.fetchone()
    if row:
        try:
            if os.path.exists(row["filepath"]):
                os.remove(row["filepath"])
        except:
            pass
    c.execute("DELETE FROM documents WHERE id=? AND user_id=?", (doc_id, user_id))
    conn.commit()
    conn.close()

def save_quiz_result(user_id, document_name, score, total):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO quizzes (user_id,document_name,score,total) VALUES (?,?,?,?)",
              (user_id, document_name, score, total))
    conn.commit()
    conn.close()

def get_all_quizzes(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM quizzes WHERE user_id=? ORDER BY taken_at DESC", (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def save_flashcard(user_id, deck_name, question, answer):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO flashcards (user_id,deck_name,question,answer) VALUES (?,?,?,?)",
              (user_id, deck_name, question, answer))
    conn.commit()
    conn.close()

def get_flashcards(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM flashcards WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def delete_flashcard(card_id, user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM flashcards WHERE id=? AND user_id=?", (card_id, user_id))
    conn.commit()
    conn.close()

def save_summary(user_id, document_id, document_name, summary_text):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO summaries (user_id,document_id,document_name,summary_text) VALUES (?,?,?,?)",
              (user_id, document_id, document_name, summary_text))
    conn.commit()
    conn.close()

def get_summaries(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM summaries WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def log_activity(user_id, activity, detail=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO study_log (user_id,activity,detail) VALUES (?,?,?)", (user_id, activity, detail))
    conn.commit()
    conn.close()

def get_activity_log(user_id, limit=50):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM study_log WHERE user_id=? ORDER BY created_at DESC LIMIT ?", (user_id, limit))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_stats(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as n FROM documents WHERE user_id=?", (user_id,))
    docs = c.fetchone()["n"]
    c.execute("SELECT COUNT(*) as n, SUM(score) as s, SUM(total) as t FROM quizzes WHERE user_id=?", (user_id,))
    qrow = dict(c.fetchone())
    c.execute("SELECT COUNT(*) as n FROM flashcards WHERE user_id=?", (user_id,))
    fc = c.fetchone()["n"]
    c.execute("SELECT COUNT(*) as n FROM summaries WHERE user_id=?", (user_id,))
    sm = c.fetchone()["n"]
    conn.close()
    return {
        "docs": docs, "quizzes": qrow["n"] or 0,
        "quiz_score": qrow["s"] or 0, "quiz_total": qrow["t"] or 0,
        "flashcards": fc, "summaries": sm,
    }
