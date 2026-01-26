"""
Risk Analysis Module Demo

Demonstrates the integration between Module 1 (Event Sensing) and
Module 2 (Risk Analysis) for end-to-end disruption detection and
risk assessment.
"""

import logging
import json
from datetime import datetime

# Import Module 1 components
from ..event_sensing.agents.news_agent import NewsAgent
from ..event_sensing.agents.weather_agent import WeatherAgent
from ..event_sensing.core.aggregator import EventAggregator
from ..event_sensing.core.normalizer import EventNormalizer

# Import Module 2 components
from .models.risk import Risk, RiskAssessment
from .models.supplier import get_simulated_suppliers
from .engines.risk_scorer import RiskScorer
from .engines.impact_analyzer import SupplierImpactAnalyzer
from .engines.geo_correlator import GeographicCorrelator
from .core.classifier import RiskClassifier
from .core.alert_generator import AlertGenerator


def setup_logging():
    """Configure logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )


def print_banner():
    """Print the demo banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    SELF-HEALING SUPPLY CHAIN FRAMEWORK                       ║
║                                                                              ║
║             Module 2: Disruption Risk Analysis - DEMO                        ║
║                                                                              ║
║   Demonstrates end-to-end event sensing → risk analysis pipeline            ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def run_demo():
    """
    Run the end-to-end risk analysis demonstration.
    
    Pipeline:
    1. Event Sensing (Module 1) - Detect disruptions
    2. Risk Scoring - Calculate risk scores
    3. Supplier Impact - Map to affected suppliers
    4. Classification - Categorize and prioritize
    5. Alert Generation - Create actionable alerts
    """
    setup_logging()
    print_banner()
    
    # =========================================================================
    # PHASE 1: Event Sensing (Module 1)
    # =========================================================================
    print_section("Phase 1: Event Sensing (Module 1)")
    
    print("Initializing sensing agents...")
    news_agent = NewsAgent(enabled=True)
    weather_agent = WeatherAgent(enabled=True)
    aggregator = EventAggregator()
    normalizer = EventNormalizer()
    
    print("Running sensing cycles...")
    for cycle in range(3):
        news_batch = news_agent.run_cycle()
        weather_batch = weather_agent.run_cycle()
        aggregator.add_batch(news_batch)
        aggregator.add_batch(weather_batch)
    
    raw_events = aggregator.get_all_events()
    normalized_events = normalizer.normalize(raw_events)
    
    print(f"\n✓ Detected {len(normalized_events)} events")
    
    if not normalized_events:
        print("\nNo events detected in this run. Try again for different results.")
        print("(Simulation mode has random event generation)")
        return
    
    for event in normalized_events:
        severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
        icon = severity_icon.get(event["severity"], "⚪")
        print(f"  {icon} {event['title']}")
    
    # =========================================================================
    # PHASE 2: Risk Analysis Initialization
    # =========================================================================
    print_section("Phase 2: Initializing Risk Analysis Components")
    
    # Initialize components
    suppliers = get_simulated_suppliers()
    risk_scorer = RiskScorer()
    impact_analyzer = SupplierImpactAnalyzer(suppliers)
    geo_correlator = GeographicCorrelator(suppliers)
    classifier = RiskClassifier()
    alert_generator = AlertGenerator()
    
    print(f"✓ Loaded {len(suppliers)} suppliers in database")
    print("✓ Risk Scorer initialized")
    print("✓ Supplier Impact Analyzer initialized")
    print("✓ Geographic Correlator initialized")
    print("✓ Risk Classifier initialized")
    print("✓ Alert Generator initialized")
    
    # Show supplier distribution
    concentration_report = geo_correlator.get_concentration_report()
    print(f"\n  Supplier Distribution across {concentration_report['unique_countries']} countries:")
    for region in concentration_report['regions'][:5]:
        print(f"    - {region['country']}: {region['supplier_count']} suppliers ({region['spend_percentage']:.1f}% spend)")
    
    # =========================================================================
    # PHASE 3: Risk Analysis Pipeline
    # =========================================================================
    print_section("Phase 3: Analyzing Risks")
    
    risk_assessment = RiskAssessment()
    
    for event in normalized_events:
        print(f"\n📊 Analyzing: {event['title'][:50]}...")
        
        # Step 1: Find affected suppliers
        affected_suppliers = impact_analyzer.find_affected_suppliers(event)
        print(f"   → Affected suppliers: {len(affected_suppliers)}")
        
        if affected_suppliers:
            for s in affected_suppliers[:3]:
                print(f"      • {s.name} ({s.get_location_string()})")
        
        # Step 2: Calculate geographic risk
        geo_risk = geo_correlator.calculate_geographic_risk(event)
        print(f"   → Geographic risk: {geo_risk['risk_factor']:.2f} ({geo_risk['concentration_risk']})")
        
        # Step 3: Calculate risk score
        score_result = risk_scorer.calculate_risk_score(
            event, 
            affected_suppliers,
            geo_risk['risk_factor']
        )
        print(f"   → Risk score: {score_result['composite_score']:.2f} ({score_result['risk_level'].value})")
        
        # Step 4: Create Risk object
        risk = Risk(
            source_event_id=event['event_id'],
            title=f"Supply Chain Risk: {event['title']}",
            description=event['description'],
            risk_score=score_result['composite_score'],
            risk_level=score_result['risk_level'],
            risk_type=risk_scorer.get_risk_type(event),
            affected_suppliers=affected_suppliers,
            geographic_scope=geo_risk['affected_region'],
            mitigation_urgency=score_result['mitigation_urgency'],
            estimated_financial_impact=score_result['estimated_financial_impact'],
            estimated_delay_days=score_result['estimated_delay_days'],
            confidence=event.get('confidence', 1.0)
        )
        
        risk_assessment.add(risk)
    
    # =========================================================================
    # PHASE 4: Risk Classification
    # =========================================================================
    print_section("Phase 4: Risk Classification")
    
    risk_matrix = classifier.create_risk_matrix(risk_assessment)
    
    for level in ['critical', 'high', 'medium', 'low']:
        risks = risk_matrix[level]
        if risks:
            print(f"\n{level.upper()} RISKS ({len(risks)}):")
            for r in risks:
                print(f"  [P{r['priority']}] {r['title'][:50]}... (score: {r['score']:.2f})")
    
    # =========================================================================
    # PHASE 5: Alert Generation
    # =========================================================================
    print_section("Phase 5: Alert Generation")
    
    alerts = alert_generator.generate_alerts(list(risk_assessment))
    
    if alerts:
        alert_summary = alert_generator.get_alert_summary(alerts)
        print(f"Generated {alert_summary['total_alerts']} alerts:")
        print(f"  P1 (Critical): {alert_summary.get('by_priority', {}).get('P1', 0)}")
        print(f"  P2 (High): {alert_summary.get('by_priority', {}).get('P2', 0)}")
        print(f"  P3 (Medium): {alert_summary.get('by_priority', {}).get('P3', 0)}")
        print(f"  P4 (Low): {alert_summary.get('by_priority', {}).get('P4', 0)}")
        
        print("\n" + "-"*70)
        
        # Display top alert
        if alerts:
            top_alert = alerts[0]
            print(alert_generator.format_alert_for_display(top_alert))
    else:
        print("No alerts generated (risks below threshold)")
    
    # =========================================================================
    # PHASE 6: Summary Report
    # =========================================================================
    print_section("Summary Report")
    
    summary = risk_assessment.get_summary()
    
    print(f"  Total Risks Analyzed: {summary['total_risks']}")
    print(f"  Critical Risks: {summary['critical_count']}")
    print(f"  Immediate Action Required: {summary['immediate_action_count']}")
    print(f"  Est. Total Financial Impact: ${summary['total_estimated_impact']:,.0f}")
    print(f"  Max Est. Delay: {summary['max_delay_days']} days")
    
    print(f"\n  Risks by Level:")
    for level, count in summary.get('risks_by_level', {}).items():
        print(f"    - {level.upper()}: {count}")
    
    print(f"\n  Risks by Type:")
    for rtype, count in summary.get('risks_by_type', {}).items():
        print(f"    - {rtype.capitalize()}: {count}")
    
    # Sample JSON output
    print_section("Sample Risk JSON (for downstream modules)")
    
    if risk_assessment.risks:
        sample_risk = risk_assessment.risks[0]
        print(json.dumps(sample_risk.to_dict(), indent=2, default=str)[:1500] + "...")
    
    print("\n" + "="*70)
    print("  Demo Complete - Risk Analysis Module is ready for integration")
    print("="*70 + "\n")


def main():
    """Entry point for the demo."""
    print("\nStarting Risk Analysis Module Demo...")
    print("(Integrating with Event Sensing Module - SIMULATION mode)\n")
    
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
