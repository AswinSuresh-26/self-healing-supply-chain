"""
Configuration Settings for Risk Analysis Module

Manages configuration with sensible defaults.
"""

import logging
from typing import Dict, Any


DEFAULT_CONFIG = {
    "module": {
        "name": "Disruption Risk Analysis Module",
        "version": "1.0.0"
    },
    "scoring": {
        "critical_threshold": 0.8,
        "high_threshold": 0.6,
        "medium_threshold": 0.4,
        "weights": {
            "event_severity": 0.30,
            "supplier_criticality": 0.30,
            "financial_exposure": 0.20,
            "geographic_risk": 0.20
        }
    },
    "alerts": {
        "enabled": True,
        "p1_threshold": 0.8,
        "p2_threshold": 0.6,
        "p3_threshold": 0.4
    },
    "logging": {
        "level": "INFO"
    }
}


class RiskAnalysisSettings:
    """Settings for the Risk Analysis Module."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self._config = config or DEFAULT_CONFIG.copy()
    
    @property
    def critical_threshold(self) -> float:
        return self._config.get("scoring", {}).get("critical_threshold", 0.8)
    
    @property
    def high_threshold(self) -> float:
        return self._config.get("scoring", {}).get("high_threshold", 0.6)
    
    @property
    def medium_threshold(self) -> float:
        return self._config.get("scoring", {}).get("medium_threshold", 0.4)
    
    @property
    def alerts_enabled(self) -> bool:
        return self._config.get("alerts", {}).get("enabled", True)


_settings = None


def get_settings() -> RiskAnalysisSettings:
    """Get global settings instance."""
    global _settings
    if _settings is None:
        _settings = RiskAnalysisSettings()
    return _settings
