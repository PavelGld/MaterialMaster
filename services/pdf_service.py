import logging
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io
from datetime import datetime
from typing import Dict, Any
import html

class PDFService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup custom styles for PDF generation"""
        # Title style with safe font
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.black
        )
        
        # Heading style with safe font
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            spaceAfter=12,
            spaceBefore=16,
            textColor=colors.black
        )
        
        # Normal style with better spacing
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            textColor=colors.black
        )
        
        # List style
        self.list_style = ParagraphStyle(
            'CustomList',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=4,
            textColor=colors.black
        )
    
    def generate_report(self, analysis: Dict[str, Any], input_text: str, language: str = 'en') -> io.BytesIO:
        """
        Generate PDF report from analysis data
        
        Args:
            analysis (Dict): Analysis results
            input_text (str): Original input text
            language (str): Report language ('en' or 'ru')
            
        Returns:
            io.BytesIO: PDF buffer
        """
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            
            # Title
            title_text = "Material Selection Analysis Report" if language == 'en' else "Отчет по анализу подбора материалов"
            story.append(Paragraph(title_text, self.title_style))
            story.append(Spacer(1, 20))
            
            # Date
            date_text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            if language == 'ru':
                date_text = f"Создано: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
            story.append(Paragraph(date_text, self.normal_style))
            story.append(Spacer(1, 20))
            
            # Input data section
            input_title = "Input Data" if language == 'en' else "Исходные данные"
            story.append(Paragraph(input_title, self.heading_style))
            story.append(Paragraph(input_text, self.normal_style))
            story.append(Spacer(1, 15))
            
            # Analysis sections
            sections = self._get_report_sections(language)
            
            for section_key, section_title in sections.items():
                if section_key in analysis:
                    story.append(Paragraph(section_title, self.heading_style))
                    section_content = self._format_section_content(analysis[section_key], language)
                    story.extend(section_content)
                    story.append(Spacer(1, 15))
            
            # Build PDF
            doc.build(story)
            
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            self.logger.error(f"Error generating PDF report: {str(e)}")
            # Return empty buffer on error
            return io.BytesIO()
    
    def _get_report_sections(self, language: str) -> Dict[str, str]:
        """Get report section titles based on language"""
        if language == 'ru':
            return {
                'product_assessment': '1. ОЦЕНКА НАЗНАЧЕНИЯ ИЗДЕЛИЯ И УСЛОВИЙ ЭКСПЛУАТАЦИИ',
                'material_selection': '2. ВЫБОР И ОБОСНОВАНИЕ МАТЕРИАЛА',
                'manufacturing_technology': '3. ТЕХНОЛОГИЯ ИЗГОТОВЛЕНИЯ И ОБРАБОТКИ',
                'structural_characteristics': '4. ХАРАКТЕРИСТИКИ СТРУКТУРЫ МАТЕРИАЛА',
                'defect_analysis': '5. АНАЛИЗ БРАКА И МЕТОДЫ ИСПРАВЛЕНИЯ',
                'testing_methods': '6. МЕТОДЫ ОПРЕДЕЛЕНИЯ СВОЙСТВ МАТЕРИАЛОВ'
            }
        else:
            return {
                'product_assessment': '1. PRODUCT PURPOSE AND OPERATING CONDITIONS ASSESSMENT',
                'material_selection': '2. MATERIAL SELECTION AND JUSTIFICATION',
                'manufacturing_technology': '3. MANUFACTURING TECHNOLOGY AND PROCESSING',
                'structural_characteristics': '4. MATERIAL STRUCTURE CHARACTERISTICS',
                'defect_analysis': '5. DEFECT ANALYSIS AND CORRECTION METHODS',
                'testing_methods': '6. MATERIAL PROPERTIES TESTING METHODS'
            }
    
    def _format_section_content(self, section_data: Any, language: str) -> list:
        """Format section content for PDF"""
        content = []
        
        if isinstance(section_data, dict):
            for key, value in section_data.items():
                if isinstance(value, str) and value.strip():
                    # Format key as subsection
                    key_formatted = key.replace('_', ' ').title()
                    content.append(Paragraph(f"<b>{key_formatted}:</b>", self.normal_style))
                    content.append(Paragraph(value, self.normal_style))
                    content.append(Spacer(1, 8))
                    
                elif isinstance(value, list) and value:
                    key_formatted = key.replace('_', ' ').title()
                    content.append(Paragraph(f"<b>{key_formatted}:</b>", self.normal_style))
                    
                    for item in value:
                        if isinstance(item, str):
                            content.append(Paragraph(f"• {item}", self.list_style))
                    content.append(Spacer(1, 8))
                    
        elif isinstance(section_data, str):
            content.append(Paragraph(section_data, self.normal_style))
            
        elif isinstance(section_data, list):
            for item in section_data:
                if isinstance(item, str):
                    content.append(Paragraph(f"• {item}", self.list_style))
        
        return content
