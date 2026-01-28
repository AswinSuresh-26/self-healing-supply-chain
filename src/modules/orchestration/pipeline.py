"""
Pipeline Stage Definitions

Defines the stages of the self-healing supply chain pipeline.
"""

from enum import Enum
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import logging


class PipelineStage(Enum):
    """Stages in the self-healing pipeline."""
    EVENT_SENSING = "event_sensing"
    RISK_ANALYSIS = "risk_analysis"
    RECOVERY_PLANNING = "recovery_planning"
    CONTRACT_DRAFTING = "contract_drafting"


class StageResult:
    """Result from a pipeline stage execution."""
    
    def __init__(
        self,
        stage: PipelineStage,
        success: bool,
        data: Any = None,
        error: str = None,
        duration_ms: float = 0
    ):
        self.stage = stage
        self.success = success
        self.data = data
        self.error = error
        self.duration_ms = duration_ms
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": self.stage.value,
            "success": self.success,
            "error": self.error,
            "duration_ms": round(self.duration_ms, 2),
            "timestamp": self.timestamp.isoformat(),
            "data_count": len(self.data) if isinstance(self.data, list) else 1 if self.data else 0
        }


class Pipeline:
    """
    Manages the execution of pipeline stages.
    """
    
    def __init__(self, name: str = "SelfHealingPipeline"):
        self.name = name
        self.stages: Dict[PipelineStage, Callable] = {}
        self.results: Dict[PipelineStage, StageResult] = {}
        self.logger = logging.getLogger(name)
    
    def register_stage(self, stage: PipelineStage, handler: Callable):
        """Register a handler for a pipeline stage."""
        self.stages[stage] = handler
        self.logger.debug(f"Registered handler for {stage.value}")
    
    def execute_stage(self, stage: PipelineStage, input_data: Any = None) -> StageResult:
        """Execute a single pipeline stage."""
        if stage not in self.stages:
            return StageResult(
                stage=stage,
                success=False,
                error=f"No handler registered for {stage.value}"
            )
        
        start_time = datetime.now()
        
        try:
            handler = self.stages[stage]
            result_data = handler(input_data)
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            result = StageResult(
                stage=stage,
                success=True,
                data=result_data,
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            result = StageResult(
                stage=stage,
                success=False,
                error=str(e),
                duration_ms=duration
            )
            self.logger.error(f"Stage {stage.value} failed: {e}")
        
        self.results[stage] = result
        return result
    
    def execute_all(self) -> Dict[PipelineStage, StageResult]:
        """Execute all stages in sequence."""
        stage_order = [
            PipelineStage.EVENT_SENSING,
            PipelineStage.RISK_ANALYSIS,
            PipelineStage.RECOVERY_PLANNING,
            PipelineStage.CONTRACT_DRAFTING
        ]
        
        current_data = None
        
        for stage in stage_order:
            if stage in self.stages:
                result = self.execute_stage(stage, current_data)
                
                if result.success:
                    current_data = result.data
                else:
                    self.logger.warning(f"Pipeline stopped at {stage.value}")
                    break
        
        return self.results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get pipeline execution summary."""
        total_duration = sum(r.duration_ms for r in self.results.values())
        successful = sum(1 for r in self.results.values() if r.success)
        
        return {
            "name": self.name,
            "stages_executed": len(self.results),
            "stages_successful": successful,
            "total_duration_ms": round(total_duration, 2),
            "results": {s.value: r.to_dict() for s, r in self.results.items()}
        }
