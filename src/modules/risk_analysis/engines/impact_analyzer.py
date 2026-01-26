"""
Supplier Impact Analyzer

Maps disruption events to affected suppliers based on
geographic location, product categories, and supply chain relationships.
"""

import logging
from typing import Dict, Any, List, Optional

from ..models.supplier import Supplier, SupplierCriticality, get_simulated_suppliers


class SupplierImpactAnalyzer:
    """
    Analyzes which suppliers are impacted by disruption events.
    
    Uses multiple matching strategies:
    - Geographic matching (country, region, city)
    - Category matching (event keywords vs supplier categories)
    - Proximity analysis for natural disasters
    """
    
    def __init__(self, suppliers: List[Supplier] = None):
        """
        Initialize the analyzer.
        
        Args:
            suppliers: List of suppliers to analyze against.
                      Uses simulated suppliers if not provided.
        """
        self.suppliers = suppliers or get_simulated_suppliers()
        self.logger = logging.getLogger("SupplierImpactAnalyzer")
    
    def find_affected_suppliers(self, event: Dict[str, Any]) -> List[Supplier]:
        """
        Find all suppliers potentially affected by an event.
        
        Args:
            event: Normalized event from Module 1
            
        Returns:
            List of affected suppliers
        """
        affected = []
        
        # Get event location
        location = event.get("location", {})
        country = location.get("country")
        region = location.get("region")
        city = location.get("city")
        
        # Get event keywords for category matching
        keywords = event.get("keywords", [])
        
        for supplier in self.suppliers:
            # Check geographic match
            geo_match = self._check_geographic_match(
                supplier, country, region, city
            )
            
            # Check category/keyword match
            category_match = self._check_category_match(supplier, keywords)
            
            # A supplier is affected if location matches OR
            # if their categories match event keywords
            if geo_match or category_match:
                affected.append(supplier)
                self.logger.debug(
                    f"Supplier affected: {supplier.name} "
                    f"(geo={geo_match}, category={category_match})"
                )
        
        if affected:
            self.logger.info(
                f"Found {len(affected)} affected suppliers for event: "
                f"{event.get('title', 'Unknown')[:40]}"
            )
        
        return affected
    
    def _check_geographic_match(
        self,
        supplier: Supplier,
        country: str = None,
        region: str = None,
        city: str = None
    ) -> bool:
        """Check if supplier location matches event location."""
        # City match is most specific
        if city and supplier.is_in_city(city):
            return True
        
        # Region match
        if region and supplier.is_in_region(region):
            return True
        
        # Country match (broader impact)
        if country and supplier.is_in_country(country):
            return True
        
        return False
    
    def _check_category_match(
        self,
        supplier: Supplier,
        event_keywords: List[str]
    ) -> bool:
        """Check if supplier categories match event keywords."""
        if not event_keywords or not supplier.categories:
            return False
        
        # Normalize keywords and categories for comparison
        event_keywords_lower = [kw.lower() for kw in event_keywords]
        
        for category in supplier.categories:
            category_lower = category.lower()
            
            # Check for direct matches
            if category_lower in event_keywords_lower:
                return True
            
            # Check for partial matches
            for keyword in event_keywords_lower:
                if category_lower in keyword or keyword in category_lower:
                    return True
        
        # Additional keyword-to-category mapping
        keyword_category_map = {
            "port": ["logistics", "freight", "shipping", "maritime"],
            "shipping": ["logistics", "freight", "maritime"],
            "freight": ["logistics", "shipping"],
            "manufacturing": ["components", "assembly"],
            "semiconductor": ["electronics", "chips"],
            "energy": ["petrochemicals", "raw materials"],
            "cyclone": ["port services", "logistics", "shipping"],
            "flood": ["manufacturing", "logistics"],
            "earthquake": ["manufacturing", "components"]
        }
        
        for keyword in event_keywords_lower:
            if keyword in keyword_category_map:
                for mapped_category in keyword_category_map[keyword]:
                    if mapped_category in [c.lower() for c in supplier.categories]:
                        return True
        
        return False
    
    def analyze_impact_severity(
        self,
        supplier: Supplier,
        event: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze the severity of impact on a specific supplier.
        
        Returns:
            Impact analysis with severity and recommendations
        """
        event_severity = event.get("severity", "medium")
        impact_score = event.get("impact_score", 0.5)
        
        # Calculate base impact from event
        severity_weights = {
            "critical": 1.0,
            "high": 0.75,
            "medium": 0.5,
            "low": 0.25
        }
        base_impact = severity_weights.get(event_severity, 0.5)
        
        # Adjust for supplier criticality
        criticality_multipliers = {
            SupplierCriticality.CRITICAL: 1.5,
            SupplierCriticality.HIGH: 1.25,
            SupplierCriticality.MEDIUM: 1.0,
            SupplierCriticality.LOW: 0.75
        }
        multiplier = criticality_multipliers.get(supplier.criticality, 1.0)
        
        # Calculate final impact
        final_impact = min(1.0, base_impact * multiplier)
        
        # Estimate recovery time based on impact and lead time
        recovery_days = int(supplier.lead_time_days * (0.5 + final_impact * 0.5))
        
        return {
            "supplier_id": supplier.supplier_id,
            "supplier_name": supplier.name,
            "impact_severity": final_impact,
            "impact_level": "high" if final_impact >= 0.7 else "medium" if final_impact >= 0.4 else "low",
            "estimated_recovery_days": recovery_days,
            "financial_exposure": supplier.annual_spend,
            "is_critical": supplier.criticality == SupplierCriticality.CRITICAL,
            "recommendations": self._generate_recommendations(supplier, final_impact)
        }
    
    def _generate_recommendations(
        self,
        supplier: Supplier,
        impact_severity: float
    ) -> List[str]:
        """Generate mitigation recommendations based on impact."""
        recommendations = []
        
        if impact_severity >= 0.8:
            recommendations.append("Activate backup supplier immediately")
            recommendations.append("Expedite existing orders if possible")
        
        if supplier.criticality == SupplierCriticality.CRITICAL:
            recommendations.append("Escalate to executive leadership")
            recommendations.append("Review business continuity plan")
        
        if impact_severity >= 0.5:
            recommendations.append("Contact supplier for status update")
            recommendations.append("Assess inventory buffer levels")
        
        if supplier.lead_time_days > 20:
            recommendations.append("Consider air freight alternatives")
        
        return recommendations
    
    def get_supplier_by_id(self, supplier_id: str) -> Optional[Supplier]:
        """Get a supplier by ID."""
        for supplier in self.suppliers:
            if supplier.supplier_id == supplier_id:
                return supplier
        return None
    
    def get_suppliers_by_country(self, country: str) -> List[Supplier]:
        """Get all suppliers in a specific country."""
        return [s for s in self.suppliers if s.is_in_country(country)]
    
    def get_critical_suppliers(self) -> List[Supplier]:
        """Get all critical suppliers."""
        return [
            s for s in self.suppliers 
            if s.criticality == SupplierCriticality.CRITICAL
        ]
