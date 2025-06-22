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
        self.model = "google/gemini-2.0-flash-exp:free"  # Using the free Gemini 2.0 Flash model
        
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
                
                # Parse the structured response
                analysis = self._parse_ai_response(content)
                return analysis
            else:
                self.logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {str(e)}")
            return None
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI analysis"""
        return """You are an expert materials engineer and technical consultant specializing in material selection for mechanical engineering applications. Your task is to analyze technical drawings, descriptions, and specifications to provide comprehensive material recommendations.

You must provide detailed analysis covering all the following sections:

1. PRODUCT PURPOSE AND OPERATING CONDITIONS
2. MATERIAL SELECTION AND JUSTIFICATION  
3. MANUFACTURING TECHNOLOGY RECOMMENDATIONS
4. STRUCTURAL CHARACTERISTICS
5. DEFECT ANALYSIS AND PREVENTION
6. TESTING METHODS AND STANDARDS

For each section, provide specific, actionable recommendations. Reference relevant GOST standards where applicable. Structure your response as JSON with clear sections and detailed explanations."""
    
    def _create_analysis_prompt(self, input_text: str) -> str:
        """Create analysis prompt from input text"""
        if language == 'ru':
            return f"""Пожалуйста, проанализируйте следующие технические описания/данные чертежей и предоставьте комплексный отчет по материаловедению:

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
            # Try to parse as JSON first
            if content.strip().startswith('{'):
                return json.loads(content)
            
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
                    "grain_structure": "Uniform grain structure",
                    "phase_composition": "Balanced phase composition",
                    "mechanical_properties": "High strength and ductility"
                },
                "defect_analysis": {
                    "common_defects": ["Cracks", "Inclusions", "Dimensional deviations"],
                    "causes": ["Material defects", "Processing errors", "Design issues"],
                    "prevention_methods": ["Proper material selection", "Process control"],
                    "correction_methods": ["Repair welding", "Machining", "Heat treatment"]
                },
                "testing_methods": {
                    "mechanical_tests": ["Tensile test", "Hardness test", "Impact test"],
                    "non_destructive_tests": ["Visual inspection", "Ultrasonic testing"],
                    "standards": ["GOST 1497", "GOST 9454"],
                    "acceptance_criteria": "Per applicable standards"
                },
                "raw_response": content
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
