"""
Event Normalizer

Normalizes and enriches events for downstream processing.
Ensures consistent formatting and adds computed fields.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .event import Event, EventSeverity, EventCategory


class EventNormalizer:
    """
    Normalizes events into a consistent format for downstream modules.
    
    Provides:
    - Confidence filtering
    - Field validation and enrichment
    - Supply chain impact scoring
    - Event formatting for downstream consumption
    """
    
    def __init__(self, confidence_threshold: float = 0.5):
        """
        Initialize the Event Normalizer.
        
        Args:
            confidence_threshold: Minimum confidence score for events
        """
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger("EventNormalizer")
        
        # Impact scoring weights by category
        self._category_weights = {
            EventCategory.LOGISTICS.value: 1.0,
            EventCategory.NATURAL_DISASTER.value: 0.9,
            EventCategory.INFRASTRUCTURE.value: 0.85,
            EventCategory.LABOR.value: 0.75,
            EventCategory.GEOPOLITICAL.value: 0.7,
            EventCategory.ECONOMIC.value: 0.6,
            EventCategory.OTHER.value: 0.4
        }
        
        # Severity multipliers
        self._severity_multipliers = {
            EventSeverity.CRITICAL.value: 1.0,
            EventSeverity.HIGH.value: 0.75,
            EventSeverity.MEDIUM.value: 0.5,
            EventSeverity.LOW.value: 0.25
        }
    
    def normalize(self, events: List[Event]) -> List[Dict[str, Any]]:
        """
        Normalize a list of events for downstream processing.
        
        Args:
            events: List of raw events
            
        Returns:
            List of normalized event dictionaries
        """
        normalized = []
        
        for event in events:
            # Filter by confidence
            if event.confidence < self.confidence_threshold:
                self.logger.debug(
                    f"Event filtered (low confidence {event.confidence:.2f}): {event.title}"
                )
                continue
            
            normalized_event = self._normalize_event(event)
            normalized.append(normalized_event)
        
        self.logger.info(f"Normalized {len(normalized)} events (filtered {len(events) - len(normalized)})")
        return normalized
    
    def _normalize_event(self, event: Event) -> Dict[str, Any]:
        """
        Normalize a single event.
        
        Adds computed fields:
        - impact_score: Estimated supply chain impact
        - priority_rank: Ordering priority
        - formatted_location: Human-readable location
        """
        # Calculate impact score
        impact_score = self._calculate_impact_score(event)
        
        # Calculate priority rank (lower = higher priority)
        priority_rank = self._calculate_priority(event, impact_score)
        
        # Create normalized structure
        normalized = {
            # Core event data
            "event_id": event.event_id,
            "title": event.title,
            "description": event.description,
            "source_type": event.source_type.value,
            "category": event.category.value,
            "severity": event.severity.value,
            "confidence": round(event.confidence, 3),
            
            # Location
            "location": {
                "formatted": str(event.location),
                "country": event.location.country,
                "region": event.location.region,
                "city": event.location.city,
                "coordinates": {
                    "lat": event.location.latitude,
                    "lon": event.location.longitude
                } if event.location.latitude else None
            },
            
            # Computed fields
            "impact_score": round(impact_score, 3),
            "priority_rank": priority_rank,
            
            # Metadata
            "keywords": event.keywords,
            "source_url": event.source_url,
            "timestamp": event.timestamp.isoformat(),
            "detected_at": event.detected_at.isoformat(),
            "processing_time": datetime.now().isoformat(),
            
            # Downstream routing hints
            "requires_analysis": impact_score >= 0.5,
            "requires_immediate_action": event.severity == EventSeverity.CRITICAL
        }
        
        return normalized
    
    def _calculate_impact_score(self, event: Event) -> float:
        """
        Calculate supply chain impact score for an event.
        
        Score is based on:
        - Event category (logistics events weighted higher)
        - Severity level
        - Confidence score
        """
        category_weight = self._category_weights.get(
            event.category.value, 0.5
        )
        severity_mult = self._severity_multipliers.get(
            event.severity.value, 0.5
        )
        
        # Impact = category_weight * severity * confidence
        impact = category_weight * severity_mult * event.confidence
        
        return min(1.0, impact)
    
    def _calculate_priority(self, event: Event, impact_score: float) -> int:
        """
        Calculate priority rank for event processing.
        
        Lower number = higher priority (1 = highest)
        """
        severity_base = {
            EventSeverity.CRITICAL: 1,
            EventSeverity.HIGH: 10,
            EventSeverity.MEDIUM: 20,
            EventSeverity.LOW: 30
        }
        
        base = severity_base.get(event.severity, 25)
        
        # Adjust by impact score (higher impact = lower rank number)
        adjusted = base - int(impact_score * 5)
        
        return max(1, adjusted)
    
    def format_for_display(self, normalized_event: Dict[str, Any]) -> str:
        """Format a normalized event for console display."""
        severity_icons = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }
        
        icon = severity_icons.get(normalized_event["severity"], "⚪")
        
        lines = [
            f"{icon} [{normalized_event['severity'].upper()}] {normalized_event['title']}",
            f"   Category: {normalized_event['category']}",
            f"   Location: {normalized_event['location']['formatted']}",
            f"   Impact Score: {normalized_event['impact_score']:.2f}",
            f"   Confidence: {normalized_event['confidence']:.0%}",
            f"   Detected: {normalized_event['detected_at']}"
        ]
        
        if normalized_event.get("requires_immediate_action"):
            lines.append("   ⚠️  REQUIRES IMMEDIATE ACTION")
        
        return "\n".join(lines)
    
    def create_summary(self, normalized_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a summary of normalized events."""
        if not normalized_events:
            return {
                "total_events": 0,
                "summary": "No events detected",
                "events_by_severity": {},
                "average_impact": 0
            }
        
        severity_counts = {}
        total_impact = 0
        critical_count = 0
        
        for event in normalized_events:
            sev = event["severity"]
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            total_impact += event["impact_score"]
            if event["severity"] == "critical":
                critical_count += 1
        
        return {
            "total_events": len(normalized_events),
            "events_by_severity": severity_counts,
            "average_impact": round(total_impact / len(normalized_events), 3),
            "critical_events": critical_count,
            "requires_action": sum(
                1 for e in normalized_events 
                if e.get("requires_immediate_action")
            ),
            "timestamp": datetime.now().isoformat()
        }
