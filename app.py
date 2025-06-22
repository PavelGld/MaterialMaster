import os
import logging
from flask import Flask, request, render_template, redirect, url_for, flash, session, send_file
from flask_babel import Babel
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import tempfile

from services.ocr_service import OCRService
from services.ai_service import AIService
from services.vector_service import VectorService
from services.pdf_service import PDFService
from utils.file_utils import allowed_file, save_uploaded_file
from config import Config

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Locale selector function
def get_locale():
    # Check if user has set a language preference
    if 'language' in session:
        return session['language']
    # Otherwise try to guess the language from the user accept header
    return request.accept_languages.best_match(['ru', 'en'], default='en')

# Simple translation function fallback
def simple_gettext(text):
    """Simple fallback translation function"""
    # Russian translations map
    ru_translations = {
        'AI Material Selection': 'ИИ подбор материалов',
        'Material Selection Analysis': 'Анализ выбора материалов',
        'About': 'О системе',
        'AI-powered material selection system for engineering applications': 'Система подбора материалов на основе ИИ для инженерных приложений',
        'Material Analysis System': 'Система анализа материалов',
        'Upload technical drawings or provide descriptions for AI-powered material recommendations': 'Загрузите технические чертежи или предоставьте описания для рекомендаций материалов на основе ИИ',
        'Input Data': 'Входные данные',
        'Technical Description': 'Техническое описание',
        'Describe the component, its purpose, operating conditions, and requirements...': 'Опишите компонент, его назначение, условия эксплуатации и требования...',
        'Provide detailed information about the component including dimensions, operating temperature, loads, environment, etc.': 'Предоставьте подробную информацию о компоненте, включая размеры, рабочую температуру, нагрузки, окружающую среду и т.д.',
        'Technical Drawing': 'Технический чертеж',
        'Upload PNG or JPEG images. OCR will extract text from technical drawings.': 'Загрузите изображения PNG или JPEG. OCR извлечет текст из технических чертежей.',
        'Note:': 'Примечание:',
        'You can provide either a text description, upload a drawing, or both. The system will analyze all available information to provide comprehensive material recommendations.': 'Вы можете предоставить текстовое описание, загрузить чертеж или и то, и другое. Система проанализирует всю доступную информацию для предоставления комплексных рекомендаций по материалам.',
        'Analyze Materials': 'Анализировать материалы',
        'OCR Processing': 'OCR обработка',
        'Extract text from technical drawings using advanced OCR technology': 'Извлечение текста из технических чертежей с использованием передовой технологии OCR',
        'AI Analysis': 'ИИ анализ',
        'Powered by Google Gemini for intelligent material recommendations': 'На основе Google Gemini для интеллектуальных рекомендаций материалов',
        'PDF Reports': 'PDF отчеты',
        'Generate professional PDF reports with detailed analysis': 'Создание профессиональных PDF отчетов с подробным анализом',
        'Analysis Report Sections': 'Разделы аналитического отчета',
        'Product Purpose Assessment': 'Оценка назначения продукта',
        'Material Selection & Justification': 'Выбор материала и обоснование',
        'Manufacturing Technology': 'Технология производства',
        'Structural Characteristics': 'Структурные характеристики',
        'Defect Analysis & Prevention': 'Анализ дефектов и предотвращение',
        'Testing Methods & Standards': 'Методы испытаний и стандарты',
        'Please provide either a text description or upload a drawing.': 'Пожалуйста, предоставьте текстовое описание или загрузите чертеж.',
        'Text successfully extracted from drawing.': 'Текст успешно извлечен из чертежа.',
        'No text could be extracted from the drawing.': 'Из чертежа не удалось извлечь текст.',
        'Invalid file format. Please upload PNG or JPEG files only.': 'Неверный формат файла. Пожалуйста, загружайте только файлы PNG или JPEG.',
        'No text available for analysis.': 'Нет текста для анализа.',
        'Failed to generate material analysis. Please try again.': 'Не удалось сгенерировать анализ материала. Пожалуйста, попробуйте еще раз.',
        'No analysis available for PDF generation.': 'Нет анализа для создания PDF.',
        'File size must be less than 16MB': 'Размер файла должен быть менее 16МБ',
        'Please upload PNG or JPEG files only': 'Пожалуйста, загружайте только файлы PNG или JPEG',
        'Please provide either a text description or upload a drawing': 'Пожалуйста, предоставьте текстовое описание или загрузите чертеж',
        'Processing...': 'Обработка...',
        'Page Not Found': 'Страница не найдена',
        'The page you are looking for does not exist.': 'Страница, которую вы ищете, не существует.',
        'Return to Home': 'Вернуться на главную',
        'Internal Server Error': 'Внутренняя ошибка сервера',
        'Something went wrong on our end. Please try again later.': 'Что-то пошло не так с нашей стороны. Пожалуйста, попробуйте позже.'
    }
    
    current_locale = get_locale()
    if current_locale == 'ru' and text in ru_translations:
        return ru_translations[text]
    return text

