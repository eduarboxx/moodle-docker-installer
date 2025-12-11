"""
Password Generator Module
Generador de contraseñas seguras
"""

import secrets
import string


class PasswordGenerator:
    """Genera contraseñas seguras"""
    
    def __init__(self, length=16):
        self.length = length
    
    def generate(self, length=None):
        """Genera una contraseña segura"""
        if length is None:
            length = self.length
        
        # Caracteres permitidos
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        
        # Generar contraseña
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            
            # Verificar que contenga al menos: 1 mayuscula, 1 minuscula, 1 digito, 1 especial
            if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%^&*" for c in password)):
                return password
