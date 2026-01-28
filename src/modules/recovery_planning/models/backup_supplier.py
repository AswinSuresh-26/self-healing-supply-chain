"""
Backup Supplier Model

Represents alternative/backup suppliers that can be activated
during supply chain disruptions.
"""

import uuid
from enum import Enum
from typing import Dict, Any, List


class SupplierStatus(Enum):
    """Status of backup supplier relationship."""
    ACTIVE = "active"           # Currently engaged
    STANDBY = "standby"         # Ready to activate
    QUALIFIED = "qualified"     # Qualified but not contracted
    PROSPECTIVE = "prospective" # Under evaluation


class BackupSupplier:
    """
    Represents a backup/alternative supplier for recovery scenarios.
    """
    
    def __init__(
        self,
        name: str,
        country: str,
        city: str = None,
        categories: List[str] = None,
        status: SupplierStatus = SupplierStatus.QUALIFIED,
        capacity_score: float = 0.7,
        quality_score: float = 0.8,
        lead_time_days: int = 21,
        cost_premium_pct: float = 10.0,
        min_order_value: float = 10000,
        max_capacity_units: int = 1000,
        certifications: List[str] = None,
        contact_email: str = None,
        supplier_id: str = None
    ):
        self.supplier_id = supplier_id or str(uuid.uuid4())
        self.name = name
        self.country = country
        self.city = city
        self.categories = categories or []
        self.status = status
        self.capacity_score = capacity_score
        self.quality_score = quality_score
        self.lead_time_days = lead_time_days
        self.cost_premium_pct = cost_premium_pct
        self.min_order_value = min_order_value
        self.max_capacity_units = max_capacity_units
        self.certifications = certifications or []
        self.contact_email = contact_email
    
    def get_overall_score(self) -> float:
        """Calculate overall supplier score."""
        # Weighted: 40% quality, 30% capacity, 30% cost efficiency
        cost_efficiency = max(0, 1 - (self.cost_premium_pct / 50))
        return (
            0.4 * self.quality_score +
            0.3 * self.capacity_score +
            0.3 * cost_efficiency
        )
    
    def can_supply(self, category: str) -> bool:
        """Check if supplier can supply a category."""
        return any(
            cat.lower() in category.lower() or category.lower() in cat.lower()
            for cat in self.categories
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "supplier_id": self.supplier_id,
            "name": self.name,
            "country": self.country,
            "city": self.city,
            "categories": self.categories,
            "status": self.status.value,
            "capacity_score": self.capacity_score,
            "quality_score": self.quality_score,
            "lead_time_days": self.lead_time_days,
            "cost_premium_pct": self.cost_premium_pct,
            "overall_score": round(self.get_overall_score(), 3),
            "certifications": self.certifications
        }
    
    def __repr__(self) -> str:
        return f"BackupSupplier({self.name}, {self.country}, score={self.get_overall_score():.2f})"


# Simulated backup supplier database
BACKUP_SUPPLIERS = [
    BackupSupplier(
        name="Vietnam Electronics Co",
        country="Vietnam",
        city="Ho Chi Minh City",
        categories=["electronics", "semiconductors", "components"],
        status=SupplierStatus.QUALIFIED,
        capacity_score=0.75,
        quality_score=0.80,
        lead_time_days=25,
        cost_premium_pct=8.0,
        certifications=["ISO 9001", "ISO 14001"]
    ),
    BackupSupplier(
        name="Malaysia Precision Parts",
        country="Malaysia",
        city="Penang",
        categories=["precision components", "machinery", "electronics"],
        status=SupplierStatus.STANDBY,
        capacity_score=0.85,
        quality_score=0.88,
        lead_time_days=20,
        cost_premium_pct=12.0,
        certifications=["ISO 9001", "AS9100"]
    ),
    BackupSupplier(
        name="Indonesia Manufacturing",
        country="Indonesia",
        city="Jakarta",
        categories=["manufacturing", "assembly", "textiles"],
        status=SupplierStatus.QUALIFIED,
        capacity_score=0.70,
        quality_score=0.75,
        lead_time_days=28,
        cost_premium_pct=5.0,
        certifications=["ISO 9001"]
    ),
    BackupSupplier(
        name="Mexico Logistics Partner",
        country="Mexico",
        city="Monterrey",
        categories=["logistics", "freight", "warehousing"],
        status=SupplierStatus.ACTIVE,
        capacity_score=0.80,
        quality_score=0.82,
        lead_time_days=14,
        cost_premium_pct=15.0,
        certifications=["C-TPAT", "ISO 9001"]
    ),
    BackupSupplier(
        name="Poland Distribution Hub",
        country="Poland",
        city="Warsaw",
        categories=["logistics", "distribution", "freight"],
        status=SupplierStatus.STANDBY,
        capacity_score=0.78,
        quality_score=0.85,
        lead_time_days=12,
        cost_premium_pct=18.0,
        certifications=["AEO", "ISO 9001"]
    ),
    BackupSupplier(
        name="South Korea Semiconductors",
        country="South Korea",
        city="Seoul",
        categories=["semiconductors", "chips", "electronics"],
        status=SupplierStatus.QUALIFIED,
        capacity_score=0.90,
        quality_score=0.92,
        lead_time_days=22,
        cost_premium_pct=20.0,
        certifications=["ISO 9001", "IATF 16949"]
    ),
    BackupSupplier(
        name="India Tech Solutions",
        country="India",
        city="Bangalore",
        categories=["components", "electronics", "software"],
        status=SupplierStatus.QUALIFIED,
        capacity_score=0.72,
        quality_score=0.78,
        lead_time_days=24,
        cost_premium_pct=6.0,
        certifications=["ISO 9001", "ISO 27001"]
    ),
    BackupSupplier(
        name="Philippines Assembly Corp",
        country="Philippines",
        city="Manila",
        categories=["assembly", "manufacturing", "components"],
        status=SupplierStatus.PROSPECTIVE,
        capacity_score=0.68,
        quality_score=0.74,
        lead_time_days=26,
        cost_premium_pct=4.0,
        certifications=["ISO 9001"]
    )
]


def get_backup_suppliers() -> List[BackupSupplier]:
    """Get list of backup suppliers."""
    return BACKUP_SUPPLIERS.copy()
