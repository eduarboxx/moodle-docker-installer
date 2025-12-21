# INFORME COMPLETO DEL PROYECTO
## Moodle Docker Infrastructure Installer

---

## INFORMACIÓN GENERAL DEL PROYECTO

### Identificación
- **Nombre del Proyecto**: Moodle Docker Infrastructure Installer
- **Versión**: 1.0
- **Autor**: Eduardo Valdés
- **Institución**: SLEP Andalien Sur / CIISA
- **Fecha de Desarrollo**: Diciembre 2024
- **Lenguajes**: Python 3.8+, Bash, YAML
- **Tecnologías**: Docker, Docker Compose, Apache HTTP Server, MySQL 8.0, PHP

### Descripción General
Sistema automatizado de instalación y gestión de infraestructura Moodle utilizando contenedores Docker. El proyecto proporciona una solución completa para desplegar ambientes de Testing y Producción de Moodle de forma aislada, con gestión de backups, SSL automático y monitoreo integrado.

### Objetivos del Proyecto
1. **Automatizar** la instalación completa de infraestructura Moodle
2. **Separar** ambientes de Testing y Producción de forma segura
3. **Simplificar** la gestión de contenedores Docker
4. **Garantizar** respaldos automáticos y recuperación de datos
5. **Proporcionar** certificados SSL para comunicación segura
6. **Soportar** múltiples distribuciones Linux

---

## ESTADÍSTICAS DEL PROYECTO

### Métricas de Código
- **Total de archivos Python**: 28 archivos
- **Total de líneas de código**: ~5,370 líneas (Python + Bash)
- **Módulos principales**: 7 (core, docker, apache, backup, config, utils)
- **Scripts de automatización**: 5 scripts Bash
- **Archivos de documentación**: 8 archivos Markdown

### Estructura de Archivos
```
Directorios principales: 7
├── backup/     - Sistema de respaldos (7 archivos)
├── config/     - Configuraciones (3 archivos)
├── core/       - Módulos principales (5 archivos)
├── docker/     - Generadores Docker (5 archivos)
├── apache/     - Configuración Apache (1 archivo)
├── utils/      - Utilidades (9 archivos)
└── Raíz        - Scripts principales (4 archivos)
```

---

## ARQUITECTURA DEL SISTEMA

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    MOODLE DOCKER INSTALLER                  │
│                         (main.py)                           │
└───────────────────┬─────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼────┐    ┌────▼─────┐   ┌────▼──────┐
│  CORE  │    │  DOCKER  │   │  APACHE   │
└───┬────┘    └────┬─────┘   └────┬──────┘
    │              │              │
    │              │              │(HOST)
┌───▼──────────────▼──────────────▼────────┐
│         INFRAESTRUCTURA DOCKER            │
│  ┌──────────────┐    ┌──────────────┐    │
│  │   TESTING    │    │  PRODUCTION  │    │
│  │              │    │              │    │
│  │ MySQL 8.0    │    │ MySQL 8.0    │    │
│  │ Moodle 4.5.5 │    │ Moodle 4.5.5 │    │
│  │ Port: 8081   │    │ Port: 8082   │    │
│  └──────────────┘    └──────────────┘    │
└───────────────────────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼─────┐      ┌─────▼──────┐
│ BACKUPS │      │ Apache SSL │
│ Sistema │      │ (Certbot)  │
└─────────┘      └────────────┘
```

### Arquitectura de Contenedores Docker

```
┌─────────────────────────────────────────────────────────┐
│                    RED: testing                         │
│  ┌──────────────────┐       ┌───────────────────┐      │
│  │  mysql_testing   │◄──────┤ moodle_testing    │      │
│  │  MySQL 8.0       │       │ Apache + PHP      │      │
│  │  Puerto: 3306    │       │ Moodle 4.5.5      │      │
│  └──────────────────┘       │ Puerto HOST: 8081 │      │
│                              └───────────────────┘      │
└─────────────────────────────────────────────────────────┘
                                     ▲
                                     │
┌────────────────────────────────────┴─────────────────────┐
│              APACHE HTTP SERVER (HOST)                   │
│                                                           │
│  Testing:    8080 → proxy → localhost:8081               │
│  Production:   80 → proxy → localhost:8082               │
│                                                           │
│  VirtualHosts:                                            │
│  - /etc/apache2/sites-available/moodle-testing.conf      │
│  - /etc/apache2/sites-available/moodle-production.conf   │
└───────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────┐
│                   RED: production                       │
│  ┌──────────────────┐       ┌───────────────────┐      │
│  │ mysql_production │◄──────┤ moodle_production │      │
│  │  MySQL 8.0       │       │ Apache + PHP      │      │
│  │  Puerto: 3306    │       │ Moodle 4.5.5      │      │
│  └──────────────────┘       │ Puerto HOST: 8082 │      │
│                              └───────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

---

## MÓDULOS Y COMPONENTES DETALLADOS

### 1. MÓDULO CORE (core/)

#### 1.1 os_detector.py
**Propósito**: Detectar automáticamente el sistema operativo y sus características.

**Funcionalidades**:
- Detección de distribución Linux (Ubuntu, Debian, Rocky, RHEL, Arch)
- Identificación de familia de SO
- Detección de gestor de paquetes
- Obtención de versión del sistema

**Sistemas Operativos Soportados**:
```python
Familias soportadas:
├── debian    → Ubuntu, Debian
├── rhel      → Rocky Linux, RHEL, CentOS
└── arch      → Arch Linux, Manjaro

Gestores de paquetes:
├── apt-get   (Debian/Ubuntu)
├── dnf       (Rocky/RHEL)
└── pacman    (Arch)
```

**Código clave**:
```python
class OSDetector:
    def detect(self):
        # Retorna:
        {
            'distro': 'Ubuntu',
            'version': '22.04',
            'family': 'debian',
            'package_manager': 'apt-get'
        }
```

#### 1.2 docker_installer.py
**Propósito**: Instalación automática de Docker y Docker Compose.

**Características**:
- Instalación específica por distribución
- Verificación de instalación previa
- Soporte para Docker Compose v1 y v2
- Configuración automática de servicios systemd
- Agregado de usuarios al grupo docker

**Proceso de Instalación**:
1. Verificar si Docker está instalado
2. Instalar dependencias según SO
3. Agregar repositorios oficiales de Docker
4. Instalar Docker CE + Docker Compose Plugin
5. Iniciar y habilitar servicio
6. Verificar instalación correcta

#### 1.3 directory_manager.py
**Propósito**: Crear y gestionar la estructura de directorios del proyecto.

