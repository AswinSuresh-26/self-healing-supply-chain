"""
Recovery Planner Engine

Generates comprehensive recovery plans for supply chain disruptions
based on risk analysis and available backup suppliers.
"""

import logging
from typing import Dict, Any, List

from ..models.recovery_plan import RecoveryPlan, RecoveryAction, ActionType, ActionPriority
from ..models.backup_supplier import BackupSupplier
from .supplier_evaluator import SupplierEvaluator


class RecoveryPlanner:
    """
    Generates recovery plans for supply chain disruptions.
    
    Creates actionable plans with:
    - Prioritized recovery actions
    - Recommended backup suppliers
    - Timeline and cost estimates
    """
    
    def __init__(self, supplier_evaluator: SupplierEvaluator = None):
        self.supplier_evaluator = supplier_evaluator or SupplierEvaluator()
        self.logger = logging.getLogger("RecoveryPlanner")
    
    def generate_plan(self, risk: Dict[str, Any]) -> RecoveryPlan:
        """
        Generate a recovery plan for a given risk.
        
        Args:
            risk: Risk dictionary from Module 2
            
        Returns:
            Complete recovery plan with actions and recommendations
        """
        risk_level = risk.get("risk_level", "medium")
        risk_id = risk.get("risk_id", "unknown")
        
        # Extract affected supplier info
        affected_suppliers = risk.get("affected_suppliers", [])
        if affected_suppliers:
            primary_supplier = affected_suppliers[0]
            supplier_name = primary_supplier.get("name", "Unknown Supplier")
            affected_country = primary_supplier.get("country")
            categories = primary_supplier.get("categories", [])
        else:
            supplier_name = "Unknown Supplier"
            affected_country = None
            categories = []
        
        # Create recovery plan
        plan = RecoveryPlan(
            risk_id=risk_id,
            title=f"Recovery Plan: {risk.get('title', 'Supply Disruption')[:50]}",
            description=f"Recovery actions for {supplier_name} disruption",
            affected_supplier_name=supplier_name,
            affected_categories=categories,
            estimated_recovery_days=risk.get("estimated_delay_days", 14)
        )
        
        # Generate actions based on risk level
        actions = self._generate_actions(risk, risk_level, affected_country)
        for action in actions:
            plan.add_action(action)
        
        # Find and recommend backup suppliers
        alternatives = self.supplier_evaluator.find_alternatives(
            required_categories=categories,
            affected_country=affected_country,
            limit=3
        )
        
        for alt in alternatives:
            plan.add_recommended_supplier({
                "supplier_id": alt["supplier_id"],
                "name": alt["name"],
                "country": alt["country"],
                "evaluation_score": alt["evaluation_score"],
                "lead_time_days": alt["lead_time_days"],
                "cost_premium_pct": alt["cost_premium_pct"],
                "recommendation": alt["recommendation"]
            })
        
        self.logger.info(f"Generated recovery plan with {len(plan.actions)} actions")
        
        return plan
    
    def _generate_actions(
        self,
        risk: Dict[str, Any],
        risk_level: str,
        affected_country: str = None
    ) -> List[RecoveryAction]:
        """Generate recovery actions based on risk level."""
        actions = []
        
        # Critical/High risk actions
        if risk_level in ["critical", "high"]:
            actions.append(RecoveryAction(
                action_type=ActionType.ACTIVATE_BACKUP,
                description="Activate pre-qualified backup supplier",
                priority=ActionPriority.CRITICAL,
                owner="Procurement Lead",
                deadline_days=1,
                estimated_cost=5000
            ))
            
            actions.append(RecoveryAction(
                action_type=ActionType.EXPEDITE_ORDER,
                description="Expedite existing orders with alternative suppliers",
                priority=ActionPriority.CRITICAL,
                owner="Supply Chain Manager",
                deadline_days=2,
                estimated_cost=15000
            ))
        
        # All risk levels
        actions.append(RecoveryAction(
            action_type=ActionType.INCREASE_INVENTORY,
            description="Assess and increase safety stock levels",
            priority=ActionPriority.HIGH if risk_level in ["critical", "high"] else ActionPriority.MEDIUM,
            owner="Inventory Manager",
            deadline_days=3,
            estimated_cost=25000
        ))
        
        actions.append(RecoveryAction(
            action_type=ActionType.DUAL_SOURCE,
            description="Implement dual-sourcing strategy for critical items",
            priority=ActionPriority.HIGH,
            owner="Category Manager",
            deadline_days=7,
            estimated_cost=10000
        ))
        
        # Logistics-specific actions
        if risk.get("risk_type") == "logistics":
            actions.append(RecoveryAction(
                action_type=ActionType.REROUTE_SHIPMENT,
                description="Identify alternative shipping routes and carriers",
                priority=ActionPriority.HIGH,
                owner="Logistics Coordinator",
                deadline_days=2,
                estimated_cost=8000
            ))
        
        # Medium/Low risk actions
        actions.append(RecoveryAction(
            action_type=ActionType.NEGOTIATE_TERMS,
            description="Negotiate expedited terms with backup suppliers",
            priority=ActionPriority.MEDIUM,
            owner="Procurement Specialist",
            deadline_days=5,
            estimated_cost=2000
        ))
        
        # Long-term actions
        actions.append(RecoveryAction(
            action_type=ActionType.SPLIT_ORDER,
            description="Split future orders across multiple suppliers",
            priority=ActionPriority.LOW,
            owner="Strategic Sourcing",
            deadline_days=14,
            estimated_cost=0
        ))
        
        return actions
    
    def generate_plans(self, risks: List[Dict[str, Any]]) -> List[RecoveryPlan]:
        """Generate recovery plans for multiple risks."""
        plans = []
        for risk in risks:
            plan = self.generate_plan(risk)
            plans.append(plan)
        
        # Sort by estimated recovery days (urgent first)
        plans.sort(key=lambda p: p.estimated_recovery_days)
        
        return plans
    
    def format_plan_summary(self, plan: RecoveryPlan) -> str:
        """Format plan for console display."""
        lines = [
            "=" * 70,
            f"  RECOVERY PLAN: {plan.title}",
            "=" * 70,
            f"  Affected Supplier: {plan.affected_supplier_name}",
            f"  Estimated Recovery: {plan.estimated_recovery_days} days",
            f"  Total Est. Cost: ${plan.total_estimated_cost:,.0f}",
            "-" * 70,
            "",
            "  ACTIONS:",
        ]
        
        for i, action in enumerate(plan.actions, 1):
            priority_icon = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }
            icon = priority_icon.get(action.priority.value, "⚪")
            lines.append(
                f"    {i}. {icon} [{action.priority.value.upper()}] {action.description}"
            )
            lines.append(
                f"       Owner: {action.owner} | Deadline: {action.deadline_days} days"
            )
        
        if plan.recommended_suppliers:
            lines.append("")
            lines.append("  RECOMMENDED BACKUP SUPPLIERS:")
            for alt in plan.recommended_suppliers:
                lines.append(
                    f"    • {alt['name']} ({alt['country']}) - "
                    f"Score: {alt['evaluation_score']:.2f}"
                )
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
