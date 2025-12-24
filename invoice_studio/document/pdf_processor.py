"""
PDF document processor
Extracts text and images from PDF files
"""
import io
from pathlib import Path
from typing import Optional, List, Tuple
import pdfplumber
from PIL import Image


class PDFProcessor:
    """Process PDF documents to extract text and images"""
    
    def __init__(self):
        """Initialize PDF processor"""
        pass
    
    def extract_text(self, pdf_path: str) -> Tuple[str, bool]:
        """
        Extract text from PDF
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            tuple: (extracted_text, is_scanned)
                - extracted_text: All text from PDF
                - is_scanned: True if PDF appears to be scanned (image-based)
        """
        try:
            all_text = []
            is_scanned = False
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text
                    text = page.extract_text()
                    
                    if text:
                        all_text.append(f"--- Page {page_num} ---\n{text}")
                    else:
                        # No text found - likely scanned PDF
                        is_scanned = True
            
            combined_text = "\n\n".join(all_text)
            
            # If very little text extracted, consider it scanned
            if len(combined_text.strip()) < 50:
                is_scanned = True
            
            return combined_text, is_scanned
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_images(self, pdf_path: str, output_dir: Optional[str] = None) -> List[str]:
        """
        Extract images from PDF pages
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save extracted images (optional)
        
        Returns:
            list: Paths to extracted image files
        """
        try:
            image_paths = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Convert page to image
                    img = page.to_image(resolution=300)  # High resolution for OCR
                    
                    if output_dir:
                        # Save image
                        output_path = Path(output_dir) / f"page_{page_num}.png"
                        img.save(str(output_path))
                        image_paths.append(str(output_path))
                    else:
                        # Return PIL Image object
                        image_paths.append(img.original)
            
            return image_paths
            
        except Exception as e:
            raise Exception(f"Failed to extract images from PDF: {str(e)}")
    
    def get_page_count(self, pdf_path: str) -> int:
        """
        Get number of pages in PDF
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            int: Number of pages
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                return len(pdf.pages)
        except Exception as e:
            raise Exception(f"Failed to get page count: {str(e)}")
    
    def extract_page_text(self, pdf_path: str, page_num: int) -> str:
        """
        Extract text from specific page
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (1-indexed)
        
        Returns:
            str: Text from page
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page_num < 1 or page_num > len(pdf.pages):
                    raise ValueError(f"Invalid page number: {page_num}")
                
                page = pdf.pages[page_num - 1]
                text = page.extract_text()
                
                return text or ""
                
        except Exception as e:
            raise Exception(f"Failed to extract text from page {page_num}: {str(e)}")
    
    def is_text_based(self, pdf_path: str) -> bool:
        """
        Check if PDF is text-based or scanned
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            bool: True if text-based, False if scanned
        """
        text, is_scanned = self.extract_text(pdf_path)
        return not is_scanned