**Estructura Creada**:
```
/opt/docker-project/
├── moodle/
│   └── 4.5.5/              # Código fuente Moodle
├── testing/
│   ├── moodledata/         # Datos Moodle Testing
│   └── mysql-data/         # Base de datos Testing
├── production/
│   ├── moodledata/         # Datos Moodle Production
│   └── mysql-data/         # Base de datos Production
├── logs/
│   ├── testing/
│   └── production/
├── backups/
│   ├── testing/
│   └── production/
├── docker-compose.yml
└── .env

Apache VirtualHosts (en el HOST):
├── /etc/apache2/sites-available/        # Debian/Ubuntu
│   ├── moodle-testing.conf
│   └── moodle-production.conf
└── /etc/httpd/conf.d/                   # RHEL/Rocky/Arch
    ├── moodle-testing.conf
    └── moodle-production.conf
```

**Permisos y Seguridad**:
- Directorios: 755 (rwxr-xr-x)
- moodledata: 755 (mejorado desde 777 por seguridad)
- Archivos de configuración: 644

#### 1.4 moodle_downloader.py
**Propósito**: Descarga automática de Moodle desde el sitio oficial.

**Características**:
- Descarga directa desde moodle.org
- Verificación de versión específica (4.5.5)
- Extracción automática de archivo .tgz
- Validación de integridad
- Manejo de errores de red

**URL de Descarga**:
```
https://download.moodle.org/download.php/direct/stable405/moodle-4.5.5.tgz
```

---

### 2. MÓDULO DOCKER (docker/)

#### 2.1 compose_generator.py
**Propósito**: Generar archivo docker-compose.yml completo.

**Servicios Generados**:

**MySQL Testing**:
```yaml
mysql_testing:
  image: mysql:8.0
  container_name: mysql_testing
  environment:
    - MYSQL_ROOT_PASSWORD=${TEST_DB_ROOT_PASS}
    - MYSQL_DATABASE=${TEST_DB_NAME}
    - MYSQL_USER=${TEST_DB_USER}
    - MYSQL_PASSWORD=${TEST_DB_PASS}
  volumes:
    - mysql_testing:/var/lib/mysql
  networks:
    - testing
  healthcheck:
    test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**Moodle Testing**:
```yaml
moodle_testing:
  build:
    context: ./moodle
    dockerfile: Dockerfile
  container_name: moodle_testing
  environment:
    - MOODLE_DATABASE_TYPE=mysqli
    - MOODLE_DATABASE_HOST=mysql_testing
    - MOODLE_DATABASE_NAME=${TEST_DB_NAME}
    - MOODLE_DATABASE_USER=${TEST_DB_USER}
    - MOODLE_DATABASE_PASSWORD=${TEST_DB_PASS}
    - MOODLE_URL=${TEST_URL}
  volumes:
    - moodledata_testing:/var/moodledata
  networks:
    - testing
  depends_on:
    mysql_testing:
      condition: service_healthy
```

**Puertos Expuestos al HOST** (para Apache):
- Testing: `8081:80` - El contenedor Moodle expone puerto 80, mapeado a 8081 en el HOST
- Production: `8082:80` - El contenedor Moodle expone puerto 80, mapeado a 8082 en el HOST
- Apache en el HOST escucha en 8080 y 80, hace proxy a estos puertos

**NOTA**: Nginx ha sido eliminado. Apache corre en el HOST como proxy reverso.

**Redes Docker**:
```yaml
networks:
  testing:
    name: testing
    driver: bridge
  production:
    name: production
    driver: bridge
```

**Volúmenes Docker**:
```yaml
volumes:
  mysql_testing:
    name: mysql_testing
  mysql_production:
    name: mysql_production
  moodledata_testing:
    name: moodledata_testing
  moodledata_production:
    name: moodledata_production
```

#### 2.2 dockerfile_generator.py
**Propósito**: Generar Dockerfiles para Moodle y Nginx.

**Dockerfile de Moodle**:
```dockerfile
FROM php:8.1-apache

# Instalar extensiones PHP requeridas
RUN apt-get update && apt-get install -y \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libzip-dev \
    libicu-dev \
    libxml2-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j$(nproc) \
        gd \
        mysqli \
        pdo_mysql \
        zip \
        intl \
        opcache \
        soap \
        xmlrpc

# Configurar PHP
RUN echo "memory_limit = 512M" >> /usr/local/etc/php/conf.d/moodle.ini
RUN echo "upload_max_filesize = 100M" >> /usr/local/etc/php/conf.d/moodle.ini
RUN echo "post_max_size = 100M" >> /usr/local/etc/php/conf.d/moodle.ini

# Habilitar mod_rewrite
RUN a2enmod rewrite

# Copiar código Moodle
COPY 4.5.5 /var/www/html

# Crear directorio moodledata
RUN mkdir -p /var/moodledata && \
    chown -R www-data:www-data /var/moodledata /var/www/html

EXPOSE 80
```

**Configuración de Apache en el HOST**:
El instalador configura automáticamente Apache en el servidor host (no en contenedor):
- Genera VirtualHosts para Testing y Production
- Configura puertos de escucha (8080 y 80)
- Establece proxy reverso a contenedores Moodle
- Habilita módulos necesarios (proxy, proxy_http)
- Recarga Apache automáticamente

#### 2.3 network_manager.py
**Propósito**: Gestionar redes Docker.

**Funcionalidades**:
- Crear redes aisladas por ambiente
- Configurar drivers de red
- Conectar contenedores a redes específicas

#### 2.4 volume_manager.py
**Propósito**: Gestionar volúmenes Docker.

**Funcionalidades**:
- Crear volúmenes persistentes
- Nombrado consistente de volúmenes
- Backup y restauración de volúmenes

---

### 3. MÓDULO APACHE (apache/)

#### 3.1 vhost_generator.py
**Propósito**: Generar VirtualHosts de Apache para proxy reverso en el HOST.

**Características**:
- Generación automática de VirtualHosts por ambiente
- Detección de SO y rutas específicas (Debian, RHEL, Arch)
- Configuración de puertos (Listen 8080 para Testing)
- Habilitación automática de sitios (a2ensite en Debian/Ubuntu)
- Recarga automática de Apache
- Headers X-Forwarded para detección correcta de protocolo en Moodle

**Configuración Testing**:
```apache
# Moodle Testing Environment VirtualHost
<VirtualHost *:8080>
    # No ServerName - acepta requests de cualquier IP/hostname

    ProxyPreserveHost On
    ProxyPass / http://localhost:8081/
    ProxyPassReverse / http://localhost:8081/

    # Headers para que Moodle conozca el protocolo y puerto original
    RequestHeader set X-Forwarded-Proto "http"
    RequestHeader set X-Forwarded-Port "8080"

    <Proxy *>
        Order deny,allow
        Allow from all
    </Proxy>

    ErrorLog ${APACHE_LOG_DIR}/moodle-testing-error.log
    CustomLog ${APACHE_LOG_DIR}/moodle-testing-access.log combined
