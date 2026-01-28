"""
Supplier Evaluator Engine

Evaluates and ranks backup suppliers based on capability
to fulfill needs during disruption recovery.
"""

import logging
from typing import Dict, Any, List, Optional

from ..models.backup_supplier import BackupSupplier, SupplierStatus, get_backup_suppliers


class SupplierEvaluator:
    """
    Evaluates backup suppliers for recovery scenarios.
    
    Scores suppliers based on:
    - Category match
    - Quality rating
    - Capacity availability
    - Lead time
    - Cost efficiency
    - Geographic diversification
    """
    
    def __init__(self, backup_suppliers: List[BackupSupplier] = None):
        self.backup_suppliers = backup_suppliers or get_backup_suppliers()
        self.logger = logging.getLogger("SupplierEvaluator")
    
    def find_alternatives(
        self,
        required_categories: List[str],
        affected_country: str = None,
        max_lead_time_days: int = 30,
        min_quality_score: float = 0.7,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find and rank alternative suppliers for given requirements.
        
        Args:
            required_categories: Categories needed
            affected_country: Country to avoid (affected by disruption)
            max_lead_time_days: Maximum acceptable lead time
            min_quality_score: Minimum quality threshold
            limit: Maximum number of suppliers to return
            
        Returns:
            Ranked list of suitable backup suppliers
        """
        candidates = []
        
        for supplier in self.backup_suppliers:
            # Skip suppliers in affected country
            if affected_country and supplier.country.lower() == affected_country.lower():
                continue
            
            # Check quality threshold
            if supplier.quality_score < min_quality_score:
                continue
            
            # Check lead time
            if supplier.lead_time_days > max_lead_time_days:
                continue
            
            # Check category match
            category_match = self._calculate_category_match(
                supplier.categories, required_categories
            )
            
            if category_match == 0:
                continue
            
            # Calculate evaluation score
            eval_score = self._calculate_evaluation_score(
                supplier, category_match
            )
            
            candidates.append({
                "supplier": supplier,
                "supplier_id": supplier.supplier_id,
                "name": supplier.name,
                "country": supplier.country,
                "city": supplier.city,
                "evaluation_score": round(eval_score, 3),
                "category_match": round(category_match, 3),
                "quality_score": supplier.quality_score,
                "capacity_score": supplier.capacity_score,
                "lead_time_days": supplier.lead_time_days,
                "cost_premium_pct": supplier.cost_premium_pct,
                "status": supplier.status.value,
                "certifications": supplier.certifications,
                "recommendation": self._get_recommendation(supplier, eval_score)
            })
        
        # Sort by evaluation score (descending)
        candidates.sort(key=lambda x: x["evaluation_score"], reverse=True)
        
        self.logger.info(f"Found {len(candidates)} suitable backup suppliers")
        
        return candidates[:limit]
    
    def _calculate_category_match(
        self,
        supplier_categories: List[str],
        required_categories: List[str]
    ) -> float:
        """Calculate how well supplier categories match requirements."""
        if not required_categories:
            return 0.5  # Default match
        
        matches = 0
        for req_cat in required_categories:
            for sup_cat in supplier_categories:
                if (req_cat.lower() in sup_cat.lower() or 
                    sup_cat.lower() in req_cat.lower()):
                    matches += 1
                    break
        
        return matches / len(required_categories)
    
    def _calculate_evaluation_score(
        self,
        supplier: BackupSupplier,
        category_match: float
    ) -> float:
        """
        Calculate comprehensive evaluation score.
        
        Weights:
        - 30% Category match
        - 25% Quality
        - 20% Capacity
        - 15% Lead time (inverse)
        - 10% Cost efficiency
        """
        # Normalize lead time (30 days = 0, 10 days = 1)
        lead_time_score = max(0, 1 - (supplier.lead_time_days - 10) / 20)
        
        # Cost efficiency (0% premium = 1, 30% premium = 0)
        cost_score = max(0, 1 - supplier.cost_premium_pct / 30)
        
        # Status bonus
        status_bonus = {
            SupplierStatus.ACTIVE: 0.1,
            SupplierStatus.STANDBY: 0.05,
            SupplierStatus.QUALIFIED: 0,
            SupplierStatus.PROSPECTIVE: -0.05
        }
        
        score = (
            0.30 * category_match +
            0.25 * supplier.quality_score +
            0.20 * supplier.capacity_score +
            0.15 * lead_time_score +
            0.10 * cost_score +
            status_bonus.get(supplier.status, 0)
        )
        
        return min(1.0, max(0, score))
    
    def _get_recommendation(self, supplier: BackupSupplier, score: float) -> str:
        """Generate recommendation based on evaluation."""
        if score >= 0.8:
            return "Highly Recommended - Activate immediately"
        elif score >= 0.65:
            return "Recommended - Good alternative"
        elif score >= 0.5:
            return "Acceptable - Consider as backup"
        else:
            return "Marginal - Use only if no alternatives"
    
    def get_supplier_details(self, supplier_id: str) -> Optional[BackupSupplier]:
        """Get backup supplier by ID."""
        for supplier in self.backup_suppliers:
            if supplier.supplier_id == supplier_id:
                return supplier
        return None
    
    def get_suppliers_by_status(self, status: SupplierStatus) -> List[BackupSupplier]:
        """Get suppliers filtered by status."""
        return [s for s in self.backup_suppliers if s.status == status]
