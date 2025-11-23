"""Database schema for Digital Forensic Surgeon."""

from __future__ import annotations

import sqlite3
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from digital_forensic_surgeon.core.exceptions import DatabaseError


class ServiceSchema:
    """Schema for services table."""
    
    CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        domain TEXT NOT NULL,
        category TEXT NOT NULL,
        deletion_url TEXT,
        privacy_policy_url TEXT,
        terms_url TEXT,
        contact_email TEXT,
        gdpr_template TEXT,
        difficulty INTEGER DEFAULT 1,
        time_required TEXT,
        requires_identity_verification BOOLEAN DEFAULT FALSE,
        requires_phone_verification BOOLEAN DEFAULT FALSE,
        breach_count INTEGER DEFAULT 0,
        privacy_rating INTEGER DEFAULT 3,
        alternative_services TEXT, -- JSON array
        legal_basis TEXT,
        api_available BOOLEAN DEFAULT FALSE,
        requires_payment_history_check BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_INDEXES = [
        "CREATE INDEX IF NOT EXISTS idx_services_domain ON services(domain)",
        "CREATE INDEX IF NOT EXISTS idx_services_category ON services(category)",
        "CREATE INDEX IF NOT EXISTS idx_services_breach_count ON services(breach_count)",
        "CREATE INDEX IF NOT EXISTS idx_services_difficulty ON services(difficulty)",
    ]
    
    INSERT_TEMPLATE = """
    INSERT OR REPLACE INTO services (
        name, domain, category, deletion_url, privacy_policy_url, terms_url,
        contact_email, gdpr_template, difficulty, time_required,
        requires_identity_verification, requires_phone_verification, breach_count,
        privacy_rating, alternative_services, legal_basis, api_available,
        requires_payment_history_check
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """


class CredentialSchema:
    """Schema for credentials table."""
    
    CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS credentials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT NOT NULL,
        username TEXT,
        email TEXT,
        credential_type TEXT DEFAULT 'password',
        hash_algorithm TEXT DEFAULT 'scrypt',
        is_discovered BOOLEAN DEFAULT FALSE,
        is_verified BOOLEAN DEFAULT FALSE,
        risk_score REAL DEFAULT 0.0,
        metadata TEXT, -- JSON
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_INDEXES = [
        "CREATE INDEX IF NOT EXISTS idx_credentials_service ON credentials(service_name)",
        "CREATE INDEX IF NOT EXISTS idx_credentials_username ON credentials(username)",
        "CREATE INDEX IF NOT EXISTS idx_credentials_email ON credentials(email)",
        "CREATE INDEX IF NOT EXISTS idx_credentials_risk ON credentials(risk_score)",
    ]


class BreachSchema:
    """Schema for breach data table."""
    
    CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS breaches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT NOT NULL,
        breach_name TEXT NOT NULL,
        breach_date DATE,
        records_count INTEGER,
        data_types TEXT, -- JSON array
        severity TEXT DEFAULT 'medium',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_INDEXES = [
        "CREATE INDEX IF NOT EXISTS idx_breaches_service ON breaches(service_name)",
        "CREATE INDEX IF NOT EXISTS idx_breaches_date ON breaches(breach_date)",
    ]


class EvidenceSchema:
    """Schema for evidence table."""
    
    CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS evidence (
        id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        type TEXT NOT NULL,
        content TEXT,
        metadata TEXT, -- JSON
        is_sensitive BOOLEAN DEFAULT FALSE,
        severity TEXT DEFAULT 'info',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_INDEXES = [
        "CREATE INDEX IF NOT EXISTS idx_evidence_timestamp ON evidence(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_evidence_source ON evidence(source)",
        "CREATE INDEX IF NOT EXISTS idx_evidence_type ON evidence(type)",
    ]


class TimelineSchema:
    """New Table: Tracks daily data consumption per company."""
    CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS privacy_ledger (
        date DATE NOT NULL,
        company_name TEXT NOT NULL,
        category TEXT,
        data_points_count INTEGER DEFAULT 0,
        risk_score REAL,
        UNIQUE(date, company_name)
    );
    """
    
    CREATE_INDEXES = [
        "CREATE INDEX IF NOT EXISTS idx_privacy_ledger_date ON privacy_ledger(date)",
        "CREATE INDEX IF NOT EXISTS idx_privacy_ledger_company ON privacy_ledger(company_name)",
    ]

    UPSERT_LEDGER = """
    INSERT INTO privacy_ledger (date, company_name, category, data_points_count, risk_score)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(date, company_name) DO UPDATE SET
        data_points_count = data_points_count + excluded.data_points_count,
        risk_score = excluded.risk_score;
    """


def create_database(db_path: str | Path) -> sqlite3.Connection:
    """Create a new database with schema."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = 10000")
        conn.execute("PRAGMA temp_store = memory")
        
        return conn
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to create database: {e}")