</VirtualHost>
```

**Configuración Production**:
```apache
# Moodle Production Environment VirtualHost
<VirtualHost *:80>
    # No ServerName - acepta requests de cualquier IP/hostname

    ProxyPreserveHost On
    ProxyPass / http://localhost:8082/
    ProxyPassReverse / http://localhost:8082/

    # Headers para que Moodle conozca el protocolo original
    RequestHeader set X-Forwarded-Proto "http"

    <Proxy *>
        Order deny,allow
        Allow from all
    </Proxy>

    ErrorLog ${APACHE_LOG_DIR}/moodle-production-error.log
    CustomLog ${APACHE_LOG_DIR}/moodle-production-access.log combined
</VirtualHost>
```

**Rutas según Distribución**:
```python
Debian/Ubuntu:
- VirtualHosts: /etc/apache2/sites-available/
- Logs: /var/log/apache2/
- Comando: a2ensite moodle-testing.conf

RHEL/Rocky Linux:
- VirtualHosts: /etc/httpd/conf.d/
- Logs: /var/log/httpd/
- Carga automática de .conf

Arch Linux:
- VirtualHosts: /etc/httpd/conf/extra/
- Logs: /var/log/httpd/
- Carga automática
```

**Métodos Principales**:
```python
class ApacheVHostGenerator:
    def generate_testing_vhost():
        """Genera VirtualHost para Testing en puerto 8080"""

    def generate_production_vhost():
        """Genera VirtualHost para Production en puerto 80"""

    def configure_ports():
        """Agrega 'Listen 8080' a la configuración de Apache"""

    def enable_sites():
        """Habilita sitios con a2ensite (solo Debian/Ubuntu)"""

    def reload_apache():
        """Recarga Apache (apache2 o httpd según SO)"""

    def generate_all():
        """Configura todo automáticamente"""
```

**Configuración SSL con Certbot**:
Después de la instalación, se pueden obtener certificados SSL válidos:
```bash
# Debian/Ubuntu
sudo apt install certbot python3-certbot-apache
sudo certbot --apache -d moodle.local

# RHEL/Rocky (requiere EPEL)
sudo yum install certbot python3-certbot-apache
sudo certbot --apache -d moodle.local
```

---

### 4. MÓDULO BACKUP (backup/)

#### 4.1 backup.sh
**Propósito**: Script principal de respaldo.

**Proceso de Backup**:
```bash
1. Validar ambiente (testing/production)
2. Crear directorio de backup con timestamp
3. Exportar variables de entorno
4. Respaldar base de datos MySQL:
   - Dump completo con rutinas y triggers
   - Comprimir con gzip
   - Guardar en: DB_NAME_TIMESTAMP.sql.gz
5. Respaldar volumen moodledata:
   - Crear archivo tar del volumen
   - Comprimir con gzip
   - Guardar en: moodledata_TIMESTAMP.tar.gz
6. Generar metadatos:
   - DB_INFO.txt (tamaño, fecha)
   - MOODLEDATA_INFO.txt (tamaño, fecha)
7. Limpieza automática de backups antiguos
8. Enviar notificación por email
9. Registrar en logs
```

**Comando de Backup MySQL**:
```bash
docker exec mysql_testing mysqldump \
  --user=root \
  --password="$DB_ROOT_PASS" \
  --routines \
  --triggers \
  --events \
  "$DB_NAME" | gzip > backup.sql.gz
```

**Comando de Backup Moodledata**:
```bash
docker run --rm \
  -v moodledata_testing:/source \
  -v /backup/path:/backup \
  alpine tar -czf /backup/moodledata.tar.gz -C /source .
```

#### 4.2 restore.sh
**Propósito**: Script de restauración de backups.

**Proceso de Restauración**:
```bash
1. Validar ambiente y timestamp
2. Verificar existencia del backup
3. Solicitar confirmación del usuario (escribe "SI")
4. Detener contenedores del ambiente
5. Restaurar base de datos:
   - Eliminar BD existente
   - Crear BD nueva
   - Importar dump comprimido
6. Restaurar volumen moodledata:
   - Limpiar volumen
   - Extraer archivo tar.gz
7. Reiniciar contenedores
8. Verificar servicios
9. Mostrar resumen
```

**Comando de Restauración MySQL**:
```bash
gunzip < backup.sql.gz | docker exec -i mysql_testing \
  mysql --user=root --password="$DB_ROOT_PASS" "$DB_NAME"
```

#### 4.3 backup_manager.py
**Propósito**: Interfaz Python para gestión de backups.

**Métodos Principales**:
```python
class BackupManager:
    def create_backup(environment):
        """Crea backup del ambiente especificado"""

    def list_backups(environment):
        """Lista backups disponibles"""

    def restore_backup(environment, timestamp):
        """Restaura backup específico"""

    def get_backup_info(environment, timestamp):
        """Obtiene información detallada del backup"""
```

**Integración con Settings**:
- Carga automática de variables .env
- Gestión de rutas de backup
- Configuración de retención

#### 4.4 scheduler.py
**Propósito**: Programación automática de backups con cron.

**Características**:
- Configuración de tareas cron
- Exportación de variables de entorno
- Horarios recomendados predefinidos
- Gestión de múltiples ambientes

**Horarios Recomendados**:
```python
schedules = {
    'daily_2am': '0 2 * * *',      # Diario a las 2 AM
    'daily_3am': '0 3 * * *',      # Diario a las 3 AM
    'weekly': '0 3 * * 0',          # Semanal (domingos 3 AM)
    'every_6h': '0 */6 * * *'       # Cada 6 horas
}
```

**Configuración Cron**:
```python
def setup_cron(environment, schedule):
    """
    Configura tarea cron para backup automático

    Ejemplo:
    scheduler.setup_cron('testing', '0 2 * * *')

    Genera entrada en crontab:
    0 2 * * * /path/to/backup.sh testing
    """
```

#### 4.5 send_mail.py
**Propósito**: Sistema de notificaciones por email.

**Características**:
- Soporte SMTP con SSL/TLS
- Múltiples destinatarios
- Archivos adjuntos
- Templates HTML/texto plano
- Manejo robusto de errores

**Configuración Gmail**:
```python
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465  # SSL
# Requiere contraseña de aplicación
# https://myaccount.google.com/apppasswords
```

**Uso**:
```bash
python3 backup/send_mail.py \
  "admin@example.com" \
  "[Backup Moodle] testing - EXITOSO" \
  "Backup completado correctamente"
