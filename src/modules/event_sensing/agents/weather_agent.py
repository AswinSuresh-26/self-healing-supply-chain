"""
Weather Agent

Monitors weather conditions and natural disaster events that could
impact supply chains. Focuses on severe weather, cyclones, floods,
earthquakes, and other natural phenomena.

In simulation mode, generates realistic synthetic weather events for testing.
"""

import random
from datetime import datetime, timedelta
from typing import List

from .base_agent import BaseAgent
from ..core.event import (
    Event, EventType, EventSeverity, EventCategory, GeoLocation
)


# Simulation data for generating realistic weather/disaster events
SIMULATED_WEATHER_EVENTS = [
    {
        "title": "Typhoon Approaching Taiwan Strait",
        "description": "Category 4 typhoon expected to impact shipping lanes in Taiwan Strait within 48 hours. Wind speeds exceeding 200 km/h.",
        "severity": EventSeverity.CRITICAL,
        "weather_type": "cyclone",
        "location": GeoLocation(country="Taiwan", region="Taiwan Strait", latitude=24.5, longitude=121.0),
        "keywords": ["typhoon", "taiwan", "shipping lane", "severe weather"]
    },
    {
        "title": "Severe Flooding in Bangkok Industrial Zone",
        "description": "Monsoon rains cause widespread flooding in eastern Bangkok. Multiple manufacturing facilities report operations suspended.",
        "severity": EventSeverity.HIGH,
        "weather_type": "flood",
        "location": GeoLocation(country="Thailand", city="Bangkok", latitude=13.75, longitude=100.52),
        "keywords": ["flood", "manufacturing", "thailand", "monsoon"]
    },
    {
        "title": "Earthquake Disrupts Japan Supply Routes",
        "description": "Magnitude 6.2 earthquake in Osaka region. Several highways and rail lines temporarily closed for inspection.",
        "severity": EventSeverity.HIGH,
        "weather_type": "earthquake",
        "location": GeoLocation(country="Japan", region="Kansai", city="Osaka", latitude=34.69, longitude=135.50),
        "keywords": ["earthquake", "japan", "infrastructure", "transport disruption"]
    },
    {
        "title": "Winter Storm Grounds Flights Across Northern Europe",
        "description": "Heavy snowfall and blizzard conditions force closure of multiple airports. Air freight operations severely impacted.",
        "severity": EventSeverity.MEDIUM,
        "weather_type": "storm",
        "location": GeoLocation(country="Germany", city="Frankfurt", latitude=50.11, longitude=8.68),
        "keywords": ["winter storm", "airport closure", "air freight", "europe"]
    },
    {
        "title": "Hurricane Warning for Gulf of Mexico",
        "description": "Category 3 hurricane forecast to make landfall near Houston within 72 hours. Energy sector facilities initiating evacuation.",
        "severity": EventSeverity.CRITICAL,
        "weather_type": "hurricane",
        "location": GeoLocation(country="USA", region="Texas", city="Houston", latitude=29.76, longitude=-95.37),
        "keywords": ["hurricane", "gulf of mexico", "energy sector", "houston"]
    },
    {
        "title": "Cyclone Impacts Kolkata Port Operations",
        "description": "Severe cyclonic storm causes port closure at Kolkata. Container terminal operations suspended for minimum 24 hours.",
        "severity": EventSeverity.HIGH,
        "weather_type": "cyclone",
        "location": GeoLocation(country="India", region="West Bengal", city="Kolkata", latitude=22.57, longitude=88.36),
        "keywords": ["cyclone", "port closure", "kolkata", "bay of bengal"]
    },
    {
        "title": "Volcanic Ash Cloud Disrupts Pacific Air Routes",
        "description": "Mount Sakurajima eruption creates ash hazard zone. Trans-Pacific flights rerouting, adding 2-4 hours to journey times.",
        "severity": EventSeverity.MEDIUM,
        "weather_type": "volcanic",
        "location": GeoLocation(country="Japan", region="Kagoshima", latitude=31.58, longitude=130.66),
        "keywords": ["volcano", "ash cloud", "air freight", "pacific routes"]
    },
    {
        "title": "Flash Floods Close Major Highway in Vietnam",
        "description": "Sudden heavy rainfall causes flooding on Highway 1 between Ho Chi Minh City and Dong Nai. Truck traffic diverted.",
        "severity": EventSeverity.MEDIUM,
        "weather_type": "flood",
        "location": GeoLocation(country="Vietnam", city="Ho Chi Minh City", latitude=10.82, longitude=106.63),
        "keywords": ["flash flood", "highway closure", "vietnam", "logistics"]
    },
    {
        "title": "Dust Storm Reduces Visibility at Dubai Ports",
        "description": "Severe dust storm impacts Jebel Ali port operations. Container handling reduced by 50% due to safety protocols.",
        "severity": EventSeverity.LOW,
        "weather_type": "storm",
        "location": GeoLocation(country="UAE", city="Dubai", latitude=25.01, longitude=55.07),
        "keywords": ["dust storm", "dubai", "jebel ali", "port operations"]
    },
    {
        "title": "Monsoon Causes Landslides on India-Nepal Border",
        "description": "Heavy monsoon rains trigger multiple landslides blocking key trade routes between India and Nepal.",
        "severity": EventSeverity.MEDIUM,
        "weather_type": "flood",
        "location": GeoLocation(country="Nepal", region="Kathmandu Valley", latitude=27.70, longitude=85.32),
        "keywords": ["landslide", "monsoon", "trade route", "nepal"]
    }
]


