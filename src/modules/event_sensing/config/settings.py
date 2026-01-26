"""
Configuration Settings

Manages configuration for the Event Sensing Module.
Loads settings from YAML file or uses defaults.
"""

import os
import logging
from typing import Dict, Any, List


# Default configuration
DEFAULT_CONFIG = {
    "module": {
        "name": "External Event Sensing Module",
        "version": "1.0.0",
        "mode": "simulation"
    },
    "agents": {
        "news": {
            "enabled": True,
            "poll_interval_seconds": 60,
            "keywords": [
                "port closure",
                "shipping delay",
                "logistics disruption",
                "supply chain",
                "transport strike",
                "cargo"
            ]
        },
        "weather": {
            "enabled": True,
            "poll_interval_seconds": 120,
            "severity_threshold": "medium",
            "event_types": [
                "cyclone",
                "flood",
                "earthquake",
                "storm",
                "hurricane"
            ]
        },
        "economic": {
            "enabled": False
        },
        "social": {
            "enabled": False
        }
    },
    "aggregator": {
        "deduplication_window_seconds": 300,
        "max_events_buffer": 100
    },
    "normalizer": {
        "confidence_threshold": 0.5
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}


class Settings:
    """
    Configuration settings for the Event Sensing Module.
    
    Provides access to configuration values with sensible defaults.
    Can load from YAML file or use environment variables for overrides.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize settings.
        
        Args:
            config: Optional configuration dictionary. Uses defaults if not provided.
        """
        self._config = config or DEFAULT_CONFIG.copy()
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging based on settings."""
        log_config = self._config.get("logging", {})
        log_level = log_config.get("level", "INFO")
        log_format = log_config.get("format", DEFAULT_CONFIG["logging"]["format"])
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format=log_format
        )
    
    @property
    def mode(self) -> str:
        """Get the operation mode (simulation or live)."""
        return self._config.get("module", {}).get("mode", "simulation")
    
    @property
    def is_simulation(self) -> bool:
        """Check if running in simulation mode."""
        return self.mode == "simulation"
    
    # News Agent Settings
    @property
    def news_enabled(self) -> bool:
        """Check if news agent is enabled."""
        return self._config.get("agents", {}).get("news", {}).get("enabled", True)
    
    @property
    def news_keywords(self) -> List[str]:
        """Get keywords for news filtering."""
        return self._config.get("agents", {}).get("news", {}).get("keywords", [])
    
    @property
    def news_poll_interval(self) -> int:
        """Get news agent poll interval in seconds."""
        return self._config.get("agents", {}).get("news", {}).get("poll_interval_seconds", 60)
    
    # Weather Agent Settings
    @property
    def weather_enabled(self) -> bool:
        """Check if weather agent is enabled."""
        return self._config.get("agents", {}).get("weather", {}).get("enabled", True)
    
    @property
    def weather_event_types(self) -> List[str]:
        """Get monitored weather event types."""
        return self._config.get("agents", {}).get("weather", {}).get("event_types", [])
    
    @property
    def weather_severity_threshold(self) -> str:
        """Get minimum severity threshold for weather alerts."""
        return self._config.get("agents", {}).get("weather", {}).get("severity_threshold", "medium")
    
    @property
    def weather_poll_interval(self) -> int:
        """Get weather agent poll interval in seconds."""
        return self._config.get("agents", {}).get("weather", {}).get("poll_interval_seconds", 120)
    
    # Aggregator Settings
    @property
    def deduplication_window(self) -> int:
        """Get deduplication window in seconds."""
        return self._config.get("aggregator", {}).get("deduplication_window_seconds", 300)
    
    @property
    def max_events_buffer(self) -> int:
        """Get maximum events to buffer."""
        return self._config.get("aggregator", {}).get("max_events_buffer", 100)
    
    # Normalizer Settings
    @property
    def confidence_threshold(self) -> float:
        """Get minimum confidence threshold for events."""
        return self._config.get("normalizer", {}).get("confidence_threshold", 0.5)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key path (dot notation)."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def to_dict(self) -> Dict[str, Any]:
        """Return the full configuration dictionary."""
        return self._config.copy()


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def load_settings(config: Dict[str, Any]) -> Settings:
    """Load settings from a configuration dictionary."""
    global _settings
    _settings = Settings(config)
    return _settings
