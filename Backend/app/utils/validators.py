"""Email and data validation utilities"""

def validate_vvit_email(email: str) -> bool:
    """
    Validate that email ends with @vvit.net domain.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    email = email.strip().lower()
    return email.endswith("@vvit.net")


def validate_email_format(email: str) -> bool:
    """
    Basic email format validation.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email has basic valid format, False otherwise
    """
    email = email.strip().lower()
    return "@" in email and "." in email and len(email) > 5


def validate_vvit_and_format(email: str) -> bool:
    """
    Validate both format and @vvit.net domain.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    return validate_email_format(email) and validate_vvit_email(email)
