"""
Recovery Plan Model

Represents recovery plans generated for supply chain disruptions.
"""

import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional


class ActionType(Enum):
    """Types of recovery actions."""
    ACTIVATE_BACKUP = "activate_backup"
    EXPEDITE_ORDER = "expedite_order"
    INCREASE_INVENTORY = "increase_inventory"
    REROUTE_SHIPMENT = "reroute_shipment"
    NEGOTIATE_TERMS = "negotiate_terms"
    SPLIT_ORDER = "split_order"
    DUAL_SOURCE = "dual_source"


class ActionPriority(Enum):
    """Priority levels for recovery actions."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecoveryAction:
    """
    Represents a single action within a recovery plan.
    """
    
    def __init__(
        self,
        action_type: ActionType,
        description: str,
        priority: ActionPriority,
        owner: str,
        deadline_days: int,
        estimated_cost: float = 0,
        backup_supplier_id: str = None,
        action_id: str = None
    ):
        self.action_id = action_id or str(uuid.uuid4())
        self.action_type = action_type
        self.description = description
        self.priority = priority
        self.owner = owner
        self.deadline_days = deadline_days
        self.estimated_cost = estimated_cost
        self.backup_supplier_id = backup_supplier_id
        self.status = "pending"
        self.created_at = datetime.now()
    
    def get_deadline(self) -> datetime:
        """Get action deadline."""
        return self.created_at + timedelta(days=self.deadline_days)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "description": self.description,
            "priority": self.priority.value,
            "owner": self.owner,
            "deadline_days": self.deadline_days,
            "deadline": self.get_deadline().isoformat(),
            "estimated_cost": self.estimated_cost,
            "backup_supplier_id": self.backup_supplier_id,
            "status": self.status
        }
    
    def __repr__(self) -> str:
        return f"RecoveryAction({self.action_type.value}, {self.priority.value})"


class RecoveryPlan:
    """
    Comprehensive recovery plan for a supply chain disruption.
    """
    
    def __init__(
        self,
        risk_id: str,
        title: str,
        description: str,
        affected_supplier_name: str,
        affected_categories: List[str],
        estimated_recovery_days: int,
        total_estimated_cost: float = 0,
        plan_id: str = None
    ):
        self.plan_id = plan_id or str(uuid.uuid4())
        self.risk_id = risk_id
        self.title = title
        self.description = description
        self.affected_supplier_name = affected_supplier_name
        self.affected_categories = affected_categories
        self.estimated_recovery_days = estimated_recovery_days
        self.total_estimated_cost = total_estimated_cost
        self.actions: List[RecoveryAction] = []
        self.recommended_suppliers: List[Dict] = []
        self.created_at = datetime.now()
        self.status = "draft"
    
    def add_action(self, action: RecoveryAction):
        """Add an action to the plan."""
        self.actions.append(action)
        self.total_estimated_cost += action.estimated_cost
    
    def add_recommended_supplier(self, supplier_info: Dict):
        """Add a recommended backup supplier."""
        self.recommended_suppliers.append(supplier_info)
    
    def get_critical_actions(self) -> List[RecoveryAction]:
        """Get critical priority actions."""
        return [a for a in self.actions if a.priority == ActionPriority.CRITICAL]
    
    def get_actions_by_priority(self) -> Dict[str, List[RecoveryAction]]:
        """Get actions grouped by priority."""
        result = {}
        for priority in ActionPriority:
            result[priority.value] = [
                a for a in self.actions if a.priority == priority
            ]
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "risk_id": self.risk_id,
            "title": self.title,
            "description": self.description,
            "affected_supplier_name": self.affected_supplier_name,
            "affected_categories": self.affected_categories,
            "estimated_recovery_days": self.estimated_recovery_days,
            "total_estimated_cost": self.total_estimated_cost,
            "actions": [a.to_dict() for a in self.actions],
            "recommended_suppliers": self.recommended_suppliers,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }
    
    def __repr__(self) -> str:
        return f"RecoveryPlan({self.title[:30]}, {len(self.actions)} actions)"
