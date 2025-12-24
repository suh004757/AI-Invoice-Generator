"""
Formatting utilities for Invoice Command Studio
"""
from datetime import datetime
from typing import Union


def format_currency(amount: Union[int, float], currency: str = "KRW") -> str:
    """
    Format number as currency string
    
    Args:
        amount: Numeric amount
        currency: Currency code (default: KRW)
    
    Returns:
        Formatted currency string (e.g., "3,000,000")
    """
    if currency == "KRW":
        return f"{int(amount):,}"
    elif currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def format_date(date: Union[datetime, str], format_str: str = "%Y-%m-%d") -> str:
    """
    Format date as string
    
    Args:
        date: datetime object or ISO string
        format_str: Output format (default: YYYY-MM-DD)
    
    Returns:
        Formatted date string
    """
    if isinstance(date, str):
        # Parse ISO format string
        date = datetime.fromisoformat(date.replace('Z', '+00:00'))
    
    return date.strftime(format_str)


def format_filename(invoice_no: str, customer: str, invoice_type: str, 
                    date: datetime = None) -> str:
    """
    Generate filename for invoice
    
    Args:
        invoice_no: Invoice number
        customer: Customer name
        invoice_type: "Tax" or "Normal"
        date: Invoice date (default: today)
    
    Returns:
        Formatted filename (e.g., "20251211_2025-001_ABC Corp_Tax.xlsx")
    """
    if date is None:
        date = datetime.now()
    
    # Clean customer name for filename
    clean_customer = "".join(c for c in customer if c.isalnum() or c in (' ', '-', '_'))
    clean_customer = clean_customer.strip()[:30]  # Limit length
    
    date_str = date.strftime("%Y%m%d")
    return f"{date_str}_{invoice_no}_{clean_customer}_{invoice_type}.xlsx"


def parse_amount(amount_str: str) -> float:
    """
    Parse amount string to float, handling Korean/English formats
    
    Args:
        amount_str: Amount as string (e.g., "3,000,000" or "3000000")
    
    Returns:
        Float value
    """
    # Remove commas and whitespace
    clean_str = amount_str.replace(',', '').replace(' ', '')
    
    # Handle Korean currency units (만원 = 10,000)
    if '만' in clean_str:
        clean_str = clean_str.replace('만원', '').replace('만', '')
        return float(clean_str) * 10000
    
    return float(clean_str)
