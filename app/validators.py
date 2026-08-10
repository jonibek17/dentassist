import re
from datetime import datetime


def is_valid_name(text: str) -> bool:
    """Validate that text looks like a name.
    
    Rules:
    - Must be 2-50 characters long
    - Only letters (Cyrillic/Latin) and spaces allowed
    - No digits
    """
    if not text or not isinstance(text, str):
        return False
    
    text = text.strip()
    
    # Check length
    if len(text) < 2 or len(text) > 50:
        return False
    
    # Check if contains only letters and spaces
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s]+$', text):
        return False
    
    # Check if contains at least one letter
    if not re.search(r'[a-zA-Zа-яА-ЯёЁ]', text):
        return False
    
    return True


def is_valid_phone(text: str) -> bool:
    """Validate that text looks like a phone number.
    
    Rules:
    - Format: +998XXXXXXXXX (country code + 9 digits) OR just 9 digits
    - After removing non-digit characters, must be exactly 9 or 12 digits
    """
    if not text or not isinstance(text, str):
        return False
    
    text = text.strip()
    
    # Check if empty
    if not text:
        return False
    
    # Extract only digits
    digits = re.sub(r'[^\d]', '', text)
    
    # Check digit count: exactly 9 or 12 digits
    if len(digits) not in (9, 12):
        return False
    
    # Check if contains only valid characters
    valid_chars = set('0123456789+- ()')
    if not all(char in valid_chars for char in text):
        return False
    
    return True


def is_valid_date(text: str) -> bool:
    """Validate that text is a valid date in DD.MM.YYYY format.
    
    Rules:
    - Format strictly DD.MM.YYYY
    - Date must not be in the past
    """
    if not text or not isinstance(text, str):
        return False
    
    text = text.strip()
    
    try:
        date_obj = datetime.strptime(text, "%d.%m.%Y")
        # Check if date is not in the past
        if date_obj < datetime.now():
            return False
        return True
    except ValueError:
        return False


def is_valid_time(text: str) -> bool:
    """Validate that text is a valid time in HH:MM format.
    
    Rules:
    - Format strictly HH:MM (24-hour)
    - Must be within clinic working hours (09:00–20:00)
    """
    if not text or not isinstance(text, str):
        return False
    
    text = text.strip()
    
    try:
        time_obj = datetime.strptime(text, "%H:%M")
        # Extract hour and minute
        hour = time_obj.hour
        minute = time_obj.minute
        
        # Check if within working hours (09:00–20:00)
        if hour < 9 or hour >= 20:
            return False
        if hour == 9 and minute < 0:
            return False
        if hour == 20 and minute > 0:
            return False
        
        return True
    except ValueError:
        return False


def is_valid_text_length(text: str, min_length: int = 2, max_length: int = 100) -> bool:
    """Basic validation for text length."""
    if not text or not isinstance(text, str):
        return False
    
    text = text.strip()
    
    if len(text) < min_length or len(text) > max_length:
        return False
    
    return True
