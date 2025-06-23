import logging
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from datetime import datetime
from typing import Dict, Any
import os

class PDFService:
    """
    PDF report generation service with full Unicode and Cyrillic support
    Creates professional material analysis reports with proper font handling
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.styles = getSampleStyleSheet()
        self._register_fonts()    # Setup Unicode fonts for proper text rendering
        self._setup_styles()      # Configure custom styles for report sections
    
    def _register_fonts(self):
        """
        Register Unicode-compatible fonts for proper Cyrillic text rendering
        DejaVu fonts provide comprehensive Unicode support including Russian characters
        """
        try:
            # Attempt to register DejaVu fonts for full Unicode support
            dejavu_path = '/usr/share/fonts/truetype/dejavu'
            if os.path.exists(dejavu_path):
                pdfmetrics.registerFont(TTFont('DejaVu', f'{dejavu_path}/DejaVuSans.ttf'))
                pdfmetrics.registerFont(TTFont('DejaVu-Bold', f'{dejavu_path}/DejaVuSans-Bold.ttf'))
                self.font_name = 'DejaVu'
                self.font_bold = 'DejaVu-Bold'
                self.logger.info("DejaVu fonts registered successfully")
            else:
                raise FileNotFoundError("DejaVu fonts not found")
        except Exception as e:
            self.logger.warning(f"Could not register DejaVu fonts: {e}")
            # Fallback to standard Helvetica (limited Unicode support)
            # Will trigger transliteration for Cyrillic text
            self.font_name = 'Helvetica'
            self.font_bold = 'Helvetica-Bold'
    
    def _setup_styles(self):
        """Setup custom styles for PDF generation"""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontName=self.font_bold,
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.black
        )
        
        # Heading style
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontName=self.font_bold,
            fontSize=14,
            spaceAfter=12,
            spaceBefore=16,
            textColor=colors.black
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontName=self.font_name,
            fontSize=11,
            spaceAfter=6,
            alignment=TA_LEFT,
            textColor=colors.black
        )
        
        # List style
        self.list_style = ParagraphStyle(
            'CustomList',
            parent=self.styles['Normal'],
            fontName=self.font_name,
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
            if language == 'ru':
                title_text = "Отчет по анализу материалов" if self.font_name == 'DejaVu' else "Otchet po analizu materialov"
            else:
                title_text = "Material Analysis Report"
            story.append(Paragraph(title_text, self.title_style))
            story.append(Spacer(1, 20))
            
            # Date
            date_text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            if language == 'ru':
                if self.font_name == 'DejaVu':
                    date_text = f"Создано: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
                else:
                    date_text = f"Sozdano: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
            story.append(Paragraph(date_text, self.normal_style))
            story.append(Spacer(1, 20))
            
            # Input data
            if language == 'ru':
                input_title = "Исходные данные" if self.font_name == 'DejaVu' else "Iskhodnye dannye"
            else:
                input_title = "Input Data"
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
        
        clean_text = str(text)
        
        # If using Helvetica font, transliterate Cyrillic
        if self.font_name == 'Helvetica':
            # Simple transliteration for basic Cyrillic characters
            cyrillic_map = {
                'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
                'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
                'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
                'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
                'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo', 'Ж': 'Zh',
                'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O',
                'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts',
                'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch', 'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
            }
            
            for cyrillic, latin in cyrillic_map.items():
                clean_text = clean_text.replace(cyrillic, latin)
        
        # Replace problematic symbols regardless of font
        replacements = {
            'σ': 'sigma',
            '°': ' grad',
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
            'µ': 'mikro',
            '•': '*',
            '…': '...'
        }
        
        for old, new in replacements.items():
            clean_text = clean_text.replace(old, new)
            
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
            if self.font_name == 'DejaVu':
                return {
                    'product_assessment': '1. Оценка назначения изделия и условий эксплуатации',
                    'material_selection': '2. Выбор и обоснование материала',
                    'manufacturing_technology': '3. Технология изготовления и обработки',
                    'structural_characteristics': '4. Структурные характеристики материала',
                    'defect_analysis': '5. Анализ дефектов и предотвращение',
                    'testing_methods': '6. Методы испытаний свойств материала'
                }
            else:
                return {
                    'product_assessment': '1. Otsenka naznacheniya izdeliya i usloviy ekspluatatsii',
                    'material_selection': '2. Vybor i obosnovanie materiala',
                    'manufacturing_technology': '3. Tekhnologiya izgotovleniya i obrabotki',
                    'structural_characteristics': '4. Strukturnye kharakteristiki materiala',
                    'defect_analysis': '5. Analiz defektov i predotvrashchenie',
                    'testing_methods': '6. Metody ispytaniy svoystv materiala'
                }
        else:
            return {
                'product_assessment': '1. Product Purpose and Operating Conditions Assessment',
                'material_selection': '2. Material Selection and Justification',
                'manufacturing_technology': '3. Manufacturing Technology and Processing',
                'structural_characteristics': '4. Material Structure Characteristics',
                'defect_analysis': '5. Defect Analysis and Prevention',
                'testing_methods': '6. Material Properties Testing Methods'
            }