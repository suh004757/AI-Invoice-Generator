"""
Cell mapping configuration manager
"""
import json
from pathlib import Path
from typing import Dict


class MappingConfig:
    """Manage template cell mapping configuration"""
    
    DEFAULT_MAPPING = {
        "invoice_no": "B3",
        "date": "B4",
        "type": "B5",
        "customer_name": "B8",
        "customer_address": "B9",
        "items_start_row": 12,
        "items_columns": {
            "no": "A",
            "description": "B",
            "quantity": "C",
            "unit_price": "D",
            "amount": "E"
        },
        "subtotal": "E21",
        "vat": "E22",
        "total": "E23"
    }
    
    def __init__(self, config_path: str = None):
        """
        Initialize mapping config
        
        Args:
            config_path: Path to mapping JSON file
        """
        if config_path is None:
            # Default to data/template_mapping.json
            data_dir = Path(__file__).parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            config_path = str(data_dir / "template_mapping.json")
        
        self.config_path = config_path
        self.mapping = self.load()
    
    def load(self) -> Dict:
        """
        Load mapping from file
        
        Returns:
            Mapping dictionary
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default mapping file
            self.save(self.DEFAULT_MAPPING)
            return self.DEFAULT_MAPPING.copy()
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in {self.config_path}, using defaults")
            return self.DEFAULT_MAPPING.copy()
    
    def save(self, mapping: Dict = None):
        """
        Save mapping to file
        
        Args:
            mapping: Mapping dictionary (default: current mapping)
        """
        if mapping is None:
            mapping = self.mapping
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    def get(self, key: str, default=None):
        """Get mapping value by key"""
        return self.mapping.get(key, default)
    
    def set(self, key: str, value):
        """Set mapping value"""
        self.mapping[key] = value
    
    def validate_cell_reference(self, cell_ref: str) -> bool:
        """
        Validate Excel cell reference format
        
        Args:
            cell_ref: Cell reference (e.g., "B3", "AA10")
        
        Returns:
            True if valid
        """
        import re
        pattern = r'^[A-Z]+\d+$'
        return bool(re.match(pattern, cell_ref.upper()))