```

---

### 5. MÓDULO CONFIG (config/)

#### 5.1 settings.py
**Propósito**: Gestión centralizada de configuraciones.

**Variables de Configuración**:

**Generales**:
```python
MOODLE_VERSION = '4.5.5'
BASE_PATH = '/opt/docker-project'
PROJECT_NAME = 'moodle_infrastructure'
```

**Testing**:
```python
TEST_URL = 'https://test.moodle.local'
TEST_DB_NAME = 'moodle_test'
TEST_DB_USER = 'moodle_test_user'
TEST_DB_PASS = (auto-generada)
TEST_HTTP_PORT = '8081'
TEST_HTTPS_PORT = '8443'
```

**Production**:
```python
PROD_URL = 'https://moodle.local'
PROD_DB_NAME = 'moodle_prod'
PROD_DB_USER = 'moodle_prod_user'
PROD_DB_PASS = (auto-generada)
PROD_HTTP_PORT = '80'
PROD_HTTPS_PORT = '443'
```

**SSL**:
```python
SSL_CERT_TYPE = 'self-signed'  # self-signed | letsencrypt | custom
SSL_LETSENCRYPT_EMAIL = ''
SSL_FORCE_HTTPS = True
```

**Backups**:
```python
BACKUP_RETENTION_DAYS = 7
BACKUP_EMAIL_TO = ''
```

**SMTP**:
```python
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465
SMTP_USER = ''
SMTP_PASSWORD = ''
SMTP_FROM_NAME = 'Moodle Backup System'
```

**Recursos**:
```python
MYSQL_MAX_CONNECTIONS = 200
PHP_MEMORY_LIMIT = '512M'
PHP_MAX_EXECUTION_TIME = 300
PHP_UPLOAD_MAX_FILESIZE = '100M'
PHP_POST_MAX_SIZE = '100M'
```

**Funcionalidades**:
```python
class Settings:
    def generate_env_file():
        """Genera archivo .env con todas las variables"""

    def load_env_file():
        """Carga variables desde .env existente"""

    def show_credentials_summary():
        """Muestra resumen de credenciales generadas"""
```

#### 5.2 env_template.py
**Propósito**: Template para generación de archivo .env.

---

### 6. MÓDULO UTILS (utils/)

#### 6.1 logger.py
**Propósito**: Sistema de logging con colores.

**Niveles de Log**:
```python
logger.info("Mensaje informativo")     # Azul
logger.success("Operación exitosa")    # Verde
logger.warning("Advertencia")          # Amarillo
logger.error("Error crítico")          # Rojo
```

#### 6.2 password_generator.py
**Propósito**: Generación de contraseñas seguras.

**Características**:
- Longitud: 16 caracteres
- Incluye: mayúsculas, minúsculas, números, símbolos
- Cumple requisitos de seguridad de Moodle
- Utiliza secrets para generación criptográfica

**Ejemplo**:
```python
pg = PasswordGenerator()
password = pg.generate()
# Resultado: "Kj8#mP2$xR9&Lq5!"
```

#### 6.3 validator.py
**Propósito**: Validaciones del sistema.

**Validaciones**:
```python
class Validator:
    def check_root():
        """Verifica permisos root/sudo"""

    def check_port_available(port):
        """Verifica si puerto está disponible"""

    def validate_url(url):
        """Valida formato de URL"""

    def check_disk_space(required_gb):
        """Verifica espacio en disco"""
```

#### 6.4 rollback.py
**Propósito**: Sistema de rollback en caso de errores.

**Funcionalidades**:
- Registro de operaciones ejecutadas
- Reversión automática en caso de fallo
- Limpieza de archivos creados
- Eliminación de contenedores y volúmenes

#### 6.5 ssl_manager.py
**Propósito**: Gestión de certificados SSL.

**Tipos de Certificados**:

**1. Autofirmados (Self-signed)**:
```bash
# Generación automática
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout testing.key \
  -out testing.crt \
  -subj "/CN=test.moodle.local"
```

**2. Let's Encrypt**:
```bash
# Instalación certbot
# Rocky Linux requiere EPEL (habilitado por install.sh)
certbot certonly --standalone \
  -d test.moodle.local \
  --email admin@moodle.local
```

**3. Personalizados**:
- Permite usar certificados comprados
- Solicita rutas de .crt y .key

**Configuración SSL en Moodle**:
```php
// Generado en moodle_config/ssl_config.php
$CFG->sslproxy = true;
$CFG->wwwroot = 'https://moodle.local';
```

#### 6.6 docker_compose_wrapper.py
**Propósito**: Compatibilidad entre Docker Compose v1 y v2.

**Características**:
- Detección automática de versión
- Wrapper transparente
- Soporte para ambos comandos:
  - `docker-compose` (v1)
  - `docker compose` (v2)

**Uso**:
```python
DockerComposeWrapper.run_compose_shell("up -d", cwd="/opt/docker-project")
```

---

## FLUJO DE INSTALACIÓN COMPLETO

### Fase 1: Preparación del Sistema
```
1. Usuario ejecuta: sudo ./install.sh
   ├── Detectar sistema operativo
   ├── Habilitar EPEL (RHEL/Rocky)
   ├── Instalar git y wget
   ├── Instalar pip3
   ├── Instalar dependencias Python
   └── Crear .env desde .env.example

2. (Opcional) Usuario edita .env
   └── Personalizar URLs, puertos, contraseñas
```

### Fase 2: Instalación Principal
```
3. Usuario ejecuta: sudo python3 main.py
   └── Menú principal → Opción 1

4. Detección y Validación
   ├── Detectar SO (Ubuntu/Rocky/Arch)
   ├── Validar permisos root
   └── Verificar espacio en disco

5. Instalación de Docker
   ├── Verificar si Docker existe
   ├── Si no existe:
   │   ├── Agregar repositorios oficiales
   │   ├── Instalar Docker CE
   │   ├── Instalar Docker Compose Plugin
   │   ├── Iniciar servicio docker
   │   └── Habilitar inicio automático
   └── Verificar instalación correcta

6. Creación de Estructura
   ├── Crear /opt/docker-project/
   ├── Crear subdirectorios:
   │   ├── moodle/4.5.5/
   │   ├── testing/
   │   ├── production/
   │   ├── nginx/
   │   ├── logs/
   │   └── backups/
   └── Establecer permisos 755

7. Descarga de Moodle
   ├── Descargar moodle-4.5.5.tgz
   ├── Verificar descarga
   ├── Extraer a moodle/4.5.5/
   └── Establecer permisos

8. Generación de Credenciales
   ├── Generar contraseñas seguras (16 chars)
   ├── Testing: DB, Admin
   └── Production: DB, Admin

9. Generación de archivo .env
   ├── Escribir todas las variables
   ├── Guardar en /opt/docker-project/.env
   └── Mostrar resumen de credenciales

10. Generación de Dockerfiles
    ├── Moodle Dockerfile
    │   ├── Imagen base: php:8.1-apache
    │   ├── Extensiones PHP
    │   └── Configuraciones PHP
    └── Nginx Dockerfile
        └── Imagen base: nginx:alpine

