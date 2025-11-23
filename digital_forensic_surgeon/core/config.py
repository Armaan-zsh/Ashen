"""Configuration management for Digital Forensic Surgeon."""

from __future__ import annotations

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from .exceptions import ConfigurationError


@dataclass
class ForensicConfig:
    """Main configuration class."""
    
    # Database settings
    db_path: str = "atlas.sqlite"
    db_url: Optional[str] = None
    
    # Scanner settings
    max_workers: int = 4
    scan_timeout: int = 300  # seconds
    evidence_retention_days: int = 90
    enable_parallel_scanning: bool = True
    
    # Risk assessment
    high_risk_threshold: float = 6.0
    critical_risk_threshold: float = 8.0
    risk_weights: Dict[str, float] = field(default_factory=lambda: {
        "financial": 2.0,
        "medical": 2.0,
        "social": 1.0,
        "entertainment": 0.5,
        "shopping": 1.5,
        "work": 1.0,
    })
    
    # Security settings
    require_password_for_secrets: bool = True
    encrypt_sensitive_data: bool = True
    master_password: Optional[str] = None
    salt_rounds: int = 100000
    
    # Output settings
    output_dir: str = "./forensic_output"
    generate_pdf: bool = False
    generate_html: bool = True
    generate_json: bool = True
    generate_csv: bool = False
    
    # Logging settings
    log_level: str = "INFO"
    log_file: Optional[str] = None
    enable_console_logging: bool = True
    
    # Browser settings
    scan_browser_data: bool = True
    browser_profiles: list[str] = field(default_factory=list)
    
    # Network settings
    scan_network_activity: bool = True
    check_for_leaks: bool = False
    user_agent: str = "Digital-Forensic-Surgeon/1.0"
    
    # Geo-Spatial Intelligence settings
    extract_image_gps: bool = True
    scan_wifi_networks: bool = True
    wigle_api_key: Optional[str] = None
    geolocation_enabled: bool = False
    
    # OSINT (Open Source Intelligence) settings
    osint_enabled: bool = False
    osint_sites: List[str] = field(default_factory=lambda: [
        "github.com/{username}",
        "reddit.com/user/{username}",
        "twitter.com/{username}",
        "instagram.com/{username}",
        "linkedin.com/in/{username}",
        "facebook.com/{username}",
        "tiktok.com/@{username}",
        "youtube.com/@{username}",
        "pornhub.com/users/{username}",
        "roblox.com/users/{username}/profile"
    ])
    osint_timeout: int = 10  # seconds per site
    osint_max_workers: int = 20
    
    # Custom settings from config file
    custom: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate and normalize configuration."""
        # Set defaults based on platform
        if not self.db_path.startswith('/'):
            self.db_path = str(Path.home() / '.local' / 'share' / 'digital_forensic_surgeon' / self.db_path)
        
        if not self.output_dir.startswith('/'):
            self.output_dir = str(Path.home() / self.output_dir)
        
        # Create directories if they don't exist
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_file(cls, config_path: str | Path) -> ForensicConfig:
        """Load configuration from YAML file."""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f) or {}
            
            return cls(**data)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    @classmethod
    def from_env(cls) -> ForensicConfig:
        """Load configuration from environment variables."""
        config = cls()
        
        # Override with environment variables if present
        if os.getenv('FORENSIC_DB_PATH'):
            config.db_path = os.getenv('FORENSIC_DB_PATH')
        
        if os.getenv('FORENSIC_OUTPUT_DIR'):
            config.output_dir = os.getenv('FORENSIC_OUTPUT_DIR')
        
        if os.getenv('FORENSIC_MAX_WORKERS'):
            config.max_workers = int(os.getenv('FORENSIC_MAX_WORKERS'))
        
        if os.getenv('FORENSIC_LOG_LEVEL'):
            config.log_level = os.getenv('FORENSIC_LOG_LEVEL')
        
        if os.getenv('FORENSIC_MASTER_PASSWORD'):
            config.master_password = os.getenv('FORENSIC_MASTER_PASSWORD')
        
        if os.getenv('FORENSIC_WIGLE_API_KEY'):
            config.wigle_api_key = os.getenv('FORENSIC_WIGLE_API_KEY')
        
        if os.getenv('FORENSIC_OSINT_ENABLED'):
            config.osint_enabled = os.getenv('FORENSIC_OSINT_ENABLED').lower() == 'true'
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'db_path': self.db_path,
            'db_url': self.db_url,
            'max_workers': self.max_workers,
            'scan_timeout': self.scan_timeout,
            'evidence_retention_days': self.evidence_retention_days,
            'enable_parallel_scanning': self.enable_parallel_scanning,
            'high_risk_threshold': self.high_risk_threshold,
            'critical_risk_threshold': self.critical_risk_threshold,
            'risk_weights': self.risk_weights,
            'require_password_for_secrets': self.require_password_for_secrets,
            'encrypt_sensitive_data': self.encrypt_sensitive_data,
            'master_password': self.master_password,  # Note: should not be serialized in production
            'salt_rounds': self.salt_rounds,
            'output_dir': self.output_dir,
            'generate_pdf': self.generate_pdf,
            'generate_html': self.generate_html,
            'generate_json': self.generate_json,
            'generate_csv': self.generate_csv,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'enable_console_logging': self.enable_console_logging,
            'scan_browser_data': self.scan_browser_data,
            'browser_profiles': self.browser_profiles,
            'scan_network_activity': self.scan_network_activity,
            'check_for_leaks': self.check_for_leaks,
            'user_agent': self.user_agent,
            'extract_image_gps': self.extract_image_gps,
            'scan_wifi_networks': self.scan_wifi_networks,
            'wigle_api_key': self.wigle_api_key,
            'geolocation_enabled': self.geolocation_enabled,
            'osint_enabled': self.osint_enabled,
            'osint_sites': self.osint_sites,
            'osint_timeout': self.osint_timeout,
            'osint_max_workers': self.osint_max_workers,
            'custom': self.custom,
        }
    
    def save_to_file(self, config_path: str | Path) -> None:
        """Save configuration to YAML file."""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)
    
    def validate(self) -> None:
        """Validate configuration settings."""
        if self.max_workers < 1 or self.max_workers > 32:
            raise ConfigurationError("max_workers must be between 1 and 32")
        
        if self.scan_timeout < 10:
            raise ConfigurationError("scan_timeout must be at least 10 seconds")
        
        if not 0.0 <= self.high_risk_threshold <= 10.0:
            raise ConfigurationError("high_risk_threshold must be between 0.0 and 10.0")
        
        if not 0.0 <= self.critical_risk_threshold <= 10.0:
            raise ConfigurationError("critical_risk_threshold must be between 0.0 and 10.0")
        
        if self.high_risk_threshold >= self.critical_risk_threshold:
            raise ConfigurationError("high_risk_threshold must be less than critical_risk_threshold")
        
        # Validate risk weights
        if not isinstance(self.risk_weights, dict):
            raise ConfigurationError("risk_weights must be a dictionary")
        
        for category, weight in self.risk_weights.items():
            if not isinstance(weight, (int, float)) or weight < 0:
                raise ConfigurationError(f"Invalid risk weight for {category}: {weight}")


# Global configuration instance
_config: ForensicConfig | None = None


def get_config() -> ForensicConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = ForensicConfig()
    return _config


def set_config(config: ForensicConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config


def load_config(config_path: str | Path | None = None) -> ForensicConfig:
    """Load configuration from file or environment."""
    if config_path and Path(config_path).exists():
        config = ForensicConfig.from_file(config_path)
    else:
        config = ForensicConfig.from_env()
    
    config.validate()
    set_config(config)
    return config
