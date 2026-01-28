"""
Module 5: Orchestration Demo

Runs the complete self-healing supply chain simulation,
demonstrating end-to-end multi-agent coordination.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
sys.path.insert(0, project_root)

from src.modules.orchestration.orchestrator import MasterOrchestrator


def run_orchestration_demo():
    """Run the complete pipeline simulation."""
    print("\n")
    print("  " + "=" * 66)
    print("  Running Self-Healing Supply Chain - Full Simulation")
    print("  " + "=" * 66)
    
    # Create orchestrator
    orchestrator = MasterOrchestrator(verbose=True)
    
    # Run complete pipeline
    result = orchestrator.run_full_pipeline()
    
    return result


if __name__ == "__main__":
    run_orchestration_demo()