11. Generación de docker-compose.yml
    ├── Servicios MySQL (testing + production)
    ├── Servicios Moodle (testing + production)
    │   ├── Testing expone puerto 8081
    │   └── Production expone puerto 8082
    ├── Redes (testing, production)
    └── Volúmenes (4 totales)

12. Generación de VirtualHosts de Apache (en el HOST)
    ├── moodle-testing.conf (puerto 8080)
    ├── moodle-production.conf (puerto 80)
    ├── Configuración de Listen 8080
    └── Recarga de Apache
```

### Fase 3: Levantamiento de Ambientes
```
13. Selección de Ambiente
    Usuario selecciona:
    ├── 1. Solo Testing
    ├── 2. Solo Production
    ├── 3. Ambos
    └── 4. Ninguno (solo instalar)

14. Para cada ambiente seleccionado:
    ├── Levantar contenedores:
    │   ├── docker compose up -d mysql_testing
    │   └── docker compose up -d moodle_testing
    └── Verificar healthchecks

    NOTA: Nginx ha sido eliminado. Apache corre en el HOST.

15. Pausa para Instalación Web
    ├── Mostrar URLs de acceso
    ├── Usuario completa wizard de Moodle
    └── Presionar Enter para continuar
```

### Fase 4: Configuración SSL (Opcional - Post-instalación)
```
16. Configuración SSL con Certbot (manual):
    ├── Usuario instala certbot:
    │   └── sudo apt install certbot python3-certbot-apache  (Debian/Ubuntu)
    │   └── sudo yum install certbot python3-certbot-apache  (RHEL/Rocky)
    ├── Usuario ejecuta certbot:
    │   └── sudo certbot --apache -d moodle.local
    └── Certbot configura automáticamente:
        ├── Obtiene certificado de Let's Encrypt
        ├── Modifica VirtualHost para HTTPS
        ├── Configura redirección HTTP → HTTPS
        └── Configura renovación automática

NOTA: La configuración SSL en Nginx ha sido reemplazada por Apache + Certbot
```

### Fase 5: Configuración de Backups
```
17. Configuración Automática de Backups
    ├── Preguntar si configurar backups
    └── Si acepta:
        ├── Testing: cron a las 2:00 AM
        └── Production: cron a las 3:00 AM

18. Resumen Final
    ├── Mostrar URLs de acceso
    ├── Mostrar puertos
    ├── Mostrar ubicación de .env
    └── Mostrar próximos pasos
```

---

## GESTIÓN POST-INSTALACIÓN

### Menú Principal (main.py)

```
===============================================================
                       MENU PRINCIPAL
===============================================================

  1. Instalar infraestructura completa

  2. Gestionar ambientes
     - Levantar/Detener Testing
     - Levantar/Detener Produccion
     - Ver estado de servicios

  3. Ver logs

  4. Gestionar backups
     - Configurar backup automatico
     - Ejecutar backup manual
     - Restaurar backup

  5. Desinstalar todo

  0. Salir

===============================================================
```

### Opción 2: Gestionar Ambientes

**Funcionalidades**:
```
1. Levantar Testing
   docker compose up -d mysql_testing moodle_testing

2. Detener Testing
   docker compose down mysql_testing moodle_testing

3. Levantar Produccion
   docker compose up -d mysql_production moodle_production

4. Detener Produccion
   docker compose down mysql_production moodle_production

5. Ver estado
   docker compose ps

6. Reiniciar Testing
   docker compose restart mysql_testing moodle_testing

7. Reiniciar Produccion
   docker compose restart mysql_production moodle_production

NOTA: Apache se gestiona en el HOST con:
- sudo systemctl restart apache2   (Debian/Ubuntu)
- sudo systemctl restart httpd     (RHEL/Rocky/Arch)
```

**Características Especiales**:
- Verificación automática de SSL al levantar
- Configuración SSL si no existe
- Aplicación automática de configuración SSL a Moodle

### Opción 3: Ver Logs

**Opciones de Logs**:
```
1. Logs Testing - Todos los servicios
   docker compose logs testing

2. Logs Production - Todos los servicios
   docker compose logs production

3-4. Logs Testing por servicio
   - Moodle: docker compose logs moodle_testing
   - MySQL: docker compose logs mysql_testing

5-6. Logs Production por servicio
   - Moodle: docker compose logs moodle_production
   - MySQL: docker compose logs mysql_production

Logs de Apache (en el HOST):
   - Testing: sudo tail -f /var/log/apache2/moodle-testing-error.log
   - Production: sudo tail -f /var/log/httpd/moodle-production-access.log
```

**Características**:
- Tail de 100 líneas
- Seguimiento en tiempo real (-f)
- Ctrl+C para salir

### Opción 4: Gestionar Backups

**Submenú de Backups**:
```
1. Crear backup manual (Testing)
   → Ejecuta backup.sh testing

2. Crear backup manual (Produccion)
   → Ejecuta backup.sh production

3. Listar backups disponibles
   → Muestra todos los backups con fechas y tamaños

4. Restaurar backup (Testing)
   → Seleccionar timestamp y confirmar

5. Restaurar backup (Produccion)
   → Seleccionar timestamp y confirmar (+ advertencia)

6. Configurar backup automatico (Testing)
   → Configurar expresión cron

7. Configurar backup automatico (Produccion)
   → Configurar expresión cron

8. Ver tareas programadas
   → crontab -l | grep backup

9. Eliminar backup automatico
   → Eliminar de crontab

10. Configurar notificaciones por email
    → Editar variables SMTP en .env

11. Ver informacion detallada de un backup
    → Tamaños, archivos, metadatos
```

**Proceso de Backup Manual**:
```
1. Usuario selecciona ambiente
2. Sistema solicita confirmación
3. Ejecuta backup.sh:
   ├── Crea directorio con timestamp
   ├── Exporta BD MySQL (comprimida)
   ├── Exporta volumen moodledata (tar.gz)
   ├── Genera metadatos
   ├── Limpia backups antiguos
   └── Envía email (si configurado)
4. Muestra resultado
```

**Proceso de Restauración**:
```
1. Usuario selecciona ambiente
2. Sistema lista backups disponibles
3. Usuario ingresa timestamp
4. ADVERTENCIA: Se perderán datos actuales
5. Usuario confirma escribiendo "SI"
6. Sistema ejecuta restore.sh:
   ├── Detiene contenedores
   ├── Restaura base de datos
   ├── Restaura moodledata
   ├── Reinicia contenedores
   └── Verifica servicios
7. Muestra resultado
```

### Opción 5: Desinstalar

**Opciones de Desinstalación**:
```
1. Eliminar solo Testing
   ├── Detener contenedores
   ├── Eliminar contenedores
   ├── Eliminar volúmenes
   ├── Eliminar directorios
   └── Eliminar logs

