"""
Data extractor - Main orchestrator for PO to Invoice data extraction
Uses LLM to extract structured data from PO documents
"""
import json
from typing import Dict, Optional, Tuple
from .llm_client import LLMClient
from .prompts import create_extraction_prompt, create_validation_prompt


class DataExtractor:
    """Extracts invoice data from PO documents using LLM"""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize data extractor
        
        Args:
            llm_client: Configured LLM client
        """
        self.llm_client = llm_client
    
    def extract(self, po_text: str, invoice_type: str = "tax") -> Tuple[Optional[Dict], float, Optional[str]]:
        """
        Extract invoice data from PO text
        
        Args:
            po_text: Raw text from PO document
            invoice_type: 'tax' or 'normal'
        
        Returns:
            tuple: (extracted_data dict, confidence_score float, error_message str or None)
        """
        try:
            # Create extraction prompt
            system_prompt, user_prompt = create_extraction_prompt(po_text, invoice_type)
            
            # Call LLM
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.llm_client.chat(messages)
            
            # Parse JSON from response
            extracted_data = self._parse_json_response(response)
            
            if not extracted_data:
                return None, 0.0, "Failed to parse JSON from LLM response"
            
            # Validate extracted data
            confidence_score = self._calculate_confidence(extracted_data, po_text)
            
            # Ensure VAT calculation is correct based on invoice type
            extracted_data = self._fix_vat_calculation(extracted_data, invoice_type)
            
            return extracted_data, confidence_score, None
            
        except Exception as e:
            return None, 0.0, f"Extraction error: {str(e)}"
    
    def validate(self, extracted_data: Dict, po_text: str) -> Dict:
        """
        Validate extracted data against original PO
        
        Args:
            extracted_data: Previously extracted data
            po_text: Original PO text
        
        Returns:
            dict: Validation results with is_valid, confidence_score, errors, warnings
        """
        try:
            system_prompt, user_prompt = create_validation_prompt(extracted_data, po_text)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.llm_client.chat(messages)
            validation_result = self._parse_json_response(response)
            
            if not validation_result:
                return {
                    "is_valid": False,
                    "confidence_score": 0.0,
                    "errors": ["Failed to parse validation response"],
                    "warnings": [],
                    "suggestions": []
                }
            
            return validation_result
            
        except Exception as e:
            return {
                "is_valid": False,
                "confidence_score": 0.0,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "suggestions": []
            }
    
    def _parse_json_response(self, response: str) -> Optional[Dict]:
        """
        Parse JSON from LLM response
        Handles cases where LLM wraps JSON in code blocks
        
        Args:
            response: Raw LLM response
        
        Returns:
            dict or None: Parsed JSON data
        """
        try:
            # Remove markdown code blocks if present
            json_str = response.strip()
            
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            data = json.loads(json_str)
            return data
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response: {response[:500]}...")  # Print first 500 chars for debugging
            return None
        except Exception as e:
            print(f"Unexpected error parsing response: {e}")
            return None
    
    def _calculate_confidence(self, extracted_data: Dict, po_text: str) -> float:
        """
        Calculate confidence score for extracted data
        
        Args:
            extracted_data: Extracted data dict
            po_text: Original PO text
        
        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        confidence = 1.0
        
        # Check required fields
        required_fields = ["customer_name", "items", "total"]
        for field in required_fields:
            if field not in extracted_data or not extracted_data[field]:
                confidence -= 0.2
        
        # Check if items have required fields
        if "items" in extracted_data and extracted_data["items"]:
            for item in extracted_data["items"]:
                if not all(k in item for k in ["description", "quantity", "unit_price", "amount"]):
                    confidence -= 0.1
        else:
            confidence -= 0.3
        
        # Check calculation accuracy
        if "items" in extracted_data and extracted_data["items"]:
            calculated_subtotal = sum(item.get("amount", 0) for item in extracted_data["items"])
            extracted_subtotal = extracted_data.get("subtotal", 0)
            
            if abs(calculated_subtotal - extracted_subtotal) > 0.01:
                confidence -= 0.1
        
        # Check VAT calculation
        if "subtotal" in extracted_data and "vat" in extracted_data:
            expected_vat = extracted_data["subtotal"] * 0.1
            actual_vat = extracted_data.get("vat", 0)
            
            if abs(expected_vat - actual_vat) > 0.01 and actual_vat != 0:
                confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _fix_vat_calculation(self, data: Dict, invoice_type: str) -> Dict:
        """
        Ensure VAT calculation is correct based on invoice type
        
        Args:
            data: Extracted data
            invoice_type: 'tax' or 'normal'
        
        Returns:
            dict: Data with corrected VAT
        """
        if "subtotal" not in data:
            # Calculate subtotal from items
            if "items" in data and data["items"]:
                data["subtotal"] = sum(item.get("amount", 0) for item in data["items"])
        
        subtotal = data.get("subtotal", 0)
        
        if invoice_type.lower() == "tax":
            # Tax invoice: VAT = 10% of subtotal
            data["vat"] = round(subtotal * 0.1, 2)
            data["total"] = round(subtotal + data["vat"], 2)
        else:
            # Normal invoice: VAT = 0
            data["vat"] = 0
            data["total"] = subtotal
        
        return data
