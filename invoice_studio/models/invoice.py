"""
Invoice business logic model
"""
from datetime import datetime
from typing import List, Dict, Optional
import json
from ..utils.validators import (
    validate_amount,
    validate_date,
    validate_invoice_number,
    validate_customer_name,
    validate_item_quantity
)


class Invoice:
    """Invoice business logic"""
    
    def __init__(self, invoice_type: str = "Tax", currency: str = "KRW"):
        """
        Initialize invoice
        
        Args:
            invoice_type: "Tax" or "Normal"
            currency: Currency code (default: KRW)
        """
        self.id = None
        self.invoice_no = None
        self.date = datetime.now()
        self.type = invoice_type
        self.customer_id = None
        self.customer_name = ""
        self.currency = currency
        self.items = []
        self.subtotal = 0.0
        self.vat = 0.0
        self.total = 0.0
        self.po_id = None
        self.extraction_confidence = None
        self.metadata = {}
        self.file_path = None
        self.notes = ""
    
    @property
    def vat_rate(self) -> float:
        """Get VAT rate based on invoice type"""
        return 0.10 if self.type == "Tax" else 0.0
    
    def add_item(self, description: str, quantity: float, unit_price: float, 
                 item_id: int = None):
        """
        Add item to invoice
        
        Args:
            description: Item description
            quantity: Quantity
            unit_price: Unit price
            item_id: Optional item master ID
        """
        # Validate
        is_valid, error = validate_item_quantity(quantity)
        if not is_valid:
            raise ValueError(error)
        
        is_valid, error = validate_amount(unit_price)
        if not is_valid:
            raise ValueError(error)
        
        amount = quantity * unit_price
        
        self.items.append({
            'item_id': item_id,
            'description': description,
            'quantity': quantity,
            'unit_price': unit_price,
            'amount': amount
        })
    
    def remove_item(self, index: int):
        """Remove item by index"""
        if 0 <= index < len(self.items):
            self.items.pop(index)
    
    def clear_items(self):
        """Clear all items"""
        self.items = []
    
    def calculate_totals(self):
        """Calculate subtotal, VAT, and total"""
        # Calculate subtotal
        self.subtotal = sum(item['amount'] for item in self.items)
        
        # Calculate VAT
        self.vat = self.calculate_vat(self.subtotal)
        
        # Calculate total
        self.total = self.subtotal + self.vat
    
    def calculate_vat(self, amount: float) -> float:
        """
        Calculate VAT for given amount
        
        Args:
            amount: Amount to calculate VAT on
        
        Returns:
            VAT amount
        """
        return round(amount * self.vat_rate, 2)
    
    def calculate_from_total(self, total_amount: float):
        """
        Calculate subtotal and VAT from total amount
        Useful when user provides total including VAT
        
        Args:
            total_amount: Total amount including VAT
        """
        if self.type == "Tax":
            # Total = Subtotal * 1.1
            # Subtotal = Total / 1.1
            self.subtotal = round(total_amount / 1.1, 2)
            self.vat = round(total_amount - self.subtotal, 2)
        else:
            self.subtotal = total_amount
            self.vat = 0.0
        
        self.total = total_amount
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate invoice data
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate invoice number
        if self.invoice_no:
            is_valid, error = validate_invoice_number(self.invoice_no)
            if not is_valid:
                return False, error
        
        # Validate date
        is_valid, error = validate_date(self.date)
        if not is_valid:
            return False, error
        
        # Validate customer
        is_valid, error = validate_customer_name(self.customer_name)
        if not is_valid:
            return False, error
        
        # Validate has items
        if not self.items:
            return False, "Invoice must have at least one item"
        
        # Validate amounts
        is_valid, error = validate_amount(self.total)
        if not is_valid:
            return False, error
        
        return True, None
    
    def to_dict(self) -> Dict:
        """
        Convert invoice to dictionary for database storage
        
        Returns:
            Dictionary with invoice data
        """
        return {
            'id': self.id,
            'invoice_no': self.invoice_no,
            'date': self.date.strftime('%Y-%m-%d') if isinstance(self.date, datetime) else self.date,
            'type': self.type,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'currency': self.currency,
            'subtotal': self.subtotal,
            'vat': self.vat,
            'total': self.total,
            'po_id': self.po_id,
            'extraction_confidence': self.extraction_confidence,
            'metadata': json.dumps(self.metadata) if self.metadata else None,
            'file_path': self.file_path,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict, items: List[Dict] = None) -> 'Invoice':
        """
        Create invoice from dictionary
        
        Args:
            data: Invoice data dictionary
            items: Optional items list
        
        Returns:
            Invoice instance
        """
        invoice = cls(
            invoice_type=data.get('type', 'Tax'),
            currency=data.get('currency', 'KRW')
        )
        
        invoice.id = data.get('id')
        invoice.invoice_no = data.get('invoice_no')
        
        # Parse date
        date_str = data.get('date')
        if isinstance(date_str, str):
            invoice.date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        elif isinstance(date_str, datetime):
            invoice.date = date_str
        
        invoice.customer_id = data.get('customer_id')
        invoice.customer_name = data.get('customer_name', '')
        invoice.subtotal = data.get('subtotal', 0.0)
        invoice.vat = data.get('vat', 0.0)
        invoice.total = data.get('total', 0.0)
        invoice.po_id = data.get('po_id')
        invoice.extraction_confidence = data.get('extraction_confidence')
        
        # Parse metadata JSON
        metadata_str = data.get('metadata')
        if metadata_str:
            import json
            invoice.metadata = json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
        
        invoice.file_path = data.get('file_path')
        invoice.notes = data.get('notes', '')
        
        # Add items if provided
        if items:
            invoice.items = items
        
        return invoice
    
    @classmethod
    def from_extracted_data(cls, extracted_data: Dict, invoice_type: str = "tax", 
                           po_id: int = None, confidence: float = None) -> 'Invoice':
        """
        Create invoice from AI-extracted PO data
        
        Args:
            extracted_data: Data extracted by AI from PO
            invoice_type: 'tax' or 'normal'
            po_id: Purchase order ID
            confidence: Extraction confidence score
        
        Returns:
            Invoice instance
        """
        # Normalize invoice type
        invoice_type = "Tax" if invoice_type.lower() == "tax" else "Normal"
        
        # Get currency
        currency = extracted_data.get("currency", "KRW")
        
        # Create invoice
        invoice = cls(invoice_type=invoice_type, currency=currency)
        
        # Set basic info
        invoice.customer_name = extracted_data.get("customer_name", "")
        invoice.po_id = po_id
        invoice.extraction_confidence = confidence
        
        # Set date if provided
        date_str = extracted_data.get("date")
        if date_str:
            try:
                invoice.date = datetime.fromisoformat(date_str)
            except:
                pass  # Keep default date
        
        # Add items
        items = extracted_data.get("items", [])
        for item in items:
            try:
                invoice.add_item(
                    description=item.get("description", ""),
                    quantity=item.get("quantity", 0),
                    unit_price=item.get("unit_price", 0)
                )
            except ValueError:
                # Skip invalid items
                continue
        
        # Set amounts (use extracted values or calculate)
        if "subtotal" in extracted_data:
            invoice.subtotal = extracted_data["subtotal"]
        else:
            invoice.calculate_totals()
        
        if "vat" in extracted_data:
            invoice.vat = extracted_data["vat"]
        else:
            invoice.calculate_totals()
        
        if "total" in extracted_data:
            invoice.total = extracted_data["total"]
        else:
            invoice.calculate_totals()
        
        # Store additional metadata
        metadata = {}
        optional_fields = ["po_number", "customer_address", "customer_contact", 
                          "payment_terms", "delivery_date", "notes"]
        for field in optional_fields:
            if field in extracted_data:
                metadata[field] = extracted_data[field]
        
        invoice.metadata = metadata
        
        # Set notes if provided
        if "notes" in extracted_data:
            invoice.notes = extracted_data["notes"]
        
        return invoice

    
    def duplicate(self, new_invoice_no: str = None, new_date: datetime = None) -> 'Invoice':
        """
        Create a duplicate of this invoice
        
        Args:
            new_invoice_no: New invoice number (optional)
            new_date: New date (default: today)
        
        Returns:
            New Invoice instance
        """
        new_invoice = Invoice(invoice_type=self.type, currency=self.currency)
        new_invoice.invoice_no = new_invoice_no
        new_invoice.date = new_date or datetime.now()
        new_invoice.customer_id = self.customer_id
        new_invoice.customer_name = self.customer_name
        new_invoice.items = [item.copy() for item in self.items]
        new_invoice.calculate_totals()
        
        return new_invoice
    
    def __repr__(self):
        return f"Invoice({self.invoice_no}, {self.type}, {self.customer_name}, {self.total})"
