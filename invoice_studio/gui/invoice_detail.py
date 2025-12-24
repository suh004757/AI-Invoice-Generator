"""
Invoice Detail panel widget
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QDateEdit, QComboBox, QRadioButton,
    QButtonGroup, QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QMessageBox, QTextEdit
)
from PySide6.QtCore import Signal, Qt, QDate
from PySide6.QtGui import QFont
from datetime import datetime
from ..models.invoice import Invoice


class InvoiceDetailPanel(QWidget):
    """Right panel showing invoice details"""
    
    # Signals
    invoice_saved = Signal(object)  # Emitted when invoice is saved
    excel_generated = Signal(str)  # Emitted when Excel is generated
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_invoice = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Invoice Details")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(title)
        
        # Header section
        header_layout = QFormLayout()
        
        # Invoice type
        type_layout = QHBoxLayout()
        self.type_group = QButtonGroup()
        
        self.tax_radio = QRadioButton("Tax Invoice (10% VAT)")
        self.tax_radio.setChecked(True)
        self.tax_radio.toggled.connect(self.on_type_changed)
        self.type_group.addButton(self.tax_radio)
        type_layout.addWidget(self.tax_radio)
        
        self.normal_radio = QRadioButton("Normal Invoice (0% VAT)")
        self.normal_radio.toggled.connect(self.on_type_changed)
        self.type_group.addButton(self.normal_radio)
        type_layout.addWidget(self.normal_radio)
        
        type_layout.addStretch()
        header_layout.addRow("Type:", type_layout)
        
        # Invoice number
        self.invoice_no = QLineEdit()
        self.invoice_no.setReadOnly(True)
        self.invoice_no.setPlaceholderText("Auto-generated")
        header_layout.addRow("Invoice No:", self.invoice_no)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        header_layout.addRow("Date:", self.date_edit)
        
        # Customer
        self.customer_combo = QComboBox()
        self.customer_combo.setEditable(True)
        self.customer_combo.setPlaceholderText("Enter or select customer")
        header_layout.addRow("Customer:", self.customer_combo)
        
        # Currency
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["KRW", "USD", "EUR", "JPY"])
        header_layout.addRow("Currency:", self.currency_combo)
        
        layout.addLayout(header_layout)
        
        # Items section
        items_label = QLabel("Items")
        items_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(items_label)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            "Description", "Quantity", "Unit Price", "Amount", ""
        ])
        
        # Set column widths
        header = self.items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        self.items_table.setColumnWidth(4, 30)
        
        # Connect cell changed signal
        self.items_table.cellChanged.connect(self.on_item_changed)
        
        layout.addWidget(self.items_table)
        
        # Add/Remove item buttons
        item_buttons = QHBoxLayout()
        
        add_item_btn = QPushButton("+ Add Item")
        add_item_btn.clicked.connect(self.add_item_row)
        item_buttons.addWidget(add_item_btn)
        
        item_buttons.addStretch()
        
        layout.addLayout(item_buttons)
        
        # Totals section
        totals_layout = QFormLayout()
        totals_layout.setLabelAlignment(Qt.AlignRight)
        
        self.subtotal_label = QLabel("0")
        self.subtotal_label.setAlignment(Qt.AlignRight)
        self.subtotal_label.setFont(QFont("Arial", 10))
        totals_layout.addRow("Subtotal:", self.subtotal_label)
        
        self.vat_label = QLabel("0")
        self.vat_label.setAlignment(Qt.AlignRight)
        self.vat_label.setFont(QFont("Arial", 10))
        totals_layout.addRow("VAT:", self.vat_label)
        
        self.total_label = QLabel("0")
        self.total_label.setAlignment(Qt.AlignRight)
        self.total_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.total_label.setStyleSheet("color: #0066cc;")
        totals_layout.addRow("Total:", self.total_label)
        
        layout.addLayout(totals_layout)
        
        # Notes
        notes_label = QLabel("Notes:")
        layout.addWidget(notes_label)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(60)
        self.notes_edit.setPlaceholderText("Optional notes...")
        layout.addWidget(self.notes_edit)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.calculate_btn = QPushButton("Calculate")
        self.calculate_btn.clicked.connect(self.calculate_totals)
        buttons_layout.addWidget(self.calculate_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_invoice)
        self.save_btn.setStyleSheet("background-color: #0066cc; color: white; font-weight: bold;")
        buttons_layout.addWidget(self.save_btn)
        
        self.excel_btn = QPushButton("Generate Excel")
        self.excel_btn.clicked.connect(self.generate_excel)
        buttons_layout.addWidget(self.excel_btn)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_form)
        buttons_layout.addWidget(self.clear_btn)
        
        layout.addLayout(buttons_layout)
        
        layout.addStretch()
    
    def load_invoice(self, invoice: Invoice):
        """
        Load invoice into form
        
        Args:
            invoice: Invoice object
        """
        self.current_invoice = invoice
        
        # Set type
        if invoice.type == "Tax":
            self.tax_radio.setChecked(True)
        else:
            self.normal_radio.setChecked(True)
        
        # Set fields
        self.invoice_no.setText(invoice.invoice_no or "")
        
        if isinstance(invoice.date, datetime):
            self.date_edit.setDate(QDate(
                invoice.date.year,
                invoice.date.month,
                invoice.date.day
            ))
        
        self.customer_combo.setCurrentText(invoice.customer_name)
        self.currency_combo.setCurrentText(invoice.currency)
        self.notes_edit.setPlainText(invoice.notes)
        
        # Load items
        self.items_table.setRowCount(0)
        for item in invoice.items:
            self.add_item_row(
                description=item.get('description', ''),
                quantity=item.get('quantity', 1),
                unit_price=item.get('unit_price', 0)
            )
        
        # Calculate totals
        self.calculate_totals()
    
    def add_item_row(self, description: str = "", quantity: float = 1, 
                     unit_price: float = 0):
        """Add a new item row"""
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        
        # Description
        desc_item = QTableWidgetItem(description)
        self.items_table.setItem(row, 0, desc_item)
        
        # Quantity
        qty_item = QTableWidgetItem(str(quantity))
        qty_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.items_table.setItem(row, 1, qty_item)
        
        # Unit price
        price_item = QTableWidgetItem(str(unit_price))
        price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.items_table.setItem(row, 2, price_item)
        
        # Amount (calculated)
        amount = quantity * unit_price
        amount_item = QTableWidgetItem(f"{amount:,.2f}")
        amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        amount_item.setFlags(amount_item.flags() & ~Qt.ItemIsEditable)
        self.items_table.setItem(row, 3, amount_item)
        
        # Delete button
        delete_btn = QPushButton("×")
        delete_btn.setMaximumWidth(30)
        delete_btn.clicked.connect(lambda: self.remove_item_row(row))
        self.items_table.setCellWidget(row, 4, delete_btn)
    
    def remove_item_row(self, row: int):
        """Remove item row"""
        self.items_table.removeRow(row)
        self.calculate_totals()
    
    def on_item_changed(self, row: int, column: int):
        """Handle item cell change"""
        if column in [1, 2]:  # Quantity or Unit Price changed
            try:
                qty_item = self.items_table.item(row, 1)
                price_item = self.items_table.item(row, 2)
                
                if qty_item and price_item:
                    qty = float(qty_item.text())
                    price = float(price_item.text())
                    amount = qty * price
                    
                    # Update amount
                    amount_item = self.items_table.item(row, 3)
                    if amount_item:
                        amount_item.setText(f"{amount:,.2f}")
            except ValueError:
                pass
    
    def on_type_changed(self):
        """Handle invoice type change"""
        self.calculate_totals()
    
    def calculate_totals(self):
        """Calculate and update totals"""
        subtotal = 0.0
        
        # Sum all items
        for row in range(self.items_table.rowCount()):
            try:
                qty_item = self.items_table.item(row, 1)
                price_item = self.items_table.item(row, 2)
                
                if qty_item and price_item:
                    qty = float(qty_item.text())
                    price = float(price_item.text())
                    amount = qty * price
                    subtotal += amount
                    
                    # Update amount display
                    amount_item = self.items_table.item(row, 3)
                    if amount_item:
                        amount_item.setText(f"{amount:,.2f}")
            except ValueError:
                continue
        
        # Calculate VAT
        vat_rate = 0.10 if self.tax_radio.isChecked() else 0.0
        vat = subtotal * vat_rate
        total = subtotal + vat
        
        # Update labels
        currency = self.currency_combo.currentText()
        if currency == "KRW":
            self.subtotal_label.setText(f"{int(subtotal):,}")
            self.vat_label.setText(f"{int(vat):,}")
            self.total_label.setText(f"{int(total):,}")
        else:
            self.subtotal_label.setText(f"{subtotal:,.2f}")
            self.vat_label.setText(f"{vat:,.2f}")
            self.total_label.setText(f"{total:,.2f}")
    
    def get_invoice(self) -> Invoice:
        """
        Get invoice from form
        
        Returns:
            Invoice object
        """
        invoice_type = "Tax" if self.tax_radio.isChecked() else "Normal"
        currency = self.currency_combo.currentText()
        
        invoice = Invoice(invoice_type=invoice_type, currency=currency)
        invoice.invoice_no = self.invoice_no.text()
        
        # Get date
        qdate = self.date_edit.date()
        invoice.date = datetime(qdate.year(), qdate.month(), qdate.day())
        
        invoice.customer_name = self.customer_combo.currentText()
        invoice.notes = self.notes_edit.toPlainText()
        
        # Get items
        invoice.clear_items()
        for row in range(self.items_table.rowCount()):
            try:
                desc = self.items_table.item(row, 0).text()
                qty = float(self.items_table.item(row, 1).text())
                price = float(self.items_table.item(row, 2).text())
                
                if desc and qty > 0:
                    invoice.add_item(desc, qty, price)
            except (ValueError, AttributeError):
                continue
        
        # Calculate totals
        invoice.calculate_totals()
        
        return invoice
    
    def save_invoice(self):
        """Save current invoice"""
        try:
            invoice = self.get_invoice()
            
            # Validate
            is_valid, error = invoice.validate()
            if not is_valid:
                QMessageBox.warning(self, "Validation Error", error)
                return
            
            self.invoice_saved.emit(invoice)
            QMessageBox.information(self, "Success", "Invoice saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save invoice: {str(e)}")
    
    def generate_excel(self):
        """Generate Excel file"""
        try:
            invoice = self.get_invoice()
            
            # Validate
            is_valid, error = invoice.validate()
            if not is_valid:
                QMessageBox.warning(self, "Validation Error", error)
                return
            
            self.excel_generated.emit(invoice)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate Excel: {str(e)}")
    
    def clear_form(self):
        """Clear the form"""
        reply = QMessageBox.question(
            self,
            "Clear Form",
            "Are you sure you want to clear the form?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_invoice = None
            self.invoice_no.clear()
            self.date_edit.setDate(QDate.currentDate())
            self.customer_combo.setCurrentIndex(0)
            self.currency_combo.setCurrentIndex(0)
            self.notes_edit.clear()
            self.items_table.setRowCount(0)
            self.tax_radio.setChecked(True)
            self.calculate_totals()
    
    def update_customer_list(self, customers: list):
        """Update customer dropdown"""
        current = self.customer_combo.currentText()
        self.customer_combo.clear()
        self.customer_combo.addItems(customers)
        
        # Restore if possible
        index = self.customer_combo.findText(current)
        if index >= 0:
            self.customer_combo.setCurrentIndex(index)
