"""
Configuration Manager Module

Handles loading and managing configuration from various sources.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """
    Manages application configuration from files and environment variables.
    
    Supports:
    - JSON configuration files
    - Environment-specific configs (dev, staging, prod)
    - Environment variable overrides
    - Configuration validation
    """
    
    def __init__(
        self,
        config_dir: str = "config",
        environment: Optional[str] = None,
    ):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory containing config files
            environment: Environment name (dev, staging, prod)
        """
        self.config_dir = Path(config_dir)
        self.environment = environment or os.getenv("ENVIRONMENT", "dev")
        self.config = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from files."""
        # Load base config
        base_config_path = self.config_dir / "base.json"
        if base_config_path.exists():
            with open(base_config_path, "r") as f:
                self.config = json.load(f)
        
        # Load environment-specific config
        env_config_path = self.config_dir / self.environment / "config.json"
        if env_config_path.exists():
            with open(env_config_path, "r") as f:
                env_config = json.load(f)
                self._deep_merge(self.config, env_config)
        
        # Override with environment variables
        self._load_env_overrides()
    
    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            update: Dictionary to merge into base
            
        Returns:
            Merged dictionary
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base
    
    def _load_env_overrides(self):
        """Load configuration overrides from environment variables."""
        # AWS configuration
        if os.getenv("AWS_REGION"):
            self.config.setdefault("aws", {})["region"] = os.getenv("AWS_REGION")
        
        # Kinesis configuration
        if os.getenv("KINESIS_STREAM_NAME"):
            self.config.setdefault("kinesis", {})["stream_name"] = os.getenv("KINESIS_STREAM_NAME")
        
        # Timestream configuration
        if os.getenv("TIMESTREAM_DATABASE"):
            self.config.setdefault("timestream", {})["database"] = os.getenv("TIMESTREAM_DATABASE")
        
        if os.getenv("TIMESTREAM_TABLE"):
            self.config.setdefault("timestream", {})["table"] = os.getenv("TIMESTREAM_TABLE")
        
        # Logging configuration
        if os.getenv("LOG_LEVEL"):
            self.config.setdefault("logging", {})["level"] = os.getenv("LOG_LEVEL")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Supports dot notation for nested keys (e.g., 'aws.region').
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split(".")
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config.copy()
    
    def validate(self, required_keys: list) -> tuple[bool, list]:
        """
        Validate that required keys exist in configuration.
        
        Args:
            required_keys: List of required configuration keys
            
        Returns:
            Tuple of (is_valid, missing_keys)
        """
        missing = []
        
        for key in required_keys:
            if self.get(key) is None:
                missing.append(key)
        
        return len(missing) == 0, missing
    
    def save(self, output_path: Optional[str] = None):
        """
        Save current configuration to file.
        
        Args:
            output_path: Optional output file path
        """
        if output_path is None:
            output_path = self.config_dir / self.environment / "config.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(self.config, f, indent=2)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "ConfigManager":
        """
        Create ConfigManager from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            ConfigManager instance
        """
        manager = cls(config_dir="")
        manager.config = config_dict
        return manager


if __name__ == "__main__":
    # Example usage
    config = ConfigManager(environment="dev")
    
    # Get values
    region = config.get("aws.region", "us-east-1")
    stream_name = config.get("kinesis.stream_name")
    
    print(f"AWS Region: {region}")
    print(f"Kinesis Stream: {stream_name}")
    
    # Validate required keys
    is_valid, missing = config.validate([
        "aws.region",
        "kinesis.stream_name",
        "timestream.database",
    ])
    
    if not is_valid:
        print(f"Missing configuration: {missing}")
