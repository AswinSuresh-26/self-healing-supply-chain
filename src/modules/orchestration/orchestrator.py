"""
Master Orchestrator

Coordinates the complete self-healing supply chain pipeline,
providing end-to-end automation from event detection to contract drafting.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from .pipeline import Pipeline, PipelineStage, StageResult


@dataclass
class PipelineResult:
    """Complete result from pipeline execution."""
    success: bool
    events_detected: int = 0
    risks_identified: int = 0
    recovery_plans_generated: int = 0
    contracts_drafted: int = 0
    total_duration_seconds: float = 0
    stages_completed: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "events_detected": self.events_detected,
            "risks_identified": self.risks_identified,
            "recovery_plans_generated": self.recovery_plans_generated,
            "contracts_drafted": self.contracts_drafted,
            "total_duration_seconds": round(self.total_duration_seconds, 2),
            "stages_completed": self.stages_completed,
            "errors": self.errors
        }


class MasterOrchestrator:
    """
    Master orchestrator for the self-healing supply chain framework.
    
    Coordinates:
    - Module 1: External Event Sensing
    - Module 2: Disruption Risk Analysis  
    - Module 3: Supplier Evaluation & Recovery Planning
    - Module 4: LLM-Based Contract Drafting
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.pipeline = Pipeline("SelfHealingSupplyChain")
        self.logger = logging.getLogger("MasterOrchestrator")
        
        # Register stage handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all pipeline stage handlers."""
        self.pipeline.register_stage(
            PipelineStage.EVENT_SENSING,
            self._handle_event_sensing
        )
        self.pipeline.register_stage(
            PipelineStage.RISK_ANALYSIS,
            self._handle_risk_analysis
        )
        self.pipeline.register_stage(
            PipelineStage.RECOVERY_PLANNING,
            self._handle_recovery_planning
        )
        self.pipeline.register_stage(
            PipelineStage.CONTRACT_DRAFTING,
            self._handle_contract_drafting
        )
    
    def _handle_event_sensing(self, _: Any) -> List[Dict]:
        """Execute event sensing stage."""
        from src.modules.event_sensing.agents.news_agent import NewsAgent
        from src.modules.event_sensing.agents.weather_agent import WeatherAgent
        from src.modules.event_sensing.core.aggregator import EventAggregator
        from src.modules.event_sensing.core.normalizer import EventNormalizer
        
        # Create agents (simulation mode controlled via settings)
        news_agent = NewsAgent()
        weather_agent = WeatherAgent()
        
        # Collect events
        aggregator = EventAggregator()
        
        news_batch = news_agent.run_cycle()
        aggregator.add_batch(news_batch)
        
        weather_batch = weather_agent.run_cycle()
        aggregator.add_batch(weather_batch)
        
        # Get prioritized events (sorted by severity)
        events = aggregator.get_all_events()[:5]
        
        # Normalize
        normalizer = EventNormalizer()
        normalized = normalizer.normalize(events)
        
        return [e.to_dict() if hasattr(e, 'to_dict') else e for e in normalized]
    
    def _handle_risk_analysis(self, events: List[Dict]) -> List[Dict]:
        """Execute risk analysis stage."""
        from src.modules.risk_analysis.engines.risk_scorer import RiskScorer
        from src.modules.risk_analysis.engines.impact_analyzer import SupplierImpactAnalyzer
        from src.modules.risk_analysis.core.classifier import RiskClassifier
        
        scorer = RiskScorer()
        analyzer = SupplierImpactAnalyzer()
        
        risks = []
        
        for event in events[:5]:
            # Find affected suppliers (returns list of Supplier objects)
            affected_suppliers = analyzer.find_affected_suppliers(event)
            
            # Calculate risk score
            risk_result = scorer.calculate_risk_score(event, affected_suppliers)
            
            # Convert affected suppliers to dict format for downstream
            affected_dicts = []
            for supplier in affected_suppliers[:3]:
                affected_dicts.append({
                    "name": supplier.name,
                    "country": supplier.country,
                    "categories": supplier.categories
                })
            
            risk_info = {
                "risk_id": f"risk-{len(risks)+1:03d}",
                "title": event.get("title", "Unknown Event"),
                "risk_level": risk_result.get("risk_level", "medium"),
                "risk_type": event.get("category", "unknown"),
                "risk_score": risk_result.get("composite_score", 0.5),
                "estimated_delay_days": risk_result.get("estimated_delay_days", 14),
                "affected_suppliers": affected_dicts
            }
            risks.append(risk_info)
        
        return risks
    
    def _handle_recovery_planning(self, risks: List[Dict]) -> List[Dict]:
        """Execute recovery planning stage."""
        from src.modules.recovery_planning.engines.supplier_evaluator import SupplierEvaluator
        from src.modules.recovery_planning.engines.recovery_planner import RecoveryPlanner
        
        evaluator = SupplierEvaluator()
        planner = RecoveryPlanner(evaluator)
        
        plans = []
        
        for risk in risks[:3]:
            plan = planner.generate_plan(risk)
            plans.append(plan.to_dict())
        
        return plans
    
    def _handle_contract_drafting(self, plans: List[Dict]) -> List[Dict]:
        """Execute contract drafting stage."""
        from src.modules.contract_drafting.generators.llm_generator import LLMContractGenerator
        
        generator = LLMContractGenerator()
        
        contracts = generator.generate_contracts(plans, limit=2)
        
        return [c.to_dict() for c in contracts]
    
    def run_full_pipeline(self) -> PipelineResult:
        """Run the complete self-healing pipeline."""
        start_time = time.time()
        
        if self.verbose:
            self._print_header()
        
        # Execute all stages
        results = self.pipeline.execute_all()
        
        # Build result
        pipeline_result = PipelineResult(success=True)
        
        for stage, result in results.items():
            if result.success:
                pipeline_result.stages_completed.append(stage.value)
                
                if stage == PipelineStage.EVENT_SENSING:
                    pipeline_result.events_detected = len(result.data) if result.data else 0
                elif stage == PipelineStage.RISK_ANALYSIS:
                    pipeline_result.risks_identified = len(result.data) if result.data else 0
                elif stage == PipelineStage.RECOVERY_PLANNING:
                    pipeline_result.recovery_plans_generated = len(result.data) if result.data else 0
                elif stage == PipelineStage.CONTRACT_DRAFTING:
                    pipeline_result.contracts_drafted = len(result.data) if result.data else 0
            else:
                pipeline_result.success = False
                if result.error:
                    pipeline_result.errors.append(f"{stage.value}: {result.error}")
        
        pipeline_result.total_duration_seconds = time.time() - start_time
        
        if self.verbose:
            self._print_results(results, pipeline_result)
        
        return pipeline_result
    
    def _print_header(self):
        """Print pipeline header."""
        print("\n")
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 10 + "SELF-HEALING SUPPLY CHAIN AI FRAMEWORK" + " " * 18 + "║")
        print("║" + " " * 15 + "COMPLETE PIPELINE SIMULATION" + " " * 24 + "║")
        print("╚" + "═" * 68 + "╝")
        print()
        print(f"  🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("  " + "-" * 66)
    
    def _print_results(self, results: Dict[PipelineStage, StageResult], final: PipelineResult):
        """Print pipeline results."""
        print("\n")
        print("┌" + "─" * 68 + "┐")
        print("│" + " " * 20 + "PIPELINE STAGES SUMMARY" + " " * 25 + "│")
        print("└" + "─" * 68 + "┘")
        
        stage_icons = {
            PipelineStage.EVENT_SENSING: "📡",
            PipelineStage.RISK_ANALYSIS: "🔍",
            PipelineStage.RECOVERY_PLANNING: "📋",
            PipelineStage.CONTRACT_DRAFTING: "📝"
        }
        
        stage_names = {
            PipelineStage.EVENT_SENSING: "Event Sensing",
            PipelineStage.RISK_ANALYSIS: "Risk Analysis",
            PipelineStage.RECOVERY_PLANNING: "Recovery Planning",
            PipelineStage.CONTRACT_DRAFTING: "Contract Drafting"
        }
        
        for stage, result in results.items():
            icon = stage_icons.get(stage, "⚙️")
            name = stage_names.get(stage, stage.value)
            status = "✅" if result.success else "❌"
            duration = f"{result.duration_ms:.0f}ms"
            
            data_info = ""
            if result.data:
                count = len(result.data) if isinstance(result.data, list) else 1
                data_info = f" ({count} items)"
            
            print(f"  {icon} {name:<20} {status} {duration:>10}{data_info}")
        
        print()
        print("┌" + "─" * 68 + "┐")
        print("│" + " " * 22 + "FINAL RESULTS DASHBOARD" + " " * 23 + "│")
        print("└" + "─" * 68 + "┘")
        
        print(f"""
  ╭──────────────────────────────────────────────────────────────────╮
  │                                                                  │
  │   📡 Events Detected:           {final.events_detected:<5}                          │
  │   🔍 Risks Identified:          {final.risks_identified:<5}                          │
  │   📋 Recovery Plans Generated:  {final.recovery_plans_generated:<5}                          │
  │   📝 Contracts Drafted:         {final.contracts_drafted:<5}                          │
  │                                                                  │
  │   ⏱️  Total Duration:           {final.total_duration_seconds:.2f} seconds                   │
  │   ✅ Pipeline Status:           {'SUCCESS' if final.success else 'FAILED':<10}                   │
  │                                                                  │
  ╰──────────────────────────────────────────────────────────────────╯
""")
        
        print("  " + "=" * 66)
        print("  ✨ Self-Healing Supply Chain Simulation Complete!")
        print("  " + "=" * 66)
