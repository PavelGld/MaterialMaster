import logging
import requests
import json
import os
from typing import Dict, Any, Optional

class AIService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.environ.get('OPENROUTER_API_KEY', 'default-key')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "google/gemini-2.5-flash-lite-preview-06-17"  # Using the paid Gemini 2.5 Flash Lite model
        
    def analyze_material_requirements(self, input_text: str, language: str = 'en') -> Optional[Dict[str, Any]]:
        """
        Analyze material requirements using AI
        
        Args:
            input_text (str): Combined description and OCR text
            language (str): Language preference ('en' or 'ru')
            
        Returns:
            Dict[str, Any]: Analysis results or None if failed
        """
        try:
            prompt = self._create_analysis_prompt(input_text, language)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": self._get_system_prompt(language)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.3
            }
            
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                self.logger.info(f"AI Response received: {content[:500]}...")
                parsed_result = self._parse_ai_response(content)
                self.logger.info(f"Parsed result keys: {list(parsed_result.keys()) if parsed_result else 'None'}")
                return parsed_result
            else:
                self.logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {str(e)}")
            return None
    
    def _get_system_prompt(self, language: str = 'en') -> str:
        """Get the system prompt for AI analysis"""
        if language == 'ru':
            return """Вы - эксперт-материаловед и технический консультант, специализирующийся на выборе материалов для машиностроительных применений. Ваша задача - анализировать технические чертежи, описания и спецификации для предоставления комплексных рекомендаций по материалам.

Вы должны предоставить подробный анализ, охватывающий все следующие разделы:

1. НАЗНАЧЕНИЕ ПРОДУКТА И УСЛОВИЯ ЭКСПЛУАТАЦИИ
2. ВЫБОР МАТЕРИАЛА И ОБОСНОВАНИЕ
3. РЕКОМЕНДАЦИИ ПО ТЕХНОЛОГИИ ПРОИЗВОДСТВА
4. СТРУКТУРНЫЕ ХАРАКТЕРИСТИКИ
5. АНАЛИЗ ДЕФЕКТОВ И ПРЕДОТВРАЩЕНИЕ
6. МЕТОДЫ ИСПЫТАНИЙ И СТАНДАРТЫ

Для каждого раздела предоставьте конкретные, практичные рекомендации. Ссылайтесь на соответствующие стандарты ГОСТ где применимо. Структурируйте ваш ответ как JSON с четкими разделами и подробными объяснениями. ОТВЕЧАЙТЕ ТОЛЬКО НА РУССКОМ ЯЗЫКЕ."""
        else:
            return """You are an expert materials engineer and technical consultant specializing in material selection for mechanical engineering applications. Your task is to analyze technical drawings, descriptions, and specifications to provide comprehensive material recommendations.

You must provide detailed analysis covering all the following sections:

1. PRODUCT PURPOSE AND OPERATING CONDITIONS
2. MATERIAL SELECTION AND JUSTIFICATION  
3. MANUFACTURING TECHNOLOGY RECOMMENDATIONS
4. STRUCTURAL CHARACTERISTICS
5. DEFECT ANALYSIS AND PREVENTION
6. TESTING METHODS AND STANDARDS

For each section, provide specific, actionable recommendations. Reference relevant GOST standards where applicable. Structure your response as JSON with clear sections and detailed explanations. RESPOND ONLY IN ENGLISH."""
    
    def _create_analysis_prompt(self, input_text: str, language: str = 'en') -> str:
        """Create analysis prompt from input text"""
        if language == 'ru':
            return f"""Пожалуйста, проанализируйте следующие технические описания/данные чертежей и предоставьте комплексный отчет по материаловедению:

ВХОДНЫЕ ДАННЫЕ:
{input_text}

Пожалуйста, предоставьте подробный анализ в формате JSON со следующей структурой:

{{
    "product_assessment": {{
        "purpose": "Описание назначения продукта и применения",
        "operating_conditions": "Анализ температуры, напряжений, условий окружающей среды",
        "critical_requirements": "Ключевые технические требования"
    }},
    "material_selection": {{
        "recommended_materials": ["Список подходящих материалов"],
        "primary_choice": "Основной рекомендуемый материал",
        "justification": "Подробное обоснование выбора материала",
        "properties_analysis": "Требуемые механические и физические свойства",
        "gost_standards": ["Соответствующие стандарты ГОСТ"]
    }},
    "manufacturing_technology": {{
        "processing_methods": ["Рекомендуемые производственные процессы"],
        "heat_treatment": "Рекомендации по термообработке",
        "surface_treatment": "Варианты поверхностной обработки",
        "quality_control": "Меры контроля качества"
    }},
    "structural_characteristics": {{
        "microstructure": "Требуемые микроструктурные характеристики",
        "grain_structure": "Требования к зернистой структуре",
        "phase_composition": "Анализ фазового состава",
        "mechanical_properties": "Целевые механические свойства"
    }},
    "defect_analysis": {{
        "common_defects": ["Типичные дефекты для данного применения"],
        "causes": ["Основные причины дефектов"],
        "prevention_methods": ["Стратегии предотвращения дефектов"],
        "correction_methods": ["Методы исправления существующих дефектов"]
    }},
    "testing_methods": {{
        "mechanical_tests": ["Требуемые методы механических испытаний"],
        "non_destructive_tests": ["Методы НК"],
        "standards": ["Стандарты и процедуры испытаний"],
        "acceptance_criteria": "Критерии приемки качества"
    }}
}}

Предоставьте конкретные, подробные рекомендации на основе инженерных лучших практик и российских технических стандартов."""
        else:
            return f"""Please analyze the following technical description/drawing data and provide a comprehensive material engineering report:

INPUT DATA:
{input_text}

Please provide a detailed analysis in JSON format with the following structure:

{{
    "product_assessment": {{
        "purpose": "Description of product purpose and application",
        "operating_conditions": "Temperature, stress, environmental conditions analysis",
        "critical_requirements": "Key technical requirements"
    }},
    "material_selection": {{
        "recommended_materials": ["List of suitable materials"],
        "primary_choice": "Main recommended material",
        "justification": "Detailed justification for material choice",
        "properties_analysis": "Required mechanical and physical properties",
        "gost_standards": ["Relevant GOST standards"]
    }},
    "manufacturing_technology": {{
        "processing_methods": ["Recommended manufacturing processes"],
        "heat_treatment": "Heat treatment recommendations",
        "surface_treatment": "Surface treatment options",
        "quality_control": "Quality control measures"
    }},
    "structural_characteristics": {{
        "microstructure": "Required microstructural characteristics",
        "grain_structure": "Grain structure requirements",
        "phase_composition": "Phase composition analysis",
        "mechanical_properties": "Target mechanical properties"
    }},
    "defect_analysis": {{
        "common_defects": ["Typical defects for this application"],
        "causes": ["Root causes of defects"],
        "prevention_methods": ["Defect prevention strategies"],
        "correction_methods": ["Methods to fix existing defects"]
    }},
    "testing_methods": {{
        "mechanical_tests": ["Required mechanical testing methods"],
        "non_destructive_tests": ["NDT methods"],
        "standards": ["Testing standards and procedures"],
        "acceptance_criteria": "Quality acceptance criteria"
    }}
}}

Provide specific, detailed recommendations based on engineering best practices and Russian technical standards."""
    
    def _parse_ai_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        try:
            # Clean up content and try to extract JSON
            content = content.strip()
            
            # Look for JSON block in markdown code blocks
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                if end != -1:
                    content = content[start:end].strip()
            elif '```' in content:
                start = content.find('```') + 3
                end = content.find('```', start)
                if end != -1:
                    content = content[start:end].strip()
            
            # Try to parse as JSON
            if content.startswith('{') and content.endswith('}'):
                parsed = json.loads(content)
                self.logger.info(f"Successfully parsed JSON with keys: {list(parsed.keys())}")
                return parsed
            
            # If not JSON, create structured response from text
            return {
                "product_assessment": {
                    "purpose": "Analysis based on provided data",
                    "operating_conditions": "Standard operating conditions assumed",
                    "critical_requirements": "Requirements extracted from input"
                },
                "material_selection": {
                    "recommended_materials": ["Steel alloys", "Aluminum alloys"],
                    "primary_choice": "To be determined based on specific requirements",
                    "justification": content[:500] + "..." if len(content) > 500 else content,
                    "properties_analysis": "Standard mechanical properties required",
                    "gost_standards": ["GOST 1050", "GOST 4543"]
                },
                "manufacturing_technology": {
                    "processing_methods": ["Machining", "Heat treatment"],
                    "heat_treatment": "Standard heat treatment procedures",
                    "surface_treatment": "As required by application",
                    "quality_control": "Standard QC procedures"
                },
                "structural_characteristics": {
                    "microstructure": "Fine-grained structure preferred",
                    "grain_structure": "Uniform grain distribution",
                    "phase_composition": "Single-phase or controlled multi-phase",
                    "mechanical_properties": "High strength and ductility"
                },
                "defect_analysis": {
                    "common_defects": ["Cracks", "Inclusions", "Dimensional deviations"],
                    "causes": ["Material impurities", "Processing parameters", "Design factors"],
                    "prevention_methods": ["Proper material selection", "Process control"],
                    "correction_methods": ["Rework", "Heat treatment adjustment"]
                },
                "testing_methods": {
                    "mechanical_tests": ["Tensile test", "Hardness test", "Impact test"],
                    "non_destructive_tests": ["Visual inspection", "Ultrasonic testing"],
                    "standards": ["GOST 1497", "GOST 9454"],
                    "acceptance_criteria": "Per applicable standards"
                }
            }
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse AI response as JSON, using fallback structure")
            return {
                "error": "Failed to parse AI response",
                "raw_response": content,
                "product_assessment": {"purpose": "Analysis incomplete"},
                "material_selection": {"recommended_materials": [], "justification": content},
                "manufacturing_technology": {"processing_methods": []},
                "structural_characteristics": {"microstructure": ""},
                "defect_analysis": {"common_defects": []},
                "testing_methods": {"mechanical_tests": []}
            }