def initialize_schema(conn: sqlite3.Connection) -> None:
    """Initialize database schema."""
    try:
        # Create tables
        conn.execute(ServiceSchema.CREATE_TABLE)
        conn.execute(CredentialSchema.CREATE_TABLE)
        conn.execute(BreachSchema.CREATE_TABLE)
        conn.execute(EvidenceSchema.CREATE_TABLE)
        conn.execute(TimelineSchema.CREATE_TABLE)
        
        # Create indexes
        for index_sql in ServiceSchema.CREATE_INDEXES:
            conn.execute(index_sql)
        
        for index_sql in CredentialSchema.CREATE_INDEXES:
            conn.execute(index_sql)
            
        for index_sql in BreachSchema.CREATE_INDEXES:
            conn.execute(index_sql)

        for index_sql in EvidenceSchema.CREATE_INDEXES:
            conn.execute(index_sql)

        for index_sql in TimelineSchema.CREATE_INDEXES:
            conn.execute(index_sql)
        
        conn.commit()
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to initialize schema: {e}")


def update_privacy_ledger(conn: sqlite3.Connection, date: str, company_name: str, category: str, data_points: int, risk_score: float):
    """Insert or update a record in the privacy ledger."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            TimelineSchema.UPSERT_LEDGER,
            (date, company_name, category, data_points, risk_score)
        )
        conn.commit()
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to update privacy ledger: {e}")



def load_services_from_csv(conn: sqlite3.Connection, csv_path: str | Path) -> None:
    """Load services from CSV file into database."""
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        raise DatabaseError(f"Services CSV file not found: {csv_path}")
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            services = list(reader)
        
        cursor = conn.cursor()
        for service in services:
            # Handle JSON fields
            alternative_services = service.get('alternative_services', '[]')
            if isinstance(alternative_services, str):
                try:
                    # Validate JSON
                    import json
                    json.loads(alternative_services)
                except json.JSONDecodeError:
                    alternative_services = '[]'
            
            cursor.execute(
                ServiceSchema.INSERT_TEMPLATE,
                (
                    service.get('name', ''),
                    service.get('domain', ''),
                    service.get('category', ''),
                    service.get('deletion_url', ''),
                    service.get('privacy_policy_url', ''),
                    service.get('terms_url', ''),
                    service.get('contact_email', ''),
                    service.get('gdpr_template', ''),
                    int(service.get('difficulty', 1)),
                    service.get('time_required', ''),
                    service.get('requires_identity_verification', 'FALSE').lower() in ('true', '1', 'yes'),
                    service.get('requires_phone_verification', 'FALSE').lower() in ('true', '1', 'yes'),
                    int(service.get('breach_count', 0)),
                    int(service.get('privacy_rating', 3)),
                    alternative_services,
                    service.get('legal_basis', ''),
                    service.get('api_available', 'FALSE').lower() in ('true', '1', 'yes'),
                    service.get('requires_payment_history_check', 'FALSE').lower() in ('true', '1', 'yes'),
                )
            )
        
        conn.commit()
    except Exception as e:
        raise DatabaseError(f"Failed to load services from CSV: {e}")


def get_service_by_name(conn: sqlite3.Connection, name: str) -> Optional[Dict[str, Any]]:
    """Get service by name."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM services WHERE name = ? OR domain = ?", (name, name))
    row = cursor.fetchone()
    
    if row:
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))
    return None


def search_services(conn: sqlite3.Connection, query: str, category: str | None = None) -> List[Dict[str, Any]]:
    """Search services by name or domain."""
    cursor = conn.cursor()
    
    if category:
        cursor.execute(
            "SELECT * FROM services WHERE (name LIKE ? OR domain LIKE ?) AND category = ? ORDER BY breach_count DESC",
            (f"%{query}%", f"%{query}%", category)
        )
    else:
        cursor.execute(
            "SELECT * FROM services WHERE name LIKE ? OR domain LIKE ? ORDER BY breach_count DESC",
            (f"%{query}%", f"%{query}%")
        )
    
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_services_by_category(conn: sqlite3.Connection, category: str) -> List[Dict[str, Any]]:
    """Get all services in a category."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM services WHERE category = ? ORDER BY name", (category,))
    
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_breach_history(conn: sqlite3.Connection, service_name: str) -> List[Dict[str, Any]]:
    """Get breach history for a service."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM breaches WHERE service_name = ? ORDER BY breach_date DESC", (service_name,))
    
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_statistics(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Get database statistics."""
    cursor = conn.cursor()
    
    stats = {}
    
    # Total services
    cursor.execute("SELECT COUNT(*) FROM services")
    stats['total_services'] = cursor.fetchone()[0]
    
    # Services by category
    cursor.execute("SELECT category, COUNT(*) FROM services GROUP BY category")
    stats['services_by_category'] = dict(cursor.fetchall())
    
    # Average breach count
    cursor.execute("SELECT AVG(breach_count) FROM services")
    stats['average_breach_count'] = cursor.fetchone()[0] or 0
    
    # Total breaches
    cursor.execute("SELECT COUNT(*) FROM breaches")
    stats['total_breaches'] = cursor.fetchone()[0]
    
    return stats


def get_daily_health_summary(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Get a summary of daily digital health from the privacy ledger."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                date,
                SUM(data_points_count) as total_data_points,
                AVG(risk_score) as average_risk_score
            FROM privacy_ledger
            GROUP BY date
            ORDER BY date DESC
            LIMIT 30
        """)
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to get daily health summary: {e}")
