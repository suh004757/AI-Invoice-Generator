"""
Command Bar widget for Invoice Command Studio
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QTextEdit, QCompleter
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QTextCursor
from ..commands.parser import get_command_suggestions


class CommandBar(QWidget):
    """Command input widget with history and autocomplete"""
    
    # Signal emitted when command is executed
    command_executed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.command_history = []
        self.history_index = -1
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Input row
        input_layout = QHBoxLayout()
        
        # Command input
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText(
            'Enter command (e.g., new tax invoice 고객="ABC Corp" 총액=3300000)'
        )
        self.command_input.setFont(QFont("Consolas", 10))
        self.command_input.returnPressed.connect(self.execute_command)
        
        # Setup autocomplete
        self.setup_autocomplete()
        
        # Run button
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.execute_command)
        self.run_button.setFixedWidth(80)
        
        input_layout.addWidget(self.command_input)
        input_layout.addWidget(self.run_button)
        
        # Command log
        self.command_log = QTextEdit()
        self.command_log.setReadOnly(True)
        self.command_log.setMaximumHeight(100)
        self.command_log.setFont(QFont("Consolas", 9))
        self.command_log.setPlaceholderText("Command history will appear here...")
        
        layout.addLayout(input_layout)
        layout.addWidget(self.command_log)
    
    def setup_autocomplete(self):
        """Setup autocomplete for command input"""
        suggestions = get_command_suggestions("")
        completer = QCompleter(suggestions, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.command_input.setCompleter(completer)
    
    def execute_command(self):
        """Execute the current command"""
        command = self.command_input.text().strip()
        
        if not command:
            return
        
        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Log command
        self.log_command(command)
        
        # Emit signal
        self.command_executed.emit(command)
        
        # Clear input
        self.command_input.clear()
    
    def log_command(self, command: str, result: str = None):
        """
        Log command to the command log
        
        Args:
            command: Command string
            result: Optional result message
        """
        # Move cursor to end
        cursor = self.command_log.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.command_log.setTextCursor(cursor)
        
        # Add command
        self.command_log.insertHtml(
            f'<span style="color: #0066cc; font-weight: bold;">&gt; {command}</span><br>'
        )
        
        # Add result if provided
        if result:
            color = "#008800" if "success" in result.lower() else "#cc0000"
            self.command_log.insertHtml(
                f'<span style="color: {color};">{result}</span><br>'
            )
        
        # Scroll to bottom
        self.command_log.verticalScrollBar().setValue(
            self.command_log.verticalScrollBar().maximum()
        )
    
    def log_result(self, message: str, is_success: bool = True):
        """
        Log result message
        
        Args:
            message: Result message
            is_success: Whether the result is success or error
        """
        cursor = self.command_log.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.command_log.setTextCursor(cursor)
        
        color = "#008800" if is_success else "#cc0000"
        self.command_log.insertHtml(
            f'<span style="color: {color};">  {message}</span><br>'
        )
        
        # Scroll to bottom
        self.command_log.verticalScrollBar().setValue(
            self.command_log.verticalScrollBar().maximum()
        )
    
    def keyPressEvent(self, event):
        """Handle key press for history navigation"""
        if event.key() == Qt.Key_Up:
            # Navigate up in history
            if self.history_index > 0:
                self.history_index -= 1
                self.command_input.setText(self.command_history[self.history_index])
        elif event.key() == Qt.Key_Down:
            # Navigate down in history
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.command_input.setText(self.command_history[self.history_index])
            else:
                self.history_index = len(self.command_history)
                self.command_input.clear()
        else:
            super().keyPressEvent(event)
