"""
Settings Module
Configuraciones generales del instalador
"""

import os
from pathlib import Path
from utils.password_generator import PasswordGenerator


class Settings:
    """Clase de configuracion del instalador"""
    
    # Rutas base
    BASE_PATH = "/opt/docker-project"
    MOODLE_VERSION = "4.5.5"
    
    def __init__(self):
        self.pg = PasswordGenerator()
        self.env_vars = {}
        self._load_default_vars()
        # Intentar cargar .env del directorio raíz del proyecto si existe
        self._try_load_project_env()

    def _try_load_project_env(self):
        """Intenta cargar .env del directorio raíz del proyecto"""
        try:
            # Obtener directorio raíz del proyecto
            project_root = Path(__file__).parent.parent
            env_file = project_root / '.env'

            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip("'\"")

                            # Solo sobrescribir si el valor no es el placeholder
                            if value and value != 'GENERAR_CONTRASEÑA_SEGURA':
                                self.env_vars[key] = value
                            # Si es placeholder y la clave es de contraseña, generar una
                            elif 'PASS' in key and value == 'GENERAR_CONTRASEÑA_SEGURA':
                                # Mantener la contraseña generada por defecto
                                pass
        except Exception as e:
            # No hacer nada si falla, usar valores por defecto
            pass

    def _load_default_vars(self):
        """Carga variables por defecto"""
        self.env_vars = {
            # General
            'MOODLE_VERSION': self.MOODLE_VERSION,
            'PROJECT_NAME': 'moodle_infrastructure',

            # Testing
            'TEST_URL': 'https://test.moodle.local',
            'TEST_DB_NAME': 'moodle_test',
            'TEST_DB_USER': 'moodle_test_user',
            'TEST_DB_PASS': self.pg.generate(),
            'TEST_DB_ROOT_PASS': self.pg.generate(),
            'TEST_MOODLE_ADMIN_USER': 'admin_test',
            'TEST_MOODLE_ADMIN_PASS': self.pg.generate(),
            'TEST_MOODLE_ADMIN_EMAIL': 'admin@test.moodle.local',
            'TEST_HTTP_PORT': '8081',
            'TEST_HTTPS_PORT': '8443',

            # Production
            'PROD_URL': 'https://moodle.local',
            'PROD_DB_NAME': 'moodle_prod',
            'PROD_DB_USER': 'moodle_prod_user',
            'PROD_DB_PASS': self.pg.generate(),
            'PROD_DB_ROOT_PASS': self.pg.generate(),
            'PROD_MOODLE_ADMIN_USER': 'admin',
            'PROD_MOODLE_ADMIN_PASS': self.pg.generate(),
            'PROD_MOODLE_ADMIN_EMAIL': 'admin@moodle.local',
            'PROD_HTTP_PORT': '80',
            'PROD_HTTPS_PORT': '443',

            # Nginx
            'NGINX_HTTP_PORT': '80',
            'NGINX_HTTPS_PORT': '443',

            # SSL Configuration
            'SSL_CERT_TYPE': 'self-signed',
            'SSL_LETSENCRYPT_EMAIL': '',
            'SSL_FORCE_HTTPS': 'true',

            # Backup Configuration
            'BACKUP_RETENTION_DAYS': '7',
            'BACKUP_EMAIL_TO': '',

            # SMTP Configuration
            'SMTP_SERVER': 'smtp.gmail.com',
            'SMTP_PORT': '465',
            'SMTP_USER': '',
            'SMTP_PASSWORD': '',
            'SMTP_FROM_NAME': 'Moodle Backup System',

            # Auto-start Configuration
            'AUTO_START_ON_BOOT': 'false',
            'AUTO_INSTALL_MOODLE': 'false',
            'AUTO_BACKUP_ON_START': 'true',
            'MONITORING_ENABLED': 'false',
            'MONITORING_INTERVAL': '60',

            # Resource Limits
            'MYSQL_MAX_CONNECTIONS': '200',
            'PHP_MEMORY_LIMIT': '512M',
            'PHP_MAX_EXECUTION_TIME': '300',
            'PHP_UPLOAD_MAX_FILESIZE': '100M',
            'PHP_POST_MAX_SIZE': '100M',
        }
    
    @property
    def MOODLE_PATH(self):
        """Ruta de instalacion de Moodle"""
        return os.path.join(self.BASE_PATH, 'moodle', self.MOODLE_VERSION)

    @property
    def TESTING_PATH(self):
        """Ruta del ambiente de testing"""
        return os.path.join(self.BASE_PATH, 'testing')
    
    @property
    def PRODUCTION_PATH(self):
        """Ruta del ambiente de produccion"""
        return os.path.join(self.BASE_PATH, 'production')
    
    @property
    def LOGS_PATH(self):
        """Ruta de logs"""
        return os.path.join(self.BASE_PATH, 'logs')
    
    @property
    def BACKUPS_PATH(self):
        """Ruta de backups"""
        return os.path.join(self.BASE_PATH, 'backups')

    @property
    def BACKUP_RETENTION_DAYS(self):
        """Días de retención de backups"""
        value = self.env_vars.get('BACKUP_RETENTION_DAYS', '7')
        # Remover comillas si existen
        if isinstance(value, str):
            value = value.strip("'\"")
        return int(value)

    @property
    def BACKUP_EMAIL_TO(self):
        """Email de destino para notificaciones de backup"""
        return self.env_vars.get('BACKUP_EMAIL_TO', '')

    @property
    def SMTP_SERVER(self):
        """Servidor SMTP"""
        return self.env_vars.get('SMTP_SERVER', 'smtp.gmail.com')

    @property
    def SMTP_PORT(self):
        """Puerto SMTP"""
        value = self.env_vars.get('SMTP_PORT', '465')
        # Remover comillas si existen
        if isinstance(value, str):
            value = value.strip("'\"")
        return int(value)

    @property
    def SMTP_USER(self):
        """Usuario SMTP"""
        return self.env_vars.get('SMTP_USER', '')

    @property
    def SMTP_PASSWORD(self):
        """Contraseña SMTP"""
        return self.env_vars.get('SMTP_PASSWORD', '')

    @property
    def SMTP_FROM_NAME(self):
        """Nombre del remitente en emails"""
        return self.env_vars.get('SMTP_FROM_NAME', 'Moodle Backup System')

    @property
    def SSL_CERT_TYPE(self):
        """Tipo de certificado SSL"""
        value = self.env_vars.get('SSL_CERT_TYPE', 'self-signed')
        if isinstance(value, str):
            value = value.strip("'\"")
        return value

    @property
    def SSL_LETSENCRYPT_EMAIL(self):
        """Email para Let's Encrypt"""
        value = self.env_vars.get('SSL_LETSENCRYPT_EMAIL', '')
        if isinstance(value, str):
            value = value.strip("'\"")
        return value

    @property
    def SSL_FORCE_HTTPS(self):
        """Forzar HTTPS en Moodle"""
        value = self.env_vars.get('SSL_FORCE_HTTPS', 'true')
        if isinstance(value, str):
            value = value.strip("'\"").lower()
        return value == 'true'

    def get_env_var(self, key, default=None):
        """Obtiene una variable de entorno"""
        return self.env_vars.get(key, default)
    
    def set_env_var(self, key, value):
        """Establece una variable de entorno"""
        self.env_vars[key] = value
    
    def generate_env_file(self):
        """Genera el archivo .env"""
        try:
            env_path = os.path.join(self.BASE_PATH, '.env')

            with open(env_path, 'w') as f:
                f.write("# Moodle Docker Infrastructure Configuration\n")
                f.write("# Generado automaticamente\n\n")

                f.write("# GENERAL\n")
                f.write(f"MOODLE_VERSION='{self.env_vars['MOODLE_VERSION']}'\n")
                f.write(f"PROJECT_NAME='{self.env_vars['PROJECT_NAME']}'\n\n")

                f.write("# TESTING ENVIRONMENT\n")
                for key in self.env_vars:
                    if key.startswith('TEST_'):
                        f.write(f"{key}='{self.env_vars[key]}'\n")
                f.write("\n")

                f.write("# PRODUCTION ENVIRONMENT\n")
                for key in self.env_vars:
                    if key.startswith('PROD_'):
                        f.write(f"{key}='{self.env_vars[key]}'\n")
                f.write("\n")

                f.write("# NGINX\n")
                for key in self.env_vars:
                    if key.startswith('NGINX_'):
                        f.write(f"{key}='{self.env_vars[key]}'\n")
                f.write("\n")

                f.write("# SSL CONFIGURATION\n")
                for key in self.env_vars:
                    if key.startswith('SSL_'):
                        f.write(f"{key}='{self.env_vars[key]}'\n")
                f.write("\n")

                f.write("# BACKUP CONFIGURATION\n")
                for key in self.env_vars:
                    if key.startswith('BACKUP_'):
                        f.write(f"{key}='{self.env_vars[key]}'\n")
                f.write("\n")

                f.write("# SMTP CONFIGURATION\n")
                for key in self.env_vars:
                    if key.startswith('SMTP_'):
                        f.write(f"{key}='{self.env_vars[key]}'\n")
                f.write("\n")

                f.write("# AUTO-START CONFIGURATION\n")
                for key in self.env_vars:
                    if key.startswith('AUTO_') or key.startswith('MONITORING_'):
                        f.write(f"{key}='{self.env_vars[key]}'\n")
                f.write("\n")

                f.write("# RESOURCE LIMITS\n")
                for key in self.env_vars:
                    if key.startswith('MYSQL_') or key.startswith('PHP_'):
                        if key not in ['MYSQL_DATABASE', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_ROOT_PASSWORD']:
                            f.write(f"{key}='{self.env_vars[key]}'\n")

            return True
        except Exception as e:
            print(f"Error generando .env: {str(e)}")
            return False
    
    def load_env_file(self):
        """Carga variables desde el archivo .env"""
        try:
            env_path = os.path.join(self.BASE_PATH, '.env')
            if not os.path.exists(env_path):
                return False

            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Remover comillas simples o dobles del valor
                        value = value.strip().strip("'\"")
                        self.env_vars[key.strip()] = value

            return True
        except Exception as e:
            print(f"Error cargando .env: {str(e)}")
            return False
    
    def prompt_urls(self):
        """Solicita las URLs al usuario"""
        print("\nConfiguracion de URLs:")
        print("Presiona Enter para usar los valores por defecto\n")
        
        test_url = input(f"URL Testing [{self.env_vars['TEST_URL']}]: ").strip()
        if test_url:
            self.env_vars['TEST_URL'] = test_url
        
        prod_url = input(f"URL Produccion [{self.env_vars['PROD_URL']}]: ").strip()
        if prod_url:
            self.env_vars['PROD_URL'] = prod_url
    
    def prompt_ports(self):
        """Solicita los puertos al usuario"""
        print("\nConfiguracion de Puertos:")
        print("Presiona Enter para usar los valores por defecto\n")
        
        test_http = input(f"Puerto HTTP Testing [{self.env_vars['TEST_HTTP_PORT']}]: ").strip()
        if test_http:
            self.env_vars['TEST_HTTP_PORT'] = test_http
        
        test_https = input(f"Puerto HTTPS Testing [{self.env_vars['TEST_HTTPS_PORT']}]: ").strip()
        if test_https:
            self.env_vars['TEST_HTTPS_PORT'] = test_https
        
        prod_http = input(f"Puerto HTTP Produccion [{self.env_vars['PROD_HTTP_PORT']}]: ").strip()
        if prod_http:
            self.env_vars['PROD_HTTP_PORT'] = prod_http
        
        prod_https = input(f"Puerto HTTPS Produccion [{self.env_vars['PROD_HTTPS_PORT']}]: ").strip()
        if prod_https:
            self.env_vars['PROD_HTTPS_PORT'] = prod_https
    
    def show_credentials_summary(self):
        """Muestra resumen de credenciales generadas"""
        print("\n" + "="*60)
        print("CREDENCIALES GENERADAS")
        print("="*60)
        
        print("\nTESTING:")
        print(f"  Admin User: {self.env_vars['TEST_MOODLE_ADMIN_USER']}")
        print(f"  Admin Pass: {self.env_vars['TEST_MOODLE_ADMIN_PASS']}")
        print(f"  DB User: {self.env_vars['TEST_DB_USER']}")
        print(f"  DB Pass: {self.env_vars['TEST_DB_PASS']}")
        print(f"  DB Root Pass: {self.env_vars['TEST_DB_ROOT_PASS']}")
        
        print("\nPRODUCCION:")
        print(f"  Admin User: {self.env_vars['PROD_MOODLE_ADMIN_USER']}")
        print(f"  Admin Pass: {self.env_vars['PROD_MOODLE_ADMIN_PASS']}")
        print(f"  DB User: {self.env_vars['PROD_DB_USER']}")
        print(f"  DB Pass: {self.env_vars['PROD_DB_PASS']}")
        print(f"  DB Root Pass: {self.env_vars['PROD_DB_ROOT_PASS']}")
        
        print("\nEstas credenciales tambien se encuentran en:")
        print(f"{self.BASE_PATH}/.env")
        print("="*60 + "\n")
