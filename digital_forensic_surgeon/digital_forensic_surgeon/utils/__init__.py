"""Utilities module for Digital Forensic Surgeon."""

from __future__ import annotations

from .helpers import (
    setup_logging,
    sanitize_path,
    format_file_size,
    format_duration,
    safe_filename,
    validate_email,
    validate_url,
    hash_data,
    encrypt_data,
    decrypt_data,
    load_json_safe,
    save_json_safe,
    ensure_directory,
    get_platform_info,
)

from .crypto import (
    generate_secure_hash,
    encrypt_sensitive_data,
    decrypt_sensitive_data,
    create_master_key,
    derive_key_from_password,
)

from .concurrency import (
    run_parallel_tasks,
    create_thread_pool,
    run_with_timeout,
    chunk_iterable,
)

__all__ = [
    # Helpers
    "setup_logging",
    "sanitize_path",
    "format_file_size", 
    "format_duration",
    "safe_filename",
    "validate_email",
    "validate_url",
    "hash_data",
    "encrypt_data",
    "decrypt_data",
    "load_json_safe",
    "save_json_safe",
    "ensure_directory",
    "get_platform_info",
    
    # Crypto
    "generate_secure_hash",
    "encrypt_sensitive_data",
    "decrypt_sensitive_data",
    "create_master_key",
    "derive_key_from_password",
    
    # Concurrency
    "run_parallel_tasks",
    "create_thread_pool",
    "run_with_timeout",
    "chunk_iterable",
]
