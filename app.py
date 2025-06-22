import os
import logging
from flask import Flask, request, render_template, redirect, url_for, flash, session, send_file
from flask_babel import Babel, gettext, ngettext
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

# Initialize Babel for internationalization
babel = Babel()
babel.init_app(app, locale_selector=get_locale)

# Make functions available to templates
@app.context_processor
def inject_template_vars():
    return {
        '_': gettext,
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
            flash(gettext('Please provide either a text description or upload a drawing.'), 'error')
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
                    flash(gettext('Text successfully extracted from drawing.'), 'success')
                else:
                    flash(gettext('No text could be extracted from the drawing.'), 'warning')
                    
            except Exception as e:
                logging.error(f"Error processing uploaded file: {str(e)}")
                flash(gettext('Error processing uploaded file: %(error)s', error=str(e)), 'error')
                return redirect(url_for('index'))
        elif uploaded_file and uploaded_file.filename:
            flash(gettext('Invalid file format. Please upload PNG or JPEG files only.'), 'error')
            return redirect(url_for('index'))
        
        # Combine description and OCR text
        combined_text = f"{description}\n\n{ocr_text}".strip()
        
        if not combined_text:
            flash(gettext('No text available for analysis.'), 'error')
            return redirect(url_for('index'))
        
        # Generate AI analysis
        analysis_result = ai_service.analyze_material_requirements(combined_text)
        
        if not analysis_result:
            flash(gettext('Failed to generate material analysis. Please try again.'), 'error')
            return redirect(url_for('index'))
        
        # Store analysis in session for PDF generation
        session['last_analysis'] = {
            'input_text': combined_text,
            'analysis': analysis_result,
            'ocr_extracted': bool(ocr_text)
        }
        
        return render_template('analysis.html', 
                             analysis=analysis_result,
                             input_text=combined_text,
                             ocr_extracted=bool(ocr_text))
        
    except Exception as e:
        logging.error(f"Error in analyze route: {str(e)}")
        flash(gettext('An error occurred during analysis: %(error)s', error=str(e)), 'error')
        return redirect(url_for('index'))

@app.route('/download_pdf')
def download_pdf():
    try:
        if 'last_analysis' not in session:
            flash(gettext('No analysis available for PDF generation.'), 'error')
            return redirect(url_for('index'))
        
        analysis_data = session['last_analysis']
        
        # Generate PDF
        pdf_buffer = pdf_service.generate_report(
            analysis_data['analysis'],
            analysis_data['input_text'],
            get_locale()
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
        flash(gettext('Error generating PDF report: %(error)s', error=str(e)), 'error')
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
