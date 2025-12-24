# AI Invoice Builder

**"PO 던지면 인보이스 나오는 상자 / This is personal Project So may need to correct some paths before use "** - Throw in a PO, get an invoice out!

AI-powered invoice generation system that automatically extracts data from Purchase Orders and creates invoices.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure LLM Provider

Copy `.env.example` to `.env` and configure your LLM provider:

```bash
# For LM Studio (Local, Free)
LLM_PROVIDER=lm_studio
LM_STUDIO_URL=http://localhost:1234
LM_STUDIO_MODEL=llama-3.3-70b-instruct

# OR for Claude API
LLM_PROVIDER=claude
CLAUDE_API_KEY=your_api_key_here

# OR for OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
```

### 3. Start LM Studio (if using local LLM)

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Download a model (recommended: Llama 3.3 70B or Qwen 2.5 7B)
3. Go to "Server" tab and click "Start Server"

### 4. Test the System

```bash
python test_ai_extraction.py
```

## 📋 Features

### ✨ AI-First Workflow

1. **Upload PO** - PDF, Image, or Text
2. **AI Analyzes** - Automatically extracts invoice data
3. **Review & Edit** - Quick verification of extracted data
4. **Generate** - Create Excel/PDF invoice

### 🤖 Multi-Provider LLM Support

- **Claude API** - Best accuracy, cloud-based
- **OpenAI API** - GPT-4 powered, cloud-based
- **LM Studio** - Local, free, privacy-focused

### 📄 Document Processing

- **PDF**: Text extraction + OCR for scanned documents
- **Images**: PNG, JPG, JPEG with OCR
- **Text**: Email body, copy-paste support

### 💡 Smart Features

- **Confidence Scoring** - Per-field confidence indicators
- **Flexible Schema** - JSON metadata for varying PO fields
- **VAT Calculation** - Automatic 10% VAT for Tax invoices
- **Bilingual** - Korean + English support

## 🏗️ Architecture

```
invoice_studio/
├── ai/                    # AI/LLM Integration
│   ├── llm_client.py     # Claude, OpenAI, LM Studio clients
│   ├── prompts.py        # Few-shot prompt templates
│   └── extractor.py      # Data extraction orchestrator
├── document/              # Document Processing
│   ├── pdf_processor.py  # PDF text/image extraction
│   ├── image_processor.py # OCR for images
│   └── text_processor.py # Text cleaning & normalization
├── models/
│   ├── invoice.py        # Invoice model with from_extracted_data()
│   └── purchase_order.py # PO model
├── database/
│   └── models.py         # SQLite schema (invoices, POs, extraction_logs)
└── config.py             # Configuration management
```

## 💻 Usage Example

```python
from invoice_studio.config import Config
from invoice_studio.ai.llm_client import LLMFactory
from invoice_studio.ai.extractor import DataExtractor
from invoice_studio.models.invoice import Invoice

# Create LLM client
llm_config = Config.get_llm_config()
llm_client = LLMFactory.create(**llm_config)

# Extract data from PO
extractor = DataExtractor(llm_client)
extracted_data, confidence, error = extractor.extract(po_text, invoice_type="tax")

# Create invoice
invoice = Invoice.from_extracted_data(
    extracted_data=extracted_data,
    invoice_type="tax",
    confidence=confidence
)

# Validate and use
is_valid, error_msg = invoice.validate()
if is_valid:
    print(f"Invoice created: {invoice.customer_name}, Total: {invoice.total}")
```

## 🔧 Configuration

### Environment Variables (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM provider (claude/openai/lm_studio) | lm_studio |
| `CLAUDE_API_KEY` | Anthropic Claude API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `LM_STUDIO_URL` | LM Studio server URL | http://localhost:1234 |
| `LM_STUDIO_MODEL` | Model name in LM Studio | llama-3.3-70b-instruct |
| `DEFAULT_CURRENCY` | Default currency code | KRW |
| `DEFAULT_INVOICE_TYPE` | Default invoice type (tax/normal) | tax |

## 📊 Database Schema

### Tables

- **invoices** - Invoice data with PO link and extraction confidence
- **purchase_orders** - Uploaded PO documents
- **extraction_logs** - AI extraction history and debugging
- **customers** - Customer master data
- **items** - Item master data
- **invoice_items** - Invoice line items

### New Fields in Invoices

- `po_id` - Link to source PO
- `extraction_confidence` - AI confidence score (0.0-1.0)
- `metadata` - JSON field for flexible PO data (delivery date, payment terms, etc.)

## 🎯 Recommended Models

### For LM Studio (Local)

1. **Llama 3.3 70B** ⭐ Best accuracy (requires 48GB+ RAM)
2. **Qwen 2.5 7B** ⭐ Best for Korean + English (8GB RAM)
3. **Llama 3.2 3B** - Fast, low memory (4GB RAM)

### For Cloud

1. **Claude 3.5 Sonnet** ⭐ Best overall
2. **GPT-4o** - Good alternative

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_ai_extraction.py
```

Tests include:
- Text PO extraction (English)
- Korean PO extraction
- Text processing utilities
- LLM connection testing

## 📝 Example PO Formats

### English PO
```
PURCHASE ORDER
PO Number: PO-2025-001
Customer: ABC Corporation
Items:
1. Laptop - Qty: 5, Price: $1,200
Total: $6,875.00
```

### Korean PO
```
발주서
발주번호: 2025-001
고객: XYZ 주식회사
품목:
1. 노트북 - 수량: 3, 단가: 1,500,000원
합계: 5,940,000원
```

## 🔍 Troubleshooting

### LM Studio Connection Failed

1. Ensure LM Studio is running
2. Check "Server" tab shows "Server running on http://localhost:1234"
3. Verify model is loaded
4. Check `.env` has correct `LM_STUDIO_URL`

### Low Extraction Accuracy

1. Try a larger model (Llama 3.3 70B or Qwen 2.5 14B)
2. Add more examples to prompts in `ai/prompts.py`
3. Use Claude API for best results

### OCR Not Working

1. Install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
2. Set `TESSERACT_PATH` in `.env`
3. Download Korean language data if needed

## 📚 Documentation

- [Implementation Plan](docs/AI_Invoice_Builder_Implementation_Plan.docx)
- [Architecture Diagrams](docs/AI_Invoice_Builder_Architecture_with_Diagrams.docx)
- [Task Checklist](C:\Users\tjwns\.gemini\antigravity\brain\3e96f4a6-f10f-4d61-b39a-d9810395495b\task.md)

## 🚧 Roadmap

- [ ] Wizard UI (Upload → Review → Generate)
- [ ] Document viewer with field highlighting
- [ ] Batch PO processing
- [ ] Email integration
- [ ] Custom field mapping per customer
- [ ] Multi-language support

## 📄 License

MIT License

## 🤝 Contributing

This is an AI-first invoice generation system. Contributions welcome!
(To be honest Just using Claude is the best option. But I will expand this someday when i have time to better one)

---


