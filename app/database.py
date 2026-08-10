import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any
from app.config import config


def init_db() -> None:
    """Initialize the database and create appointments table."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_user_id INTEGER NOT NULL,
            username TEXT,
            patient_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            service TEXT NOT NULL,
            preferred_date TEXT NOT NULL,
            preferred_time TEXT NOT NULL,
            comment TEXT,
            status TEXT DEFAULT 'new',
            rejection_reason TEXT,
            created_at TEXT NOT NULL
        )
    """)
    
    # Add rejection_reason column if it doesn't exist (for existing databases)
    cursor.execute("PRAGMA table_info(appointments)")
    columns = [column[1] for column in cursor.fetchall()]
    if "rejection_reason" not in columns:
        cursor.execute("ALTER TABLE appointments ADD COLUMN rejection_reason TEXT")
    
    conn.commit()
    conn.close()


def create_appointment(data: Dict[str, Any]) -> int:
    """Create a new appointment and return its ID."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO appointments (
            telegram_user_id, username, patient_name, phone, service,
            preferred_date, preferred_time, comment, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["telegram_user_id"],
        data.get("username"),
        data["patient_name"],
        data["phone"],
        data["service"],
        data["preferred_date"],
        data["preferred_time"],
        data.get("comment", ""),
        "new",
        datetime.now().isoformat()
    ))
    
    appointment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return appointment_id


def get_appointment(appointment_id: int) -> Optional[Dict[str, Any]]:
    """Get appointment by ID."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        columns = [
            "id", "telegram_user_id", "username", "patient_name", "phone",
            "service", "preferred_date", "preferred_time", "comment", "status", "rejection_reason", "created_at"
        ]
        return dict(zip(columns, row))
    return None


def update_appointment_status(appointment_id: int, status: str) -> bool:
    """Update appointment status."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE appointments SET status = ? WHERE id = ?",
        (status, appointment_id)
    )
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success


def update_appointment_with_rejection(appointment_id: int, status: str, rejection_reason: str) -> bool:
    """Update appointment status with rejection reason."""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE appointments SET status = ?, rejection_reason = ? WHERE id = ?",
        (status, rejection_reason, appointment_id)
    )
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success
