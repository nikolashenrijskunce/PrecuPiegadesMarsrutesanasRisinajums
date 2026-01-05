# Sis fails nodefine lietotaja modeli, kuru izmanto flask_login biblioteka, lai veiktu kontroli ar lietotajiem, kas ir pieslegusies
# Saja faila User klase ir maksliga intelekta genereta un autora modificeta
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

class User:
    def __init__(self, id, roles):
        self.id = id
        self.roles = roles

    def get_id(self):
        return str(f"{self.roles}:{self.id}")

    def get_roles(self):
        return self.roles

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False



# Decorator funkcija, kas dod piekluvi lietotajiem atkariba no to iedotas lomas
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.get_roles() != role:
                flash('Access Denied!')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator