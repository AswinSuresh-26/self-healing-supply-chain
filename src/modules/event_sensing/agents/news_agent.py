"""
News Agent

Monitors news sources for supply chain disruption events.
Focuses on logistics disruptions such as port closures, shipping delays,
and transportation issues.

In simulation mode, generates realistic synthetic events for testing.
"""

import random
from datetime import datetime, timedelta
from typing import List

from .base_agent import BaseAgent
from ..core.event import (
    Event, EventType, EventSeverity, EventCategory, GeoLocation
)


# Simulation data for generating realistic test events
SIMULATED_NEWS_EVENTS = [
    {
        "title": "Major Port Congestion at Singapore",
        "description": "Container ship backlog at Port of Singapore reaches 3-day delays. Shipping companies report significant disruptions to Asia-Pacific routes.",
        "category": EventCategory.LOGISTICS,
        "severity": EventSeverity.HIGH,
        "location": GeoLocation(country="Singapore", city="Singapore", latitude=1.29, longitude=103.85),
        "keywords": ["port congestion", "shipping delay", "container backlog", "singapore"]
    },
    {
        "title": "Rotterdam Port Workers Announce Strike",
        "description": "Dock workers at Europe's largest port announce 48-hour strike starting Monday. Expected to impact EU supply chains significantly.",
        "category": EventCategory.LABOR,
        "severity": EventSeverity.HIGH,
        "location": GeoLocation(country="Netherlands", city="Rotterdam", latitude=51.92, longitude=4.48),
        "keywords": ["port strike", "labor dispute", "rotterdam", "supply chain disruption"]
    },
    {
        "title": "Suez Canal Traffic Resumes After Vessel Breakdown",
        "description": "Container vessel engine failure caused 12-hour blockage. Traffic now flowing but delays expected for 48 hours.",
        "category": EventCategory.LOGISTICS,
        "severity": EventSeverity.MEDIUM,
        "location": GeoLocation(country="Egypt", region="Suez", latitude=30.45, longitude=32.35),
        "keywords": ["suez canal", "shipping route", "vessel breakdown", "maritime"]
    },
    {
        "title": "Los Angeles Port Reports Record Container Backlog",
        "description": "Over 40 container ships anchored outside LA/Long Beach ports. Average wait time exceeds 7 days.",
        "category": EventCategory.LOGISTICS,
        "severity": EventSeverity.CRITICAL,
        "location": GeoLocation(country="USA", region="California", city="Los Angeles", latitude=33.74, longitude=-118.27),
        "keywords": ["port congestion", "container backlog", "los angeles", "shipping crisis"]
    },
    {
        "title": "Rail Freight Disruption in Northern China",
        "description": "Heavy snowfall halts rail freight operations across Heilongjiang province. Recovery expected in 3-4 days.",
        "category": EventCategory.LOGISTICS,
        "severity": EventSeverity.MEDIUM,
        "location": GeoLocation(country="China", region="Heilongjiang", latitude=45.75, longitude=126.65),
        "keywords": ["rail disruption", "freight", "china", "weather impact"]
    },
    {
        "title": "Panama Canal Implements Water Restrictions",
        "description": "Drought conditions force Panama Canal to reduce daily transits by 25%. Shipping companies rerouting vessels.",
        "category": EventCategory.INFRASTRUCTURE,
        "severity": EventSeverity.HIGH,
        "location": GeoLocation(country="Panama", region="Panama Canal", latitude=9.08, longitude=-79.68),
        "keywords": ["panama canal", "water restrictions", "shipping route", "transit limits"]
    },
    {
        "title": "Truck Driver Shortage Worsens in UK",
        "description": "Industry reports 15% driver vacancy rate affecting retail supply chains. Delivery delays spreading nationwide.",
        "category": EventCategory.LABOR,
        "severity": EventSeverity.MEDIUM,
        "location": GeoLocation(country="United Kingdom", latitude=51.51, longitude=-0.13),
        "keywords": ["truck driver shortage", "logistics", "uk", "delivery delays"]
    },
    {
        "title": "Mumbai Port Operations Suspended Due to Cyclone Warning",
        "description": "Jawaharlal Nehru Port suspends operations ahead of approaching cyclone. Container handling halted for 48 hours.",
        "category": EventCategory.NATURAL_DISASTER,
        "severity": EventSeverity.HIGH,
        "location": GeoLocation(country="India", region="Maharashtra", city="Mumbai", latitude=18.95, longitude=72.95),
        "keywords": ["port closure", "cyclone", "mumbai", "jnpt"]
    }
]


class NewsAgent(BaseAgent):
    """
    Agent for monitoring news sources for logistics disruptions.
    
    Detects events such as:
    - Port congestion and closures
    - Shipping delays and route disruptions
    - Transportation strikes and labor issues
    - Infrastructure problems affecting logistics
    
    In simulation mode, generates realistic synthetic events for testing.
    In live mode (future), would integrate with NewsAPI or RSS feeds.
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize the News Agent."""
        super().__init__(enabled=enabled)
        self._simulated_event_index = 0
    
    def get_agent_name(self) -> str:
        return "NewsAgent"
    
    def get_event_type(self) -> EventType:
        return EventType.NEWS
    
    def sense(self) -> List[Event]:
        """
        Perform news sensing cycle.
        
        In simulation mode: Returns a subset of simulated events
        In live mode: Would query news APIs (not implemented)
        """
        if self.settings.is_simulation:
            return self._generate_simulated_events()
        else:
            return self._fetch_live_events()
    
    def _generate_simulated_events(self) -> List[Event]:
        """Generate simulated news events for testing."""
        events = []
        
        # Randomly decide how many events to generate (0-2 per cycle)
        num_events = random.choice([0, 0, 1, 1, 1, 2])
        
        if num_events == 0:
            self.logger.debug("No news events in this simulation cycle")
            return events
        
        # Select random events from the simulation pool
        available_events = random.sample(
            SIMULATED_NEWS_EVENTS, 
            min(num_events, len(SIMULATED_NEWS_EVENTS))
        )
        
        for event_data in available_events:
            # Add some randomness to the event
            confidence = random.uniform(0.7, 0.95)
            
            # Create the event with slight time variance
            time_offset = timedelta(minutes=random.randint(-30, 0))
            
            event = Event(
                title=event_data["title"],
                description=event_data["description"],
                source_type=EventType.NEWS,
                category=event_data["category"],
                severity=event_data["severity"],
                location=event_data["location"],
                confidence=confidence,
                keywords=event_data["keywords"],
                source_url=f"https://news.example.com/article/{random.randint(1000, 9999)}",
                raw_data={"simulated": True, "source": "NewsAgent"},
                timestamp=datetime.now() + time_offset
            )
            events.append(event)
            self.logger.info(f"[SIMULATED] Detected: {event.title}")
        
        return events
    
    def _fetch_live_events(self) -> List[Event]:
        """
        Fetch live news events from external APIs.
        
        This is a placeholder for future implementation.
        Would integrate with NewsAPI, GDELT, or RSS feeds.
        """
        self.logger.warning("Live news fetching not implemented. Use simulation mode.")
        return []
