"""
Event Sensing Module Demo

Demonstrates the multi-agent coordination for supply chain
disruption detection. Runs sensing agents in simulation mode
and shows how events are aggregated and normalized.
"""

import time
import json
import logging
from datetime import datetime

from .agents.news_agent import NewsAgent
from .agents.weather_agent import WeatherAgent
from .core.aggregator import EventAggregator
from .core.normalizer import EventNormalizer
from .config.settings import get_settings


def setup_logging():
    """Configure logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)-15s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )


def print_banner():
    """Print the demo banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SELF-HEALING SUPPLY CHAIN FRAMEWORK                       ║
║                                                                              ║
║             Module 1: External Event Sensing - DEMO                          ║
║                                                                              ║
║   Demonstrates multi-agent coordination for disruption detection             ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def run_demo(num_cycles: int = 3, cycle_delay: float = 2.0):
    """
    Run the event sensing demonstration.
    
    Args:
        num_cycles: Number of sensing cycles to run
        cycle_delay: Delay between cycles in seconds
    """
    setup_logging()
    print_banner()
    
    settings = get_settings()
    
    # Print configuration
    print_section("Configuration")
    print(f"  Mode: {settings.mode.upper()}")
    print(f"  News Agent: {'Enabled' if settings.news_enabled else 'Disabled'}")
    print(f"  Weather Agent: {'Enabled' if settings.weather_enabled else 'Disabled'}")
    print(f"  Cycles to run: {num_cycles}")
    
    # Initialize components
    print_section("Initializing Agents")
    
    agents = []
    
    if settings.news_enabled:
        news_agent = NewsAgent(enabled=True)
        agents.append(news_agent)
        print(f"  ✓ {news_agent.get_agent_name()} initialized")
    
    if settings.weather_enabled:
        weather_agent = WeatherAgent(enabled=True)
        agents.append(weather_agent)
        print(f"  ✓ {weather_agent.get_agent_name()} initialized")
    
    # Initialize aggregator and normalizer
    aggregator = EventAggregator(
        deduplication_window_seconds=settings.deduplication_window,
        max_buffer_size=settings.max_events_buffer
    )
    normalizer = EventNormalizer(
        confidence_threshold=settings.confidence_threshold
    )
    
    print(f"  ✓ EventAggregator initialized")
    print(f"  ✓ EventNormalizer initialized")
    
    # Run sensing cycles
    print_section("Running Sensing Cycles")
    
    all_events = []
    
    for cycle in range(1, num_cycles + 1):
        print(f"\n--- Cycle {cycle}/{num_cycles} ---")
        
        # Run each agent
        for agent in agents:
            batch = agent.run_cycle()
            
            if len(batch) > 0:
                added = aggregator.add_batch(batch)
                print(f"  {agent.get_agent_name()}: {len(batch)} events detected, {added} new")
            else:
                print(f"  {agent.get_agent_name()}: No events")
        
        # Show cycle summary
        stats = aggregator.get_statistics()
        print(f"  Buffer: {stats['total_events']} total events")
        
        if cycle < num_cycles:
            time.sleep(cycle_delay)
    
    # Process and display results
    print_section("Event Analysis Results")
    
    all_raw_events = aggregator.get_all_events()
    normalized_events = normalizer.normalize(all_raw_events)
    
    if not normalized_events:
        print("  No events were detected during this demo run.")
        print("  (This can happen due to randomization in simulation mode)")
        print("  Try running the demo again for different results.")
        return
    
    # Display normalized events
    print(f"Total Events Detected: {len(normalized_events)}\n")
    
    for event in normalized_events:
        print(normalizer.format_for_display(event))
        print()
    
    # Show summary
    print_section("Summary Report")
    
    summary = normalizer.create_summary(normalized_events)
    
    print(f"  Total Events: {summary['total_events']}")
    print(f"  Average Impact Score: {summary['average_impact']:.2f}")
    print(f"  Critical Events: {summary['critical_events']}")
    print(f"  Requiring Action: {summary['requires_action']}")
    print(f"\n  Events by Severity:")
    for severity, count in summary['events_by_severity'].items():
        print(f"    - {severity.upper()}: {count}")
    
    # Agent status
    print_section("Agent Status")
    
    for agent in agents:
        status = agent.get_status()
        print(f"  {status['agent_name']}:")
        print(f"    - Events detected: {status['total_events_detected']}")
        print(f"    - Last run: {status['last_run']}")
    
    # Export sample JSON
    print_section("Sample Event JSON (for downstream modules)")
    
    if normalized_events:
        sample = normalized_events[0]
        print(json.dumps(sample, indent=2))
    
    print("\n" + "="*70)
    print("  Demo Complete - Event Sensing Module is ready for integration")
    print("="*70 + "\n")


def main():
    """Entry point for the demo."""
    print("\nStarting Event Sensing Module Demo...")
    print("(Running in SIMULATION mode - generating synthetic events)\n")
    
    try:
        run_demo(num_cycles=3, cycle_delay=1.0)
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError during demo: {e}")
        raise


if __name__ == "__main__":
    main()
