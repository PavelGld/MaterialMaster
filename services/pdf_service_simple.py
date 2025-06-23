import logging
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
from datetime import datetime
from typing import Dict, Any

class PDFService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup custom styles for PDF generation"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.black
        )
        
        # Heading style
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            spaceAfter=12,
            spaceBefore=16,
            textColor=colors.black
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            spaceAfter=6,
            alignment=TA_LEFT,
            textColor=colors.black
        )
        
        # List style
        self.list_style = ParagraphStyle(
            'CustomList',
            parent=self.styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leftIndent=20,
            spaceAfter=4,
            textColor=colors.black
        )
    
    def generate_report(self, analysis: Dict[str, Any], input_text: str, language: str = 'en') -> io.BytesIO:
        """Generate PDF report from analysis data"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            story = []
            
            # Title
            title_text = "Material Analysis Report" if language == 'en' else "Otchet po analizu materialov"
            story.append(Paragraph(title_text, self.title_style))
            story.append(Spacer(1, 20))
            
            # Date
            date_text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            if language == 'ru':
                date_text = f"Sozdano: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
            story.append(Paragraph(date_text, self.normal_style))
            story.append(Spacer(1, 20))
            
            # Input data
            input_title = "Input Data" if language == 'en' else "Iskhodnye dannye"
            story.append(Paragraph(input_title, self.heading_style))
            clean_input = self._clean_text(input_text[:500] + "..." if len(input_text) > 500 else input_text)
            story.append(Paragraph(clean_input, self.normal_style))
            story.append(Spacer(1, 15))
            
            # Analysis sections
            sections = self._get_sections(language)
            
            for section_key, section_title in sections.items():
                if section_key in analysis:
                    story.append(Paragraph(section_title, self.heading_style))
                    content = self._format_content(analysis[section_key])
                    story.extend(content)
                    story.append(Spacer(1, 15))
            
            doc.build(story)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            self.logger.error(f"Error generating PDF: {str(e)}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean text for safe PDF generation"""
        if not text:
            return ""
        
        # Convert to string and handle encoding
        clean_text = str(text)
        
        # Replace problematic characters
        replacements = {
            'σ': 'sigma',
            '°': ' deg',
            '≥': '>=',
            '≤': '<=',
            'МПа': 'MPa',
            'НВ': 'HB',
            'Дж/см²': 'J/cm2',
            '№': 'No.',
            '–': '-',
            '—': '-',
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            'µ': 'micro'
        }
        
        for old, new in replacements.items():
            clean_text = clean_text.replace(old, new)
        
        # Remove any remaining problematic characters
        try:
            clean_text.encode('ascii', 'ignore').decode('ascii')
        except:
            pass
            
        return clean_text
    
    def _format_content(self, data) -> list:
        """Format content for PDF"""
        content = []
        
        if isinstance(data, str):
            clean_text = self._clean_text(data)
            content.append(Paragraph(clean_text, self.normal_style))
        elif isinstance(data, list):
            for item in data:
                clean_item = self._clean_text(str(item))
                content.append(Paragraph(f"* {clean_item}", self.list_style))
        elif isinstance(data, dict):
            for key, value in data.items():
                clean_key = self._clean_text(str(key))
                if isinstance(value, str):
                    clean_value = self._clean_text(value)
                    content.append(Paragraph(f"{clean_key}: {clean_value}", self.normal_style))
                elif isinstance(value, list):
                    content.append(Paragraph(f"{clean_key}:", self.normal_style))
                    for item in value:
                        clean_item = self._clean_text(str(item))
                        content.append(Paragraph(f"* {clean_item}", self.list_style))
        
        return content
    
    def _get_sections(self, language: str) -> Dict[str, str]:
        """Get section titles"""
        if language == 'ru':
            return {
                'product_assessment': '1. Otsenka naznacheniya izdeliya',
                'material_selection': '2. Vybor materiala',
                'manufacturing_technology': '3. Tekhnologiya izgotovleniya',
                'structural_characteristics': '4. Strukturnye kharakteristiki',
                'defect_analysis': '5. Analiz defektov',
                'testing_methods': '6. Metody ispytaniy'
            }
        else:
            return {
                'product_assessment': '1. Product Assessment',
                'material_selection': '2. Material Selection',
                'manufacturing_technology': '3. Manufacturing Technology',
                'structural_characteristics': '4. Structural Characteristics',
                'defect_analysis': '5. Defect Analysis',
                'testing_methods': '6. Testing Methods'
            }