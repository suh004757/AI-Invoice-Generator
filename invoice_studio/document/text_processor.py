"""
Text processor for cleaning and normalizing text
"""
import re
from typing import Optional


class TextProcessor:
    """Process and clean text data"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text
        
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with parsing
        # but keep important punctuation
        text = re.sub(r'[^\w\s\-.,:()\[\]/@$₩€¥%]', '', text)
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text.strip()
    
    @staticmethod
    def extract_email_body(email_text: str) -> str:
        """
        Extract body from email text
        Removes headers and signatures
        
        Args:
            email_text: Full email text
        
        Returns:
            str: Email body
        """
        # Simple heuristic: remove common email headers
        lines = email_text.split('\n')
        body_lines = []
        in_body = False
        
        for line in lines:
            # Skip header lines
            if not in_body and ':' in line:
                header_keywords = ['from:', 'to:', 'subject:', 'date:', 'cc:', 'bcc:']
                if any(line.lower().startswith(kw) for kw in header_keywords):
                    continue
            
            in_body = True
            
            # Stop at signature
            if line.strip() in ['--', '---', 'Best regards', 'Regards', 'Thanks']:
                break
            
            body_lines.append(line)
        
        return '\n'.join(body_lines).strip()
    
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect if text is primarily Korean or English
        
        Args:
            text: Text to analyze
        
        Returns:
            str: 'korean', 'english', or 'mixed'
        """
        if not text:
            return 'unknown'
        
        # Count Korean characters (Hangul)
        korean_chars = len(re.findall(r'[가-힣]', text))
        
        # Count English characters
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        total = korean_chars + english_chars
        
        if total == 0:
            return 'unknown'
        
        korean_ratio = korean_chars / total
        
        if korean_ratio > 0.7:
            return 'korean'
        elif korean_ratio < 0.3:
            return 'english'
        else:
            return 'mixed'
    
    @staticmethod
    def normalize_currency(text: str) -> str:
        """
        Normalize currency symbols to standard codes
        
        Args:
            text: Text with currency symbols
        
        Returns:
            str: Text with normalized currency codes
        """
        # Replace currency symbols with codes
        replacements = {
            '$': 'USD',
            '₩': 'KRW',
            '€': 'EUR',
            '¥': 'JPY',
            '£': 'GBP'
        }
        
        for symbol, code in replacements.items():
            text = text.replace(symbol, code)
        
        return text
    
    @staticmethod
    def extract_numbers(text: str) -> list:
        """
        Extract all numbers from text
        
        Args:
            text: Text to search
        
        Returns:
            list: List of numbers found
        """
        # Match numbers with optional commas and decimals
        pattern = r'\d{1,3}(?:,\d{3})*(?:\.\d+)?'
        matches = re.findall(pattern, text)
        
        # Remove commas and convert to float
        numbers = [float(m.replace(',', '')) for m in matches]
        
        return numbers
