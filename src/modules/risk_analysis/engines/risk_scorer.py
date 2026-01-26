"""
Risk Scoring Engine

Calculates risk scores for supply chain disruption events
based on event severity, supplier criticality, and geographic factors.
"""

import logging
from typing import Dict, Any, List

from ..models.risk import RiskLevel, RiskType, MitigationUrgency
from ..models.supplier import Supplier, SupplierCriticality


class RiskScorer:
    """
    Engine for calculating risk scores from disruption events.
    
    Combines multiple factors to produce a composite risk score:
    - Event severity and confidence
    - Affected supplier criticality
    - Geographic concentration risk
    - Financial exposure
    """
    
    def __init__(self):
        self.logger = logging.getLogger("RiskScorer")
        
        # Weight factors for risk calculation
        self._weights = {
            "event_severity": 0.30,
            "supplier_criticality": 0.30,
            "financial_exposure": 0.20,
            "geographic_risk": 0.20
        }
        
        # Severity value mapping
        self._severity_values = {
            "critical": 1.0,
            "high": 0.75,
            "medium": 0.5,
            "low": 0.25
        }
        
        # Criticality value mapping
        self._criticality_values = {
            SupplierCriticality.CRITICAL: 1.0,
            SupplierCriticality.HIGH: 0.75,
            SupplierCriticality.MEDIUM: 0.5,
            SupplierCriticality.LOW: 0.25
        }
    
    def calculate_risk_score(
        self,
        event: Dict[str, Any],
        affected_suppliers: List[Supplier],
        geographic_risk_factor: float = 0.5
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score for an event.
        
        Args:
            event: Normalized event from Module 1
            affected_suppliers: List of suppliers impacted by the event
            geographic_risk_factor: Geographic concentration risk (0-1)
            
        Returns:
            Dictionary with risk score and component scores
        """
        # Calculate component scores
        severity_score = self._calculate_severity_score(event)
        criticality_score = self._calculate_criticality_score(affected_suppliers)
        financial_score = self._calculate_financial_score(affected_suppliers)
        geo_score = geographic_risk_factor
        
        # Calculate weighted composite score
        composite_score = (
            self._weights["event_severity"] * severity_score +
            self._weights["supplier_criticality"] * criticality_score +
            self._weights["financial_exposure"] * financial_score +
            self._weights["geographic_risk"] * geo_score
        )
        
        # Determine risk level
        risk_level = RiskLevel.from_score(composite_score)
        
        # Determine mitigation urgency
        urgency = self._determine_urgency(composite_score, criticality_score)
        
        # Estimate impacts
        financial_impact = self._estimate_financial_impact(affected_suppliers, composite_score)
        delay_days = self._estimate_delay_days(event, composite_score)
        
        result = {
            "composite_score": round(composite_score, 3),
            "risk_level": risk_level,
            "mitigation_urgency": urgency,
            "component_scores": {
                "severity": round(severity_score, 3),
                "supplier_criticality": round(criticality_score, 3),
                "financial_exposure": round(financial_score, 3),
                "geographic": round(geo_score, 3)
            },
            "estimated_financial_impact": financial_impact,
            "estimated_delay_days": delay_days
        }
        
        self.logger.debug(
            f"Risk score calculated: {composite_score:.3f} ({risk_level.value})"
        )
        
        return result
    
    def _calculate_severity_score(self, event: Dict[str, Any]) -> float:
        """Calculate score based on event severity and confidence."""
        severity = event.get("severity", "medium")
        confidence = event.get("confidence", 1.0)
        impact_score = event.get("impact_score", 0.5)
        
        severity_value = self._severity_values.get(severity, 0.5)
        
        # Combine severity with confidence and existing impact score
        score = (severity_value * 0.5 + impact_score * 0.5) * confidence
        
        return min(1.0, score)
    
    def _calculate_criticality_score(self, suppliers: List[Supplier]) -> float:
        """Calculate score based on affected supplier criticality."""
        if not suppliers:
            return 0.0
        
        # Use maximum criticality of affected suppliers
        max_criticality = max(
            self._criticality_values.get(s.criticality, 0.5)
            for s in suppliers
        )
        
        # Add bonus for multiple affected suppliers
        count_bonus = min(0.2, len(suppliers) * 0.05)
        
        return min(1.0, max_criticality + count_bonus)
    
    def _calculate_financial_score(self, suppliers: List[Supplier]) -> float:
        """Calculate score based on financial exposure."""
        if not suppliers:
            return 0.0
        
        total_spend = sum(s.annual_spend for s in suppliers)
        
        # Normalize based on typical exposure thresholds
        # >$10M = high risk, >$5M = medium, <$1M = low
        if total_spend >= 10000000:
            return 1.0
        elif total_spend >= 5000000:
            return 0.7
        elif total_spend >= 1000000:
            return 0.4
        else:
            return 0.2
    
    def _determine_urgency(
        self, 
        composite_score: float, 
        criticality_score: float
    ) -> MitigationUrgency:
        """Determine mitigation urgency based on scores."""
        if composite_score >= 0.8 or criticality_score >= 0.9:
            return MitigationUrgency.IMMEDIATE
        elif composite_score >= 0.6:
            return MitigationUrgency.SHORT_TERM
        elif composite_score >= 0.4:
            return MitigationUrgency.MEDIUM_TERM
        else:
            return MitigationUrgency.LONG_TERM
    
    def _estimate_financial_impact(
        self, 
        suppliers: List[Supplier], 
        risk_score: float
    ) -> float:
        """Estimate potential financial impact."""
        if not suppliers:
            return 0
        
        # Base impact on affected spend
        total_spend = sum(s.annual_spend for s in suppliers)
        
        # Apply risk multiplier (higher risk = potentially larger impact)
        # Assume disruption affects 1-4 weeks of annual spend
        weeks_affected = 1 + (risk_score * 3)  # 1-4 weeks
        weekly_spend = total_spend / 52
        
        return round(weekly_spend * weeks_affected, 2)
    
    def _estimate_delay_days(self, event: Dict[str, Any], risk_score: float) -> int:
        """Estimate potential supply delay in days."""
        # Base delay on event severity
        severity_delays = {
            "critical": 14,
            "high": 7,
            "medium": 3,
            "low": 1
        }
        
        severity = event.get("severity", "medium")
        base_delay = severity_delays.get(severity, 3)
        
        # Adjust by risk score
        adjusted_delay = int(base_delay * (1 + risk_score))
        
        return adjusted_delay
    
    def get_risk_type(self, event: Dict[str, Any]) -> RiskType:
        """Determine risk type from event category."""
        category = event.get("category", "other")
        
        category_mapping = {
            "logistics": RiskType.LOGISTICS,
            "natural_disaster": RiskType.SUPPLY,
            "labor": RiskType.OPERATIONAL,
            "infrastructure": RiskType.LOGISTICS,
            "geopolitical": RiskType.GEOPOLITICAL,
            "economic": RiskType.FINANCIAL
        }
        
        return category_mapping.get(category, RiskType.OPERATIONAL)
