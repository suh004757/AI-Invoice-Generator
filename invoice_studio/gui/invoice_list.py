"""
Invoice List panel widget
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLabel, QComboBox, QDateEdit,
    QPushButton, QHeaderView, QMenu
)
from PySide6.QtCore import Signal, Qt, QDate
from PySide6.QtGui import QAction
from datetime import datetime, timedelta


class InvoiceListPanel(QWidget):
    """Left panel showing invoice list with filters"""
    
    # Signals
    invoice_selected = Signal(dict)  # Emitted when invoice is selected
    invoice_double_clicked = Signal(dict)  # Emitted when invoice is double-clicked
    refresh_requested = Signal(dict)  # Emitted when filters change
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.invoices = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Invoice List")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        layout.addWidget(title)
        
        # Filters section
        filters_layout = QVBoxLayout()
        
        # Date range filter
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("From:"))
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-3))
        self.date_from.dateChanged.connect(self.apply_filters)
        date_layout.addWidget(self.date_from)
        
        date_layout.addWidget(QLabel("To:"))
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.dateChanged.connect(self.apply_filters)
        date_layout.addWidget(self.date_to)
        
        filters_layout.addLayout(date_layout)
        
        # Customer filter
        customer_layout = QHBoxLayout()
        customer_layout.addWidget(QLabel("Customer:"))
        
        self.customer_filter = QComboBox()
        self.customer_filter.setEditable(True)
        self.customer_filter.addItem("All")
        self.customer_filter.currentTextChanged.connect(self.apply_filters)
        customer_layout.addWidget(self.customer_filter)
        
        filters_layout.addLayout(customer_layout)
        
        # Type filter
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "Tax", "Normal"])
        self.type_filter.currentTextChanged.connect(self.apply_filters)
        type_layout.addWidget(self.type_filter)
        
        filters_layout.addLayout(type_layout)
        
        # Clear filters button
        clear_btn = QPushButton("Clear Filters")
        clear_btn.clicked.connect(self.clear_filters)
        filters_layout.addWidget(clear_btn)
        
        layout.addLayout(filters_layout)
        
        # Invoice table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Date", "Number", "Customer", "Type", "Total"
        ])
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        # Enable sorting
        self.table.setSortingEnabled(True)
        
        # Connect signals
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemDoubleClicked.connect(self.on_double_clicked)
        
        # Context menu
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.table)
    
    def load_invoices(self, invoices: list):
        """
        Load invoices into table
        
        Args:
            invoices: List of invoice dictionaries
        """
        self.invoices = invoices
        self.table.setRowCount(0)
        
        for invoice in invoices:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Date
            date_item = QTableWidgetItem(invoice.get('date', ''))
            self.table.setItem(row, 0, date_item)
            
            # Number
            number_item = QTableWidgetItem(invoice.get('invoice_no', ''))
            self.table.setItem(row, 1, number_item)
            
            # Customer
            customer_item = QTableWidgetItem(invoice.get('customer_name', ''))
            self.table.setItem(row, 2, customer_item)
            
            # Type
            type_item = QTableWidgetItem(invoice.get('type', ''))
            self.table.setItem(row, 3, type_item)
            
            # Total
            total = invoice.get('total', 0)
            total_item = QTableWidgetItem(f"{total:,.0f}")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 4, total_item)
            
            # Store invoice data in row
            for col in range(5):
                item = self.table.item(row, col)
                if item:
                    item.setData(Qt.UserRole, invoice)
    
    def get_selected_invoice(self):
        """Get currently selected invoice"""
        selected_rows = self.table.selectedItems()
        if selected_rows:
            return selected_rows[0].data(Qt.UserRole)
        return None
    
    def on_selection_changed(self):
        """Handle selection change"""
        invoice = self.get_selected_invoice()
        if invoice:
            self.invoice_selected.emit(invoice)
    
    def on_double_clicked(self, item):
        """Handle double click"""
        invoice = item.data(Qt.UserRole)
        if invoice:
            self.invoice_double_clicked.emit(invoice)
    
    def apply_filters(self):
        """Apply current filters"""
        filters = self.get_filters()
        self.refresh_requested.emit(filters)
    
    def get_filters(self) -> dict:
        """Get current filter values"""
        filters = {}
        
        # Date range
        date_from = self.date_from.date().toPython()
        date_to = self.date_to.date().toPython()
        filters['date_from'] = date_from.strftime('%Y-%m-%d')
        filters['date_to'] = date_to.strftime('%Y-%m-%d')
        
        # Customer
        customer = self.customer_filter.currentText()
        if customer and customer != "All":
            filters['customer'] = customer
        
        # Type
        invoice_type = self.type_filter.currentText()
        if invoice_type and invoice_type != "All":
            filters['type'] = invoice_type
        
        return filters
    
    def clear_filters(self):
        """Clear all filters"""
        self.date_from.setDate(QDate.currentDate().addMonths(-3))
        self.date_to.setDate(QDate.currentDate())
        self.customer_filter.setCurrentIndex(0)
        self.type_filter.setCurrentIndex(0)
    
    def update_customer_list(self, customers: list):
        """
        Update customer filter dropdown
        
        Args:
            customers: List of customer names
        """
        current = self.customer_filter.currentText()
        self.customer_filter.clear()
        self.customer_filter.addItem("All")
        self.customer_filter.addItems(customers)
        
        # Restore previous selection if possible
        index = self.customer_filter.findText(current)
        if index >= 0:
            self.customer_filter.setCurrentIndex(index)
    
    def show_context_menu(self, position):
        """Show context menu for invoice actions"""
        if not self.get_selected_invoice():
            return
        
        menu = QMenu(self)
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(lambda: self.on_double_clicked(
            self.table.itemAt(position)
        ))
        menu.addAction(open_action)
        
        duplicate_action = QAction("Duplicate", self)
        menu.addAction(duplicate_action)
        
        menu.addSeparator()
        
        delete_action = QAction("Delete", self)
        menu.addAction(delete_action)
        
        export_action = QAction("Export to Excel", self)
        menu.addAction(export_action)
        
        menu.exec_(self.table.viewport().mapToGlobal(position))
