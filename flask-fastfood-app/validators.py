# validators.py
import re
from flask import flash


def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not email or not re.match(email_regex, email):
        flash("Invalid Email Address.")
        return False
    return True

def validate_password(password):
    if len(password) < 8:
        flash("Password Must be at Least 8 Characters Long.")
        return False
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        flash("Password Must Contain Both Letters and Numbers.")
        return False
    return True


def validate_phone(phone):
    phone = phone.strip()
    
    if not phone.isdigit():
        flash("Phone Number Cannot Contain Alphabet/Symbol!")
        return False
    
    if len(phone) >= 15:
        flash("Maximum Digit is 15!")
        return False

def validate_ewallet(phone):
    """
    Validate e-wallet phone number
    Returns: (bool, str) - (is_valid, error_message)
    """
    if not phone:
        return False, "Phone number is required"
    if not phone.startswith('08'):
        return False, "E-wallet phone number must start with '08'"
    if not phone.isdigit():
        return False, "Phone number must contain only digits"
    if not (10 <= len(phone) <= 14):
        return False, "Phone number must be between 10 and 14 digits"
    return True, None

def validate_card(card_number, bank):
    """
    Validate card number based on bank requirements
    Returns: (bool, str) - (is_valid, error_message)
    """
    if not card_number:
        return False, "Card number is required"
    
    card_number = card_number.replace(' ', '')
    
    if not card_number.isdigit():
        return False, "Card number must contain only digits"
    
    BANK_RULES = {
        'BRI': {
            'prefix': '002',
            'length': 15,
            'name': 'BRI'
        },
        'BCA': {
            'prefix': '014',
            'length': 10,
            'name': 'BCA'
        },
        'Mandiri': {
            'prefix': '008',
            'length': 13,
            'name': 'Mandiri'
        }
    }
    
    if bank not in BANK_RULES:
        return False, "Invalid bank selected"
        
    rules = BANK_RULES[bank]
    
    if not card_number.startswith(rules['prefix']):
        return False, f"{rules['name']} card must start with '{rules['prefix']}'"
    
    if len(card_number) != rules['length']:
        return False, f"{rules['name']} card must be {rules['length']} digits long"
    
    return True, None
    


