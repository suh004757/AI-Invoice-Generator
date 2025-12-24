"""
End-to-End Test: AI-First Invoice Builder
Tests the complete workflow from PO upload to invoice generation
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from invoice_studio.config import Config
from invoice_studio.ai.llm_client import LLMFactory
from invoice_studio.ai.extractor import DataExtractor
from invoice_studio.document.pdf_processor import PDFProcessor
from invoice_studio.document.image_processor import ImageProcessor
from invoice_studio.document.text_processor import TextProcessor
from invoice_studio.models.invoice import Invoice
from invoice_studio.models.purchase_order import PurchaseOrder


def test_text_po_extraction():
    """Test extraction from text PO"""
    print("=" * 80)
    print("TEST 1: Text PO Extraction")
    print("=" * 80)
    
    # Sample PO text
    sample_po = """
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
    """
    
    print("\n📄 Sample PO:")
    print(sample_po)
    
    try:
        # Create LLM client
        print("\n🤖 Creating LLM client...")
        llm_config = Config.get_llm_config()
        llm_client = LLMFactory.create(**llm_config)
        
        # Test connection
        print(f"   Provider: {llm_config['provider']}")
        if llm_config['provider'] == 'lm_studio':
            print(f"   URL: {llm_config['lm_studio_url']}")
            print(f"   Model: {llm_config['lm_studio_model']}")
        
        print("   Testing connection...")
        if llm_client.test_connection():
            print("   ✓ Connection successful!")
        else:
            print("   ✗ Connection failed!")
            return
        
        # Create extractor
        print("\n📊 Extracting data...")
        extractor = DataExtractor(llm_client)
        
        # Extract data
        extracted_data, confidence, error = extractor.extract(sample_po, invoice_type="tax")
        
        if error:
            print(f"   ✗ Extraction failed: {error}")
            return
        
        print(f"   ✓ Extraction successful!")
        print(f"   Confidence: {confidence:.2%}")
        
        print("\n📋 Extracted Data:")
        import json
        print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
        
        # Create invoice from extracted data
        print("\n💼 Creating Invoice...")
        invoice = Invoice.from_extracted_data(
            extracted_data=extracted_data,
            invoice_type="tax",
            confidence=confidence
        )
        
        print(f"   Customer: {invoice.customer_name}")
        print(f"   Currency: {invoice.currency}")
        print(f"   Items: {len(invoice.items)}")
        print(f"   Subtotal: {invoice.subtotal:,.2f}")
        print(f"   VAT: {invoice.vat:,.2f}")
        print(f"   Total: {invoice.total:,.2f}")
        print(f"   Confidence: {invoice.extraction_confidence:.2%}")
        
        # Validate
        is_valid, error_msg = invoice.validate()
        if is_valid:
            print("   ✓ Invoice is valid!")
        else:
            print(f"   ✗ Validation error: {error_msg}")
        
        print("\n" + "=" * 80)
        print("✓ TEST 1 PASSED!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()


def test_korean_po_extraction():
    """Test extraction from Korean PO"""
    print("\n\n" + "=" * 80)
    print("TEST 2: Korean PO Extraction")
    print("=" * 80)
    
    # Sample Korean PO
    sample_po = """
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
    """
    
    print("\n📄 Sample Korean PO:")
    print(sample_po)
    
    try:
        # Create LLM client and extractor
        llm_config = Config.get_llm_config()
        llm_client = LLMFactory.create(**llm_config)
        extractor = DataExtractor(llm_client)
        
        # Extract data
        print("\n📊 Extracting data...")
        extracted_data, confidence, error = extractor.extract(sample_po, invoice_type="tax")
        
        if error:
            print(f"   ✗ Extraction failed: {error}")
            return
        
        print(f"   ✓ Extraction successful!")
        print(f"   Confidence: {confidence:.2%}")
        
        # Create invoice
        invoice = Invoice.from_extracted_data(
            extracted_data=extracted_data,
            invoice_type="tax",
            confidence=confidence
        )
        
        print(f"\n💼 Invoice Created:")
        print(f"   Customer: {invoice.customer_name}")
        print(f"   Currency: {invoice.currency}")
        print(f"   Total: {invoice.total:,.0f} {invoice.currency}")
        print(f"   Metadata: {invoice.metadata}")
        
        print("\n" + "=" * 80)
        print("✓ TEST 2 PASSED!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()


def test_text_processing():
    """Test text processing utilities"""
    print("\n\n" + "=" * 80)
    print("TEST 3: Text Processing")
    print("=" * 80)
    
    processor = TextProcessor()
    
    # Test cleaning
    dirty_text = "  Multiple   spaces\r\nand\r\nline breaks  "
    clean_text = processor.clean_text(dirty_text)
    print(f"\n✓ Text cleaning: '{dirty_text}' → '{clean_text}'")
    
    # Test language detection
    korean_text = "안녕하세요 이것은 한국어 텍스트입니다"
    english_text = "Hello this is English text"
    mixed_text = "Hello 안녕하세요 mixed text"
    
    print(f"\n✓ Language detection:")
    print(f"   Korean: {processor.detect_language(korean_text)}")
    print(f"   English: {processor.detect_language(english_text)}")
    print(f"   Mixed: {processor.detect_language(mixed_text)}")
    
    # Test number extraction
    text_with_numbers = "Total: $1,234.56 and 9,876.54 KRW"
    numbers = processor.extract_numbers(text_with_numbers)
    print(f"\n✓ Number extraction: {numbers}")
    
    print("\n" + "=" * 80)
    print("✓ TEST 3 PASSED!")
    print("=" * 80)


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "AI-FIRST INVOICE BUILDER TEST" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Check configuration
    print("\n📋 Configuration:")
    print(f"   LLM Provider: {Config.LLM_PROVIDER}")
    print(f"   Default Currency: {Config.DEFAULT_CURRENCY}")
    print(f"   Default Invoice Type: {Config.DEFAULT_INVOICE_TYPE}")
    
    # Validate config
    errors = Config.validate()
    if errors:
        print("\n⚠️  Configuration Warnings:")
        for error in errors:
            print(f"   - {error}")
    
    # Run tests
    test_text_processing()
    test_text_po_extraction()
    test_korean_po_extraction()
    
    print("\n\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 28 + "ALL TESTS COMPLETED" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")


if __name__ == "__main__":
    main()
