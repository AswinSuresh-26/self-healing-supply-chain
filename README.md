# Self-Healing Supply Chain - Agentic AI Framework

A software-defined, agentic AI framework for detecting supply chain disruptions and enabling autonomous recovery planning.

## Overview

This framework implements a multi-agent system designed to:
- **Detect** supply chain disruptions from external information sources
- **Analyze** disruption risks and their potential impact
- **Plan** recovery strategies through autonomous decision orchestration
- **Reduce** human reaction latency in supply chain recovery

## Architecture

The system consists of 5 core modules:

1. **External Event Sensing Module** ✅ (Implemented)
2. Disruption Risk Analysis Module (Future)
3. Supplier Evaluation & Recovery Planning Module (Future)
4. Contract Drafting Module - LLM-Based (Future)
5. Orchestration & Control Module (Future)

## Module 1: External Event Sensing Module

The Event Sensing Module monitors external data sources to detect potential supply chain disruptions.

### Features

- **News Agent**: Monitors news sources for logistics disruptions (port delays, transport issues)
- **Weather Agent**: Tracks natural disasters (storms, floods, cyclones)
- **Event Aggregation**: Collects and deduplicates events from multiple agents
- **Event Normalization**: Standardizes events into a common format for downstream processing

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the demo
python -m src.modules.event_sensing.demo
```

### Project Structure

```
src/
└── modules/
    └── event_sensing/
        ├── agents/           # Sensing agents
        │   ├── base_agent.py
        │   ├── news_agent.py
        │   └── weather_agent.py
        ├── core/             # Core components
        │   ├── event.py
        │   ├── aggregator.py
        │   └── normalizer.py
        ├── config/           # Configuration
        │   └── settings.py
        └── demo.py           # Demo runner
```

## Technology Stack

- **Language**: Python 3.8+
- **HTTP Client**: requests
- **Data Format**: JSON-based event models
- **Architecture**: Multi-agent coordination pattern

## License

MIT License - Academic/Research Use

## Authors

Self-Healing Supply Chain Research Team