"""
Event Data Model

Defines the core event structure used across all sensing agents.
Events are normalized into this common format for downstream processing.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List


class EventType(Enum):
    """Types of events that can be detected by sensing agents."""
    NEWS = "news"
    WEATHER = "weather"
    ECONOMIC = "economic"
    SOCIAL = "social"


class EventSeverity(Enum):
    """Severity levels for supply chain disruption events."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    @classmethod
    def from_score(cls, score: float) -> "EventSeverity":
        """Convert a numeric score (0-1) to severity level."""
        if score >= 0.8:
            return cls.CRITICAL
        elif score >= 0.6:
            return cls.HIGH
        elif score >= 0.4:
            return cls.MEDIUM
        else:
            return cls.LOW


class EventCategory(Enum):
    """Categories of supply chain disruptions."""
    LOGISTICS = "logistics"
    NATURAL_DISASTER = "natural_disaster"
    GEOPOLITICAL = "geopolitical"
    ECONOMIC = "economic"
    LABOR = "labor"
    INFRASTRUCTURE = "infrastructure"
    OTHER = "other"


class GeoLocation:
    """Geographic location information for an event."""
    
    def __init__(
        self,
        country: str = None,
        region: str = None,
        city: str = None,
        latitude: float = None,
        longitude: float = None
    ):
        self.country = country
        self.region = region
        self.city = city
        self.latitude = latitude
        self.longitude = longitude
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert location to dictionary."""
        return {
            "country": self.country,
            "region": self.region,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GeoLocation":
        """Create location from dictionary."""
        return cls(
            country=data.get("country"),
            region=data.get("region"),
            city=data.get("city"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude")
        )
    
    def __repr__(self) -> str:
        parts = [p for p in [self.city, self.region, self.country] if p]
        return ", ".join(parts) if parts else "Unknown Location"


class Event:
    """
    Represents a detected supply chain disruption event.
    
    This is the core data structure used to communicate between
    sensing agents and downstream modules.
    """
    
    def __init__(
        self,
        title: str,
        description: str,
        source_type: EventType,
        category: EventCategory,
        severity: EventSeverity,
        location: GeoLocation = None,
        confidence: float = 1.0,
        keywords: List[str] = None,
        source_url: str = None,
        raw_data: Dict[str, Any] = None,
        event_id: str = None,
        timestamp: datetime = None,
        detected_at: datetime = None
    ):
        """
        Initialize a new Event.
        
        Args:
            title: Short description of the event
            description: Detailed event information
            source_type: Type of source (news, weather, etc.)
            category: Category of disruption
            severity: Severity level (low to critical)
            location: Geographic location of the event
            confidence: AI confidence score (0-1)
            keywords: Relevant keywords detected
            source_url: Original source URL
            raw_data: Original source data
            event_id: Unique event identifier (auto-generated if not provided)
            timestamp: When the event occurred
            detected_at: When the event was detected by the system
        """
        self.event_id = event_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.source_type = source_type
        self.category = category
        self.severity = severity
        self.location = location or GeoLocation()
        self.confidence = min(max(confidence, 0.0), 1.0)  # Clamp to 0-1
        self.keywords = keywords or []
        self.source_url = source_url
        self.raw_data = raw_data or {}
        self.timestamp = timestamp or datetime.now()
        self.detected_at = detected_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "title": self.title,
            "description": self.description,
            "source_type": self.source_type.value,
            "category": self.category.value,
            "severity": self.severity.value,
            "location": self.location.to_dict(),
            "confidence": self.confidence,
            "keywords": self.keywords,
            "source_url": self.source_url,
            "raw_data": self.raw_data,
            "timestamp": self.timestamp.isoformat(),
            "detected_at": self.detected_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Create event from dictionary."""
        return cls(
            event_id=data.get("event_id"),
            title=data["title"],
            description=data["description"],
            source_type=EventType(data["source_type"]),
            category=EventCategory(data["category"]),
            severity=EventSeverity(data["severity"]),
            location=GeoLocation.from_dict(data.get("location", {})),
            confidence=data.get("confidence", 1.0),
            keywords=data.get("keywords", []),
            source_url=data.get("source_url"),
            raw_data=data.get("raw_data", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
            detected_at=datetime.fromisoformat(data["detected_at"]) if data.get("detected_at") else None
        )
    
    def __repr__(self) -> str:
        return (
            f"Event(id={self.event_id[:8]}..., "
            f"title='{self.title[:30]}...', "
            f"severity={self.severity.value}, "
            f"category={self.category.value})"
        )
    
    def __eq__(self, other) -> bool:
        """Check equality based on event_id."""
        if isinstance(other, Event):
            return self.event_id == other.event_id
        return False
    
    def __hash__(self) -> int:
        return hash(self.event_id)


class EventBatch:
    """A collection of events for batch processing."""
    
    def __init__(self, events: List[Event] = None, source_agent: str = None):
        self.events = events or []
        self.source_agent = source_agent
        self.batch_id = str(uuid.uuid4())
        self.created_at = datetime.now()
    
    def add(self, event: Event):
        """Add an event to the batch."""
        self.events.append(event)
    
    def __len__(self) -> int:
        return len(self.events)
    
    def __iter__(self):
        return iter(self.events)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert batch to dictionary."""
        return {
            "batch_id": self.batch_id,
            "source_agent": self.source_agent,
            "created_at": self.created_at.isoformat(),
            "event_count": len(self.events),
            "events": [e.to_dict() for e in self.events]
        }
