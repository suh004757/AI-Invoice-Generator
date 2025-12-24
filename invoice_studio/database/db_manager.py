"""
Database manager for Invoice Command Studio
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from .models import (
    CREATE_INVOICES_TABLE,
    CREATE_CUSTOMERS_TABLE,
    CREATE_ITEMS_TABLE,
    CREATE_INVOICE_ITEMS_TABLE,
    CREATE_PURCHASE_ORDERS_TABLE,
    CREATE_EXTRACTION_LOGS_TABLE,
    CREATE_INDEXES
)


class DatabaseManager:
    """Manages all database operations"""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            # Default to data/invoices.db
            data_dir = Path(__file__).parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "invoices.db")
        
        self.db_path = db_path
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish database connection"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Enable column access by name
        # Enable foreign keys
        self.connection.execute("PRAGMA foreign_keys = ON")
    
    def create_tables(self):
        """Create all database tables if they don't exist"""
        cursor = self.connection.cursor()
        
        # Create tables
        cursor.execute(CREATE_CUSTOMERS_TABLE)
        cursor.execute(CREATE_ITEMS_TABLE)
        cursor.execute(CREATE_PURCHASE_ORDERS_TABLE)
        cursor.execute(CREATE_EXTRACTION_LOGS_TABLE)
        cursor.execute(CREATE_INVOICES_TABLE)
        cursor.execute(CREATE_INVOICE_ITEMS_TABLE)
        
        # Create indexes
        for index_sql in CREATE_INDEXES:
            cursor.execute(index_sql)
        
        self.connection.commit()
    
    # ========== Invoice Operations ==========
    
    def add_invoice(self, invoice_data: Dict, items: List[Dict]) -> int:
        """
        Add new invoice with items
        
        Args:
            invoice_data: Dictionary with invoice fields
            items: List of item dictionaries
        
        Returns:
            Invoice ID
        """
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()
        
        # Insert invoice
        cursor.execute("""
            INSERT INTO invoices (
                invoice_no, date, type, customer_id, customer_name,
                currency, subtotal, vat, total, file_path, notes,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            invoice_data['invoice_no'],
            invoice_data['date'],
            invoice_data['type'],
            invoice_data.get('customer_id'),
            invoice_data['customer_name'],
            invoice_data.get('currency', 'KRW'),
            invoice_data['subtotal'],
            invoice_data['vat'],
            invoice_data['total'],
            invoice_data.get('file_path'),
            invoice_data.get('notes'),
            now,
            now
        ))
        
        invoice_id = cursor.lastrowid
        
        # Insert invoice items
        for idx, item in enumerate(items):
            cursor.execute("""
                INSERT INTO invoice_items (
                    invoice_id, item_id, description, quantity,
                    unit_price, amount, line_order
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_id,
                item.get('item_id'),
                item['description'],
                item['quantity'],
                item['unit_price'],
                item['amount'],
                idx
            ))
        
        self.connection.commit()
        return invoice_id
    
    def get_invoice(self, invoice_id: int) -> Optional[Dict]:
        """
        Get invoice by ID
        
        Args:
            invoice_id: Invoice ID
        
        Returns:
            Invoice dictionary with items, or None
        """
        cursor = self.connection.cursor()
        
        # Get invoice
        cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        invoice = dict(row)
        
        # Get items
        cursor.execute("""
            SELECT * FROM invoice_items 
            WHERE invoice_id = ? 
            ORDER BY line_order
        """, (invoice_id,))
        
        invoice['items'] = [dict(row) for row in cursor.fetchall()]
        
        return invoice
    
    def get_invoice_by_number(self, invoice_no: str) -> Optional[Dict]:
        """
        Get invoice by invoice number
        
        Args:
            invoice_no: Invoice number
        
        Returns:
            Invoice dictionary with items, or None
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM invoices WHERE invoice_no = ?", (invoice_no,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return self.get_invoice(row['id'])
    
    def search_invoices(self, filters: Dict = None) -> List[Dict]:
        """
        Search invoices with filters
        
        Args:
            filters: Dictionary with filter criteria
                - customer: Customer name (partial match)
                - type: Invoice type (Tax/Normal)
                - date_from: Start date
                - date_to: End date
                - month: Month in YYYY-MM format
        
        Returns:
            List of invoice dictionaries
        """
        cursor = self.connection.cursor()
        
        query = "SELECT * FROM invoices WHERE 1=1"
        params = []
        
        if filters:
            if 'customer' in filters:
                query += " AND customer_name LIKE ?"
                params.append(f"%{filters['customer']}%")
            
            if 'type' in filters:
                query += " AND type = ?"
                params.append(filters['type'])
            
            if 'date_from' in filters:
                query += " AND date >= ?"
                params.append(filters['date_from'])
            
            if 'date_to' in filters:
                query += " AND date <= ?"
                params.append(filters['date_to'])
            
            if 'month' in filters:
                # Month format: YYYY-MM
                query += " AND date LIKE ?"
                params.append(f"{filters['month']}%")
        
        query += " ORDER BY date DESC, invoice_no DESC"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def update_invoice(self, invoice_id: int, invoice_data: Dict, items: List[Dict] = None):
        """
        Update existing invoice
        
        Args:
            invoice_id: Invoice ID
            invoice_data: Updated invoice fields
            items: Updated items list (if provided, replaces all items)
        """
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()
        
        # Update invoice
        cursor.execute("""
            UPDATE invoices SET
                invoice_no = ?, date = ?, type = ?, customer_id = ?,
                customer_name = ?, currency = ?, subtotal = ?, vat = ?,
                total = ?, file_path = ?, notes = ?, updated_at = ?
            WHERE id = ?
        """, (
            invoice_data['invoice_no'],
            invoice_data['date'],
            invoice_data['type'],
            invoice_data.get('customer_id'),
            invoice_data['customer_name'],
            invoice_data.get('currency', 'KRW'),
            invoice_data['subtotal'],
            invoice_data['vat'],
            invoice_data['total'],
            invoice_data.get('file_path'),
            invoice_data.get('notes'),
            now,
            invoice_id
        ))
        
        # Update items if provided
        if items is not None:
            # Delete existing items
            cursor.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
            
            # Insert new items
            for idx, item in enumerate(items):
                cursor.execute("""
                    INSERT INTO invoice_items (
                        invoice_id, item_id, description, quantity,
                        unit_price, amount, line_order
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    invoice_id,
                    item.get('item_id'),
                    item['description'],
                    item['quantity'],
                    item['unit_price'],
                    item['amount'],
                    idx
                ))
        
        self.connection.commit()
    
    def delete_invoice(self, invoice_id: int):
        """Delete invoice and its items"""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
        self.connection.commit()
    
    def get_next_invoice_number(self, year: int = None) -> str:
        """
        Generate next invoice number
        
        Args:
            year: Year for invoice number (default: current year)
        
        Returns:
            Invoice number in format YYYY-NNN
        """
        if year is None:
            year = datetime.now().year
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT invoice_no FROM invoices 
            WHERE invoice_no LIKE ? 
            ORDER BY invoice_no DESC 
            LIMIT 1
        """, (f"{year}-%",))
        
        row = cursor.fetchone()
        
        if row:
            # Extract number and increment
            last_no = row['invoice_no']
            try:
                num = int(last_no.split('-')[1]) + 1
            except (IndexError, ValueError):
                num = 1
        else:
            num = 1
        
        return f"{year}-{num:03d}"
    
    # ========== Customer Operations ==========
    
    def add_customer(self, customer_data: Dict) -> int:
        """Add new customer"""
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO customers (
                name, contact_person, address, email, phone,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_data['name'],
            customer_data.get('contact_person'),
            customer_data.get('address'),
            customer_data.get('email'),
            customer_data.get('phone'),
            now,
            now
        ))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_customer(self, customer_id: int) -> Optional[Dict]:
        """Get customer by ID"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_customer_by_name(self, name: str) -> Optional[Dict]:
        """Get customer by exact name"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM customers WHERE name = ?", (name,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def search_customers(self, name_filter: str = None) -> List[Dict]:
        """Search customers"""
        cursor = self.connection.cursor()
        
        if name_filter:
            cursor.execute(
                "SELECT * FROM customers WHERE name LIKE ? ORDER BY name",
                (f"%{name_filter}%",)
            )
        else:
            cursor.execute("SELECT * FROM customers ORDER BY name")
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_customer(self, customer_id: int, customer_data: Dict):
        """Update customer"""
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE customers SET
                name = ?, contact_person = ?, address = ?,
                email = ?, phone = ?, updated_at = ?
            WHERE id = ?
        """, (
            customer_data['name'],
            customer_data.get('contact_person'),
            customer_data.get('address'),
            customer_data.get('email'),
            customer_data.get('phone'),
            now,
            customer_id
        ))
        
        self.connection.commit()
    
    def delete_customer(self, customer_id: int):
        """Delete customer"""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
        self.connection.commit()
    
    # ========== Item Operations ==========
    
    def add_item(self, item_data: Dict) -> int:
        """Add new item"""
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO items (
                name, description, default_price, unit,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            item_data['name'],
            item_data.get('description'),
            item_data.get('default_price'),
            item_data.get('unit', 'EA'),
            now,
            now
        ))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_item(self, item_id: int) -> Optional[Dict]:
        """Get item by ID"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def search_items(self, name_filter: str = None) -> List[Dict]:
        """Search items"""
        cursor = self.connection.cursor()
        
        if name_filter:
            cursor.execute(
                "SELECT * FROM items WHERE name LIKE ? ORDER BY name",
                (f"%{name_filter}%",)
            )
        else:
            cursor.execute("SELECT * FROM items ORDER BY name")
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_item(self, item_id: int, item_data: Dict):
        """Update item"""
        cursor = self.connection.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE items SET
                name = ?, description = ?, default_price = ?,
                unit = ?, updated_at = ?
            WHERE id = ?
        """, (
            item_data['name'],
            item_data.get('description'),
            item_data.get('default_price'),
            item_data.get('unit', 'EA'),
            now,
            item_id
        ))
        
        self.connection.commit()
    
    def delete_item(self, item_id: int):
        """Delete item"""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        self.connection.commit()
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
