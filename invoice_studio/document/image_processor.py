"""
Image processor with OCR capabilities
Extracts text from images using Tesseract OCR
"""
import os
from pathlib import Path
from typing import Optional
from PIL import Image
import pytesseract


class ImageProcessor:
    """Process images and extract text using OCR"""
    
    def __init__(self, tesseract_path: Optional[str] = None, lang: str = "kor+eng"):
        """
        Initialize image processor
        
        Args:
            tesseract_path: Path to tesseract executable (Windows)
            lang: OCR language (default: kor+eng for Korean and English)
        """
        self.lang = lang
        
        # Set Tesseract path if provided
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def extract_text(self, image_path: str) -> str:
        """
        Extract text from image using OCR
        
        Args:
            image_path: Path to image file
        
        Returns:
            str: Extracted text
        """
        try:
            # Open image
            image = Image.open(image_path)
            
            # Preprocess image for better OCR
            image = self._preprocess_image(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang=self.lang)
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Failed to extract text from image: {str(e)}")
    
    def extract_text_from_pil(self, image: Image.Image) -> str:
        """
        Extract text from PIL Image object
        
        Args:
            image: PIL Image object
        
        Returns:
            str: Extracted text
        """
        try:
            # Preprocess image
            image = self._preprocess_image(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang=self.lang)
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PIL image: {str(e)}")
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results
        
        Args:
            image: PIL Image object
        
        Returns:
            Image: Preprocessed image
        """
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too small (improves OCR accuracy)
        width, height = image.size
        if width < 1000 or height < 1000:
            scale_factor = max(1000 / width, 1000 / height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    def get_image_info(self, image_path: str) -> dict:
        """
        Get image information
        
        Args:
            image_path: Path to image file
        
        Returns:
            dict: Image information (size, format, mode)
        """
        try:
            image = Image.open(image_path)
            return {
                "size": image.size,
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode
            }
        except Exception as e:
            raise Exception(f"Failed to get image info: {str(e)}")
    
    def is_supported_format(self, file_path: str) -> bool:
        """
        Check if file format is supported
        
        Args:
            file_path: Path to file
        
        Returns:
            bool: True if supported
        """
        supported_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']
        ext = Path(file_path).suffix.lower()
        return ext in supported_formats
