"""
Validation utilities for Invoice Command Studio
"""
from datetime import datetime
from typing import Optional, Tuple


def validate_amount(amount: float) -> Tuple[bool, Optional[str]]:
    """
    Validate amount value
    
    Args:
        amount: Amount to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if amount < 0:
        return False, "Amount cannot be negative"
    
    if amount > 999999999999:  # 1 trillion limit
        return False, "Amount exceeds maximum allowed value"
    
    return True, None


def validate_date(date: datetime) -> Tuple[bool, Optional[str]]:
    """
    Validate date value
    
    Args:
        date: Date to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if date is not too far in the past
    min_date = datetime(2000, 1, 1)
    if date < min_date:
        return False, "Date cannot be before year 2000"
    
    # Check if date is not too far in the future
    max_date = datetime(2100, 12, 31)
    if date > max_date:
        return False, "Date cannot be after year 2100"
    
    return True, None


def validate_invoice_number(invoice_no: str) -> Tuple[bool, Optional[str]]:
    """
    Validate invoice number format
    
    Args:
        invoice_no: Invoice number to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not invoice_no:
        return False, "Invoice number cannot be empty"
    
    if len(invoice_no) > 50:
        return False, "Invoice number too long (max 50 characters)"
    
    return True, None


def validate_customer_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate customer name
    
    Args:
        name: Customer name to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Customer name cannot be empty"
    
    if len(name) > 200:
        return False, "Customer name too long (max 200 characters)"
    
    return True, None


def validate_item_quantity(quantity: float) -> Tuple[bool, Optional[str]]:
    """
    Validate item quantity
    
    Args:
        quantity: Quantity to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if quantity <= 0:
        return False, "Quantity must be greater than 0"
    
    if quantity > 1000000:
        return False, "Quantity exceeds maximum allowed value"
    
    return True, None
