import os
import logging
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename):
    """
    Check if file extension is allowed
    
    Args:
        filename (str): Name of the file
        
    Returns:
        bool: True if file extension is allowed
    """
    if not filename:
        return False
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_uploaded_file(file):
    """
    Save uploaded file to upload directory
    
    Args:
        file: FileStorage object from Flask
        
    Returns:
        str: Path to saved file
        
    Raises:
        Exception: If file saving fails
    """
    logger = logging.getLogger(__name__)
    
    try:
        if not file or not file.filename:
            raise ValueError("No file provided")
        
        if not allowed_file(file.filename):
            raise ValueError("File type not allowed")
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Ensure upload directory exists
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        # Create full file path
        file_path = os.path.join(upload_folder, filename)
        
        # Handle duplicate filenames
        counter = 1
        base_name, extension = os.path.splitext(filename)
        while os.path.exists(file_path):
            new_filename = f"{base_name}_{counter}{extension}"
            file_path = os.path.join(upload_folder, new_filename)
            counter += 1
        
        # Save the file
        file.save(file_path)
        
        logger.info(f"File saved successfully: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error saving uploaded file: {str(e)}")
        raise

def cleanup_temp_files(directory=None):
    """
    Clean up temporary files older than 1 hour
    
    Args:
        directory (str): Directory to clean (defaults to upload folder)
    """
    logger = logging.getLogger(__name__)
    
    try:
        if directory is None:
            directory = current_app.config['UPLOAD_FOLDER']
        
        if not os.path.exists(directory):
            return
        
        import time
        current_time = time.time()
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            if os.path.isfile(file_path):
                # Check if file is older than 1 hour (3600 seconds)
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > 3600:
                    try:
                        os.remove(file_path)
                        logger.info(f"Cleaned up old file: {file_path}")
                    except Exception as e:
                        logger.warning(f"Could not remove file {file_path}: {str(e)}")
                        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

def get_file_size(file_path):
    """
    Get file size in bytes
    
    Args:
        file_path (str): Path to file
        
    Returns:
        int: File size in bytes
    """
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

def validate_file_size(file, max_size_mb=16):
    """
    Validate file size
    
    Args:
        file: FileStorage object
        max_size_mb (int): Maximum file size in MB
        
    Returns:
        bool: True if file size is acceptable
    """
    try:
        # Get file size by seeking to end
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset to beginning
        
        max_size_bytes = max_size_mb * 1024 * 1024
        return size <= max_size_bytes
        
    except Exception:
        return False
