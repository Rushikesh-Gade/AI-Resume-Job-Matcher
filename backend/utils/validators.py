"""
Input validation utilities
"""
import re


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Validate password strength
    Requirements: min 8 chars, 1 uppercase, 1 lowercase, 1 number
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, "Valid password"


def validate_file_extension(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)


def validate_file_size(file_size_bytes, max_size_mb):
    """Check if file size is within limit"""
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size_bytes <= max_size_bytes
