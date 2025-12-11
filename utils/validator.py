"""
Validator Module
Validaciones del sistema
"""

import os
import socket
import subprocess


class Validator:
    """Clase para validaciones del sistema"""
    
    def check_root(self):
        """Verifica si se ejecuta como root"""
        return os.geteuid() == 0
    
    def check_port_available(self, port):
        """Verifica si un puerto esta disponible"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', int(port)))
                return True
        except OSError:
            return False
    
    def check_command_exists(self, command):
        """Verifica si un comando existe en el sistema"""
        try:
            subprocess.run(
                ['which', command],
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def check_disk_space(self, path, required_gb=10):
        """Verifica espacio en disco disponible"""
        try:
            stat = os.statvfs(path if os.path.exists(path) else '/')
            # Espacio disponible en GB
            available_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            return available_gb >= required_gb
        except Exception:
            return False
    
    def check_internet_connection(self):
        """Verifica conexion a internet"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    def validate_url(self, url):
        """Valida formato de URL"""
        import re
        pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return pattern.match(url) is not None
    
    def validate_installation_requirements(self):
        """Valida todos los requisitos de instalacion"""
        results = {
            'root': self.check_root(),
            'disk_space': self.check_disk_space('/opt', 10),
            'internet': self.check_internet_connection()
        }
        return results
