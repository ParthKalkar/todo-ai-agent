"""Database persistence for agent runs and tasks."""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'agent_runs.db')

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Runs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY,
            goal TEXT NOT NULL,
            model TEXT,
            mode TEXT,
            status TEXT,
            created_at TIMESTAMP,
            completed_at TIMESTAMP,
            error TEXT
        )
    ''')
    
    # Tasks table
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER,
            run_id TEXT NOT NULL,
            title TEXT,
            description TEXT,
            status TEXT,
            result TEXT,
            reflection TEXT,
            created_at TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (run_id) REFERENCES runs(id),
            PRIMARY KEY (run_id, id)
        )
    ''')
    
    # Events table (for streaming)
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            event_type TEXT,
            event_data TEXT,
            created_at TIMESTAMP,
            FOREIGN KEY (run_id) REFERENCES runs(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_run(run_id: str, goal: str, model: Optional[str] = None, mode: str = 'auto') -> bool:
    """Create a new run record."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            'INSERT INTO runs (id, goal, model, mode, status, created_at) VALUES (?, ?, ?, ?, ?, ?)',
            (run_id, goal, model, mode, 'running', datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[database] Error creating run: {e}")
        return False

def update_run_status(run_id: str, status: str, error: Optional[str] = None):
    """Update run status."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            'UPDATE runs SET status = ?, completed_at = ?, error = ? WHERE id = ?',
            (status, datetime.now().isoformat(), error, run_id)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[database] Error updating run status: {e}")

def add_task(run_id: str, task_id: int, title: str, description: str):
    """Add a task to a run."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            'INSERT INTO tasks (id, run_id, title, description, status, created_at) VALUES (?, ?, ?, ?, ?, ?)',
            (task_id, run_id, title, description, 'pending', datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[database] Error adding task: {e}")

def update_task(run_id: str, task_id: int, status: str, result: Optional[str] = None, reflection: Optional[str] = None):
    """Update task status and result."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            'UPDATE tasks SET status = ?, result = ?, reflection = ?, completed_at = ? WHERE run_id = ? AND id = ?',
            (status, result, reflection, datetime.now().isoformat(), run_id, task_id)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[database] Error updating task: {e}")

def add_event(run_id: str, event_type: str, event_data: Dict[str, Any]):
    """Add an event for a run."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            'INSERT INTO events (run_id, event_type, event_data, created_at) VALUES (?, ?, ?, ?)',
            (run_id, event_type, json.dumps(event_data), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[database] Error adding event: {e}")

def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    """Get a run by ID."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM runs WHERE id = ?', (run_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception as e:
        print(f"[database] Error getting run: {e}")
        return None

def get_run_tasks(run_id: str) -> List[Dict[str, Any]]:
    """Get all tasks for a run."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM tasks WHERE run_id = ? ORDER BY id', (run_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"[database] Error getting run tasks: {e}")
        return []

def get_run_events(run_id: str) -> List[Dict[str, Any]]:
    """Get all events for a run."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM events WHERE run_id = ? ORDER BY id', (run_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"[database] Error getting run events: {e}")
        return []

def get_all_runs() -> List[Dict[str, Any]]:
    """Get all runs (most recent first)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM runs ORDER BY created_at DESC')
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"[database] Error getting all runs: {e}")
        return []

def delete_run(run_id: str) -> bool:
    """Delete a run and all its tasks and events."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM events WHERE run_id = ?', (run_id,))
        c.execute('DELETE FROM tasks WHERE run_id = ?', (run_id,))
        c.execute('DELETE FROM runs WHERE id = ?', (run_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[database] Error deleting run: {e}")
        return False