# Make functions available to templates
@app.context_processor
def inject_template_vars():
    return {
        '_': simple_gettext,
        'get_locale': get_locale
    }

# Initialize services
ocr_service = OCRService()
ai_service = AIService()
vector_service = VectorService()
pdf_service = PDFService()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_language/<language>')
def set_language(language=None):
    session['language'] = language
    return redirect(request.referrer or url_for('index'))

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Get form data
        description = request.form.get('description', '')
        uploaded_file = request.files.get('drawing')
        
        if not description and not uploaded_file:
            flash(simple_gettext('Please provide either a text description or upload a drawing.'), 'error')
            return redirect(url_for('index'))
        
        # Process uploaded file if provided
        ocr_text = ""
        if uploaded_file and uploaded_file.filename and allowed_file(uploaded_file.filename):
            try:
                # Save uploaded file
                file_path = save_uploaded_file(uploaded_file)
                
                # Extract text using OCR
                ocr_text = ocr_service.extract_text(file_path)
                
                # Clean up uploaded file
                os.remove(file_path)
                
                if ocr_text:
                    flash(simple_gettext('Text successfully extracted from drawing.'), 'success')
                else:
                    flash(simple_gettext('No text could be extracted from the drawing.'), 'warning')
                    
            except Exception as e:
                logging.error(f"Error processing uploaded file: {str(e)}")
                flash(f"Error processing uploaded file: {str(e)}", 'error')
                return redirect(url_for('index'))
        elif uploaded_file and uploaded_file.filename:
            flash(simple_gettext('Invalid file format. Please upload PNG or JPEG files only.'), 'error')
            return redirect(url_for('index'))
        
        # Combine description and OCR text
        combined_text = f"{description}\n\n{ocr_text}".strip()
        
        if not combined_text:
            flash(simple_gettext('No text available for analysis.'), 'error')
            return redirect(url_for('index'))
        
        # Generate AI analysis
        analysis_result = ai_service.analyze_material_requirements(combined_text)
        
        if not analysis_result:
            flash(simple_gettext('Failed to generate material analysis. Please try again.'), 'error')
            return redirect(url_for('index'))
        
        # Store minimal analysis data in session for PDF generation
        # Compress data to avoid session size limits
        session['last_analysis'] = {
            'input_text': combined_text[:1000] + ('...' if len(combined_text) > 1000 else ''),  # Truncate long text
            'analysis': analysis_result,
            'ocr_extracted': bool(ocr_text),
            'language': get_locale()
        }
        
        return render_template('analysis.html', 
                             analysis=analysis_result,
                             input_text=combined_text,
                             ocr_extracted=bool(ocr_text),
                             current_language=get_locale())
        
    except Exception as e:
        logging.error(f"Error in analyze route: {str(e)}")
        flash(f"An error occurred during analysis: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/download_pdf')
def download_pdf():
    try:
        if 'last_analysis' not in session:
            flash(simple_gettext('No analysis available for PDF generation.'), 'error')
            return redirect(url_for('index'))
        
        analysis_data = session['last_analysis']
        
        # Generate PDF using the stored language preference
        stored_language = analysis_data.get('language', get_locale())
        pdf_buffer = pdf_service.generate_report(
            analysis_data['analysis'],
            analysis_data['input_text'],
            stored_language
        )
        
        # Create temporary file for download
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_buffer.getvalue())
            tmp_file_path = tmp_file.name
        
        return send_file(
            tmp_file_path,
            as_attachment=True,
            download_name=f"material_analysis_report_{get_locale()}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logging.error(f"Error generating PDF: {str(e)}")
        flash(f"Error generating PDF report: {str(e)}", 'error')
        return redirect(request.referrer or url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {str(error)}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