class WeatherAgent(BaseAgent):
    """
    Agent for monitoring weather and natural disaster events.
    
    Detects events such as:
    - Cyclones, typhoons, and hurricanes
    - Floods and monsoon impacts
    - Earthquakes
    - Severe storms (winter, dust, etc.)
    - Volcanic activity affecting transport
    
    In simulation mode, generates realistic synthetic events for testing.
    In live mode (future), would integrate with OpenWeatherMap or NOAA.
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize the Weather Agent."""
        super().__init__(enabled=enabled)
        self._monitored_types = self.settings.weather_event_types
    
    def get_agent_name(self) -> str:
        return "WeatherAgent"
    
    def get_event_type(self) -> EventType:
        return EventType.WEATHER
    
    def sense(self) -> List[Event]:
        """
        Perform weather sensing cycle.
        
        In simulation mode: Returns a subset of simulated events
        In live mode: Would query weather APIs (not implemented)
        """
        if self.settings.is_simulation:
            return self._generate_simulated_events()
        else:
            return self._fetch_live_events()
    
    def _generate_simulated_events(self) -> List[Event]:
        """Generate simulated weather events for testing."""
        events = []
        
        # Weather events are less frequent but more impactful
        # Generate 0-1 events per cycle
        if random.random() > 0.4:  # 60% chance of an event
            return events
        
        # Filter events by monitored types
        filtered_events = [
            e for e in SIMULATED_WEATHER_EVENTS
            if e["weather_type"] in self._monitored_types or not self._monitored_types
        ]
        
        if not filtered_events:
            return events
        
        # Select a random event
        event_data = random.choice(filtered_events)
        
        # Apply severity threshold
        severity_order = [EventSeverity.LOW, EventSeverity.MEDIUM, EventSeverity.HIGH, EventSeverity.CRITICAL]
        threshold = self.settings.weather_severity_threshold
        threshold_idx = next(
            (i for i, s in enumerate(severity_order) if s.value == threshold),
            0
        )
        event_severity_idx = severity_order.index(event_data["severity"])
        
        if event_severity_idx < threshold_idx:
            self.logger.debug(f"Event below severity threshold: {event_data['title']}")
            return events
        
        # Create the event
        confidence = random.uniform(0.85, 0.98)  # Weather data usually high confidence
        time_offset = timedelta(minutes=random.randint(-15, 0))
        
        event = Event(
            title=event_data["title"],
            description=event_data["description"],
            source_type=EventType.WEATHER,
            category=EventCategory.NATURAL_DISASTER,
            severity=event_data["severity"],
            location=event_data["location"],
            confidence=confidence,
            keywords=event_data["keywords"],
            source_url=f"https://weather.example.com/alert/{random.randint(1000, 9999)}",
            raw_data={
                "simulated": True,
                "source": "WeatherAgent",
                "weather_type": event_data["weather_type"]
            },
            timestamp=datetime.now() + time_offset
        )
        events.append(event)
        self.logger.info(f"[SIMULATED] Detected: {event.title}")
        
        return events
    
    def _fetch_live_events(self) -> List[Event]:
        """
        Fetch live weather events from external APIs.
        
        This is a placeholder for future implementation.
        Would integrate with OpenWeatherMap, NOAA, or similar services.
        """
        self.logger.warning("Live weather fetching not implemented. Use simulation mode.")
        return []
