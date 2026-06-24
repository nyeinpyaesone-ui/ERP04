"""Tax calculation service for Myanmar tax system."""
import json
import os
from typing import Dict, Optional, List
from backend.config import settings


class TaxService:
    """Service for calculating various Myanmar taxes."""
    
    # Default tax rates (can be overridden by JSON file)
    DEFAULT_TAX_RATES = {
        "commercial": {"rate": 0.02, "description": "Commercial Tax"},
        "income_individual": {"rate": 0.05, "description": "Individual Income Tax (Basic Rate)"},
        "income_corporate": {"rate": 0.25, "description": "Corporate Income Tax"},
        "customs": {"rate": 0.05, "description": "Customs Duty (Average)"},
        "specific_goods": {"rate": 0.05, "description": "Specific Goods Tax"},
        "property": {"rate": 0.01, "description": "Property Tax"},
    }
    
    def __init__(self):
        self.tax_rates = self._load_tax_rates()
    
    def _load_tax_rates(self) -> Dict[str, Dict]:
        """Load tax rates from JSON file or use defaults."""
        if os.path.exists(settings.TAX_RATES_FILE):
            try:
                with open(settings.TAX_RATES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load tax rates file: {e}. Using defaults.")
        return self.DEFAULT_TAX_RATES
    
    def get_tax_rate(self, tax_type: str) -> Optional[Dict]:
        """Get tax rate information for a specific tax type."""
        return self.tax_rates.get(tax_type)
    
    def calculate_tax(
        self, 
        amount: float, 
        tax_type: str, 
        township: Optional[str] = None
    ) -> Dict:
        """
        Calculate tax for a given amount and tax type.
        
        Args:
            amount: The amount to calculate tax on
            tax_type: Type of tax (commercial, income_individual, etc.)
            township: Optional township for local tax variations
            
        Returns:
            Dictionary with tax calculation details
        """
        tax_info = self.get_tax_rate(tax_type)
        
        if not tax_info:
            raise ValueError(f"Unknown tax type: {tax_type}. Available types: {list(self.tax_rates.keys())}")
        
        rate = tax_info["rate"]
        tax_amount = amount * rate
        total_amount = amount + tax_amount
        
        return {
            "original_amount": amount,
            "tax_type": tax_type,
            "tax_rate": rate,
            "tax_amount": tax_amount,
            "total_amount": total_amount,
            "township": township,
            "description": tax_info.get("description", "")
        }
    
    def list_available_taxes(self) -> List[Dict]:
        """List all available tax types with their rates."""
        return [
            {
                "tax_type": key,
                "rate": value["rate"],
                "description": value.get("description", "")
            }
            for key, value in self.tax_rates.items()
        ]
