"""
Geographic Correlator

Analyzes geographic concentration risk and correlates events
with supplier locations to assess regional exposure.
"""

import logging
import math
from typing import Dict, Any, List, Tuple

from ..models.supplier import Supplier, get_simulated_suppliers


class GeographicCorrelator:
    """
    Correlates events with geographic supplier distribution.
    
    Provides:
    - Geographic concentration risk analysis
    - Distance-based impact assessment
    - Regional dependency mapping
    """
    
    def __init__(self, suppliers: List[Supplier] = None):
        """
        Initialize the correlator.
        
        Args:
            suppliers: List of suppliers to analyze.
                      Uses simulated suppliers if not provided.
        """
        self.suppliers = suppliers or get_simulated_suppliers()
        self.logger = logging.getLogger("GeographicCorrelator")
        
        # Pre-calculate geographic distribution
        self._country_distribution = self._calculate_country_distribution()
    
    def _calculate_country_distribution(self) -> Dict[str, Dict]:
        """Calculate supplier distribution by country."""
        distribution = {}
        
        for supplier in self.suppliers:
            country = supplier.country
            if country not in distribution:
                distribution[country] = {
                    "supplier_count": 0,
                    "total_spend": 0,
                    "suppliers": []
                }
            
            distribution[country]["supplier_count"] += 1
            distribution[country]["total_spend"] += supplier.annual_spend
            distribution[country]["suppliers"].append(supplier.name)
        
        return distribution
    
    def calculate_geographic_risk(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate geographic risk factor for an event.
        
        Considers:
        - Concentration of suppliers in affected region
        - Total spend exposed in region
        - Criticality of suppliers in region
        
        Returns:
            Geographic risk analysis with risk factor (0-1)
        """
        location = event.get("location", {})
        country = location.get("country")
        region = location.get("region")
        city = location.get("city")
        
        if not country:
            return {
                "risk_factor": 0.3,  # Default moderate risk for unknown location
                "affected_region": "Unknown",
                "concentration_risk": "unknown",
                "suppliers_in_region": 0,
                "spend_at_risk": 0
            }
        
        # Get country distribution
        country_data = self._country_distribution.get(country, {})
        suppliers_in_country = country_data.get("supplier_count", 0)
        spend_in_country = country_data.get("total_spend", 0)
        
        # Calculate concentration risk
        total_suppliers = len(self.suppliers)
        total_spend = sum(s.annual_spend for s in self.suppliers)
        
        if total_suppliers == 0:
            concentration = 0
        else:
            concentration = suppliers_in_country / total_suppliers
        
        if total_spend == 0:
            spend_concentration = 0
        else:
            spend_concentration = spend_in_country / total_spend
        
        # Risk factor based on concentration
        # Higher concentration = higher risk
        risk_factor = (concentration * 0.4 + spend_concentration * 0.6)
        
        # Adjust for event severity
        severity = event.get("severity", "medium")
        severity_multipliers = {
            "critical": 1.3,
            "high": 1.15,
            "medium": 1.0,
            "low": 0.8
        }
        risk_factor *= severity_multipliers.get(severity, 1.0)
        risk_factor = min(1.0, risk_factor)
        
        # Determine concentration risk level
        if concentration >= 0.3:
            concentration_level = "high"
        elif concentration >= 0.15:
            concentration_level = "medium"
        else:
            concentration_level = "low"
        
        result = {
            "risk_factor": round(risk_factor, 3),
            "affected_region": self._format_region(country, region, city),
            "affected_country": country,
            "concentration_risk": concentration_level,
            "suppliers_in_region": suppliers_in_country,
            "spend_at_risk": spend_in_country,
            "supplier_concentration": round(concentration * 100, 1),
            "spend_concentration": round(spend_concentration * 100, 1)
        }
        
        self.logger.debug(
            f"Geographic risk: {risk_factor:.3f} for {country} "
            f"({suppliers_in_country} suppliers)"
        )
        
        return result
    
    def _format_region(
        self, 
        country: str, 
        region: str = None, 
        city: str = None
    ) -> str:
        """Format region string for display."""
        parts = [p for p in [city, region, country] if p]
        return ", ".join(parts) if parts else "Unknown"
    
    def find_nearby_suppliers(
        self,
        event: Dict[str, Any],
        radius_km: float = 500
    ) -> List[Tuple[Supplier, float]]:
        """
        Find suppliers within a radius of the event location.
        
        Args:
            event: Event with location coordinates
            radius_km: Search radius in kilometers
            
        Returns:
            List of (supplier, distance_km) tuples
        """
        location = event.get("location", {})
        coords = location.get("coordinates", {})
        
        event_lat = coords.get("lat") if coords else None
        event_lon = coords.get("lon") if coords else None
        
        if event_lat is None or event_lon is None:
            # Fall back to country-based matching
            return []
        
        nearby = []
        
        for supplier in self.suppliers:
            if supplier.latitude is None or supplier.longitude is None:
                continue
            
            distance = self._calculate_distance(
                event_lat, event_lon,
                supplier.latitude, supplier.longitude
            )
            
            if distance <= radius_km:
                nearby.append((supplier, distance))
        
        # Sort by distance
        nearby.sort(key=lambda x: x[1])
        
        return nearby
    
    def _calculate_distance(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float
    ) -> float:
        """
        Calculate distance between two points using Haversine formula.
        
        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (
            math.sin(delta_lat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) *
            math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def get_concentration_report(self) -> Dict[str, Any]:
        """
        Generate a concentration risk report for all regions.
        
        Returns:
            Report with concentration metrics by country
        """
        total_suppliers = len(self.suppliers)
        total_spend = sum(s.annual_spend for s in self.suppliers)
        
        regions = []
        
        for country, data in self._country_distribution.items():
            supplier_pct = (data["supplier_count"] / total_suppliers * 100) if total_suppliers > 0 else 0
            spend_pct = (data["total_spend"] / total_spend * 100) if total_spend > 0 else 0
            
            regions.append({
                "country": country,
                "supplier_count": data["supplier_count"],
                "total_spend": data["total_spend"],
                "supplier_percentage": round(supplier_pct, 1),
                "spend_percentage": round(spend_pct, 1),
                "suppliers": data["suppliers"]
            })
        
        # Sort by spend percentage
        regions.sort(key=lambda x: x["spend_percentage"], reverse=True)
        
        return {
            "total_suppliers": total_suppliers,
            "total_spend": total_spend,
            "unique_countries": len(self._country_distribution),
            "regions": regions
        }
