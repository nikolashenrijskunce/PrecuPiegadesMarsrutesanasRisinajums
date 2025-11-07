from app import bcrypt

def verify_login(username, password):
    if username != 'admin':
        return False

    try:
        with open('passwords.txt') as f:
            stored_hash = f.readline().strip()
    except FileNotFoundError:
        return False

    return bcrypt.check_password_hash(stored_hash, password)
