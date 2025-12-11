"""
Dockerfile Generator Module
Genera los Dockerfiles para Moodle y Nginx
"""

import os


class DockerfileGenerator:
    """Genera Dockerfiles personalizados"""
    
    def __init__(self, settings):
        self.settings = settings
        self.base_path = settings.BASE_PATH
    
    def generate_all(self):
        """Genera todos los Dockerfiles necesarios"""
        try:
            self.generate_moodle_dockerfile()
            self.generate_nginx_dockerfile()
            return True
        except Exception as e:
            print(f"Error generando Dockerfiles: {str(e)}")
            return False
    
    def generate_moodle_dockerfile(self):
        """Genera Dockerfile para Moodle"""
        dockerfile_content = """FROM php:8.1-apache

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \\
    libpng-dev \\
    libjpeg-dev \\
    libfreetype6-dev \\
    libxml2-dev \\
    libzip-dev \\
    libicu-dev \\
    libldap2-dev \\
    libpq-dev \\
    ghostscript \\
    cron \\
    git \\
    unzip \\
    && rm -rf /var/lib/apt/lists/*

# Configurar extensiones PHP
RUN docker-php-ext-configure gd --with-freetype --with-jpeg \\
    && docker-php-ext-install -j$(nproc) \\
    gd \\
    mysqli \\
    pdo \\
    pdo_mysql \\
    opcache \\
    intl \\
    zip \\
    soap \\
    exif

# Configurar PHP
RUN { \\
    echo 'memory_limit = 256M'; \\
    echo 'upload_max_filesize = 100M'; \\
    echo 'post_max_size = 100M'; \\
    echo 'max_execution_time = 300'; \\
    echo 'max_input_vars = 5000'; \\
    echo 'opcache.enable = 1'; \\
    echo 'opcache.memory_consumption = 128'; \\
    echo 'opcache.max_accelerated_files = 10000'; \\
    echo 'opcache.revalidate_freq = 60'; \\
} > /usr/local/etc/php/conf.d/moodle.ini

# Habilitar modulos Apache
RUN a2enmod rewrite expires headers ssl

# Copiar Moodle
COPY """ + self.settings.MOODLE_VERSION + """/ /var/www/html/

# Permisos
RUN chown -R www-data:www-data /var/www/html

# Puerto
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \\
    CMD curl -f http://localhost/ || exit 1

CMD ["apache2-foreground"]
"""
        
        dockerfile_path = os.path.join(self.base_path, 'moodle', 'Dockerfile')
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(dockerfile_path), exist_ok=True)
        
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        print(f"Dockerfile de Moodle creado: {dockerfile_path}")
        return True
    
    def generate_nginx_dockerfile(self):
        """Genera Dockerfile para Nginx"""
        dockerfile_content = """FROM nginx:alpine

# Las configuraciones se montan como volúmenes en docker-compose
# Permisos
RUN chown -R nginx:nginx /var/cache/nginx \\
    && chown -R nginx:nginx /var/log/nginx

# Puerto
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \\
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
"""

        dockerfile_path = os.path.join(self.base_path, 'nginx', 'Dockerfile')

        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)

        print(f"Dockerfile de Nginx creado: {dockerfile_path}")
        return True
