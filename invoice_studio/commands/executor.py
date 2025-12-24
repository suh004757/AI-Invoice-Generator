"""
Command executor for Invoice Command Studio
"""
from datetime import datetime
from typing import Dict, Optional, Callable
from ..models.invoice import Invoice
from ..database.db_manager import DatabaseManager
from ..utils.formatters import parse_amount


class CommandExecutor:
    """Execute parsed commands"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize executor
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        self.callbacks = {}
    
    def register_callback(self, event: str, callback: Callable):
        """
        Register callback for events
        
        Args:
            event: Event name (e.g., 'invoice_created', 'invoice_loaded')
            callback: Callback function
        """
        self.callbacks[event] = callback
    
    def _trigger_callback(self, event: str, data: any = None):
        """Trigger registered callback"""
        if event in self.callbacks:
            self.callbacks[event](data)
    
    def execute(self, parsed_command: Dict) -> Dict:
        """
        Execute parsed command
        
        Args:
            parsed_command: Parsed command dictionary from parser
        
        Returns:
            Result dictionary with success status and message/data
        """
        cmd_type = parsed_command.get('type')
        
        if cmd_type == 'unknown':
            return {
                'success': False,
                'message': parsed_command.get('error', 'Unknown command')
            }
        
        # Route to appropriate handler
        handlers = {
            'new_tax': self._handle_new_tax,
            'new_normal': self._handle_new_normal,
            'search': self._handle_search,
            'open': self._handle_open,
            'duplicate': self._handle_duplicate,
        }
        
        handler = handlers.get(cmd_type)
        
        if handler:
            try:
                return handler(parsed_command['params'])
            except Exception as e:
                return {
                    'success': False,
                    'message': f'Error executing command: {str(e)}'
                }
        
        return {
            'success': False,
            'message': f'No handler for command type: {cmd_type}'
        }
    
    def _handle_new_tax(self, params: Dict) -> Dict:
        """Handle 'new tax invoice' command"""
        return self._handle_new_invoice(params, invoice_type='Tax')
    
    def _handle_new_normal(self, params: Dict) -> Dict:
        """Handle 'new normal invoice' command"""
        return self._handle_new_invoice(params, invoice_type='Normal')
    
    def _handle_new_invoice(self, params: Dict, invoice_type: str) -> Dict:
        """
        Handle new invoice creation
        
        Args:
            params: Command parameters
            invoice_type: 'Tax' or 'Normal'
        
        Returns:
            Result dictionary
        """
        # Create new invoice
        currency = params.get('통화', params.get('currency', 'KRW'))
        invoice = Invoice(invoice_type=invoice_type, currency=currency)
        
        # Generate invoice number
        invoice.invoice_no = self.db.get_next_invoice_number()
        
        # Set customer
        customer_name = params.get('고객', params.get('customer', ''))
        if customer_name:
            invoice.customer_name = customer_name
            
            # Try to find existing customer
            customer = self.db.get_customer_by_name(customer_name)
            if customer:
                invoice.customer_id = customer['id']
        
        # Handle total amount if provided
        total_amount = params.get('총액', params.get('total', params.get('amount')))
        if total_amount:
            if isinstance(total_amount, str):
                total_amount = parse_amount(total_amount)
            
            invoice.calculate_from_total(float(total_amount))
        
        # Trigger callback to load invoice in GUI
        self._trigger_callback('invoice_created', invoice)
        
        return {
            'success': True,
            'message': f'Created new {invoice_type} invoice: {invoice.invoice_no}',
            'data': invoice
        }
    
    def _handle_search(self, params: Dict) -> Dict:
        """
        Handle 'search invoice' command
        
        Args:
            params: Search parameters
        
        Returns:
            Result dictionary with matching invoices
        """
        filters = {}
        
        # Map Korean/English parameter names
        if '고객' in params or 'customer' in params:
            filters['customer'] = params.get('고객', params.get('customer'))
        
        if '월' in params or 'month' in params:
            filters['month'] = params.get('월', params.get('month'))
        
        if '타입' in params or 'type' in params:
            filters['type'] = params.get('타입', params.get('type'))
        
        if '시작일' in params or 'date_from' in params:
            filters['date_from'] = params.get('시작일', params.get('date_from'))
        
        if '종료일' in params or 'date_to' in params:
            filters['date_to'] = params.get('종료일', params.get('date_to'))
        
        # Search database
        results = self.db.search_invoices(filters)
        
        # Trigger callback to update invoice list
        self._trigger_callback('search_results', results)
        
        return {
            'success': True,
            'message': f'Found {len(results)} invoice(s)',
            'data': results
        }
    
    def _handle_open(self, params: Dict) -> Dict:
        """
        Handle 'open invoice' command
        
        Args:
            params: Parameters with invoice number
        
        Returns:
            Result dictionary
        """
        invoice_no = params.get('번호', params.get('number', params.get('no')))
        
        if not invoice_no:
            return {
                'success': False,
                'message': 'Invoice number required. Use: open invoice 번호="2025-001"'
            }
        
        # Get invoice from database
        invoice_data = self.db.get_invoice_by_number(str(invoice_no))
        
        if not invoice_data:
            return {
                'success': False,
                'message': f'Invoice not found: {invoice_no}'
            }
        
        # Convert to Invoice object
        items = invoice_data.pop('items', [])
        invoice = Invoice.from_dict(invoice_data, items)
        
        # Trigger callback to load invoice in GUI
        self._trigger_callback('invoice_loaded', invoice)
        
        return {
            'success': True,
            'message': f'Opened invoice: {invoice_no}',
            'data': invoice
        }
    
    def _handle_duplicate(self, params: Dict) -> Dict:
        """
        Handle 'duplicate invoice' command
        
        Args:
            params: Parameters with invoice number
        
        Returns:
            Result dictionary
        """
        invoice_no = params.get('번호', params.get('number', params.get('no')))
        
        if not invoice_no:
            return {
                'success': False,
                'message': 'Invoice number required. Use: duplicate invoice 번호="2025-001"'
            }
        
        # Get original invoice
        invoice_data = self.db.get_invoice_by_number(str(invoice_no))
        
        if not invoice_data:
            return {
                'success': False,
                'message': f'Invoice not found: {invoice_no}'
            }
        
        # Convert to Invoice object
        items = invoice_data.pop('items', [])
        original_invoice = Invoice.from_dict(invoice_data, items)
        
        # Create duplicate with new number
        new_invoice_no = self.db.get_next_invoice_number()
        new_invoice = original_invoice.duplicate(
            new_invoice_no=new_invoice_no,
            new_date=datetime.now()
        )
        
        # Trigger callback to load new invoice in GUI
        self._trigger_callback('invoice_created', new_invoice)
        
        return {
            'success': True,
            'message': f'Duplicated invoice {invoice_no} as {new_invoice_no}',
            'data': new_invoice
        }
