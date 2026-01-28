"""
Module 4: Contract Drafting Demo

Demonstrates LLM-based contract generation:
1. Receives recovery plans from Module 3
2. Generates emergency supplier contracts
3. Shows contract structure and content
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.insert(0, project_root)


def run_contract_drafting_demo(recovery_plans=None, verbose=True):
    """Run the contract drafting demonstration."""
    
    if verbose:
        print("\n" + "=" * 70)
        print("   MODULE 4: LLM-BASED CONTRACT DRAFTING")
        print("=" * 70)
    
    # Get recovery plans if not provided
    if recovery_plans is None:
        from src.modules.recovery_planning.demo import run_recovery_planning_demo
        recovery_plans = run_recovery_planning_demo()
    
    # Convert RecoveryPlan objects to dicts if needed
    plans_data = []
    for plan in recovery_plans:
        if hasattr(plan, 'to_dict'):
            plans_data.append(plan.to_dict())
        else:
            plans_data.append(plan)
    
    if not plans_data:
        if verbose:
            print("⚠️  No recovery plans - creating sample for demo")
        plans_data = [{
            "plan_id": "demo-plan-001",
            "title": "Recovery Plan: Port Disruption",
            "affected_categories": ["electronics", "components"],
            "total_estimated_cost": 65000,
            "estimated_recovery_days": 14,
            "recommended_suppliers": [{
                "name": "Malaysia Precision Parts",
                "country": "Malaysia",
                "city": "Penang",
                "lead_time_days": 20,
                "cost_premium_pct": 12.0,
                "certifications": ["ISO 9001", "AS9100"]
            }]
        }]
    
    # Import generator
    from src.modules.contract_drafting.generators.llm_generator import LLMContractGenerator
    
    generator = LLMContractGenerator()
    
    if verbose:
        print(f"\n📝 Generating contracts for {len(plans_data)} recovery plans...\n")
    
    # Generate contracts
    contracts = generator.generate_contracts(plans_data, limit=2)
    
    if verbose:
        print("-" * 70)
        print(f"  GENERATED {len(contracts)} CONTRACTS")
        print("-" * 70 + "\n")
        
        for contract in contracts:
            print(generator.format_contract_summary(contract))
            print()
            
            # Show first section as sample
            if contract.content_sections:
                first_section = list(contract.content_sections.keys())[0]
                print(f"  SAMPLE SECTION - {first_section}:")
                print("-" * 70)
                content = contract.content_sections[first_section]
                # Show first few lines
                lines = content.strip().split('\n')[:10]
                for line in lines:
                    print(f"  {line}")
                print("  ...")
                print("-" * 70)
        
        # Summary
        total_value = sum(c.total_value for c in contracts)
        
        print()
        print("=" * 70)
        print("  CONTRACT DRAFTING SUMMARY")
        print("=" * 70)
        print(f"  Contracts Generated: {len(contracts)}")
        print(f"  Total Contract Value: ${total_value:,.2f}")
        print(f"  Status: All contracts in DRAFT status")
        print("=" * 70)
    
    return contracts


if __name__ == "__main__":
    run_contract_drafting_demo()
