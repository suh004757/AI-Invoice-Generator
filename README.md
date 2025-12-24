# Invoice Command Studio

A Windows desktop application for generating Tax (10% VAT) and Non-Tax (0% VAT) invoices with an intuitive command-bar interface.

## Features

- **Command-Driven Interface**: Control the app using natural commands like `new tax invoice 고객="ABC Corp" 총액=3300000`
- **Two Invoice Types**:
  - Tax Invoice (10% VAT)
  - Non-Tax Invoice (0% VAT)
- **Excel Template-Based**: Generate professional invoices from customizable Excel templates
- **Database Management**: Store and search invoice history with SQLite
- **Customer & Item Masters**: Maintain frequently used customers and items
- **PDF Export**: Convert invoices to PDF format

## Installation

1. **Clone or download this project**

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**:
   ```bash
   # Windows
   venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

1. **Run the application**:
   ```bash
   python -m invoice_studio.main
   ```

2. **Create your first invoice using the Command Bar**:
   ```
   new tax invoice 고객="ABC Corp" 총액=3300000
   ```

3. **Or use the GUI**:
   - Click "New Tax Invoice" button
   - Fill in customer and item details
   - Click "Generate Excel"

## Command Syntax Reference

### Create New Invoice
```
new tax invoice 고객="Customer Name" 총액=3300000
new normal invoice 고객="Customer Name" 통화="USD"
```

### Search Invoices
```
search invoice 고객="ABC" 월=2025-12
search invoice 번호="2025-001"
```

### Open Existing Invoice
```
open invoice 번호="2025-001"
```

### Duplicate Invoice
```
duplicate invoice 번호="2025-001"
```

## Project Structure

```
NEW PROJECT/
├── invoice_studio/          # Main application package
│   ├── database/           # Database models and operations
│   ├── commands/           # Command parser and executor
│   ├── excel/              # Excel template handling
│   ├── gui/                # GUI components
│   ├── models/             # Business logic
│   └── utils/              # Utilities
├── data/                   # Data files
│   ├── invoices.db        # SQLite database
│   ├── Invoice template.xlsx
│   └── template_mapping.json
├── output/                 # Generated invoices
└── requirements.txt
```

## Configuration

### Template Cell Mapping

Edit `data/template_mapping.json` to customize where data appears in your Excel template:

```json
{
  "invoice_no": "B4",
  "date": "B5",
  "customer_name": "B6",
  "items_start_row": 10,
  "subtotal": "E20",
  "vat": "E21",
  "total": "E22"
}
```

Or use the Settings dialog in the app: **Tools → Settings → Template Mapping**

## Troubleshooting

### Excel file won't open
- Ensure Microsoft Excel or LibreOffice is installed
- Check that the template file exists in `data/Invoice template.xlsx`

### Commands not working
- Check command syntax (use quotes for values with spaces)
- View command history with the dropdown in Command Bar

### Database errors
- Delete `data/invoices.db` to reset the database (warning: loses all data)
- Check file permissions in the `data/` folder

## Future Enhancements

- [ ] LLM integration for natural language commands
- [ ] Multi-currency support
- [ ] Email invoice directly from app
- [ ] Cloud backup/sync
- [ ] Custom template designer

## License

MIT License

## Support

For issues or questions, please create an issue in the project repository.
