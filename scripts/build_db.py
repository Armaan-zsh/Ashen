#!/usr/bin/env python3
"""Build the Digital Forensic Surgeon database from CSV files."""

from __future__ import annotations

import argparse
import sqlite3
import csv
import json
from pathlib import Path
from typing import Dict, Any, List

# Import database schema functions
from digital_forensic_surgeon.db.schema import (
    create_database,
    initialize_schema, 
    load_services_from_csv,
    get_statistics
)
from digital_forensic_surgeon.core.exceptions import DatabaseError


def build_database(db_path: Path, services_csv: Path, force: bool = False) -> Dict[str, Any]:
    """Build the complete forensic database."""
    
    print(f"Building forensic database at: {db_path}")
    
    # Check if database exists
    if db_path.exists() and not force:
        response = input(f"Database {db_path} already exists. Overwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Aborted.")
            return {'success': False, 'error': 'User cancelled'}
        
        # Remove existing database
        db_path.unlink()
    
    # Create database directory
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Create and initialize database
        print("Creating database...")
        conn = create_database(db_path)
        
        print("Initializing schema...")
        initialize_schema(conn)
        
        # Load services data
        if services_csv.exists():
            print(f"Loading services from: {services_csv}")
            load_services_from_csv(conn, services_csv)
        else:
            print(f"WARNING: Services CSV not found: {services_csv}")
        
        # Get statistics
        stats = get_statistics(conn)
        
        # Close connection
        conn.close()
        
        print("\nDatabase built successfully!")
        print(f"Services loaded: {stats.get('total_services', 0)}")
        print(f"Categories: {len(stats.get('services_by_category', {}))}")
        print(f"Breaches recorded: {stats.get('total_breaches', 0)}")
        
        return {
            'success': True,
            'stats': stats,
            'db_path': str(db_path)
        }
        
    except Exception as e:
        print(f"ERROR: Failed to build database: {e}")
        return {'success': False, 'error': str(e)}


def add_sample_breach_data(db_path: Path) -> None:
    """Add sample breach data to the database."""
    print("Adding sample breach data...")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Sample breach data
    breaches = [
        ("Facebook", "Cambridge Analytica", "2018-03-17", 87000000, '["names", "political_affiliations"]', "high"),
        ("Twitter", "Database Leak", "2022-07-01", 5400000, '["usernames", "emails", "password_hashes"]', "high"),
        ("LinkedIn", "Member Password Violation", "2012-06-05", 117000000, '["hashed_passwords", "emails"]', "medium"),
        ("Dropbox", "User Information Breach", "2012-07-01", 69000000, '["email_addresses", "password_hashes"]', "high"),
        ("Adobe", "Customer Security Announcement", "2013-10-03", 38000000, '["credit_cards", "passwords", "names"]', "critical"),
        ("LinkedIn", "Member Password Breach", "2016-05-18", 117000000, '["password_hashes", "emails"]', "high"),
        ("MySpace", "Account Security Information", "2016-05-31", 360000000, '["emails", "passwords", "usernames"]', "high"),
        ("Badoo", "Account Database Breach", "2013-06-03", 410000000, '["usernames", "emails", "passwords"]', "high"),
        ("VK", "Account Database Exposure", "2016-01-03", 100000000, '["usernames", "emails", "phone_numbers"]', "medium"),
        ("Instagram", "Fitness App Database Leak", "2019-04-18", 49000000, '["emails", "phone_numbers", "bio"]', "medium"),
    ]
    
    insert_breach = """
    INSERT INTO breaches (
        service_name, breach_name, breach_date, records_count, data_types, severity
    ) VALUES (?, ?, ?, ?, ?, ?)
    """
    
    try:
        cursor.executemany(insert_breach, breaches)
        conn.commit()
        print(f"Added {len(breaches)} breach records")
    except Exception as e:
        print(f"ERROR: Failed to add breach data: {e}")
    finally:
        conn.close()


