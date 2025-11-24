# Guarda la información de la sesión actual del usuario
_current_user = None

def set_current_user(u):
    global _current_user
    _current_user = u

def get_current_user():
    return _current_user