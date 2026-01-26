# Event Sensing Module
"""
External Event Sensing Module for the Self-Healing Supply Chain Framework.

This module monitors external data sources to detect potential supply chain
disruptions including logistics issues, natural disasters, and other events.
"""

from .core.event import Event, EventType, EventSeverity
from .core.aggregator import EventAggregator
from .core.normalizer import EventNormalizer
from .agents.base_agent import BaseAgent
from .agents.news_agent import NewsAgent
from .agents.weather_agent import WeatherAgent

__version__ = "1.0.0"
__all__ = [
    "Event",
    "EventType", 
    "EventSeverity",
    "EventAggregator",
    "EventNormalizer",
    "BaseAgent",
    "NewsAgent",
    "WeatherAgent",
]
