"""
Alert Generator

Generates alerts based on risk thresholds and escalation rules.
Provides formatted alerts for different channels and stakeholders.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid

from ..models.risk import Risk, RiskLevel, MitigationUrgency


class AlertPriority(Enum):
    """Alert priority levels."""
    P1 = "P1"  # Critical - immediate attention
    P2 = "P2"  # High - urgent attention
    P3 = "P3"  # Medium - timely attention
    P4 = "P4"  # Low - informational


class AlertChannel(Enum):
    """Alert delivery channels."""
    DASHBOARD = "dashboard"
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"


class Alert:
    """
    Represents a generated alert from risk analysis.
    """
    
    def __init__(
        self,
        risk: Risk,
        priority: AlertPriority,
        title: str,
        message: str,
        channels: List[AlertChannel] = None,
        recipients: List[str] = None,
        action_required: str = None,
        expires_at: datetime = None,
        alert_id: str = None
    ):
        self.alert_id = alert_id or str(uuid.uuid4())
        self.risk_id = risk.risk_id
        self.priority = priority
        self.title = title
        self.message = message
        self.channels = channels or [AlertChannel.DASHBOARD]
        self.recipients = recipients or []
        self.action_required = action_required
        self.expires_at = expires_at
        self.created_at = datetime.now()
        self.acknowledged = False
        self.acknowledged_by = None
        self.acknowledged_at = None
        
        # Store reference to risk for details
        self._risk = risk
    
    def acknowledge(self, user: str):
        """Mark alert as acknowledged."""
        self.acknowledged = True
        self.acknowledged_by = user
        self.acknowledged_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "risk_id": self.risk_id,
            "priority": self.priority.value,
            "title": self.title,
            "message": self.message,
            "channels": [c.value for c in self.channels],
            "recipients": self.recipients,
            "action_required": self.action_required,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }
    
    def __repr__(self) -> str:
        return f"Alert({self.priority.value}: {self.title[:40]}...)"


class AlertGenerator:
    """
    Generates alerts based on risk analysis results.
    
    Applies thresholds and rules to determine:
    - Which risks warrant alerts
    - Alert priority and channels
    - Recipients based on risk type
    """
    
    def __init__(
        self,
        critical_threshold: float = 0.8,
        high_threshold: float = 0.6,
        medium_threshold: float = 0.4
    ):
        """
        Initialize the alert generator.
        
        Args:
            critical_threshold: Score threshold for P1 alerts
            high_threshold: Score threshold for P2 alerts
            medium_threshold: Score threshold for P3 alerts
        """
        self.critical_threshold = critical_threshold
        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold
        self.logger = logging.getLogger("AlertGenerator")
        
        # Recipient mapping by priority
        self._recipient_map = {
            AlertPriority.P1: ["exec-team", "supply-chain-vp", "risk-management"],
            AlertPriority.P2: ["supply-chain-director", "procurement-lead"],
            AlertPriority.P3: ["supply-chain-manager", "category-manager"],
            AlertPriority.P4: ["supply-chain-analyst"]
        }
        
        # Channel mapping by priority
        self._channel_map = {
            AlertPriority.P1: [AlertChannel.DASHBOARD, AlertChannel.EMAIL, AlertChannel.SMS],
            AlertPriority.P2: [AlertChannel.DASHBOARD, AlertChannel.EMAIL],
            AlertPriority.P3: [AlertChannel.DASHBOARD, AlertChannel.EMAIL],
            AlertPriority.P4: [AlertChannel.DASHBOARD]
        }
    
    def generate_alert(self, risk: Risk) -> Optional[Alert]:
        """
        Generate an alert for a risk if it meets thresholds.
        
        Args:
            risk: Risk to evaluate
            
        Returns:
            Alert if risk meets threshold, None otherwise
        """
        # Determine if alert is needed
        priority = self._determine_priority(risk)
        
        if priority is None:
            self.logger.debug(f"Risk {risk.risk_id[:8]} below alert threshold")
            return None
        
        # Generate alert content
        title = self._generate_title(risk, priority)
        message = self._generate_message(risk)
        action = self._generate_action_required(risk)
        
        # Get channels and recipients
        channels = self._channel_map.get(priority, [AlertChannel.DASHBOARD])
        recipients = self._recipient_map.get(priority, [])
        
        alert = Alert(
            risk=risk,
            priority=priority,
            title=title,
            message=message,
            channels=channels,
            recipients=recipients,
            action_required=action
        )
        
        self.logger.info(
            f"Alert generated: {priority.value} - {title[:50]}"
        )
        
        return alert
    
    def generate_alerts(self, risks: List[Risk]) -> List[Alert]:
        """
        Generate alerts for a list of risks.
        
        Args:
            risks: List of risks to evaluate
            
        Returns:
            List of generated alerts
        """
        alerts = []
        
        for risk in risks:
            alert = self.generate_alert(risk)
            if alert:
                alerts.append(alert)
        
        # Sort by priority
        alerts.sort(key=lambda a: a.priority.value)
        
        self.logger.info(f"Generated {len(alerts)} alerts from {len(risks)} risks")
        
        return alerts
    
    def _determine_priority(self, risk: Risk) -> Optional[AlertPriority]:
        """Determine alert priority based on risk score and level."""
        # P1: Critical risks or very high scores
        if (risk.risk_level == RiskLevel.CRITICAL or 
            risk.risk_score >= self.critical_threshold):
            return AlertPriority.P1
        
        # P2: High risks with critical suppliers
        if (risk.risk_level == RiskLevel.HIGH or
            risk.risk_score >= self.high_threshold):
            if risk.has_critical_suppliers:
                return AlertPriority.P1  # Escalate if critical suppliers
            return AlertPriority.P2
        
        # P3: Medium risks
        if (risk.risk_level == RiskLevel.MEDIUM or
            risk.risk_score >= self.medium_threshold):
            return AlertPriority.P3
        
        # P4: Low risks (optional alerting)
        if risk.risk_level == RiskLevel.LOW:
            return AlertPriority.P4
        
        return None
    
    def _generate_title(self, risk: Risk, priority: AlertPriority) -> str:
        """Generate alert title."""
        prefix = {
            AlertPriority.P1: "🔴 CRITICAL",
            AlertPriority.P2: "🟠 HIGH",
            AlertPriority.P3: "🟡 MEDIUM",
            AlertPriority.P4: "🟢 LOW"
        }
        
        return f"{prefix.get(priority, '')} | {risk.title}"
    
    def _generate_message(self, risk: Risk) -> str:
        """Generate detailed alert message."""
        lines = [
            f"Risk Score: {risk.risk_score:.2f} ({risk.risk_level.value.upper()})",
            f"Type: {risk.risk_type.value.capitalize()}",
            f"",
            f"Description: {risk.description}",
            f"",
            f"Geographic Scope: {risk.geographic_scope or 'Not specified'}",
            f"Affected Suppliers: {risk.affected_supplier_count}"
        ]
        
        if risk.affected_suppliers:
            supplier_names = ", ".join(risk.get_affected_supplier_names()[:3])
            if risk.affected_supplier_count > 3:
                supplier_names += f" (+{risk.affected_supplier_count - 3} more)"
            lines.append(f"Suppliers: {supplier_names}")
        
        if risk.estimated_financial_impact > 0:
            lines.append(f"Est. Financial Impact: ${risk.estimated_financial_impact:,.0f}")
        
        if risk.estimated_delay_days > 0:
            lines.append(f"Est. Delay: {risk.estimated_delay_days} days")
        
        return "\n".join(lines)
    
    def _generate_action_required(self, risk: Risk) -> str:
        """Generate required action statement."""
        urgency_actions = {
            MitigationUrgency.IMMEDIATE: "Immediate action required within 24 hours",
            MitigationUrgency.SHORT_TERM: "Action required within 1 week",
            MitigationUrgency.MEDIUM_TERM: "Plan mitigation within 1 month",
            MitigationUrgency.LONG_TERM: "Add to risk register for monitoring"
        }
        
        return urgency_actions.get(
            risk.mitigation_urgency,
            "Review and assess appropriate response"
        )
    
    def format_alert_for_display(self, alert: Alert) -> str:
        """Format alert for console display."""
        lines = [
            "=" * 70,
            f"  ALERT: {alert.priority.value}",
            "=" * 70,
            f"  {alert.title}",
            "-" * 70,
            "",
            alert.message,
            "",
            "-" * 70,
            f"  ⚡ ACTION: {alert.action_required}",
            f"  📧 Recipients: {', '.join(alert.recipients)}",
            f"  📅 Created: {alert.created_at.strftime('%Y-%m-%d %H:%M')}",
            "=" * 70
        ]
        
        return "\n".join(lines)
    
    def get_alert_summary(self, alerts: List[Alert]) -> Dict[str, Any]:
        """Generate summary of alerts."""
        priority_counts = {}
        for alert in alerts:
            p = alert.priority.value
            priority_counts[p] = priority_counts.get(p, 0) + 1
        
        return {
            "total_alerts": len(alerts),
            "by_priority": priority_counts,
            "p1_count": priority_counts.get("P1", 0),
            "p2_count": priority_counts.get("P2", 0),
            "requiring_immediate_action": sum(
                1 for a in alerts if a.priority in [AlertPriority.P1, AlertPriority.P2]
            )
        }
