"""
Module 3: Supplier Evaluation & Recovery Planning Demo

Demonstrates the recovery planning workflow:
1. Receives risks from Module 2
2. Evaluates backup suppliers
3. Generates recovery plans with action items
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.insert(0, project_root)

from src.modules.event_sensing.demo import run_event_sensing_demo
from src.modules.risk_analysis.demo import run_risk_analysis_demo
from src.modules.recovery_planning.engines.supplier_evaluator import SupplierEvaluator
from src.modules.recovery_planning.engines.recovery_planner import RecoveryPlanner


def run_recovery_planning_demo():
    """Run the complete recovery planning demonstration."""
    print("\n" + "=" * 70)
    print("   MODULE 3: SUPPLIER EVALUATION & RECOVERY PLANNING")
    print("=" * 70)
    
    # Run Module 1 + 2 to get risks
    print("\n📡 Running Event Sensing (Module 1)...")
    events = run_event_sensing_demo(verbose=False)
    
    print("🔍 Running Risk Analysis (Module 2)...")
    risks = run_risk_analysis_demo(events, verbose=False)
    
    if not risks:
        print("⚠️  No risks detected - generating sample risk for demo")
        risks = [{
            "risk_id": "demo-risk-001",
            "title": "Port Closure - Shanghai",
            "risk_level": "high",
            "risk_type": "logistics",
            "estimated_delay_days": 14,
            "affected_suppliers": [
                {"name": "Shanghai Electronics", "country": "China", "categories": ["electronics"]}
            ]
        }]
    
    print(f"\n📋 Processing {len(risks)} risks...\n")
    
    # Initialize engines
    evaluator = SupplierEvaluator()
    planner = RecoveryPlanner(evaluator)
    
    # Display backup supplier pool
    print("-" * 70)
    print("  BACKUP SUPPLIER POOL")
    print("-" * 70)
    
    from src.modules.recovery_planning.models.backup_supplier import get_backup_suppliers
    suppliers = get_backup_suppliers()
    
    for supplier in suppliers[:5]:
        score = supplier.get_overall_score()
        print(f"  • {supplier.name} ({supplier.country}) - Score: {score:.2f}")
    print(f"  ... and {len(suppliers) - 5} more suppliers\n")
    
    # Generate recovery plans
    plans = planner.generate_plans(risks)
    
    print("-" * 70)
    print(f"  GENERATED {len(plans)} RECOVERY PLANS")
    print("-" * 70 + "\n")
    
    for plan in plans[:2]:  # Show first 2 plans
        print(planner.format_plan_summary(plan))
        print()
    
    # Summary
    total_actions = sum(len(p.actions) for p in plans)
    total_cost = sum(p.total_estimated_cost for p in plans)
    
    print()
    print("=" * 70)
    print("  RECOVERY PLANNING SUMMARY")
    print("=" * 70)
    print(f"  Total Plans Generated: {len(plans)}")
    print(f"  Total Actions Identified: {total_actions}")
    print(f"  Total Estimated Cost: ${total_cost:,.0f}")
    print("=" * 70)
    
    return plans


if __name__ == "__main__":
    run_recovery_planning_demo()
