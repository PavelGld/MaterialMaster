import logging
import pytesseract
from PIL import Image
import os

class OCRService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configure tesseract for Russian and English languages
        self.languages = 'rus+eng'
        
    def extract_text(self, image_path):
        """
        Extract text from image using OCR
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Extracted text or empty string if no text found
        """
        try:
            if not os.path.exists(image_path):
                self.logger.error(f"Image file not found: {image_path}")
                return ""
            
            # Open and process image
            with Image.open(image_path) as image:
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Extract text using tesseract
                text = pytesseract.image_to_string(
                    image, 
                    lang=self.languages,
                    config='--oem 3 --psm 6'  # Use LSTM OCR Engine Mode with uniform block of text
                )
                
                # Clean up the extracted text
                cleaned_text = self._clean_text(text)
                
                self.logger.info(f"Successfully extracted {len(cleaned_text)} characters from image")
                return cleaned_text
                
        except Exception as e:
            self.logger.error(f"Error during OCR processing: {str(e)}")
            return ""
    
    def _clean_text(self, text):
        """
        Clean and normalize extracted text
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace and normalize line breaks
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if line:  # Only add non-empty lines
                lines.append(line)
        
        # Join lines with single spaces, preserving paragraph breaks
        cleaned = '\n'.join(lines)
        
        # Remove excessive whitespace
        import re
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        
        return cleaned.strip()
    
    def is_tesseract_available(self):
        """
        Check if tesseract is available on the system
        
        Returns:
            bool: True if tesseract is available
        """
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
