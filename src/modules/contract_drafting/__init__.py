# Contract Drafting Module
"""
Module 4: LLM-Based Contract Drafting

Generates emergency supplier contracts based on recovery plans.
Uses simulated LLM for prototype.
"""

from .models.contract import Contract, ContractType, ContractStatus
from .generators.llm_generator import LLMContractGenerator
from .generators.template_engine import ContractTemplateEngine

__version__ = "1.0.0"
__all__ = [
    "Contract",
    "ContractType",
    "ContractStatus",
    "LLMContractGenerator",
    "ContractTemplateEngine",
]
