"""
Base Agent

Abstract base class for all sensing agents in the Event Sensing Module.
Provides common functionality for event detection and emission.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..core.event import Event, EventBatch, EventType
from ..config.settings import get_settings


class BaseAgent(ABC):
    """
    Abstract base class for sensing agents.
    
    Each agent is responsible for monitoring a specific type of external
    data source and generating normalized events when disruptions are detected.
    
    Subclasses must implement:
        - sense(): Perform one sensing cycle and return detected events
        - get_agent_name(): Return the agent's name
        - get_event_type(): Return the type of events this agent produces
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize the base agent.
        
        Args:
            enabled: Whether the agent is enabled
        """
        self.enabled = enabled
        self.settings = get_settings()
        self.logger = logging.getLogger(self.get_agent_name())
        self._last_run = None
        self._events_detected = 0
    
    @abstractmethod
    def get_agent_name(self) -> str:
        """Return the name of this agent."""
        pass
    
    @abstractmethod
    def get_event_type(self) -> EventType:
        """Return the type of events this agent produces."""
        pass
    
    @abstractmethod
    def sense(self) -> List[Event]:
        """
        Perform one sensing cycle.
        
        This method should check the external data source for any
        new events and return them as a list of normalized Event objects.
        
        Returns:
            List of detected events (may be empty)
        """
        pass
    
    def run_cycle(self) -> EventBatch:
        """
        Run a complete sensing cycle.
        
        This is the main entry point for running the agent.
        It handles logging, error handling, and returns events in a batch.
        
        Returns:
            EventBatch containing detected events
        """
        if not self.enabled:
            self.logger.debug(f"{self.get_agent_name()} is disabled, skipping cycle")
            return EventBatch(source_agent=self.get_agent_name())
        
        self.logger.info(f"Starting sensing cycle for {self.get_agent_name()}")
        self._last_run = datetime.now()
        
        try:
            events = self.sense()
            self._events_detected += len(events)
            
            if events:
                self.logger.info(f"Detected {len(events)} events")
                for event in events:
                    self.logger.debug(f"  - {event.title} ({event.severity.value})")
            else:
                self.logger.debug("No events detected in this cycle")
            
            return EventBatch(events=events, source_agent=self.get_agent_name())
            
        except Exception as e:
            self.logger.error(f"Error during sensing cycle: {str(e)}")
            return EventBatch(source_agent=self.get_agent_name())
    
    def get_status(self) -> dict:
        """Get the current status of the agent."""
        return {
            "agent_name": self.get_agent_name(),
            "event_type": self.get_event_type().value,
            "enabled": self.enabled,
            "last_run": self._last_run.isoformat() if self._last_run else None,
            "total_events_detected": self._events_detected
        }
    
    def __repr__(self) -> str:
        status = "enabled" if self.enabled else "disabled"
        return f"{self.get_agent_name()}({status})"
