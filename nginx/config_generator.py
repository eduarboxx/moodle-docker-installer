"""
Nginx Config Generator Module
Genera configuraciones de Nginx para Testing y Produccion
"""

import os
import socket


class NginxConfigGenerator:
    """Genera configuraciones de Nginx"""
    
    def __init__(self, settings):
        self.settings = settings
        self.nginx_path = settings.NGINX_PATH

    def _get_host_ip(self):
        """Obtiene la IP del host"""
        try:
            # Crear un socket temporal para obtener la IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "localhost"

    def _should_use_ip(self, url):
        """Determina si debe usar IP en lugar de URL"""
        default_urls = ['https://test.moodle.local', 'https://moodle.local',
                       'http://test.moodle.local', 'http://moodle.local']
        return not url or url in default_urls

    def generate_all(self):
        """Genera todas las configuraciones de Nginx"""
        try:
            self.generate_testing_config()
            self.generate_production_config()
            self.generate_default_config()
            return True
        except Exception as e:
            print(f"Error generando configuraciones Nginx: {str(e)}")
            return False
    
    def generate_testing_config(self):
        """Genera configuracion de Nginx para Testing"""
        test_url = self.settings.get_env_var('TEST_URL', 'https://test.moodle.local')

        # Si la URL no está definida o es la por defecto, usar IP del host
        if self._should_use_ip(test_url):
            host_ip = self._get_host_ip()
            test_port = self.settings.get_env_var('TEST_HTTP_PORT', '8080')
            test_port_ssl = self.settings.get_env_var('TEST_HTTPS_PORT', '8443')
            server_name = f"{host_ip}"
            print(f"Usando IP del host para Testing: {host_ip}:{test_port_ssl}")
        else:
            server_name = test_url.replace('https://', '').replace('http://', '')

        config = f"""# Testing Environment
server {{
    listen 8080;
    server_name {server_name};

    # Redirigir HTTP a HTTPS
    return 301 https://$server_name:8443$request_uri;
}}

server {{
    listen 8443 ssl;
    http2 on;
    server_name {server_name};

    # SSL (certificados autofirmados por defecto)
    ssl_certificate /etc/nginx/ssl/testing.crt;
    ssl_certificate_key /etc/nginx/ssl/testing.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Logs
    access_log /var/log/nginx/testing_access.log;
    error_log /var/log/nginx/testing_error.log;

    # Configuracion Moodle
    client_max_body_size 100M;

    location / {{
        proxy_pass http://moodle_testing;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }}
}}
"""

        # Crear archivo de configuración directamente en conf.d
        config_dir = os.path.join(self.nginx_path, 'conf.d')
        os.makedirs(config_dir, exist_ok=True)

        config_path = os.path.join(config_dir, 'testing.conf')

        with open(config_path, 'w') as f:
            f.write(config)

        print(f"Configuracion Testing creada: {config_path}")
        return True
    
    def generate_production_config(self):
        """Genera configuracion de Nginx para Produccion"""
        prod_url = self.settings.get_env_var('PROD_URL', 'https://moodle.local')

        # Si la URL no está definida o es la por defecto, usar IP del host
        if self._should_use_ip(prod_url):
            host_ip = self._get_host_ip()
            prod_port = self.settings.get_env_var('PROD_HTTP_PORT', '80')
            prod_port_ssl = self.settings.get_env_var('PROD_HTTPS_PORT', '443')
            server_name = f"{host_ip}"
            print(f"Usando IP del host para Produccion: {host_ip}:{prod_port_ssl}")
        else:
            server_name = prod_url.replace('https://', '').replace('http://', '')

        config = f"""# Production Environment
server {{
    listen 80;
    server_name {server_name};

    # Redirigir HTTP a HTTPS
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl;
    http2 on;
    server_name {server_name};

    # SSL (certificados autofirmados por defecto)
    ssl_certificate /etc/nginx/ssl/production.crt;
    ssl_certificate_key /etc/nginx/ssl/production.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Logs
    access_log /var/log/nginx/production_access.log;
    error_log /var/log/nginx/production_error.log;

    # Configuracion Moodle
    client_max_body_size 100M;

    location / {{
        proxy_pass http://moodle_production;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }}
}}
"""

        # Crear archivo de configuración directamente en conf.d
        config_dir = os.path.join(self.nginx_path, 'conf.d')
        os.makedirs(config_dir, exist_ok=True)

        config_path = os.path.join(config_dir, 'production.conf')

        with open(config_path, 'w') as f:
            f.write(config)

        print(f"Configuracion Produccion creada: {config_path}")
        return True
    
    def generate_default_config(self):
        """Genera configuracion por defecto de Nginx"""
        # Ya no necesitamos un default.conf global
        # Cada ambiente tendrá su propio default.conf
        return True
    
    def generate_self_signed_certs(self):
        """Genera certificados SSL autofirmados"""
        import subprocess
        
        ssl_path = os.path.join(self.nginx_path, 'ssl')
        os.makedirs(ssl_path, exist_ok=True)
        
        environments = ['testing', 'production']
        
        for env in environments:
            cert_file = os.path.join(ssl_path, f'{env}.crt')
            key_file = os.path.join(ssl_path, f'{env}.key')
            
            if os.path.exists(cert_file) and os.path.exists(key_file):
                print(f"Certificados SSL para {env} ya existen")
                continue
            
            try:
                cmd = f"""openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\
                    -keyout {key_file} \\
                    -out {cert_file} \\
                    -subj "/C=CL/ST=Chile/L=Santiago/O=Moodle/CN={env}.moodle.local"
                """
                subprocess.run(cmd, shell=True, check=True, capture_output=True)
                print(f"Certificado SSL generado para {env}")
            except Exception as e:
                print(f"Error generando certificado SSL para {env}: {str(e)}")
                return False
        
        return True
