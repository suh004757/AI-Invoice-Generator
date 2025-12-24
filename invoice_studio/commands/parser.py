"""
Command parser for Invoice Command Studio DSL
"""
import re
from typing import Dict, Optional, List


class CommandParser:
    """Parse command-line style commands"""
    
    # Command patterns
    PATTERNS = {
        'new_tax': r'^new\s+tax\s+invoice',
        'new_normal': r'^new\s+normal\s+invoice',
        'search': r'^search\s+invoice',
        'open': r'^open\s+invoice',
        'duplicate': r'^duplicate\s+invoice',
    }
    
    def __init__(self):
        """Initialize parser"""
        pass
    
    def parse(self, command: str) -> Optional[Dict]:
        """
        Parse command string
        
        Args:
            command: Command string
        
        Returns:
            Dictionary with parsed command, or None if invalid
        """
        command = command.strip()
        
        if not command:
            return None
        
        # Determine command type
        cmd_type = self._identify_command(command)
        
        if not cmd_type:
            return {
                'type': 'unknown',
                'raw': command,
                'error': 'Unknown command. Try: new tax invoice, new normal invoice, search invoice, open invoice, duplicate invoice'
            }
        
        # Parse parameters
        params = self._parse_parameters(command)
        
        return {
            'type': cmd_type,
            'params': params,
            'raw': command
        }
    
    def _identify_command(self, command: str) -> Optional[str]:
        """Identify command type from string"""
        command_lower = command.lower()
        
        for cmd_type, pattern in self.PATTERNS.items():
            if re.match(pattern, command_lower):
                return cmd_type
        
        return None
    
    def _parse_parameters(self, command: str) -> Dict:
        """
        Parse key-value parameters from command
        
        Supports formats:
        - 고객="ABC Corp"
        - 총액=3300000
        - 월=2025-12
        - 통화="USD"
        
        Args:
            command: Command string
        
        Returns:
            Dictionary of parameters
        """
        params = {}
        
        # Pattern for key="value" or key=value
        pattern = r'(\w+)=(?:"([^"]+)"|(\S+))'
        
        matches = re.finditer(pattern, command)
        
        for match in matches:
            key = match.group(1)
            # Value is either in quotes (group 2) or without (group 3)
            value = match.group(2) if match.group(2) else match.group(3)
            
            # Try to convert to number if possible
            try:
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                # Keep as string
                pass
            
            params[key] = value
        
        return params
    
    def get_suggestions(self, partial_command: str) -> List[str]:
        """
        Get command suggestions for autocomplete
        
        Args:
            partial_command: Partial command string
        
        Returns:
            List of suggested commands
        """
        suggestions = [
            'new tax invoice 고객="" 총액=',
            'new normal invoice 고객="" 통화="USD"',
            'search invoice 고객="" 월=',
            'open invoice 번호=""',
            'duplicate invoice 번호=""',
        ]
        
        if not partial_command:
            return suggestions
        
        partial_lower = partial_command.lower()
        
        # Filter suggestions that start with partial command
        filtered = [s for s in suggestions if s.lower().startswith(partial_lower)]
        
        if filtered:
            return filtered
        
        # If no exact match, return suggestions that contain any word from partial
        words = partial_lower.split()
        if words:
            filtered = [s for s in suggestions if any(word in s.lower() for word in words)]
        
        return filtered if filtered else suggestions


# Singleton instance
_parser = CommandParser()


def parse_command(command: str) -> Optional[Dict]:
    """
    Parse command string (convenience function)
    
    Args:
        command: Command string
    
    Returns:
        Parsed command dictionary
    """
    return _parser.parse(command)


def get_command_suggestions(partial: str) -> List[str]:
    """
    Get command suggestions (convenience function)
    
    Args:
        partial: Partial command
    
    Returns:
        List of suggestions
    """
    return _parser.get_suggestions(partial)
