# Invoice Command Studio - Quick Reference

## Command Syntax

### Create New Invoice

**Tax Invoice (10% VAT):**
```
new tax invoice 고객="Customer Name" 총액=3300000
new tax invoice customer="Customer Name" total=3300000
```

**Normal Invoice (0% VAT):**
```
new normal invoice 고객="Customer Name" 통화="USD"
new normal invoice customer="Customer Name" currency="USD"
```

### Search Invoices

```
search invoice 고객="ABC"
search invoice 월=2025-12
search invoice customer="ABC" month=2025-12
```

### Open Invoice

```
open invoice 번호="2025-001"
open invoice number="2025-001"
```

### Duplicate Invoice

```
duplicate invoice 번호="2025-001"
duplicate invoice number="2025-001"
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+T` | New Tax Invoice |
| `Ctrl+N` | New Normal Invoice |
| `F5` | Refresh Invoice List |
| `Ctrl+Q` | Exit Application |
| `↑` / `↓` | Navigate command history |
| `Enter` | Execute command |

## Parameter Names

| Korean | English | Description |
|--------|---------|-------------|
| 고객 | customer | Customer name |
| 총액 | total, amount | Total amount (including VAT) |
| 통화 | currency | Currency code (KRW, USD, EUR, JPY) |
| 월 | month | Month in YYYY-MM format |
| 번호 | number, no | Invoice number |
| 타입 | type | Invoice type (Tax/Normal) |

## File Locations

- **Database**: `data/invoices.db`
- **Template**: `data/Invoice template.xlsx`
- **Mapping**: `data/template_mapping.json`
- **Output**: `output/` (generated Excel files)

## Invoice Number Format

- Format: `YYYY-NNN` (e.g., 2025-001, 2025-002)
- Auto-generated sequentially per year
- Unique constraint enforced

## VAT Calculation

**Tax Invoice:**
- User enters: Total = 3,300,000
- System calculates: Subtotal = 3,000,000, VAT = 300,000
- Formula: Subtotal = Total / 1.1, VAT = Total - Subtotal

**Normal Invoice:**
- VAT = 0
- Total = Subtotal

## Tips

1. **Quick Entry**: Use command bar for fastest invoice creation
2. **Autocomplete**: Start typing and press Tab for suggestions
3. **History**: Use ↑/↓ arrows to recall previous commands
4. **Filters**: Use date range and customer filters to find invoices quickly
5. **Double-Click**: Double-click any invoice in list to open it
6. **Context Menu**: Right-click invoice for more options
7. **Save First**: Always save invoice before generating Excel
8. **Currency**: Change currency in detail panel before adding items

## Common Workflows

### Workflow 1: Quick Tax Invoice
1. Command: `new tax invoice 고객="ABC Corp" 총액=3300000`
2. Add item details in table
3. Click "Save"
4. Click "Generate Excel"

### Workflow 2: Detailed Normal Invoice
1. Menu: File → New Normal Invoice
2. Select customer from dropdown
3. Add multiple items with "+ Add Item"
4. Click "Calculate" to verify totals
5. Click "Save"
6. Click "Generate Excel"

### Workflow 3: Find and Duplicate
1. Command: `search invoice 고객="ABC"`
2. Double-click invoice to open
3. Command: `duplicate invoice 번호="2025-001"`
4. Modify date and amounts
5. Click "Save"

## Troubleshooting

**Problem**: Command not recognized  
**Solution**: Check syntax, use quotes for values with spaces

**Problem**: Excel generation fails  
**Solution**: Ensure invoice is saved first, check template exists

**Problem**: Can't find invoice  
**Solution**: Check date range filter, clear filters and try again

**Problem**: VAT calculation wrong  
**Solution**: Verify invoice type (Tax vs Normal), click Calculate

**Problem**: Database error  
**Solution**: Check `data/invoices.db` exists, restart application
