"""
Risk Classifier

Classifies risks into actionable categories based on
type, urgency, and recommended mitigation strategies.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from ..models.risk import Risk, RiskLevel, RiskType, MitigationUrgency, RiskAssessment


class RiskClassifier:
    """
    Classifies risks for actionable decision-making.
    
    Provides:
    - Risk categorization by type and urgency
    - Mitigation strategy recommendations
    - Priority ranking for action
    """
    
    def __init__(self):
        self.logger = logging.getLogger("RiskClassifier")
        
        # Mitigation strategy templates by risk type
        self._mitigation_strategies = {
            RiskType.SUPPLY: [
                "Activate backup suppliers",
                "Increase safety stock levels",
                "Expedite existing orders",
                "Source from alternative regions"
            ],
            RiskType.LOGISTICS: [
                "Reroute shipments via alternative routes",
                "Switch transportation modes",
                "Pre-position inventory at alternative hubs",
                "Coordinate with logistics partners"
            ],
            RiskType.FINANCIAL: [
                "Review hedging positions",
                "Assess cost pass-through options",
                "Negotiate payment terms",
                "Evaluate pricing adjustments"
            ],
            RiskType.OPERATIONAL: [
                "Implement contingency procedures",
                "Cross-train staff for critical functions",
                "Review BCP documentation",
                "Coordinate with operations teams"
            ],
            RiskType.GEOPOLITICAL: [
                "Monitor regulatory developments",
                "Diversify supplier base",
                "Review compliance requirements",
                "Engage government affairs team"
            ]
        }
    
    def classify_risk(self, risk: Risk) -> Dict[str, Any]:
        """
        Classify a risk and generate recommendations.
        
        Args:
            risk: Risk object to classify
            
        Returns:
            Classification with action items
        """
        # Determine action priority
        priority = self._calculate_priority(risk)
        
        # Get mitigation strategies
        strategies = self._get_strategies(risk)
        
        # Generate action items
        action_items = self._generate_action_items(risk, strategies)
        
        # Determine response deadline
        deadline = self._calculate_deadline(risk.mitigation_urgency)
        
        classification = {
            "risk_id": risk.risk_id,
            "classification": {
                "level": risk.risk_level.value,
                "type": risk.risk_type.value,
                "urgency": risk.mitigation_urgency.value,
                "priority": priority,
                "priority_label": self._get_priority_label(priority)
            },
            "response": {
                "deadline": deadline,
                "strategies": strategies,
                "action_items": action_items
            },
            "escalation": {
                "required": risk.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH],
                "level": self._get_escalation_level(risk)
            }
        }
        
        self.logger.debug(
            f"Risk classified: {risk.risk_id[:8]} - "
            f"Priority {priority} ({classification['classification']['priority_label']})"
        )
        
        return classification
    
    def _calculate_priority(self, risk: Risk) -> int:
        """
        Calculate priority score (lower = higher priority).
        
        Priority 1-3: Immediate action
        Priority 4-6: Short-term action
        Priority 7-9: Medium-term planning
        Priority 10+: Monitoring
        """
        # Base priority from risk level
        level_base = {
            RiskLevel.CRITICAL: 1,
            RiskLevel.HIGH: 4,
            RiskLevel.MEDIUM: 7,
            RiskLevel.LOW: 10
        }
        base = level_base.get(risk.risk_level, 7)
        
        # Adjust for urgency
        urgency_adjust = {
            MitigationUrgency.IMMEDIATE: -1,
            MitigationUrgency.SHORT_TERM: 0,
            MitigationUrgency.MEDIUM_TERM: 1,
            MitigationUrgency.LONG_TERM: 2
        }
        adjust = urgency_adjust.get(risk.mitigation_urgency, 0)
        
        # Adjust for critical suppliers
        if risk.has_critical_suppliers:
            adjust -= 1
        
        # Adjust for financial impact
        if risk.estimated_financial_impact > 1000000:
            adjust -= 1
        
        return max(1, base + adjust)
    
    def _get_priority_label(self, priority: int) -> str:
        """Get human-readable priority label."""
        if priority <= 3:
            return "IMMEDIATE"
        elif priority <= 6:
            return "HIGH"
        elif priority <= 9:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_strategies(self, risk: Risk) -> List[str]:
        """Get mitigation strategies for risk type."""
        strategies = self._mitigation_strategies.get(risk.risk_type, [])
        
        # Limit to top 3 most relevant strategies
        return strategies[:3]
    
    def _generate_action_items(
        self,
        risk: Risk,
        strategies: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate specific action items."""
        action_items = []
        
        # Add supplier-specific actions
        if risk.affected_suppliers:
            for i, supplier in enumerate(risk.affected_suppliers[:3]):
                action_items.append({
                    "action": f"Contact {supplier.name} for status update",
                    "owner": "Procurement",
                    "priority": i + 1
                })
        
        # Add strategy-based actions
        for i, strategy in enumerate(strategies):
            action_items.append({
                "action": strategy,
                "owner": "Supply Chain",
                "priority": len(action_items) + 1
            })
        
        # Add monitoring action
        action_items.append({
            "action": "Monitor situation for updates",
            "owner": "Risk Management",
            "priority": len(action_items) + 1
        })
        
        return action_items
    
    def _calculate_deadline(self, urgency: MitigationUrgency) -> str:
        """Calculate response deadline based on urgency."""
        deadlines = {
            MitigationUrgency.IMMEDIATE: "Within 24 hours",
            MitigationUrgency.SHORT_TERM: "Within 1 week",
            MitigationUrgency.MEDIUM_TERM: "Within 1 month",
            MitigationUrgency.LONG_TERM: "Within 3 months"
        }
        return deadlines.get(urgency, "To be determined")
    
    def _get_escalation_level(self, risk: Risk) -> str:
        """Determine escalation level."""
        if risk.risk_level == RiskLevel.CRITICAL:
            return "Executive Leadership"
        elif risk.risk_level == RiskLevel.HIGH and risk.has_critical_suppliers:
            return "VP Supply Chain"
        elif risk.risk_level == RiskLevel.HIGH:
            return "Director Level"
        elif risk.risk_level == RiskLevel.MEDIUM:
            return "Manager Level"
        else:
            return "Team Lead"
    
    def create_risk_matrix(
        self,
        assessment: RiskAssessment
    ) -> Dict[str, List[Dict]]:
        """
        Create a risk matrix organized by level and type.
        
        Returns:
            Matrix with risks organized for visualization
        """
        matrix = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for risk in assessment:
            classification = self.classify_risk(risk)
            
            matrix_entry = {
                "risk_id": risk.risk_id,
                "title": risk.title,
                "type": risk.risk_type.value,
                "score": risk.risk_score,
                "priority": classification["classification"]["priority"],
                "affected_suppliers": risk.affected_supplier_count,
                "deadline": classification["response"]["deadline"]
            }
            
            matrix[risk.risk_level.value].append(matrix_entry)
        
        # Sort each level by priority
        for level in matrix:
            matrix[level].sort(key=lambda x: x["priority"])
        
        return matrix
