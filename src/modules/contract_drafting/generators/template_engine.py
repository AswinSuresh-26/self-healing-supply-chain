"""
Contract Template Engine

Generates structured contract templates for emergency procurement.
"""

from typing import Dict, Any
from datetime import datetime


class ContractTemplateEngine:
    """
    Generates contract section templates with placeholder filling.
    """
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load standard contract section templates."""
        return {
            "header": self._get_header_template(),
            "parties": self._get_parties_template(),
            "scope": self._get_scope_template(),
            "pricing": self._get_pricing_template(),
            "delivery": self._get_delivery_template(),
            "quality": self._get_quality_template(),
            "termination": self._get_termination_template(),
            "signature": self._get_signature_template()
        }
    
    def _get_header_template(self) -> str:
        return """
EMERGENCY SUPPLY AGREEMENT
Contract Number: {contract_id}
Effective Date: {effective_date}

This Emergency Supply Agreement ("Agreement") is entered into as of 
the Effective Date by and between the parties identified below.
"""
    
    def _get_parties_template(self) -> str:
        return """
BUYER: {buyer_name}
Address: {buyer_address}

SUPPLIER: {supplier_name}
Address: {supplier_address}
Country: {supplier_country}
"""
    
    def _get_scope_template(self) -> str:
        return """
This Agreement covers the emergency procurement of the following 
items/services due to supply chain disruption:

Categories: {categories}
Recovery Plan Reference: {recovery_plan_id}

The Supplier agrees to provide the items listed in Schedule A 
attached hereto.
"""
    
    def _get_pricing_template(self) -> str:
        return """
TOTAL CONTRACT VALUE: ${total_value:,.2f}

Payment Terms:
- {payment_terms}
- Net {payment_days} days from invoice date
- Emergency orders may be subject to {premium_pct}% expedite premium

Currency: {currency}
"""
    
    def _get_delivery_template(self) -> str:
        return """
DELIVERY REQUIREMENTS:

Lead Time: {lead_time_days} days from order confirmation
Delivery Location: {delivery_location}
Shipping Terms: {shipping_terms}

Time is of the essence for all deliveries under this Agreement.
"""
    
    def _get_quality_template(self) -> str:
        return """
QUALITY REQUIREMENTS:

- All items must meet specifications in Schedule B
- Supplier certifications required: {certifications}
- Quality inspection: {inspection_terms}
- Defect tolerance: {defect_tolerance}%
"""
    
    def _get_termination_template(self) -> str:
        return """
TERMINATION:

This Agreement shall automatically expire {duration_days} days 
from the Effective Date unless extended in writing.

Either party may terminate with {notice_days} days written notice.
"""
    
    def _get_signature_template(self) -> str:
        return """
IN WITNESS WHEREOF, the parties have executed this Agreement.

BUYER:                          SUPPLIER:
_____________________          _____________________
{buyer_signatory}              {supplier_signatory}
Date: ______________           Date: ______________
"""
    
    def render_section(self, section: str, context: Dict[str, Any]) -> str:
        """Render a section with context values."""
        template = self.templates.get(section, "")
        try:
            return template.format(**context)
        except KeyError as e:
            # Fill missing values with placeholder
            return template.format_map(DefaultDict(f"[{e}]", context))


class DefaultDict(dict):
    """Dict that returns default for missing keys."""
    def __init__(self, default, *args, **kwargs):
        self.default = default
        super().__init__(*args, **kwargs)
    
    def __missing__(self, key):
        return f"[{key}]"
