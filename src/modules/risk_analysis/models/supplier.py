"""
Supplier Data Model

Represents suppliers in the supply chain with location,
criticality ratings, and product category information.
"""

import uuid
from enum import Enum
from typing import Dict, Any, List, Optional


class SupplierCriticality(Enum):
    """Criticality levels for suppliers."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    @classmethod
    def from_score(cls, score: float) -> "SupplierCriticality":
        """Convert a numeric score (0-1) to criticality level."""
        if score >= 0.9:
            return cls.CRITICAL
        elif score >= 0.7:
            return cls.HIGH
        elif score >= 0.4:
            return cls.MEDIUM
        else:
            return cls.LOW


class SupplierTier(Enum):
    """Supplier tier in the supply chain."""
    TIER_1 = "tier_1"  # Direct suppliers
    TIER_2 = "tier_2"  # Sub-suppliers
    TIER_3 = "tier_3"  # Third-level suppliers


class Supplier:
    """
    Represents a supplier in the supply chain.
    
    Contains location, criticality, and product category information
    used for risk analysis and impact assessment.
    """
    
    def __init__(
        self,
        name: str,
        country: str,
        city: str = None,
        region: str = None,
        latitude: float = None,
        longitude: float = None,
        criticality: SupplierCriticality = SupplierCriticality.MEDIUM,
        tier: SupplierTier = SupplierTier.TIER_1,
        categories: List[str] = None,
        lead_time_days: int = 14,
        annual_spend: float = 0,
        supplier_id: str = None
    ):
        """
        Initialize a Supplier.
        
        Args:
            name: Supplier company name
            country: Country where supplier is located
            city: City location
            region: Region/state/province
            latitude: Geographic latitude
            longitude: Geographic longitude
            criticality: How critical this supplier is
            tier: Supply chain tier level
            categories: Product/service categories
            lead_time_days: Average lead time in days
            annual_spend: Annual spend with supplier
            supplier_id: Unique identifier (auto-generated if not provided)
        """
        self.supplier_id = supplier_id or str(uuid.uuid4())
        self.name = name
        self.country = country
        self.city = city
        self.region = region
        self.latitude = latitude
        self.longitude = longitude
        self.criticality = criticality
        self.tier = tier
        self.categories = categories or []
        self.lead_time_days = lead_time_days
        self.annual_spend = annual_spend
    
    def get_location_string(self) -> str:
        """Get human-readable location string."""
        parts = [p for p in [self.city, self.region, self.country] if p]
        return ", ".join(parts) if parts else "Unknown"
    
    def is_in_country(self, country: str) -> bool:
        """Check if supplier is in the specified country."""
        if not country:
            return False
        return self.country.lower() == country.lower()
    
    def is_in_region(self, region: str) -> bool:
        """Check if supplier is in the specified region."""
        if not region or not self.region:
            return False
        return self.region.lower() == region.lower()
    
    def is_in_city(self, city: str) -> bool:
        """Check if supplier is in the specified city."""
        if not city or not self.city:
            return False
        return self.city.lower() == city.lower()
    
    def matches_location(self, country: str = None, region: str = None, city: str = None) -> bool:
        """Check if supplier matches any of the specified location criteria."""
        if city and self.is_in_city(city):
            return True
        if region and self.is_in_region(region):
            return True
        if country and self.is_in_country(country):
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert supplier to dictionary."""
        return {
            "supplier_id": self.supplier_id,
            "name": self.name,
            "country": self.country,
            "city": self.city,
            "region": self.region,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "criticality": self.criticality.value,
            "tier": self.tier.value,
            "categories": self.categories,
            "lead_time_days": self.lead_time_days,
            "annual_spend": self.annual_spend
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Supplier":
        """Create supplier from dictionary."""
        return cls(
            supplier_id=data.get("supplier_id"),
            name=data["name"],
            country=data["country"],
            city=data.get("city"),
            region=data.get("region"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            criticality=SupplierCriticality(data.get("criticality", "medium")),
            tier=SupplierTier(data.get("tier", "tier_1")),
            categories=data.get("categories", []),
            lead_time_days=data.get("lead_time_days", 14),
            annual_spend=data.get("annual_spend", 0)
        )
    
    def __repr__(self) -> str:
        return f"Supplier({self.name}, {self.get_location_string()}, {self.criticality.value})"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Supplier):
            return self.supplier_id == other.supplier_id
        return False
    
    def __hash__(self) -> int:
        return hash(self.supplier_id)


# Simulated supplier database for prototype
SIMULATED_SUPPLIERS = [
    Supplier(
        name="TechParts Asia",
        country="China",
        city="Shenzhen",
        region="Guangdong",
        latitude=22.54,
        longitude=114.06,
        criticality=SupplierCriticality.HIGH,
        tier=SupplierTier.TIER_1,
        categories=["electronics", "semiconductors", "components"],
        lead_time_days=21,
        annual_spend=5000000
    ),
    Supplier(
        name="Rotterdam Logistics BV",
        country="Netherlands",
        city="Rotterdam",
        latitude=51.92,
        longitude=4.48,
        criticality=SupplierCriticality.CRITICAL,
        tier=SupplierTier.TIER_1,
        categories=["freight", "logistics", "warehousing"],
        lead_time_days=7,
        annual_spend=3000000
    ),
    Supplier(
        name="Singapore Shipping Corp",
        country="Singapore",
        city="Singapore",
        latitude=1.29,
        longitude=103.85,
        criticality=SupplierCriticality.HIGH,
        tier=SupplierTier.TIER_1,
        categories=["maritime", "shipping", "freight"],
        lead_time_days=14,
        annual_spend=4000000
    ),
    Supplier(
        name="Mumbai Components Ltd",
        country="India",
        city="Mumbai",
        region="Maharashtra",
        latitude=18.95,
        longitude=72.95,
        criticality=SupplierCriticality.MEDIUM,
        tier=SupplierTier.TIER_2,
        categories=["manufacturing", "components", "assembly"],
        lead_time_days=28,
        annual_spend=1500000
    ),
    Supplier(
        name="Texas Energy Solutions",
        country="USA",
        city="Houston",
        region="Texas",
        latitude=29.76,
        longitude=-95.37,
        criticality=SupplierCriticality.HIGH,
        tier=SupplierTier.TIER_1,
        categories=["energy", "petrochemicals", "raw materials"],
        lead_time_days=10,
        annual_spend=6000000
    ),
    Supplier(
        name="Japan Precision Industries",
        country="Japan",
        city="Osaka",
        region="Kansai",
        latitude=34.69,
        longitude=135.50,
        criticality=SupplierCriticality.CRITICAL,
        tier=SupplierTier.TIER_1,
        categories=["precision components", "machinery", "electronics"],
        lead_time_days=18,
        annual_spend=8000000
    ),
    Supplier(
        name="Bangkok Manufacturing",
        country="Thailand",
        city="Bangkok",
        latitude=13.75,
        longitude=100.52,
        criticality=SupplierCriticality.MEDIUM,
        tier=SupplierTier.TIER_2,
        categories=["manufacturing", "assembly", "textiles"],
        lead_time_days=25,
        annual_spend=1200000
    ),
    Supplier(
        name="Taiwan Semiconductor",
        country="Taiwan",
        city="Taipei",
        latitude=25.03,
        longitude=121.57,
        criticality=SupplierCriticality.CRITICAL,
        tier=SupplierTier.TIER_1,
        categories=["semiconductors", "chips", "electronics"],
        lead_time_days=30,
        annual_spend=12000000
    ),
    Supplier(
        name="Kolkata Port Services",
        country="India",
        city="Kolkata",
        region="West Bengal",
        latitude=22.57,
        longitude=88.36,
        criticality=SupplierCriticality.MEDIUM,
        tier=SupplierTier.TIER_2,
        categories=["port services", "freight", "logistics"],
        lead_time_days=14,
        annual_spend=800000
    ),
    Supplier(
        name="Dubai Logistics Hub",
        country="UAE",
        city="Dubai",
        latitude=25.01,
        longitude=55.07,
        criticality=SupplierCriticality.HIGH,
        tier=SupplierTier.TIER_1,
        categories=["logistics", "freight", "distribution"],
        lead_time_days=12,
        annual_spend=2500000
    )
]


def get_simulated_suppliers() -> List[Supplier]:
    """Get the list of simulated suppliers for prototype testing."""
    return SIMULATED_SUPPLIERS.copy()
