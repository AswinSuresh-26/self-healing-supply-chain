# Risk Analysis Module
"""
Disruption Risk Analysis Module for the Self-Healing Supply Chain Framework.

This module analyzes events from the Event Sensing Module to assess
supply chain disruption risks and generate alerts.
"""

from .models.risk import Risk, RiskLevel, RiskType, MitigationUrgency
from .models.supplier import Supplier, SupplierCriticality
from .engines.risk_scorer import RiskScorer
from .engines.impact_analyzer import SupplierImpactAnalyzer
from .engines.geo_correlator import GeographicCorrelator
from .core.classifier import RiskClassifier
from .core.alert_generator import AlertGenerator, Alert

__version__ = "1.0.0"
__all__ = [
    "Risk",
    "RiskLevel",
    "RiskType",
    "MitigationUrgency",
    "Supplier",
    "SupplierCriticality",
    "RiskScorer",
    "SupplierImpactAnalyzer",
    "GeographicCorrelator",
    "RiskClassifier",
    "AlertGenerator",
    "Alert",
]
