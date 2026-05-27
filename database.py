from __future__ import annotations

import sqlite3
import os
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "chatbot.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            topic TEXT,
            upvotes INTEGER DEFAULT 0,
            downvotes INTEGER DEFAULT 0,
            needs_review BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS learned_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keywords TEXT NOT NULL,
            answer TEXT NOT NULL,
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS faq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT UNIQUE NOT NULL,
            answer TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS facility_hours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            facility TEXT NOT NULL,
            day_type TEXT NOT NULL,
            hours TEXT NOT NULL,
            extra TEXT,
            UNIQUE(facility, day_type)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS advisor_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            message TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    piscina_hours = [
        ("piscina", "lunes", "6:00 - 8:00 y 18:00 - 21:00", "Solo alumnos con matrícula vigente"),
        ("piscina", "martes", "6:00 - 8:00 y 18:00 - 21:00", "Solo alumnos con matrícula vigente"),
        ("piscina", "miércoles", "6:00 - 8:00 y 18:00 - 21:00", "Solo alumnos con matrícula vigente"),
        ("piscina", "jueves", "6:00 - 8:00 y 18:00 - 21:00", "Solo alumnos con matrícula vigente"),
        ("piscina", "viernes", "6:00 - 8:00 y 18:00 - 20:00", "Solo alumnos con matrícula vigente"),
        ("piscina", "sábado", "8:00 - 12:00", "Solo alumnos con matrícula vigente"),
        ("piscina", "domingo", "Cerrado", "No hay servicio"),
        ("piscina", "festivo", "Cerrado", "No hay servicio"),
    ]

    for facility, day_type, hours, extra in piscina_hours:
        c.execute(
            "INSERT OR IGNORE INTO facility_hours (facility, day_type, hours, extra) VALUES (?, ?, ?, ?)",
            (facility, day_type, hours, extra),
        )

    conn.commit()
    conn.close()


def vote_conversation(conv_id: int, vote: str) -> None:
    conn = get_db()
    c = conn.cursor()
    if vote == "up":
        c.execute("UPDATE conversations SET upvotes = upvotes + 1 WHERE id = ?", (conv_id,))
    elif vote == "down":
        c.execute("UPDATE conversations SET downvotes = downvotes + 1 WHERE id = ?", (conv_id,))
    conn.commit()
    conn.close()


def save_learned_response(keywords: str, answer: str) -> None:
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO learned_responses (keywords, answer) VALUES (?, ?)",
        (keywords, answer),
    )
    conn.commit()
    conn.close()


def get_learned_response(keywords: str) -> Optional[str]:
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT answer FROM learned_responses WHERE keywords LIKE ? ORDER BY usage_count DESC LIMIT 1",
        (f"%{keywords}%",),
    )
    row = c.fetchone()
    conn.close()
    return row["answer"] if row else None


def increment_learned_usage(keywords: str) -> None:
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "UPDATE learned_responses SET usage_count = usage_count + 1 WHERE keywords LIKE ?",
        (f"%{keywords}%",),
    )
    conn.commit()
    conn.close()


def get_facility_hours(facility: str, day_type: str) -> Optional[str]:
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT hours, extra FROM facility_hours WHERE facility = ? AND day_type = ?",
        (facility, day_type),
    )
    row = c.fetchone()
    conn.close()
    if row:
        extra = row["extra"] or ""
        return f"{row['hours']}" + (f" — {extra}" if extra else "")
    return None


def get_facility_all_hours(facility: str) -> list[dict]:
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT day_type, hours, extra FROM facility_hours WHERE facility = ? ORDER BY id",
        (facility,),
    )
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_unknown_questions(limit: int = 20) -> list[dict]:
    """Preguntas marcadas para revisión (downvotes o needs_review=True)."""
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT id, question, answer, topic, upvotes, downvotes, created_at FROM conversations "
        "WHERE needs_review = TRUE OR downvotes > 0 ORDER BY downvotes DESC, created_at DESC LIMIT ?",
        (limit,)
    )
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_user_by_email(email: str) -> Optional[dict]:
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, username, email, password_hash, is_admin FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[dict]:
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, username, email, is_admin FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def create_user(username: str, email: str, password_hash: str) -> int:
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, password_hash)
    )
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    return user_id


def flag_for_review(conv_id: int) -> None:
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE conversations SET needs_review = TRUE WHERE id = ?", (conv_id,))
    conn.commit()
    conn.close()


def get_all_learned_responses() -> list[dict]:
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, keywords, answer, usage_count, created_at FROM learned_responses ORDER BY usage_count DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_learned_response(id: int) -> None:
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM learned_responses WHERE id = ?", (id,))
    conn.commit()
    conn.close()


def get_conversation_by_id(conv_id: int) -> Optional[dict]:
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def save_conversation(question: str, answer: str, topic: Optional[str] = None, user_id: Optional[int] = None) -> int:
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO conversations (question, answer, topic, user_id) VALUES (?, ?, ?, ?)",
        (question, answer, topic, user_id)
    )
    conv_id = c.lastrowid
    conn.commit()
    conn.close()
    return conv_id


def get_user_history(user_id: int, limit: int = 10) -> list[dict]:
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT question, answer FROM conversations WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    )
    rows = c.fetchall()
    conn.close()

    history = []
    for row in reversed(rows):
        history.append({"role": "user", "content": row["question"]})
        history.append({"role": "assistant", "content": row["answer"]})
    return history


def create_advisor_request(name: str, email: str, phone: Optional[str], message: str) -> int:
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO advisor_requests (name, email, phone, message) VALUES (?, ?, ?, ?)",
        (name, email, phone, message)
    )
    request_id = c.lastrowid
    conn.commit()
    conn.close()
    return request_id

def get_advisor_requests() -> list[dict]:
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM advisor_requests ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_advisor_request_status(request_id: int, status: str) -> None:
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE advisor_requests SET status = ? WHERE id = ?", (status, request_id))
    conn.commit()
    conn.close()
