"""
Contract Model

Represents emergency supplier contracts generated for recovery.
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional


class ContractType(Enum):
    """Types of emergency contracts."""
    EXPEDITED_PURCHASE = "expedited_purchase"
    SPOT_BUY = "spot_buy"
    EMERGENCY_SERVICE = "emergency_service"
    TEMPORARY_AGREEMENT = "temporary_agreement"


class ContractStatus(Enum):
    """Contract lifecycle status."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    EXECUTED = "executed"
    EXPIRED = "expired"


class Contract:
    """
    Represents an emergency supplier contract.
    """
    
    def __init__(
        self,
        supplier_name: str,
        contract_type: ContractType,
        title: str,
        total_value: float,
        duration_days: int,
        items: List[Dict[str, Any]] = None,
        terms: Dict[str, Any] = None,
        recovery_plan_id: str = None,
        contract_id: str = None
    ):
        self.contract_id = contract_id or str(uuid.uuid4())
        self.supplier_name = supplier_name
        self.contract_type = contract_type
        self.title = title
        self.total_value = total_value
        self.duration_days = duration_days
        self.items = items or []
        self.terms = terms or {}
        self.recovery_plan_id = recovery_plan_id
        self.status = ContractStatus.DRAFT
        self.created_at = datetime.now()
        self.content_sections: Dict[str, str] = {}
    
    def add_section(self, section_name: str, content: str):
        """Add a section to the contract."""
        self.content_sections[section_name] = content
    
    def get_expiry_date(self) -> datetime:
        """Get contract expiry date."""
        return self.created_at + timedelta(days=self.duration_days)
    
    def get_full_content(self) -> str:
        """Get complete contract text."""
        sections = []
        for name, content in self.content_sections.items():
            sections.append(f"\n{name}\n{'=' * len(name)}\n{content}")
        return "\n".join(sections)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "supplier_name": self.supplier_name,
            "contract_type": self.contract_type.value,
            "title": self.title,
            "total_value": self.total_value,
            "duration_days": self.duration_days,
            "items": self.items,
            "terms": self.terms,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expiry_date": self.get_expiry_date().isoformat(),
            "sections": list(self.content_sections.keys())
        }
    
    def __repr__(self) -> str:
        return f"Contract({self.title[:30]}, ${self.total_value:,.0f})"