2. Eliminar solo Production
   ├── Ofrecer crear backup
   ├── Confirmar con "SI"
   ├── Detener contenedores
   ├── Eliminar contenedores
   ├── Eliminar volúmenes
   ├── Eliminar directorios
   └── Eliminar logs

3. Eliminar TODO
   ├── Ofrecer backup de Production
   ├── Confirmar con "ELIMINAR TODO"
   ├── docker compose down -v
   ├── rm -rf /opt/docker-project
   └── Finalizar
```

---

## SEGURIDAD

### Prácticas de Seguridad Implementadas

1. **Generación de Contraseñas**:
   - Longitud: 16 caracteres
   - Caracteres especiales, números, mayúsculas, minúsculas
   - Utiliza módulo `secrets` (criptográficamente seguro)

2. **Permisos de Archivos**:
   - Directorios: 755 (rwxr-xr-x)
   - Archivos de configuración: 644 (rw-r--r--)
   - Archivo .env: Solo lectura para owner

3. **Aislamiento de Ambientes**:
   - Redes Docker separadas
   - Bases de datos independientes
   - Volúmenes aislados
   - Contenedores con nombres únicos

4. **SSL/TLS**:
   - Redirección automática HTTP → HTTPS
   - Protocolos: TLSv1.2, TLSv1.3
   - Ciphers seguros: HIGH:!aNULL:!MD5
   - Forzar HTTPS en Moodle

5. **Backup de Credenciales**:
   - No se almacenan contraseñas en logs
   - Archivo .env fuera del control de versiones (.gitignore)
   - Backups no incluyen contraseñas en texto plano

6. **Contenedores**:
   - Imágenes oficiales (mysql:8.0, php:8.1-apache, nginx:alpine)
   - Healthchecks configurados
   - Restart policy: unless-stopped
   - Sin puertos innecesarios expuestos

---

## COMPATIBILIDAD Y REQUISITOS

### Sistemas Operativos Soportados

**Familia Debian**:
- Ubuntu 20.04 LTS
- Ubuntu 22.04 LTS
- Ubuntu 24.04 LTS
- Debian 10 (Buster)
- Debian 11 (Bullseye)
- Debian 12 (Bookworm)

**Familia RHEL**:
- Rocky Linux 8
- Rocky Linux 9
- RHEL 8
- RHEL 9
- CentOS Stream 8/9

**Familia Arch**:
- Arch Linux
- Manjaro

### Requisitos de Hardware

**Mínimos**:
- CPU: 2 cores
- RAM: 4 GB
- Disco: 20 GB libres
- Red: Conexión a Internet

**Recomendados**:
- CPU: 4+ cores
- RAM: 8+ GB
- Disco: 50+ GB libres (SSD recomendado)
- Red: 100 Mbps+

### Requisitos de Software

**Esenciales**:
- Python 3.8 o superior
- pip3
- Git
- Wget
- Permisos root/sudo

**Instalados Automáticamente**:
- Docker CE 20.10+
- Docker Compose Plugin
- Dependencias Python (ver requirements.txt)

### Dependencias Python (requirements.txt)

```python
# Core
requests>=2.31.0       # Descargas HTTP
pyyaml>=6.0            # Generación de YAML
python-dotenv>=1.0.0   # Gestión de .env

# Sistema
psutil>=5.9.0          # Monitoreo de recursos
distro>=1.8.0          # Detección de SO

# UI (opcional)
colorama>=0.4.6        # Colores en terminal
```

---

## TROUBLESHOOTING

### Problemas Comunes y Soluciones

#### 1. Error: Puerto ocupado

**Síntoma**:
```
Error starting userland proxy: listen tcp4 0.0.0.0:80: bind: address already in use
```

**Solución**:
```bash
# Verificar qué proceso usa el puerto
sudo lsof -i :80

# Editar .env y cambiar puerto
nano /opt/docker-project/.env
# Cambiar: PROD_HTTP_PORT='8090'

# Reiniciar contenedores
cd /opt/docker-project
docker compose restart
```

#### 2. Docker no inicia

**Síntoma**:
```
Cannot connect to the Docker daemon
```

**Solución**:
```bash
# Verificar estado
sudo systemctl status docker

# Iniciar Docker
sudo systemctl start docker

# Habilitar inicio automático
sudo systemctl enable docker

# Verificar instalación
docker --version
docker compose version
```

#### 3. Error de permisos en moodledata

**Síntoma**:
```
Can not create directory /var/moodledata
```

**Solución**:
```bash
# Dentro del contenedor
docker exec -it moodle_testing chown -R www-data:www-data /var/moodledata
docker exec -it moodle_testing chmod -R 755 /var/moodledata
```

#### 4. Error SSL - Contenido mixto

**Síntoma**:
```
Mixed Content: The page was loaded over HTTPS, but requested an insecure resource
```

**Solución**:
```bash
# Verificar configuración SSL
cat /opt/docker-project/production/moodle_config/ssl_config.php

# Aplicar configuración SSL
sudo bash utils/apply_ssl_config.sh production

# Limpiar cache de Moodle
docker exec moodle_production php /var/www/html/admin/cli/purge_caches.php
```

#### 5. Backup falla - Sin espacio

**Síntoma**:
```
No space left on device
```

**Solución**:
```bash
# Verificar espacio
df -h

# Limpiar backups antiguos manualmente
rm -rf /opt/docker-project/backups/testing/2024-01-*

# Limpiar imágenes Docker no usadas
docker system prune -a

# Ajustar retención de backups
nano /opt/docker-project/.env
# BACKUP_RETENTION_DAYS='3'
```

#### 6. MySQL no inicia - Error de InnoDB

**Síntoma**:
```
InnoDB: Cannot allocate memory for the buffer pool
```

**Solución**:
```bash
# Verificar RAM disponible
free -h

# Aumentar memoria del sistema
# O reducir max_connections en .env

# Reiniciar MySQL
docker compose restart mysql_testing
```

#### 7. Error Let's Encrypt - Puerto 80 no accesible

**Síntoma**:
```
Certbot failed: Port 80 is already in use
```

**Solución**:
```bash
# Detener Nginx temporalmente
docker compose stop nginx

# Ejecutar certbot standalone
sudo certbot certonly --standalone -d moodle.local

# Copiar certificados a nginx/ssl/
cp /etc/letsencrypt/live/moodle.local/fullchain.pem nginx/ssl/production.crt
cp /etc/letsencrypt/live/moodle.local/privkey.pem nginx/ssl/production.key

# Reiniciar Nginx
docker compose start nginx
```

#### 8. Email de backups no se envía

**Síntoma**:
```
Email notification failed
```

**Solución**:
```bash
# Verificar configuración SMTP
grep SMTP /opt/docker-project/.env

# Para Gmail: usar contraseña de aplicación
# https://myaccount.google.com/apppasswords

