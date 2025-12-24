"""
Database schema for Invoice Command Studio
"""

# SQL schema definitions
CREATE_INVOICES_TABLE = """
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_no TEXT UNIQUE NOT NULL,
    date TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('Tax', 'Normal')),
    customer_id INTEGER,
    customer_name TEXT NOT NULL,
    currency TEXT DEFAULT 'KRW',
    subtotal REAL NOT NULL,
    vat REAL NOT NULL,
    total REAL NOT NULL,
    po_id INTEGER,
    extraction_confidence REAL,
    metadata TEXT,
    file_path TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (po_id) REFERENCES purchase_orders(id)
)
"""

CREATE_PURCHASE_ORDERS_TABLE = """
CREATE TABLE IF NOT EXISTS purchase_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    extracted_text TEXT,
    status TEXT DEFAULT 'uploaded',
    upload_date TEXT NOT NULL
)
"""

CREATE_EXTRACTION_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS extraction_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    po_id INTEGER NOT NULL,
    llm_provider TEXT NOT NULL,
    confidence_score REAL,
    extracted_data TEXT,
    prompt_used TEXT,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(id) ON DELETE CASCADE
)
"""


CREATE_CUSTOMERS_TABLE = """
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    contact_person TEXT,
    address TEXT,
    email TEXT,
    phone TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""

CREATE_ITEMS_TABLE = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    default_price REAL,
    unit TEXT DEFAULT 'EA',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""

CREATE_INVOICE_ITEMS_TABLE = """
CREATE TABLE IF NOT EXISTS invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    item_id INTEGER,
    description TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit_price REAL NOT NULL,
    amount REAL NOT NULL,
    line_order INTEGER NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id)
)
"""

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(date)",
    "CREATE INDEX IF NOT EXISTS idx_invoices_customer ON invoices(customer_name)",
    "CREATE INDEX IF NOT EXISTS idx_invoices_type ON invoices(type)",
    "CREATE INDEX IF NOT EXISTS idx_invoices_po ON invoices(po_id)",
    "CREATE INDEX IF NOT EXISTS idx_invoice_items_invoice ON invoice_items(invoice_id)",
    "CREATE INDEX IF NOT EXISTS idx_purchase_orders_status ON purchase_orders(status)",
    "CREATE INDEX IF NOT EXISTS idx_extraction_logs_po ON extraction_logs(po_id)",
]

