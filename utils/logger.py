"""
Logger Module
Sistema de logging para el instalador
"""

import sys
from datetime import datetime


class Logger:
    """Clase para manejar logs del instalador"""
    
    # Colores ANSI
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    GRAY = '\033[90m'
    
    def __init__(self, use_colors=True):
        self.use_colors = use_colors and sys.stdout.isatty()
    
    def _format_message(self, level, message, color=None):
        """Formatea un mensaje con timestamp y nivel"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {message}"
        
        if self.use_colors and color:
            return f"{color}{formatted}{self.RESET}"
        return formatted
    
    def info(self, message):
        """Log nivel INFO"""
        print(self._format_message("INFO", message, self.BLUE))
    
    def success(self, message):
        """Log nivel SUCCESS"""
        print(self._format_message("SUCCESS", message, self.GREEN))
    
    def warning(self, message):
        """Log nivel WARNING"""
        print(self._format_message("WARNING", message, self.YELLOW))
    
    def error(self, message):
        """Log nivel ERROR"""
        print(self._format_message("ERROR", message, self.RED), file=sys.stderr)
    
    def debug(self, message):
        """Log nivel DEBUG"""
        print(self._format_message("DEBUG", message, self.GRAY))