# Probar envío manual
python3 backup/send_mail.py "test@email.com" "Test" "Mensaje de prueba"
```

---

## MANTENIMIENTO

### Tareas de Mantenimiento Recomendadas

#### Diarias
```bash
# Verificar estado de contenedores
docker compose ps

# Verificar logs por errores
docker compose logs --tail=50 | grep -i error
```

#### Semanales
```bash
# Verificar backups
ls -lh /opt/docker-project/backups/production/

# Verificar espacio en disco
df -h /opt/docker-project

# Actualizar sistema operativo
sudo apt update && sudo apt upgrade  # Ubuntu/Debian
sudo dnf update                       # Rocky/RHEL
```

#### Mensuales
```bash
# Probar restauración de backup (en Testing)
# Limpiar logs antiguos
find /opt/docker-project/logs -name "*.log" -mtime +30 -delete

# Actualizar imágenes Docker
docker compose pull
docker compose up -d
```

#### Semestrales
```bash
# Actualizar versión de Moodle
# Renovar certificados SSL (si no son automáticos)
# Revisar y actualizar contraseñas
# Auditoría de seguridad
```

### Actualización de Moodle

```bash
# 1. Crear backup de Production
bash backup/backup.sh production

# 2. Descargar nueva versión
cd /opt/docker-project/moodle
wget https://download.moodle.org/download.php/direct/stable406/moodle-4.6.0.tgz
tar -xzf moodle-4.6.0.tgz
mv moodle 4.6.0

# 3. Actualizar .env
nano /opt/docker-project/.env
# MOODLE_VERSION='4.6.0'

# 4. Reconstruir contenedores
docker compose build --no-cache moodle_production
docker compose up -d moodle_production

# 5. Completar actualización vía web
# Acceder a https://moodle.local
```

### Monitoreo de Recursos

```bash
# Ver uso de CPU/RAM por contenedor
docker stats

# Ver tamaño de volúmenes
docker system df -v

# Ver logs de un contenedor específico
docker logs -f moodle_production

# Verificar healthchecks
docker inspect moodle_production | grep -A 10 Health
```

---

## MEJORAS FUTURAS

### Roadmap de Desarrollo

#### Versión 1.1 (Corto Plazo)
- [ ] Dashboard web de administración
- [ ] Monitoreo automático con alertas
- [ ] Backup incremental
- [ ] Sincronización con almacenamiento remoto (S3, rsync)
- [ ] Soporte para múltiples instancias de Moodle

#### Versión 1.2 (Mediano Plazo)
- [ ] Integración con Prometheus + Grafana
- [ ] Backup diferencial
- [ ] API REST para gestión remota
- [ ] Cliente CLI mejorado
- [ ] Soporte para Kubernetes

#### Versión 2.0 (Largo Plazo)
- [ ] Clúster de alta disponibilidad
- [ ] Auto-escalado horizontal
- [ ] Balanceo de carga automático
- [ ] Migración entre clouds
- [ ] Modo multi-tenant

---

## DOCUMENTACIÓN ADICIONAL

### Archivos de Documentación Incluidos

1. **README.md**: Documentación principal del proyecto
2. **CHANGELOG.md**: Historial de cambios y versiones
3. **QUICKSTART.md**: Guía rápida de inicio
4. **backup/README.md**: Documentación del sistema de backups
5. **utils/SSL_CONFIGURATION.md**: Configuración SSL detallada
6. **utils/CERTBOT_ROCKY_LINUX.md**: Let's Encrypt en Rocky Linux
7. **utils/DOCKER_COMPOSE_COMPATIBILITY.md**: Compatibilidad v1/v2
8. **SISTEMA_RESPALDOS_INTEGRADO.md**: Sistema de respaldos integrado

### Comandos Útiles de Docker

```bash
# Ver todos los contenedores
docker ps -a

# Ver logs de un contenedor
docker logs -f <container_name>

# Ejecutar comando en contenedor
docker exec -it <container_name> bash

# Ver uso de recursos
docker stats

# Limpiar sistema
docker system prune -a

# Ver redes
docker network ls

# Ver volúmenes
docker volume ls

# Inspeccionar contenedor
docker inspect <container_name>

# Ver imágenes
docker images

# Eliminar imagen
docker rmi <image_id>
```

### Comandos Docker Compose

```bash
# Levantar servicios
docker compose up -d

# Detener servicios
docker compose down

# Ver estado
docker compose ps

# Ver logs
docker compose logs -f

# Reiniciar servicio
docker compose restart <service_name>

# Reconstruir imagen
docker compose build --no-cache

# Escalar servicio
docker compose up -d --scale moodle_testing=3

# Validar archivo
docker compose config
```

---

## CONCLUSIONES

### Logros del Proyecto

1. **Automatización Completa**: Instalación de infraestructura Moodle en menos de 30 minutos
2. **Portabilidad**: Funciona en 3 familias de Linux diferentes
3. **Seguridad**: Generación automática de contraseñas, SSL integrado
4. **Backup Robusto**: Sistema completo de respaldo y restauración
5. **Facilidad de Uso**: Menú interactivo intuitivo
6. **Documentación Completa**: Más de 8 documentos de referencia

### Beneficios Principales

**Para Administradores**:
- Despliegue rápido de ambientes
- Gestión centralizada
- Backups automatizados
- Recuperación ante desastres

**Para Desarrolladores**:
- Ambiente de testing aislado
- Código modular y extensible
- Fácil personalización
- Buenas prácticas implementadas

**Para la Institución**:
- Reducción de costos operativos
- Mayor disponibilidad del servicio
- Cumplimiento de estándares de seguridad
- Escalabilidad futura

### Impacto Educativo

El proyecto proporciona a SLEP Andalien Sur:
- Infraestructura Moodle moderna y segura
- Ambientes separados para desarrollo y producción
- Sistema de respaldos confiable
- Documentación completa para mantenimiento
- Independencia tecnológica

---

## CRÉDITOS Y LICENCIA

### Autor
**Eduardo Valdés**
- Institución: SLEP Andalien Sur
- Proyecto: CIISA - 2º Año
- Email: [Configurar en .env]

### Historial de Desarrollo
- 2024-12-01: Correcciones Post-Integración
- 2024-12-03: Mejoras de Seguridad y Verificaciones
- 2024-12-05: Optimización de Infraestructura Docker
- 2024-12-07: Sistema de Respaldos Completo
- 2024-12-08: Mejoras en Gestión y Configuración
- 2024-12-09: Corrección de Errores y Limpieza de Código
- 2024-12-10: Limpieza y Consolidación de Documentación
- 2024-12-21: Migración de Nginx a Apache HTTP Server

### Tecnologías Utilizadas

**Lenguajes**:
- Python 3.8+
- Bash
- YAML
- PHP 8.1
- SQL

**Frameworks y Librerías**:
- Moodle 4.5.5
- Docker Engine
- Docker Compose
- Apache HTTP Server 2.4 (HOST)
- MySQL 8.0

**Herramientas**:
- Git
- OpenSSL
- Certbot (Let's Encrypt)
- Cron
- SMTP

### Licencia
MIT License

Copyright (c) 2024 Eduardo Valdés - SLEP Andalien Sur

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## ANEXOS

### Anexo A: Ejemplo de Archivo .env Completo

```bash
# Moodle Docker Infrastructure Configuration
# Generado automáticamente

