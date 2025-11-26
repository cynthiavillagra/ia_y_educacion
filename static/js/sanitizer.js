// HTML Sanitization utilities
// Prevent XSS attacks by escaping HTML

/**
 * Escape HTML special characters to prevent XSS
 */
function escapeHTML(str) {
    if (!str) return '';

    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * Safely set text content (never use innerHTML with user data)
 */
function safeSetText(element, text) {
    if (!element) return;
    element.textContent = text || '';
}

/**
 * Safely set HTML attribute
 */
function safeSetAttribute(element, attr, value) {
    if (!element) return;

    // For href attributes, validate URL
    if (attr === 'href' && value) {
        // Only allow http/https URLs
        if (!value.startsWith('http://') && !value.startsWith('https://') && !value.startsWith('/')) {
            console.warn('Invalid URL blocked:', value);
            return;
        }
    }

    element.setAttribute(attr, value || '');
}

/**
 * Create safe HTML element with text content
 */
function createSafeElement(tag, text, className = '') {
    const el = document.createElement(tag);
    if (text) el.textContent = text;
    if (className) el.className = className;
    return el;
}

// Export for use in other scripts
window.HTMLSanitizer = {
    escapeHTML,
    safeSetText,
    safeSetAttribute,
    createSafeElement
};
