# Orchestration & Control Module
"""
Module 5: Master Orchestrator

Coordinates the complete self-healing supply chain pipeline:
Event Sensing → Risk Analysis → Recovery Planning → Contract Drafting
"""

from .orchestrator import MasterOrchestrator, PipelineResult
from .pipeline import Pipeline, PipelineStage

__version__ = "1.0.0"
__all__ = [
    "MasterOrchestrator",
    "PipelineResult",
    "Pipeline",
    "PipelineStage",
]
