/**
 * Material Analysis Application - Main JavaScript
 */

// Global application object
const MaterialApp = {
    // Configuration
    config: {
        maxFileSize: 16 * 1024 * 1024, // 16MB
        allowedTypes: ['image/png', 'image/jpeg', 'image/jpg'],
        uploadTimeout: 60000 // 60 seconds
    },

    // Initialize application
    init() {
        this.setupEventListeners();
        this.initializeTooltips();
        this.setupFileUpload();
        this.setupFormValidation();
    },

    // Setup event listeners
    setupEventListeners() {
        // Language switcher
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeComponents();
        });

        // Handle form submissions
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                this.handleFormSubmit(e);
            });
        });

        // Handle file uploads
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                this.handleFileUpload(e);
            });
        });

        // Handle alert dismissal
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(alert => {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    this.dismissAlert(alert);
                });
            }
        });
    },

    // Initialize Bootstrap components
    initializeComponents() {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    },

    // Setup file upload functionality
    setupFileUpload() {
        const fileInput = document.getElementById('drawing');
        const filePreview = document.getElementById('filePreview');
        const removeFileBtn = document.getElementById('removeFile');

        if (!fileInput || !filePreview) return;

        // Handle file selection
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                if (this.validateFile(file)) {
                    this.showFilePreview(file);
                } else {
                    this.clearFileInput();
                }
            } else {
                this.hideFilePreview();
            }
        });

        // Handle file removal
        if (removeFileBtn) {
            removeFileBtn.addEventListener('click', () => {
                this.clearFileInput();
            });
        }

        // Drag and drop functionality
        this.setupDragAndDrop(fileInput);
    },

    // Setup drag and drop
    setupDragAndDrop(fileInput) {
        const dropZone = fileInput.parentElement;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('drag-over');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('drag-over');
            }, false);
        });

        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                fileInput.dispatchEvent(new Event('change'));
            }
        }, false);
    },

    // Prevent default drag behaviors
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    },

    // Validate uploaded file
    validateFile(file) {
        // Check file size
        if (file.size > this.config.maxFileSize) {
            this.showAlert('error', `File size must be less than ${this.formatFileSize(this.config.maxFileSize)}`);
            return false;
        }

        // Check file type
        if (!this.config.allowedTypes.includes(file.type)) {
            this.showAlert('error', 'Please upload PNG or JPEG files only');
            return false;
        }

        return true;
    },

    // Show file preview
    showFilePreview(file) {
        const preview = document.getElementById('filePreview');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');

        if (preview && fileName && fileSize) {
            fileName.textContent = file.name;
            fileSize.textContent = this.formatFileSize(file.size);
            preview.style.display = 'block';
        }
    },

    // Hide file preview
    hideFilePreview() {
        const preview = document.getElementById('filePreview');
        if (preview) {
            preview.style.display = 'none';
        }
    },

    // Clear file input
    clearFileInput() {
        const fileInput = document.getElementById('drawing');
        if (fileInput) {
            fileInput.value = '';
            this.hideFilePreview();
        }
    },

    // Setup form validation
    setupFormValidation() {
        const form = document.getElementById('analysisForm');
        if (!form) return;

        form.addEventListener('submit', (e) => {
            if (!this.validateForm(form)) {
                e.preventDefault();
            }
        });
    },

    // Validate form before submission
    validateForm(form) {
        const description = form.querySelector('#description');
        const fileInput = form.querySelector('#drawing');

        const hasDescription = description && description.value.trim().length > 0;
        const hasFile = fileInput && fileInput.files.length > 0;

        if (!hasDescription && !hasFile) {
            this.showAlert('error', 'Please provide either a text description or upload a drawing');
            return false;
        }

        return true;
    },

    // Handle form submission
    handleFormSubmit(e) {
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn) {
            this.setLoadingState(submitBtn, true);
            
            // Set timeout to reset loading state if something goes wrong
            setTimeout(() => {
                this.setLoadingState(submitBtn, false);
            }, this.config.uploadTimeout);
        }
    },

    // Set loading state for buttons
    setLoadingState(button, loading) {
        if (loading) {
            button.disabled = true;
            const originalContent = button.innerHTML;
            button.dataset.originalContent = originalContent;
            
            const loadingText = button.dataset.loadingText || 'Processing...';
            // Use textContent to safely set the loading text
            button.innerHTML = '';
            const spinner = document.createElement('span');
            spinner.className = 'spinner-border spinner-border-sm me-2';
            const textNode = document.createTextNode(loadingText);
            button.appendChild(spinner);
            button.appendChild(textNode);
        } else {
            button.disabled = false;
            if (button.dataset.originalContent) {
                button.innerHTML = button.dataset.originalContent;
            }
        }
    },

    // Show alert message
    showAlert(type, message) {
        const alertContainer = document.createElement('div');
        alertContainer.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        
        // Create icon element
        const icon = document.createElement('i');
        icon.className = `fas fa-${this.getAlertIcon(type)} me-2`;
        
        // Create message text node
        const messageText = document.createTextNode(message);
        
        // Create close button
        const closeBtn = document.createElement('button');
        closeBtn.type = 'button';
        closeBtn.className = 'btn-close';
        closeBtn.setAttribute('data-bs-dismiss', 'alert');
        
        // Assemble the alert
        alertContainer.appendChild(icon);
        alertContainer.appendChild(messageText);
        alertContainer.appendChild(closeBtn);

        // Insert at top of main content
        const mainContent = document.querySelector('.main-content .container');
        if (mainContent) {
            mainContent.insertBefore(alertContainer, mainContent.firstChild);
            
            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                this.dismissAlert(alertContainer);
            }, 5000);
        }
    },

    // Get icon for alert type
    getAlertIcon(type) {
        const icons = {
            'error': 'exclamation-triangle',
            'success': 'check-circle',
            'warning': 'exclamation-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    },

    // Dismiss alert
    dismissAlert(alert) {
        if (alert && alert.parentNode) {
            alert.classList.remove('show');
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 150);
        }
    },

    // Format file size
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Initialize tooltips
    initializeTooltips() {
        // Add tooltips to form elements
        const elementsWithTooltips = [
            { selector: '#description', title: 'Provide detailed technical specifications and requirements' },
            { selector: '#drawing', title: 'Upload PNG or JPEG files up to 16MB' }
        ];

        elementsWithTooltips.forEach(({ selector, title }) => {
            const element = document.querySelector(selector);
            if (element) {
                element.setAttribute('data-bs-toggle', 'tooltip');
                element.setAttribute('data-bs-placement', 'top');
                element.setAttribute('title', title);
            }
        });
    },

    // Utility: Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Utility: Throttle function
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    MaterialApp.init();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden - pause any ongoing operations
        console.log('Page hidden - pausing operations');
    } else {
        // Page is visible - resume operations
        console.log('Page visible - resuming operations');
    }
});

// Handle online/offline status
window.addEventListener('online', () => {
    MaterialApp.showAlert('success', 'Connection restored');
});

window.addEventListener('offline', () => {
    MaterialApp.showAlert('warning', 'Connection lost. Please check your internet connection.');
});

// Export for use in other scripts
window.MaterialApp = MaterialApp;
