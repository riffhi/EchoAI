import sqlite3
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from contextlib import contextmanager
from datetime import datetime

@dataclass
class User:
    user_id: int
    name: str
    device_type: str
    preferences: dict = None

@dataclass
class App:
    app_id: int
    name: str
    category: str
    user_id: int
    is_running: bool = False
    last_used: str = None

@dataclass
class CalendarEvent:
    event_id: int
    title: str
    date: str
    time: str
    duration: int
    user_id: int
    status: str = "pending"  # pending, approved, completed
    reminder: bool = False

@dataclass
class Transaction:
    transaction_id: int
    type: str  # payment, transfer, purchase
    amount: float
    description: str
    timestamp: str
    status: str  # pending, approved, completed, failed
    user_id: int
    approval_needed: bool = True

@dataclass
class AppUsageMetric:
    metric_id: int
    app_id: int
    user_id: int
    start_time: str
    end_time: str = None
    duration: int = 0

@dataclass
class TaskFeedback:
    feedback_id: int
    task_type: str  # app_switch, calendar, transaction, analysis
    task_id: int
    user_id: int
    status: str  # pending, approved, rejected
    feedback: str = None
    timestamp: str = None

class DatabaseDriver:
    def __init__(self, db_path: str = "smartphone_assistant.sqlite"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dictionary access to rows
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create users table with preferences
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    device_type TEXT NOT NULL,
                    preferences TEXT DEFAULT '{}'
                )
            """)
            
            # Create apps table with running status
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS apps (
                    app_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    is_running BOOLEAN DEFAULT 0,
                    last_used TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Enhanced calendar_events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calendar_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    reminder BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Create transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    timestamp TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    user_id INTEGER NOT NULL,
                    approval_needed BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Create app_usage_metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_usage_metrics (
                    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    app_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration INTEGER DEFAULT 0,
                    FOREIGN KEY (app_id) REFERENCES apps (app_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Create task_feedback table for AI feedback and approval
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_feedback (
                    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_type TEXT NOT NULL,
                    task_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    feedback TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            conn.commit()

    # User methods
    def create_user(self, name: str, device_type: str, preferences: Dict = None) -> User:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            prefs = preferences if preferences else {}
            prefs_str = str(prefs).replace("'", "\"")
            
            cursor.execute(
                "INSERT INTO users (name, device_type, preferences) VALUES (?, ?, ?)",
                (name, device_type, prefs_str)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return User(user_id=user_id, name=name, device_type=device_type, preferences=prefs)

    def get_user_by_name(self, name: str) -> Optional[User]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
            row = cursor.fetchone()
            if not row:
                return None
            
            import json
            preferences = json.loads(row['preferences']) if row['preferences'] else {}
            
            return User(
                user_id=row['user_id'],
                name=row['name'],
                device_type=row['device_type'],
                preferences=preferences
            )
    
    def update_user_preferences(self, user_id: int, preferences: Dict) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            prefs_str = str(preferences).replace("'", "\"")
            cursor.execute(
                "UPDATE users SET preferences = ? WHERE user_id = ?",
                (prefs_str, user_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    # App methods
    def add_app(self, name: str, category: str, user_id: int) -> App:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO apps (name, category, user_id, last_used) VALUES (?, ?, ?, ?)",
                (name, category, user_id, now)
            )
            app_id = cursor.lastrowid
            conn.commit()
            return App(app_id=app_id, name=name, category=category, user_id=user_id, last_used=now)
    
    def get_apps_for_user(self, user_id: int) -> List[App]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM apps WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()
            
            return [App(
                app_id=row['app_id'],
                name=row['name'],
                category=row['category'],
                user_id=row['user_id'],
                is_running=bool(row['is_running']),
                last_used=row['last_used']
            ) for row in rows]
    
    def get_app_by_name(self, name: str, user_id: int) -> Optional[App]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM apps WHERE name = ? AND user_id = ?", (name, user_id))
            row = cursor.fetchone()
            if not row:
                return None
            
            return App(
                app_id=row['app_id'],
                name=row['name'],
                category=row['category'],
                user_id=row['user_id'],
                is_running=bool(row['is_running']),
                last_used=row['last_used']
            )
    
    def switch_app(self, app_id: int, user_id: int) -> bool:
        """Switch to an app by closing all running apps and opening the requested one"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            # First, close all running apps
            cursor.execute(
                "UPDATE apps SET is_running = 0 WHERE user_id = ?", 
                (user_id,)
            )
            
            # Then open the requested app
            cursor.execute(
                "UPDATE apps SET is_running = 1, last_used = ? WHERE app_id = ? AND user_id = ?",
                (now, app_id, user_id)
            )
            
            # Record app usage start
            cursor.execute(
                "INSERT INTO app_usage_metrics (app_id, user_id, start_time) VALUES (?, ?, ?)",
                (app_id, user_id, now)
            )
            
            conn.commit()
            return cursor.rowcount > 0
    
    def close_app(self, app_id: int, user_id: int) -> bool:
        """Close a running app and record usage metrics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            # Set the app as not running
            cursor.execute(
                "UPDATE apps SET is_running = 0 WHERE app_id = ? AND user_id = ?",
                (app_id, user_id)
            )
            
            # Update the latest app usage metric
            cursor.execute(
                """
                UPDATE app_usage_metrics 
                SET end_time = ?, 
                    duration = ROUND((JULIANDAY(?) - JULIANDAY(start_time)) * 86400)
                WHERE app_id = ? AND user_id = ? AND end_time IS NULL
                """,
                (now, now, app_id, user_id)
            )
            
            conn.commit()
            return cursor.rowcount > 0
    
    # Calendar methods
    def add_calendar_event(self, title: str, date: str, time: str, duration: int, 
                           user_id: int, reminder: bool = False) -> CalendarEvent:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO calendar_events 
                (title, date, time, duration, user_id, reminder) 
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (title, date, time, duration, user_id, reminder)
            )
            event_id = cursor.lastrowid
            
            # Create task feedback entry for approval
            now = datetime.now().isoformat()
            cursor.execute(
                """
                INSERT INTO task_feedback 
                (task_type, task_id, user_id, status, timestamp) 
                VALUES (?, ?, ?, ?, ?)
                """,
                ("calendar", event_id, user_id, "pending", now)
            )
            
            conn.commit()
            return CalendarEvent(
                event_id=event_id,
                title=title,
                date=date,
                time=time,
                duration=duration,
                user_id=user_id,
                reminder=reminder,
                status="pending"
            )
    
    def get_calendar_events_for_user(self, user_id: int, status: str = None) -> List[CalendarEvent]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if status:
                cursor.execute(
                    "SELECT * FROM calendar_events WHERE user_id = ? AND status = ? ORDER BY date, time",
                    (user_id, status)
                )
            else:
                cursor.execute(
                    "SELECT * FROM calendar_events WHERE user_id = ? ORDER BY date, time", 
                    (user_id,)
                )
                
            rows = cursor.fetchall()
            
            return [CalendarEvent(
                event_id=row['event_id'],
                title=row['title'],
                date=row['date'],
                time=row['time'],
                duration=row['duration'],
                user_id=row['user_id'],
                status=row['status'],
                reminder=bool(row['reminder'])
            ) for row in rows]
    
    def update_calendar_event_status(self, event_id: int, status: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE calendar_events SET status = ? WHERE event_id = ?",
                (status, event_id)
            )
            
            # Update the task feedback as well
            cursor.execute(
                "UPDATE task_feedback SET status = ? WHERE task_type = 'calendar' AND task_id = ?",
                (status, event_id)
            )
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_calendar_event(self, event_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # First delete associated feedback
            cursor.execute(
                "DELETE FROM task_feedback WHERE task_type = 'calendar' AND task_id = ?",
                (event_id,)
            )
            
            # Then delete the event
            cursor.execute(
                "DELETE FROM calendar_events WHERE event_id = ?", 
                (event_id,)
            )
            
            conn.commit()
            return cursor.rowcount > 0
    
    # Transaction methods
    def create_transaction(self, type: str, amount: float, description: str, 
                          user_id: int, approval_needed: bool = True) -> Transaction:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute(
                """
                INSERT INTO transactions 
                (type, amount, description, timestamp, user_id, approval_needed, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (type, amount, description, now, user_id, approval_needed, 
                 "pending" if approval_needed else "approved")
            )
            transaction_id = cursor.lastrowid
            
            # Create task feedback entry if approval is needed
            if approval_needed:
                cursor.execute(
                    """
                    INSERT INTO task_feedback 
                    (task_type, task_id, user_id, status, timestamp) 
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    ("transaction", transaction_id, user_id, "pending", now)
                )
            
            conn.commit()
            return Transaction(
                transaction_id=transaction_id,
                type=type,
                amount=amount,
                description=description,
                timestamp=now,
                status="pending" if approval_needed else "approved",
                user_id=user_id,
                approval_needed=approval_needed
            )
    
    def get_transactions_for_user(self, user_id: int, status: str = None) -> List[Transaction]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if status:
                cursor.execute(
                    "SELECT * FROM transactions WHERE user_id = ? AND status = ? ORDER BY timestamp DESC",
                    (user_id, status)
                )
            else:
                cursor.execute(
                    "SELECT * FROM transactions WHERE user_id = ? ORDER BY timestamp DESC", 
                    (user_id,)
                )
                
            rows = cursor.fetchall()
            
            return [Transaction(
                transaction_id=row['transaction_id'],
                type=row['type'],
                amount=row['amount'],
                description=row['description'],
                timestamp=row['timestamp'],
                status=row['status'],
                user_id=row['user_id'],
                approval_needed=bool(row['approval_needed'])
            ) for row in rows]
    
    def update_transaction_status(self, transaction_id: int, status: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE transactions SET status = ? WHERE transaction_id = ?",
                (status, transaction_id)
            )
            
            # Update the task feedback as well
            cursor.execute(
                "UPDATE task_feedback SET status = ? WHERE task_type = 'transaction' AND task_id = ?",
                (status, transaction_id)
            )
            
            conn.commit()
            return cursor.rowcount > 0
    
    # Metrics analysis methods
    def get_app_usage_metrics(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT a.name, a.category, 
                       COUNT(m.metric_id) as sessions,
                       SUM(m.duration) as total_duration,
                       AVG(m.duration) as avg_duration
                FROM app_usage_metrics m
                JOIN apps a ON m.app_id = a.app_id
                WHERE m.user_id = ? 
                AND m.start_time >= datetime('now', ?) 
                GROUP BY a.app_id
                ORDER BY total_duration DESC
                """,
                (user_id, f'-{days} days')
            )
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_app_category_usage(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT a.category, 
                       SUM(m.duration) as total_duration,
                       COUNT(DISTINCT a.app_id) as unique_apps
                FROM app_usage_metrics m
                JOIN apps a ON m.app_id = a.app_id
                WHERE m.user_id = ? 
                AND m.start_time >= datetime('now', ?) 
                GROUP BY a.category
                ORDER BY total_duration DESC
                """,
                (user_id, f'-{days} days')
            )
            
            return [dict(row) for row in cursor.fetchall()]
    
    # Task feedback and approval methods
    def get_pending_tasks(self, user_id: int) -> Dict[str, List]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get pending calendar tasks
            cursor.execute(
                """
                SELECT c.*, f.feedback_id
                FROM calendar_events c
                JOIN task_feedback f ON c.event_id = f.task_id
                WHERE c.user_id = ? AND f.status = 'pending' AND f.task_type = 'calendar'
                """,
                (user_id,)
            )
            calendar_tasks = [dict(row) for row in cursor.fetchall()]
            
            # Get pending transaction tasks
            cursor.execute(
                """
                SELECT t.*, f.feedback_id
                FROM transactions t
                JOIN task_feedback f ON t.transaction_id = f.task_id
                WHERE t.user_id = ? AND f.status = 'pending' AND f.task_type = 'transaction'
                """,
                (user_id,)
            )
            transaction_tasks = [dict(row) for row in cursor.fetchall()]
            
            return {
                "calendar": calendar_tasks,
                "transaction": transaction_tasks
            }
    
    def submit_task_feedback(self, feedback_id: int, status: str, feedback: str = None) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute(
                """
                UPDATE task_feedback
                SET status = ?, feedback = ?, timestamp = ?
                WHERE feedback_id = ?
                """,
                (status, feedback, now, feedback_id)
            )
            
            # Get the task details to update the original item
            cursor.execute(
                "SELECT task_type, task_id FROM task_feedback WHERE feedback_id = ?",
                (feedback_id,)
            )
            task = cursor.fetchone()
            
            if task:
                # Update the status of the original item
                if task['task_type'] == 'calendar':
                    cursor.execute(
                        "UPDATE calendar_events SET status = ? WHERE event_id = ?",
                        (status, task['task_id'])
                    )
                elif task['task_type'] == 'transaction':
                    cursor.execute(
                        "UPDATE transactions SET status = ? WHERE transaction_id = ?",
                        (status, task['task_id'])
                    )
            
            conn.commit()
            return cursor.rowcount > 0