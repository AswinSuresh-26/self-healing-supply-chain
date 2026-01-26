"""
Risk Data Model

Represents analyzed risks derived from supply chain disruption events.
Contains risk scoring, classification, and affected supplier information.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional

from .supplier import Supplier


class RiskLevel(Enum):
    """Risk severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    @classmethod
    def from_score(cls, score: float) -> "RiskLevel":
        """Convert a numeric score (0-1) to risk level."""
        if score >= 0.8:
            return cls.CRITICAL
        elif score >= 0.6:
            return cls.HIGH
        elif score >= 0.4:
            return cls.MEDIUM
        else:
            return cls.LOW


class RiskType(Enum):
    """Types of supply chain risks."""
    SUPPLY = "supply"              # Supply disruption
    LOGISTICS = "logistics"        # Transportation/shipping issues
    FINANCIAL = "financial"        # Cost/financial impact
    OPERATIONAL = "operational"    # Operations disruption
    QUALITY = "quality"           # Quality/compliance issues
    GEOPOLITICAL = "geopolitical" # Political/regulatory risks


class MitigationUrgency(Enum):
    """Urgency level for risk mitigation."""
    IMMEDIATE = "immediate"      # Act within 24 hours
    SHORT_TERM = "short_term"    # Act within 1 week
    MEDIUM_TERM = "medium_term"  # Act within 1 month
    LONG_TERM = "long_term"      # Plan for future


