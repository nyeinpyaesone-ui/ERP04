"""Township service for Myanmar location data."""
import json
import os
from typing import Dict, List, Optional
from backend.config import settings


class TownshipService:
    """Service for managing Myanmar township data."""
    
    # Default townships (sample - can be extended)
    DEFAULT_TOWNSHIPS = [
        {"name": "Yangon", "state_region": "Yangon Region", "district": "Yangon"},
        {"name": "Mandalay", "state_region": "Mandalay Region", "district": "Mandalay"},
        {"name": "Naypyidaw", "state_region": "Naypyidaw Union Territory", "district": "Naypyidaw"},
        {"name": "Pathein", "state_region": "Ayeyarwady Region", "district": "Pathein"},
        {"name": "Mawlamyine", "state_region": "Mon State", "district": "Mawlamyine"},
        {"name": "Taunggyi", "state_region": "Shan State", "district": "Taunggyi"},
        {"name": "Myitkyina", "state_region": "Kachin State", "district": "Myitkyina"},
        {"name": "Sittwe", "state_region": "Rakhine State", "district": "Sittwe"},
        {"name": "Hpa-An", "state_region": "Kayin State", "district": "Hpa-An"},
        {"name": "Loikaw", "state_region": "Kayah State", "district": "Loikaw"},
        {"name": "Hakha", "state_region": "Chin State", "district": "Hakha"},
        {"name": "Dawei", "state_region": "Tanintharyi Region", "district": "Dawei"},
    ]
    
    def __init__(self):
        self.townships = self._load_townships()
    
    def _load_townships(self) -> List[Dict]:
        """Load township data from JSON file or use defaults."""
        if os.path.exists(settings.TOWNSHIPS_FILE):
            try:
                with open(settings.TOWNSHIPS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load townships file: {e}. Using defaults.")
        return self.DEFAULT_TOWNSHIPS
    
    def get_all_townships(self) -> List[Dict]:
        """Get all townships."""
        return self.townships
    
    def get_township_by_name(self, name: str) -> Optional[Dict]:
        """Get township by name (case-insensitive)."""
        name_lower = name.lower()
        for township in self.townships:
            if township["name"].lower() == name_lower:
                return township
        return None
    
    def get_townships_by_state(self, state_region: str) -> List[Dict]:
        """Get all townships in a specific state/region."""
        state_lower = state_region.lower()
        return [
            t for t in self.townships 
            if t.get("state_region", "").lower() == state_lower
        ]
    
    def get_townships_by_district(self, district: str) -> List[Dict]:
        """Get all townships in a specific district."""
        district_lower = district.lower()
        return [
            t for t in self.townships 
            if t.get("district", "").lower() == district_lower
        ]
    
    def search_townships(self, query: str) -> List[Dict]:
        """Search townships by name."""
        query_lower = query.lower()
        return [
            t for t in self.townships 
            if query_lower in t["name"].lower()
        ]
    
    def validate_township(self, name: str) -> bool:
        """Check if a township exists."""
        return self.get_township_by_name(name) is not None