# GENERAL
MOODLE_VERSION='4.5.5'
PROJECT_NAME='moodle_infrastructure'

# TESTING ENVIRONMENT
TEST_URL='https://test.moodle.local'
TEST_DB_NAME='moodle_test'
TEST_DB_USER='moodle_test_user'
TEST_DB_PASS='Kj8#mP2$xR9&Lq5!'
TEST_DB_ROOT_PASS='Mn3@pL7*vT4&Wd2!'
TEST_MOODLE_ADMIN_USER='admin_test'
TEST_MOODLE_ADMIN_PASS='Rt5$nK9@bX3&Hm7!'
TEST_MOODLE_ADMIN_EMAIL='admin@test.moodle.local'
TEST_HTTP_PORT='8081'
TEST_HTTPS_PORT='8443'

# PRODUCTION ENVIRONMENT
PROD_URL='https://moodle.local'
PROD_DB_NAME='moodle_prod'
PROD_DB_USER='moodle_prod_user'
PROD_DB_PASS='Qw6&jF4$mN8@Xy2!'
PROD_DB_ROOT_PASS='Zv9!tC5#rL3@Pk7!'
PROD_MOODLE_ADMIN_USER='admin'
PROD_MOODLE_ADMIN_PASS='Bt8@vM2$kD6&Ln4!'
PROD_MOODLE_ADMIN_EMAIL='admin@moodle.local'
PROD_HTTP_PORT='80'
PROD_HTTPS_PORT='443'

# APACHE CONFIGURATION
# Apache corre en el HOST como proxy reverso
# Testing: Apache escucha en 8080 → Moodle contenedor en 8081
# Production: Apache escucha en 80 → Moodle contenedor en 8082

# SSL CONFIGURATION (para Apache en el HOST)
# Configurar SSL con: sudo certbot --apache -d tusitio.com
SSL_FORCE_HTTPS='false'

# BACKUP CONFIGURATION
BACKUP_RETENTION_DAYS='7'
BACKUP_EMAIL_TO='admin@example.com'

# SMTP CONFIGURATION
SMTP_SERVER='smtp.gmail.com'
SMTP_PORT='465'
SMTP_USER='backups@slep.cl'
SMTP_PASSWORD='app_password_here'
SMTP_FROM_NAME='Moodle Backup System'

# AUTO-START CONFIGURATION
AUTO_START_ON_BOOT='false'
AUTO_INSTALL_MOODLE='false'
AUTO_BACKUP_ON_START='true'
MONITORING_ENABLED='false'
MONITORING_INTERVAL='60'

# RESOURCE LIMITS
MYSQL_MAX_CONNECTIONS='200'
PHP_MEMORY_LIMIT='512M'
PHP_MAX_EXECUTION_TIME='300'
PHP_UPLOAD_MAX_FILESIZE='100M'
PHP_POST_MAX_SIZE='100M'
```

### Anexo B: Estructura Completa de Archivos del Proyecto

```
moodle-docker-installer/
├── backup/
│   ├── __init__.py
│   ├── backup.sh              # Script de respaldo
│   ├── restore.sh             # Script de restauración
│   ├── backup_manager.py      # Gestor Python de backups
│   ├── scheduler.py           # Programación cron
│   ├── send_mail.py          # Notificaciones email
│   └── README.md             # Documentación backups
├── config/
│   ├── __init__.py
│   ├── settings.py           # Configuraciones generales
│   └── env_template.py       # Template de .env
├── core/
│   ├── __init__.py
│   ├── os_detector.py        # Detección de SO
│   ├── docker_installer.py   # Instalación Docker
│   ├── directory_manager.py  # Gestión de directorios
│   └── moodle_downloader.py  # Descarga de Moodle
├── docker/
│   ├── __init__.py
│   ├── compose_generator.py  # Genera docker-compose.yml
│   ├── dockerfile_generator.py # Genera Dockerfiles
│   ├── network_manager.py    # Gestión de redes
│   └── volume_manager.py     # Gestión de volúmenes
├── apache/
│   ├── __init__.py
│   └── vhost_generator.py    # Generador de VirtualHosts
├── utils/
│   ├── __init__.py
│   ├── logger.py             # Sistema de logging
│   ├── password_generator.py # Generador de contraseñas
│   ├── validator.py          # Validaciones
│   ├── rollback.py           # Sistema de rollback
│   ├── ssl_manager.py        # Gestión SSL
│   ├── docker_compose_wrapper.py # Wrapper v1/v2
│   ├── apply_ssl_config.sh   # Aplicar SSL a Moodle
│   ├── apply_ssl_to_moodle.sh
│   ├── fix_moodle_production.sh
│   ├── SSL_CONFIGURATION.md
│   ├── CERTBOT_ROCKY_LINUX.md
│   └── DOCKER_COMPOSE_COMPATIBILITY.md
├── main.py                   # Script principal
├── install.sh                # Instalación de dependencias
├── test.py                   # Suite de pruebas
├── requirements.txt          # Dependencias Python
├── .env.example              # Ejemplo de configuración
├── .gitignore
├── README.md                 # Documentación principal
├── CHANGELOG.md              # Historial de cambios
├── QUICKSTART.md             # Guía rápida
├── SISTEMA_RESPALDOS_INTEGRADO.md
├── STRUCTURE.txt
└── INFORME_PROYECTO_COMPLETO.md  # Este documento
```

### Anexo C: Expresiones Cron Comunes

```bash
# Formato: minuto hora día mes día_semana comando

# Cada minuto
* * * * * comando

# Cada 5 minutos
*/5 * * * * comando

# Cada hora
0 * * * * comando

# Diario a medianoche
0 0 * * * comando

# Diario a las 2 AM
0 2 * * * comando

# Todos los domingos a las 3 AM
0 3 * * 0 comando

# Primer día de cada mes a las 4 AM
0 4 1 * * comando

# Cada 6 horas
0 */6 * * * comando

# Lunes a viernes a las 8 AM
0 8 * * 1-5 comando

# Fines de semana a las 10 AM
0 10 * * 6,0 comando
```

---

**Documento generado el**: 14 de Diciembre de 2024
**Versión del documento**: 1.0
**Autor**: Eduardo Valdés
**Proyecto**: CIISA - 2º Año
**Institución**: SLEP Andalien Sur

---

**FIN DEL INFORME**
