"""
SQLite Database Layer for CivicEase AI.
Handles user management, document tracking, analysis caching, and report persistence.
"""
import hashlib
import json
import sqlite3
from typing import Any, Dict, List, Optional

from config.settings import DATABASE_PATH
from database.models import AnalysisRecord, DocumentRecord, UserRecord
from utils.logging import get_logger

logger = get_logger(__name__)


def hash_password(password: str) -> str:
    """Simple SHA-256 password hashing for hackathon authentication."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class DatabaseManager:
    """Manages SQLite database connections, tables, and CRUD operations."""

    def __init__(self, db_path: str = str(DATABASE_PATH)):
        self.db_path = db_path
        self._init_db()
        self._seed_default_users()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create tables if they do not already exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'citizen',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    file_size_bytes INTEGER DEFAULT 0,
                    page_count INTEGER DEFAULT 1,
                    storage_path TEXT NOT NULL,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Analysis Results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    composite_score REAL NOT NULL,
                    score_tier TEXT NOT NULL,
                    score_breakdown_json TEXT NOT NULL,
                    rule_metrics_json TEXT NOT NULL,
                    detected_issues_json TEXT NOT NULL,
                    missing_info_json TEXT NOT NULL,
                    citizen_explanation_json TEXT NOT NULL,
                    recommendations_json TEXT NOT NULL,
                    before_after_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents(id)
                )
            """)

            # Audit Reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id INTEGER NOT NULL,
                    report_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_results(id)
                )
            """)
            conn.commit()
            logger.info("Database schema initialized successfully.")

    def _seed_default_users(self):
        """Seed demo accounts for instant hackathon evaluation."""
        demo_accounts = [
            ("citizen", hash_password("citizen123"), "Priya Sharma (Citizen)", "citizen"),
            ("auditor", hash_password("auditor123"), "Dr. Rajesh Kumar (Senior Auditor)", "auditor"),
            ("admin", hash_password("admin123"), "System Administrator", "admin"),
        ]
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for username, pwd_hash, full_name, role in demo_accounts:
                cursor.execute("""
                    INSERT OR IGNORE INTO users (username, password_hash, full_name, role)
                    VALUES (?, ?, ?, ?)
                """, (username, pwd_hash, full_name, role))
            conn.commit()

    def authenticate_user(self, username: str, password: str) -> Optional[UserRecord]:
        """Authenticate username and password."""
        pwd_hash = hash_password(password)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, password_hash, full_name, role, created_at
                FROM users WHERE username = ? AND password_hash = ?
            """, (username.strip(), pwd_hash))
            row = cursor.fetchone()
            if row:
                return UserRecord(
                    id=row["id"],
                    username=row["username"],
                    password_hash=row["password_hash"],
                    full_name=row["full_name"],
                    role=row["role"],
                    created_at=row["created_at"]
                )
        return None

    def register_user(self, username: str, password: str, full_name: str, role: str = "citizen") -> Optional[UserRecord]:
        """Register a new user account."""
        pwd_hash = hash_password(password)
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (username, password_hash, full_name, role)
                    VALUES (?, ?, ?, ?)
                """, (username.strip(), pwd_hash, full_name.strip(), role))
                user_id = cursor.lastrowid
                conn.commit()
                return UserRecord(
                    id=user_id,
                    username=username.strip(),
                    password_hash=pwd_hash,
                    full_name=full_name.strip(),
                    role=role
                )
        except sqlite3.IntegrityError:
            logger.warning("Attempted to register duplicate username: %s", username)
            return None

    def save_document(self, doc: DocumentRecord) -> int:
        """Store uploaded document metadata."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO documents (user_id, filename, file_type, file_hash, file_size_bytes, page_count, storage_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                doc.user_id,
                doc.filename,
                doc.file_type,
                doc.file_hash,
                doc.file_size_bytes,
                doc.page_count,
                doc.storage_path
            ))
            doc_id = cursor.lastrowid
            conn.commit()
            return doc_id

    def save_analysis(self, analysis: AnalysisRecord) -> int:
        """Save complete analysis result."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analysis_results (
                    document_id, composite_score, score_tier, score_breakdown_json,
                    rule_metrics_json, detected_issues_json, missing_info_json,
                    citizen_explanation_json, recommendations_json, before_after_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis.document_id,
                analysis.composite_score,
                analysis.score_tier,
                json.dumps(analysis.score_breakdown),
                json.dumps(analysis.rule_metrics),
                json.dumps(analysis.detected_issues),
                json.dumps(analysis.missing_info),
                json.dumps(analysis.citizen_explanation),
                json.dumps(analysis.recommendations),
                json.dumps(analysis.before_after_comparison),
            ))
            analysis_id = cursor.lastrowid
            conn.commit()
            return analysis_id

    def get_analysis_by_id(self, analysis_id: int) -> Optional[AnalysisRecord]:
        """Fetch analysis by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM analysis_results WHERE id = ?
            """, (analysis_id,))
            row = cursor.fetchone()
            if row:
                return AnalysisRecord(
                    id=row["id"],
                    document_id=row["document_id"],
                    composite_score=row["composite_score"],
                    score_tier=row["score_tier"],
                    score_breakdown=json.loads(row["score_breakdown_json"]),
                    rule_metrics=json.loads(row["rule_metrics_json"]),
                    detected_issues=json.loads(row["detected_issues_json"]),
                    missing_info=json.loads(row["missing_info_json"]),
                    citizen_explanation=json.loads(row["citizen_explanation_json"]),
                    recommendations=json.loads(row["recommendations_json"]),
                    before_after_comparison=json.loads(row["before_after_json"]),
                    created_at=row["created_at"]
                )
        return None

    def get_recent_analyses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent document analyses with metadata."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.id, a.composite_score, a.score_tier, a.created_at,
                       d.filename, d.file_type, d.page_count
                FROM analysis_results a
                JOIN documents d ON a.document_id = d.id
                ORDER BY a.created_at DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]


# Singleton instance
db = DatabaseManager()
