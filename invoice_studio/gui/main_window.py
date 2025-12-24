"""
Main window for Invoice Command Studio
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QMenuBar, QMenu, QMessageBox,
    QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from pathlib import Path

from .command_bar import CommandBar
from .invoice_list import InvoiceListPanel
from .invoice_detail import InvoiceDetailPanel
from ..database.db_manager import DatabaseManager
from ..commands.parser import parse_command
from ..commands.executor import CommandExecutor
from ..excel.template_handler import TemplateHandler
from ..models.invoice import Invoice


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice Command Studio")
        self.setGeometry(100, 100, 1400, 800)
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.command_executor = CommandExecutor(self.db_manager)
        self.template_handler = None
        
        # Try to initialize template handler
        try:
            self.template_handler = TemplateHandler()
        except FileNotFoundError:
            # Template will be created later
            pass
        
        # Register callbacks
        self.command_executor.register_callback('invoice_created', self.on_invoice_created)
        self.command_executor.register_callback('invoice_loaded', self.on_invoice_loaded)
        self.command_executor.register_callback('search_results', self.on_search_results)
        
        self.setup_ui()
        self.setup_menu()
        self.load_initial_data()
    
    def setup_ui(self):
        """Setup UI components"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Command bar at top
        self.command_bar = CommandBar()
        self.command_bar.command_executed.connect(self.execute_command)
        main_layout.addWidget(self.command_bar)
        
        # Splitter for left and right panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Invoice list
        self.invoice_list = InvoiceListPanel()
        self.invoice_list.invoice_selected.connect(self.on_invoice_selected)
        self.invoice_list.invoice_double_clicked.connect(self.on_invoice_double_clicked)
        self.invoice_list.refresh_requested.connect(self.refresh_invoice_list)
        splitter.addWidget(self.invoice_list)
        
        # Right panel - Invoice detail
        self.invoice_detail = InvoiceDetailPanel()
        self.invoice_detail.invoice_saved.connect(self.save_invoice)
        self.invoice_detail.excel_generated.connect(self.generate_excel)
        splitter.addWidget(self.invoice_detail)
        
        # Set splitter sizes (30% left, 70% right)
        splitter.setSizes([400, 1000])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status("Ready")
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_tax_action = QAction("New Tax Invoice", self)
        new_tax_action.setShortcut("Ctrl+T")
        new_tax_action.triggered.connect(lambda: self.create_new_invoice("Tax"))
        file_menu.addAction(new_tax_action)
        
        new_normal_action = QAction("New Normal Invoice", self)
        new_normal_action.setShortcut("Ctrl+N")
        new_normal_action.triggered.connect(lambda: self.create_new_invoice("Normal"))
        file_menu.addAction(new_normal_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        refresh_action = QAction("Refresh List", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(lambda: self.refresh_invoice_list({}))
        edit_menu.addAction(refresh_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        customers_action = QAction("Customer Master", self)
        customers_action.triggered.connect(self.show_customer_master)
        tools_menu.addAction(customers_action)
        
        items_action = QAction("Item Master", self)
        items_action.triggered.connect(self.show_item_master)
        tools_menu.addAction(items_action)
        
        tools_menu.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def load_initial_data(self):
        """Load initial data"""
        # Load invoices
        self.refresh_invoice_list({})
        
        # Load customers for dropdowns
        customers = self.db_manager.search_customers()
        customer_names = [c['name'] for c in customers]
        self.invoice_list.update_customer_list(customer_names)
        self.invoice_detail.update_customer_list(customer_names)
    
    def execute_command(self, command: str):
        """
        Execute command from command bar
        
        Args:
            command: Command string
        """
        # Parse command
        parsed = parse_command(command)
        
        if not parsed:
            self.command_bar.log_result("Invalid command", False)
            return
        
        # Execute command
        result = self.command_executor.execute(parsed)
        
        # Log result
        self.command_bar.log_result(
            result.get('message', 'Command executed'),
            result.get('success', False)
        )
        
        # Update status
        if result.get('success'):
            self.update_status(result.get('message', 'Command executed'))
    
    def create_new_invoice(self, invoice_type: str):
        """Create new invoice"""
        invoice = Invoice(invoice_type=invoice_type)
        invoice.invoice_no = self.db_manager.get_next_invoice_number()
        self.invoice_detail.load_invoice(invoice)
        self.update_status(f"Created new {invoice_type} invoice")
    
    def on_invoice_created(self, invoice: Invoice):
        """Handle invoice created from command"""
        self.invoice_detail.load_invoice(invoice)
        self.update_status(f"Created invoice: {invoice.invoice_no}")
    
    def on_invoice_loaded(self, invoice: Invoice):
        """Handle invoice loaded from command"""
        self.invoice_detail.load_invoice(invoice)
        self.update_status(f"Loaded invoice: {invoice.invoice_no}")
    
    def on_search_results(self, results: list):
        """Handle search results from command"""
        self.invoice_list.load_invoices(results)
        self.update_status(f"Found {len(results)} invoice(s)")
    
    def on_invoice_selected(self, invoice_data: dict):
        """Handle invoice selection from list"""
        # Load full invoice with items
        full_invoice = self.db_manager.get_invoice(invoice_data['id'])
        if full_invoice:
            items = full_invoice.pop('items', [])
            invoice = Invoice.from_dict(full_invoice, items)
            self.invoice_detail.load_invoice(invoice)
    
    def on_invoice_double_clicked(self, invoice_data: dict):
        """Handle invoice double-click"""
        self.on_invoice_selected(invoice_data)
    
    def save_invoice(self, invoice: Invoice):
        """
        Save invoice to database
        
        Args:
            invoice: Invoice object
        """
        try:
            # Check if updating or creating new
            if invoice.id:
                # Update existing
                self.db_manager.update_invoice(
                    invoice.id,
                    invoice.to_dict(),
                    invoice.items
                )
                self.update_status(f"Updated invoice: {invoice.invoice_no}")
            else:
                # Create new
                # Ensure invoice number is set
                if not invoice.invoice_no:
                    invoice.invoice_no = self.db_manager.get_next_invoice_number()
                
                invoice_id = self.db_manager.add_invoice(
                    invoice.to_dict(),
                    invoice.items
                )
                invoice.id = invoice_id
                self.update_status(f"Saved invoice: {invoice.invoice_no}")
            
            # Refresh list
            self.refresh_invoice_list({})
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save invoice: {str(e)}")
    
    def generate_excel(self, invoice: Invoice):
        """
        Generate Excel file for invoice
        
        Args:
            invoice: Invoice object
        """
        try:
            # Ensure template handler is initialized
            if not self.template_handler:
                # Try to create template first
                self.create_template()
                self.template_handler = TemplateHandler()
            
            # Ensure invoice is saved first
            if not invoice.id:
                reply = QMessageBox.question(
                    self,
                    "Save Invoice",
                    "Invoice must be saved before generating Excel. Save now?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.save_invoice(invoice)
                else:
                    return
            
            # Generate Excel
            output_path = self.template_handler.generate_invoice(invoice)
            
            # Update invoice file path
            invoice.file_path = output_path
            if invoice.id:
                invoice_dict = invoice.to_dict()
                self.db_manager.update_invoice(invoice.id, invoice_dict)
            
            # Show success message
            reply = QMessageBox.information(
                self,
                "Success",
                f"Excel file generated:\n{output_path}\n\nOpen file?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                import os
                os.startfile(output_path)
            
            self.update_status(f"Generated Excel: {output_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate Excel: {str(e)}")
    
    def refresh_invoice_list(self, filters: dict):
        """Refresh invoice list with filters"""
        invoices = self.db_manager.search_invoices(filters)
        self.invoice_list.load_invoices(invoices)
        self.update_status(f"Loaded {len(invoices)} invoice(s)")
    
    def create_template(self):
        """Create sample template"""
        reply = QMessageBox.question(
            self,
            "Create Template",
            "Invoice template not found. Create a sample template?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Run template creation script
                import sys
                sys.path.insert(0, str(Path(__file__).parent.parent.parent))
                from create_template import create_sample_template
                create_sample_template()
                QMessageBox.information(
                    self,
                    "Success",
                    "Sample template created successfully!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to create template: {str(e)}"
                )
    
    def show_customer_master(self):
        """Show customer master dialog"""
        QMessageBox.information(self, "Customer Master", "Customer master dialog - To be implemented")
    
    def show_item_master(self):
        """Show item master dialog"""
        QMessageBox.information(self, "Item Master", "Item master dialog - To be implemented")
    
    def show_settings(self):
        """Show settings dialog"""
        QMessageBox.information(self, "Settings", "Settings dialog - To be implemented")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Invoice Command Studio",
            "<h2>Invoice Command Studio</h2>"
            "<p>Version 1.0.0</p>"
            "<p>A Windows desktop application for generating Tax and Non-Tax invoices "
            "with a command-bar interface.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Command-driven interface</li>"
            "<li>Tax Invoice (10% VAT) and Normal Invoice (0% VAT)</li>"
            "<li>Excel template-based generation</li>"
            "<li>Customer and item master data</li>"
            "</ul>"
        )
    
    def update_status(self, message: str):
        """Update status bar"""
        self.status_bar.showMessage(message)
    
    def closeEvent(self, event):
        """Handle window close"""
        self.db_manager.close()
        event.accept()
