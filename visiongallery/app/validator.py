import phonenumbers
import re

# Validates user-inputs to prevent certain attacks like
#   SQL Injection and Server Side Injection

def valid_name(name):
    name = name.lower()

    if name.isalpha():
        name_list = list(name)

        if not name_list[0].isupper():
            name_list[0] = name_list[0].upper()
            name = "".join(name_list)

            return name

        return name
    else:
        return None

def valid_username(username):
    for c in username:
        if c.isupper():
            return False
    
    if " " in username:
        return False

    return True
    
def valid_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    if re.fullmatch(regex, email):
        return True

def valid_phone(phone):
    try:
        my_number = phonenumbers.parse(phone)
        return phonenumbers.is_possible_number(my_number)
    except:
        return False

def valid_password(password):
    return False if " " in password else True

def valid_recovery_code(code):
    if len(code) == 10:
        return code.isalnum()
    else:
        return False
