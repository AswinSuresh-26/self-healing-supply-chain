#!/usr/bin/env python
"""
Self-Healing Supply Chain AI Framework
Main Entry Point

Run the complete simulation with:
    python main.py
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from src.modules.orchestration import MasterOrchestrator


def main():
    """Main entry point for the framework."""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║          SELF-HEALING SUPPLY CHAIN - AGENTIC AI FRAMEWORK             ║")
    print("║                                                                       ║")
    print("║   A software-defined framework for detecting supply chain             ║")
    print("║   disruptions and enabling autonomous recovery planning               ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    
    # Create and run orchestrator
    orchestrator = MasterOrchestrator(verbose=True)
    result = orchestrator.run_full_pipeline()
    
    if result.success:
        print("\n  🎉 Framework simulation completed successfully!")
    else:
        print("\n  ⚠️  Simulation completed with errors:")
        for error in result.errors:
            print(f"     - {error}")
    
    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