def validate_database(db_path: Path) -> Dict[str, Any]:
    """Validate the built database."""
    print(f"Validating database: {db_path}")
    
    if not db_path.exists():
        return {'valid': False, 'error': 'Database file does not exist'}
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check table existence
        tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [table[0] for table in tables]
        
        required_tables = ['services', 'credentials', 'breaches']
        missing_tables = [t for t in required_tables if t not in table_names]
        
        if missing_tables:
            return {'valid': False, 'error': f'Missing tables: {missing_tables}'}
        
        # Check data counts
        service_count = cursor.execute("SELECT COUNT(*) FROM services").fetchone()[0]
        breach_count = cursor.execute("SELECT COUNT(*) FROM breaches").fetchone()[0]
        
        # Check for required columns
        cursor.execute("PRAGMA table_info(services)")
        service_columns = [row[1] for row in cursor.fetchall()]
        required_columns = ['name', 'domain', 'category', 'difficulty', 'breach_count']
        missing_columns = [col for col in required_columns if col not in service_columns]
        
        if missing_columns:
            return {'valid': False, 'error': f'Missing columns in services: {missing_columns}'}
        
        conn.close()
        
        return {
            'valid': True,
            'stats': {
                'services': service_count,
                'breaches': breach_count,
                'tables': table_names
            }
        }
        
    except Exception as e:
        return {'valid': False, 'error': str(e)}


def create_backup(db_path: Path, backup_path: Path) -> bool:
    """Create a backup of the database."""
    try:
        source = sqlite3.connect(str(db_path))
        backup = sqlite3.connect(str(backup_path))
        source.backup(backup)
        source.close()
        backup.close()
        print(f"Backup created: {backup_path}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create backup: {e}")
        return False


def main():
    """Main entry point for database build script."""
    parser = argparse.ArgumentParser(
        description="Build the Digital Forensic Surgeon database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_db.py --output /path/to/atlas.sqlite
  python build_db.py --force --output /path/to/atlas.sqlite
  python build_db.py --validate /path/to/atlas.sqlite
  python build_db.py --backup /path/to/atlas.sqlite /path/to/backup.sqlite
        """
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output database path (default: ./atlas.sqlite)'
    )
    
    parser.add_argument(
        '--services-csv', '-s', 
        type=Path,
        help='Services CSV file path (default: ./data/services.csv)'
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Force overwrite existing database'
    )
    
    parser.add_argument(
        '--validate', '-v',
        type=Path,
        help='Validate existing database file'
    )
    
    parser.add_argument(
        '--backup',
        type=str,
        help='Create backup of database (specify backup path)'
    )
    
    parser.add_argument(
        '--add-breach-data',
        action='store_true',
        help='Add sample breach data to database'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics'
    )
    
    args = parser.parse_args()
    
    # Set default paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    if args.output:
        db_path = Path(args.output)
    else:
        db_path = project_root / 'db' / 'atlas.sqlite'
    
    if args.services_csv:
        services_csv = Path(args.services_csv)
    else:
        services_csv = project_root / 'data' / 'services.csv'
    
    # Handle different commands
    if args.validate:
        result = validate_database(Path(args.validate))
        if result['valid']:
            print("✅ Database validation passed")
            if args.stats:
                print(f"Services: {result['stats']['services']}")
                print(f"Breaches: {result['stats']['breaches']}")
                print(f"Tables: {', '.join(result['stats']['tables'])}")
        else:
            print(f"❌ Database validation failed: {result['error']}")
            return 1
        return 0
    
    if args.backup:
        backup_path = Path(args.backup)
        if create_backup(db_path, backup_path):
            return 0
        else:
            return 1
    
    if args.stats:
        if not db_path.exists():
            print(f"Database not found: {db_path}")
            return 1
        
        conn = sqlite3.connect(str(db_path))
        stats = get_statistics(conn)
        conn.close()
        
        print("Database Statistics:")
        print(f"  Total Services: {stats['total_services']}")
        print(f"  Total Breaches: {stats['total_breaches']}")
        print(f"  Average Breaches per Service: {stats['average_breach_count']:.2f}")
        print(f"  Categories:")
        for category, count in stats['services_by_category'].items():
            print(f"    {category}: {count}")
        return 0
    
    # Build database
    result = build_database(db_path, services_csv, args.force)
    
    if not result['success']:
        print(f"❌ Database build failed: {result['error']}")
        return 1
    
    print("✅ Database built successfully!")
    
    # Optionally add breach data
    if args.add_breach_data:
        add_sample_breach_data(db_path)
    
    # Validate the built database
    validation = validate_database(db_path)
    if validation['valid']:
        print("✅ Database validation passed")
    else:
        print(f"❌ Database validation failed: {validation['error']}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
