import re
from typing import Dict, Any


def validate_email(email: str) -> bool:
    """Validate an email address.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(email_pattern, email))
    
    
def validate_phone(phone: str) -> bool:
    """Validate a phone number.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if phone number is valid, False otherwise
    """
    # Simple phone number validation - allow digits, spaces, dashes, parentheses, and plus
    phone_pattern = r'^[\d\s\-\(\)\+]{7,20}$'
    return bool(re.match(phone_pattern, phone))
    
    
def validate_input(current_step: str, user_input: str) -> Dict[str, Any]:
    """Validate user input based on current step.
    
    Args:
        current_step: Current interview step
        user_input: User's input text
        
    Returns:
        Dictionary with validation result and message
    """
    # Only validate specific fields
    if current_step == "email":
        if not validate_email(user_input):
            return {
                "valid": False,
                "field_type": "email address",
                "error": "That doesn't appear to be a valid email address. Please provide a valid email in the format example@domain.com."
            }
                
    elif current_step == "phone":
        if not validate_phone(user_input):
            return {
                "valid": False,
                "field_type": "phone number",
                "error": "That doesn't appear to be a valid phone number. Please provide a valid phone number."
            }
    
    return {"valid": True, "message": ""} 