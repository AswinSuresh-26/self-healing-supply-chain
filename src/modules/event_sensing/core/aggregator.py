"""
Event Aggregator

Collects events from multiple sensing agents and provides
deduplication, correlation, and prioritization capabilities.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Set
from collections import defaultdict

from .event import Event, EventBatch, EventSeverity


class EventAggregator:
    """
    Aggregates events from multiple sensing agents.
    
    Provides:
    - Collection of events from all agents
    - Deduplication of similar events
    - Correlation of related events
    - Priority ordering by severity
    """
    
    def __init__(
        self,
        deduplication_window_seconds: int = 300,
        max_buffer_size: int = 100
    ):
        """
        Initialize the Event Aggregator.
        
        Args:
            deduplication_window_seconds: Time window for deduplication
            max_buffer_size: Maximum events to keep in buffer
        """
        self.deduplication_window = timedelta(seconds=deduplication_window_seconds)
        self.max_buffer_size = max_buffer_size
        self.logger = logging.getLogger("EventAggregator")
        
        # Event storage
        self._event_buffer: List[Event] = []
        self._seen_events: Dict[str, datetime] = {}  # For deduplication
        self._events_by_category: Dict[str, List[Event]] = defaultdict(list)
    
    def add_batch(self, batch: EventBatch) -> int:
        """
        Add a batch of events from an agent.
        
        Args:
            batch: EventBatch from a sensing agent
            
        Returns:
            Number of new events added (after deduplication)
        """
        added_count = 0
        
        for event in batch:
            if self._add_event(event):
                added_count += 1
        
        if added_count > 0:
            self.logger.info(
                f"Added {added_count} events from {batch.source_agent} "
                f"(buffer size: {len(self._event_buffer)})"
            )
        
        return added_count
    
    def _add_event(self, event: Event) -> bool:
        """
        Add a single event to the buffer.
        
        Returns:
            True if event was added, False if deduplicated
        """
        # Check for duplicates
        if self._is_duplicate(event):
            self.logger.debug(f"Duplicate event filtered: {event.title[:50]}")
            return False
        
        # Add to buffer
        self._event_buffer.append(event)
        self._seen_events[self._get_event_signature(event)] = event.detected_at
        self._events_by_category[event.category.value].append(event)
        
        # Enforce buffer size limit
        if len(self._event_buffer) > self.max_buffer_size:
            self._prune_oldest()
        
        return True
    
    def _is_duplicate(self, event: Event) -> bool:
        """Check if an event is a duplicate of a recent event."""
        signature = self._get_event_signature(event)
        
        if signature in self._seen_events:
            last_seen = self._seen_events[signature]
            if datetime.now() - last_seen < self.deduplication_window:
                return True
        
        return False
    
    def _get_event_signature(self, event: Event) -> str:
        """
        Generate a signature for deduplication.
        
        Events with the same title and location within the dedup window
        are considered duplicates.
        """
        location_str = ""
        if event.location:
            location_str = f"{event.location.country}_{event.location.city}"
        
        return f"{event.title.lower()[:50]}_{location_str}_{event.category.value}"
    
    def _prune_oldest(self):
        """Remove oldest events when buffer is full."""
        # Remove 10% of oldest events
        prune_count = max(1, len(self._event_buffer) // 10)
        
        # Sort by timestamp and remove oldest
        self._event_buffer.sort(key=lambda e: e.timestamp, reverse=True)
        removed = self._event_buffer[self.max_buffer_size:]
        self._event_buffer = self._event_buffer[:self.max_buffer_size]
        
        self.logger.debug(f"Pruned {len(removed)} old events from buffer")
    
    def get_all_events(self) -> List[Event]:
        """Get all events in the buffer, sorted by severity then timestamp."""
        severity_order = {
            EventSeverity.CRITICAL: 0,
            EventSeverity.HIGH: 1,
            EventSeverity.MEDIUM: 2,
            EventSeverity.LOW: 3
        }
        
        return sorted(
            self._event_buffer,
            key=lambda e: (severity_order.get(e.severity, 99), -e.timestamp.timestamp())
        )
    
    def get_events_by_severity(self, severity: EventSeverity) -> List[Event]:
        """Get events filtered by severity level."""
        return [e for e in self._event_buffer if e.severity == severity]
    
    def get_events_by_category(self, category: str) -> List[Event]:
        """Get events filtered by category."""
        return self._events_by_category.get(category, [])
    
    def get_critical_events(self) -> List[Event]:
        """Get only critical and high severity events."""
        return [
            e for e in self._event_buffer
            if e.severity in [EventSeverity.CRITICAL, EventSeverity.HIGH]
        ]
    
    def get_recent_events(self, minutes: int = 60) -> List[Event]:
        """Get events from the last N minutes."""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [e for e in self._event_buffer if e.detected_at >= cutoff]
    
    def clear(self):
        """Clear all events from the buffer."""
        self._event_buffer.clear()
        self._seen_events.clear()
        self._events_by_category.clear()
        self.logger.info("Event buffer cleared")
    
    def get_statistics(self) -> Dict:
        """Get aggregator statistics."""
        severity_counts = defaultdict(int)
        category_counts = defaultdict(int)
        
        for event in self._event_buffer:
            severity_counts[event.severity.value] += 1
            category_counts[event.category.value] += 1
        
        return {
            "total_events": len(self._event_buffer),
            "buffer_capacity": self.max_buffer_size,
            "events_by_severity": dict(severity_counts),
            "events_by_category": dict(category_counts)
        }
    
    def __len__(self) -> int:
        return len(self._event_buffer)