class Risk:
    """
    Represents an analyzed supply chain risk.
    
    Derived from disruption events detected by the Event Sensing Module,
    enriched with supplier impact analysis and risk scoring.
    """
    
    def __init__(
        self,
        source_event_id: str,
        title: str,
        description: str,
        risk_score: float,
        risk_level: RiskLevel,
        risk_type: RiskType,
        affected_suppliers: List[Supplier] = None,
        geographic_scope: str = None,
        mitigation_urgency: MitigationUrgency = MitigationUrgency.MEDIUM_TERM,
        estimated_financial_impact: float = 0,
        estimated_delay_days: int = 0,
        confidence: float = 1.0,
        risk_id: str = None,
        created_at: datetime = None
    ):
        """
        Initialize a Risk.
        
        Args:
            source_event_id: ID of the triggering event from Module 1
            title: Short risk description
            description: Detailed risk information
            risk_score: Computed risk score (0-1)
            risk_level: Risk severity level
            risk_type: Type of supply chain risk
            affected_suppliers: List of impacted suppliers
            geographic_scope: Affected geographic region
            mitigation_urgency: How urgently mitigation is needed
            estimated_financial_impact: Estimated cost impact
            estimated_delay_days: Estimated supply delay in days
            confidence: Confidence in the risk assessment
            risk_id: Unique identifier (auto-generated if not provided)
            created_at: When the risk was created
        """
        self.risk_id = risk_id or str(uuid.uuid4())
        self.source_event_id = source_event_id
        self.title = title
        self.description = description
        self.risk_score = min(max(risk_score, 0.0), 1.0)
        self.risk_level = risk_level
        self.risk_type = risk_type
        self.affected_suppliers = affected_suppliers or []
        self.geographic_scope = geographic_scope
        self.mitigation_urgency = mitigation_urgency
        self.estimated_financial_impact = estimated_financial_impact
        self.estimated_delay_days = estimated_delay_days
        self.confidence = min(max(confidence, 0.0), 1.0)
        self.created_at = created_at or datetime.now()
    
    @property
    def affected_supplier_count(self) -> int:
        """Get count of affected suppliers."""
        return len(self.affected_suppliers)
    
    @property
    def has_critical_suppliers(self) -> bool:
        """Check if any critical suppliers are affected."""
        from .supplier import SupplierCriticality
        return any(
            s.criticality == SupplierCriticality.CRITICAL 
            for s in self.affected_suppliers
        )
    
    @property
    def total_affected_spend(self) -> float:
        """Calculate total annual spend affected."""
        return sum(s.annual_spend for s in self.affected_suppliers)
    
    def get_affected_supplier_names(self) -> List[str]:
        """Get list of affected supplier names."""
        return [s.name for s in self.affected_suppliers]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert risk to dictionary."""
        return {
            "risk_id": self.risk_id,
            "source_event_id": self.source_event_id,
            "title": self.title,
            "description": self.description,
            "risk_score": round(self.risk_score, 3),
            "risk_level": self.risk_level.value,
            "risk_type": self.risk_type.value,
            "affected_suppliers": [s.to_dict() for s in self.affected_suppliers],
            "affected_supplier_count": self.affected_supplier_count,
            "geographic_scope": self.geographic_scope,
            "mitigation_urgency": self.mitigation_urgency.value,
            "estimated_financial_impact": self.estimated_financial_impact,
            "estimated_delay_days": self.estimated_delay_days,
            "confidence": round(self.confidence, 3),
            "has_critical_suppliers": self.has_critical_suppliers,
            "total_affected_spend": self.total_affected_spend,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Risk":
        """Create risk from dictionary."""
        from .supplier import Supplier
        
        suppliers = [
            Supplier.from_dict(s) for s in data.get("affected_suppliers", [])
        ]
        
        return cls(
            risk_id=data.get("risk_id"),
            source_event_id=data["source_event_id"],
            title=data["title"],
            description=data["description"],
            risk_score=data["risk_score"],
            risk_level=RiskLevel(data["risk_level"]),
            risk_type=RiskType(data["risk_type"]),
            affected_suppliers=suppliers,
            geographic_scope=data.get("geographic_scope"),
            mitigation_urgency=MitigationUrgency(data.get("mitigation_urgency", "medium_term")),
            estimated_financial_impact=data.get("estimated_financial_impact", 0),
            estimated_delay_days=data.get("estimated_delay_days", 0),
            confidence=data.get("confidence", 1.0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        )
    
    def __repr__(self) -> str:
        return (
            f"Risk(id={self.risk_id[:8]}..., "
            f"level={self.risk_level.value}, "
            f"score={self.risk_score:.2f}, "
            f"suppliers={self.affected_supplier_count})"
        )
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Risk):
            return self.risk_id == other.risk_id
        return False
    
    def __hash__(self) -> int:
        return hash(self.risk_id)


class RiskAssessment:
    """
    A collection of risks from an assessment cycle.
    
    Provides summary statistics and aggregated views.
    """
    
    def __init__(self, risks: List[Risk] = None):
        self.risks = risks or []
        self.assessment_id = str(uuid.uuid4())
        self.created_at = datetime.now()
    
    def add(self, risk: Risk):
        """Add a risk to the assessment."""
        self.risks.append(risk)
    
    @property
    def total_risks(self) -> int:
        return len(self.risks)
    
    @property
    def critical_risks(self) -> List[Risk]:
        return [r for r in self.risks if r.risk_level == RiskLevel.CRITICAL]
    
    @property
    def high_risks(self) -> List[Risk]:
        return [r for r in self.risks if r.risk_level == RiskLevel.HIGH]
    
    @property
    def immediate_action_required(self) -> List[Risk]:
        return [r for r in self.risks if r.mitigation_urgency == MitigationUrgency.IMMEDIATE]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get assessment summary."""
        level_counts = {}
        type_counts = {}
        total_impact = 0
        total_delay = 0
        
        for risk in self.risks:
            level_counts[risk.risk_level.value] = level_counts.get(risk.risk_level.value, 0) + 1
            type_counts[risk.risk_type.value] = type_counts.get(risk.risk_type.value, 0) + 1
            total_impact += risk.estimated_financial_impact
            total_delay = max(total_delay, risk.estimated_delay_days)
        
        return {
            "assessment_id": self.assessment_id,
            "total_risks": self.total_risks,
            "risks_by_level": level_counts,
            "risks_by_type": type_counts,
            "critical_count": len(self.critical_risks),
            "immediate_action_count": len(self.immediate_action_required),
            "total_estimated_impact": total_impact,
            "max_delay_days": total_delay,
            "created_at": self.created_at.isoformat()
        }
    
    def __len__(self) -> int:
        return len(self.risks)
    
    def __iter__(self):
        return iter(self.risks)
