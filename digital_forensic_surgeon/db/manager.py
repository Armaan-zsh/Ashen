"""Database manager for Digital Forensic Surgeon."""

from __future__ import annotations

import sqlite3
import threading
import contextlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Iterator
from functools import lru_cache

from digital_forensic_surgeon.core.exceptions import DatabaseError
from digital_forensic_surgeon.db.schema import (
    get_service_by_name,
    search_services, 
    get_services_by_category,
    get_breach_history,
    get_statistics,
)


class DatabaseManager:
    """Manages database connections and operations with lazy loading."""
    
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self._local = threading.local()
        self._lock = threading.RLock()
        
    def get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'conn'):
            self._local.conn = self._create_connection()
        return self._local.conn
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create new database connection."""
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                timeout=30.0
            )
            
            # Configure connection
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = 10000")
            conn.execute("PRAGMA temp_store = memory")
            
            # Enable row factory for dict-like access
            conn.row_factory = sqlite3.Row
            
            return conn
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to create database connection: {e}")
    
    def close(self) -> None:
        """Close all database connections."""
        with self._lock:
            if hasattr(self._local, 'conn'):
                try:
                    self._local.conn.close()
                except Exception:
                    pass
                delattr(self._local, 'conn')
    
    def execute(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute query and return results."""
        conn = self.get_connection()
        try:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            raise DatabaseError(f"Database query failed: {e}")
    
    def executemany(self, query: str, params_list: List[tuple]) -> None:
        """Execute query with multiple parameter sets."""
        conn = self.get_connection()
        try:
            conn.executemany(query, params_list)
            conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Database query failed: {e}")
    
    def execute_many(self, query: str, params: Iterator[tuple]) -> int:
        """Execute query with multiple parameters."""
        conn = self.get_connection()
        try:
            cursor = conn.executemany(query, params)
            conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            raise DatabaseError(f"Database query failed: {e}")
    
    @contextlib.contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        conn = self.get_connection()
        try:
            conn.execute("BEGIN TRANSACTION")
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise DatabaseError(f"Transaction failed: {e}")
    
    @lru_cache(maxsize=128)
    def get_service(self, name: str) -> Optional[Dict[str, Any]]:
        """Get service by name (cached)."""
        return get_service_by_name(self.get_connection(), name)
    
    @lru_cache(maxsize=64)
    def search_services(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search services (cached)."""
        return search_services(self.get_connection(), query, category)
    
    @lru_cache(maxsize=32)
    def get_services_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get services by category (cached)."""
        return get_services_by_category(self.get_connection(), category)
    
    @lru_cache(maxsize=128)
    def get_breach_history(self, service_name: str) -> List[Dict[str, Any]]:
        """Get breach history for service (cached)."""
        return get_breach_history(self.get_connection(), service_name)
    
    @lru_cache(maxsize=1)
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Get all services."""
        conn = self.get_connection()
        cursor = conn.execute("SELECT * FROM services ORDER BY name")
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    @lru_cache(maxsize=1)
    def get_categories(self) -> List[str]:
        """Get all service categories."""
        conn = self.get_connection()
        cursor = conn.execute("SELECT DISTINCT category FROM services ORDER BY category")
        return [row[0] for row in cursor.fetchall()]
    
    @lru_cache(maxsize=1)
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        return get_statistics(self.get_connection())
    
    def add_service(self, service_data: Dict[str, Any]) -> int:
        """Add new service to database."""
        conn = self.get_connection()
        
        query = """
        INSERT INTO services (
            name, domain, category, deletion_url, privacy_policy_url, terms_url,
            contact_email, gdpr_template, difficulty, time_required,
            requires_identity_verification, requires_phone_verification, breach_count,
            privacy_rating, alternative_services, legal_basis, api_available,
            requires_payment_history_check
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            service_data.get('name', ''),
            service_data.get('domain', ''),
            service_data.get('category', ''),
            service_data.get('deletion_url', ''),
            service_data.get('privacy_policy_url', ''),
            service_data.get('terms_url', ''),
            service_data.get('contact_email', ''),
            service_data.get('gdpr_template', ''),
            int(service_data.get('difficulty', 1)),
            service_data.get('time_required', ''),
            bool(service_data.get('requires_identity_verification', False)),
            bool(service_data.get('requires_phone_verification', False)),
            int(service_data.get('breach_count', 0)),
            int(service_data.get('privacy_rating', 3)),
            service_data.get('alternative_services', '[]'),
            service_data.get('legal_basis', ''),
            bool(service_data.get('api_available', False)),
            bool(service_data.get('requires_payment_history_check', False)),
        )
        
        cursor = conn.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    
    def update_service(self, service_id: int, updates: Dict[str, Any]) -> bool:
        """Update service in database."""
        conn = self.get_connection()
        
        if not updates:
            return False
        
        set_clauses = []
        params = []
        
        for key, value in updates.items():
            if key in ['name', 'domain', 'category', 'deletion_url', 'privacy_policy_url', 
                      'terms_url', 'contact_email', 'gdpr_template', 'time_required', 
                      'legal_basis', 'alternative_services']:
                set_clauses.append(f"{key} = ?")
                params.append(value)
            elif key in ['difficulty', 'breach_count', 'privacy_rating']:
                set_clauses.append(f"{key} = ?")
                params.append(int(value))
            elif key in ['requires_identity_verification', 'requires_phone_verification', 
                        'api_available', 'requires_payment_history_check']:
                set_clauses.append(f"{key} = ?")
                params.append(bool(value))
        
        if not set_clauses:
            return False
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        params.append(service_id)
        
        query = f"UPDATE services SET {', '.join(set_clauses)} WHERE id = ?"
        
        cursor = conn.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0
    
    def delete_service(self, service_id: int) -> bool:
        """Delete service from database."""
        conn = self.get_connection()
        cursor = conn.execute("DELETE FROM services WHERE id = ?", (service_id,))
        conn.commit()
        return cursor.rowcount > 0
    
    def backup(self, backup_path: str | Path) -> None:
        """Create database backup."""
        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        source = sqlite3.connect(str(self.db_path))
        backup = sqlite3.connect(str(backup_path))
        
        source.backup(backup)
        source.close()
        backup.close()
    
    def vacuum(self) -> None:
        """Optimize database."""
        conn = self.get_connection()
        conn.execute("VACUUM")
        conn.execute("ANALYZE")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get database health status."""
        try:
            conn = self.get_connection()
            
            # Check if database is accessible
            conn.execute("SELECT 1")
            
            # Get basic stats
            cursor = conn.execute("SELECT COUNT(*) FROM services")
            service_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM breaches")
            breach_count = cursor.fetchone()[0]
            
            return {
                'status': 'healthy',
                'service_count': service_count,
                'breach_count': breach_count,
                'last_check': sqlite3.datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'last_check': sqlite3.datetime.now().isoformat(),
            }
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
