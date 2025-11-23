"""
ServicesDB for Digital Forensic Surgeon
Handles loading and querying the services database.
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional, Any

class ServicesDB:
    """
    A simple in-memory database for services, loaded from a CSV file.
    """
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self._services: Dict[str, Dict[str, Any]] = {}
        self._load_services()

    def _load_services(self):
        """
        Loads the services from the CSV file into memory.
        """
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    domain = row.get('domain')
                    if domain:
                        self._services[domain] = row
        except FileNotFoundError:
            # Handle case where file doesn't exist
            pass

    def get_service_by_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves service information by domain.
        """
        return self._services.get(domain)

    def get_all_services(self) -> List[Dict[str, Any]]:
        """
        Returns all loaded services.
        """
        return list(self._services.values())

    @property
    def count(self) -> int:
        """
        Returns the number of loaded services.
        """
        return len(self._services)
