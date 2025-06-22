import os

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # API Configuration
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', 'default-key')
    AITUNNEL_API_KEY = os.environ.get('AITUNNEL_API_KEY', 'default-key')
    
    # Supported file extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # Babel configuration
    LANGUAGES = {
        'en': 'English',
        'ru': 'Русский'
    }
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
