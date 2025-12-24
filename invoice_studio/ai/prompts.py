"""
Prompt templates for PO data extraction
Uses few-shot learning for better accuracy
"""

# JSON schema for invoice data
INVOICE_JSON_SCHEMA = """{
  "po_number": "string",
  "date": "string (YYYY-MM-DD)",
  "customer_name": "string",
  "customer_address": "string (optional)",
  "customer_contact": "string (optional)",
  "items": [
    {
      "description": "string",
      "quantity": number,
      "unit_price": number,
      "amount": number
    }
  ],
  "subtotal": number,
  "vat": number,
  "total": number,
  "currency": "string (KRW, USD, EUR, JPY, etc.)",
  "payment_terms": "string (optional)",
  "delivery_date": "string (YYYY-MM-DD, optional)",
  "notes": "string (optional)"
}"""


# Few-shot examples for better extraction
FEW_SHOT_EXAMPLES = """
=== Example 1: English PO ===
Input:
PURCHASE ORDER
PO Number: PO-2025-001
Date: 2025-12-10

Supplier: Tech Solutions Inc.
Customer: ABC Corporation
Address: 123 Main Street, Seoul, Korea

Items:
1. Laptop Computer - Qty: 5, Unit Price: $1,200.00
2. Wireless Mouse - Qty: 10, Unit Price: $25.00

Subtotal: $6,250.00
VAT (10%): $625.00
Total: $6,875.00

Payment Terms: Net 30
Delivery Date: 2025-12-20

Output:
{
  "po_number": "PO-2025-001",
  "date": "2025-12-10",
  "customer_name": "ABC Corporation",
  "customer_address": "123 Main Street, Seoul, Korea",
  "items": [
    {
      "description": "Laptop Computer",
      "quantity": 5,
      "unit_price": 1200.00,
      "amount": 6000.00
    },
    {
      "description": "Wireless Mouse",
      "quantity": 10,
      "unit_price": 25.00,
      "amount": 250.00
    }
  ],
  "subtotal": 6250.00,
  "vat": 625.00,
  "total": 6875.00,
  "currency": "USD",
  "payment_terms": "Net 30",
  "delivery_date": "2025-12-20"
}

=== Example 2: Korean PO ===
Input:
발주서
발주번호: 2025-002
날짜: 2025-12-11

공급자: 테크솔루션
고객: XYZ 주식회사
주소: 서울시 강남구 테헤란로 123

품목:
1. 노트북 컴퓨터 - 수량: 3대, 단가: 1,500,000원
2. 모니터 - 수량: 3대, 단가: 300,000원

소계: 5,400,000원
부가세 (10%): 540,000원
합계: 5,940,000원

결제조건: 30일
납품일: 2025-12-25

Output:
{
  "po_number": "2025-002",
  "date": "2025-12-11",
  "customer_name": "XYZ 주식회사",
  "customer_address": "서울시 강남구 테헤란로 123",
  "items": [
    {
      "description": "노트북 컴퓨터",
      "quantity": 3,
      "unit_price": 1500000,
      "amount": 4500000
    },
    {
      "description": "모니터",
      "quantity": 3,
      "unit_price": 300000,
      "amount": 900000
    }
  ],
  "subtotal": 5400000,
  "vat": 540000,
  "total": 5940000,
  "currency": "KRW",
  "payment_terms": "30일",
  "delivery_date": "2025-12-25"
}
"""


def create_extraction_prompt(po_text: str, invoice_type: str = "tax") -> str:
    """
    Create prompt for extracting invoice data from PO
    
    Args:
        po_text: Raw text from PO document
        invoice_type: 'tax' or 'normal'
    
    Returns:
        str: Complete prompt for LLM
    """
    
    system_prompt = """You are an expert invoice data extraction assistant.
Your task is to extract structured data from Purchase Order (PO) documents and return valid JSON only.

Key rules:
1. Extract ALL relevant information from the PO
2. Calculate amounts correctly (quantity × unit_price = amount)
3. For Tax invoices: VAT should be 10% of subtotal, total = subtotal + VAT
4. For Normal invoices: VAT = 0, total = subtotal
5. Detect currency from the document (look for $, ₩, €, ¥ symbols or KRW, USD, EUR, JPY text)
6. Return ONLY valid JSON, no other text or explanation
7. If a field is not found, use null or omit it
8. Numbers should be numeric values, not strings
9. Dates should be in YYYY-MM-DD format"""
    
    vat_instruction = ""
    if invoice_type.lower() == "tax":
        vat_instruction = "\nNOTE: This is a TAX invoice. VAT must be 10% of subtotal."
    else:
        vat_instruction = "\nNOTE: This is a NORMAL invoice. VAT must be 0."
    
    user_prompt = f"""Extract invoice data from the following Purchase Order and return as JSON.

Required JSON format:
{INVOICE_JSON_SCHEMA}

Here are examples of correct extractions:
{FEW_SHOT_EXAMPLES}

{vat_instruction}

=== Now extract from this PO ===
Input:
{po_text}

Output (JSON only, no other text):
"""
    
    return system_prompt, user_prompt


def create_validation_prompt(extracted_data: dict, po_text: str) -> str:
    """
    Create prompt for validating extracted data
    
    Args:
        extracted_data: Previously extracted data
        po_text: Original PO text
    
    Returns:
        tuple: (system_prompt, user_prompt)
    """
    
    system_prompt = """You are a data validation assistant.
Review the extracted invoice data and verify it matches the original PO document.
Return a JSON object with validation results."""
    
    user_prompt = f"""Validate this extracted data against the original PO:

Original PO:
{po_text}

Extracted Data:
{extracted_data}

Check:
1. Are all items correctly extracted?
2. Are quantities and prices accurate?
3. Are calculations correct (amounts, subtotal, VAT, total)?
4. Is the customer information accurate?
5. Are dates in correct format?

Return JSON:
{{
  "is_valid": true/false,
  "confidence_score": 0.0-1.0,
  "errors": ["list of errors if any"],
  "warnings": ["list of warnings if any"],
  "suggestions": ["list of suggestions for improvement"]
}}
"""
    
    return system_prompt, user_prompt
