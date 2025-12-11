# Moodle Docker Infrastructure Installer

Instalador automatizado de infraestructura Moodle con Docker para ambientes de Testing y Produccion.

## Caracteristicas

- Deteccion automatica de SO (Ubuntu/Debian, Rocky/RHEL, Arch Linux)
- Instalacion automatica de Docker y Docker Compose
- Descarga de Moodle 4.5.5 desde sitio oficial
- Ambientes separados de Testing y Produccion
- Bases de datos MySQL independientes
- Proxy reverso Nginx unificado con SSL
- **Sistema completo de backups y restauracion**
- **Configuracion automatica de backups durante instalacion**
- Gestion completa desde menu interactivo
- Variables de entorno mejoradas para optimizacion

## Requisitos

- Sistema operativo soportado:
  - Ubuntu/Debian (LTS)
  - Rocky Linux/RHEL (LTS)
  - Arch Linux
- Permisos de root/sudo
- Minimo 10GB de espacio en disco
- Conexion a internet

## Instalacion Rapida

```bash
# Clonar o descargar el proyecto
cd moodle-docker-installer

# 1. IMPORTANTE: Ejecutar script de instalación de dependencias
#    Este script instalará git, wget, pip y creará el archivo .env
sudo ./install.sh

# 2. (OPCIONAL) Editar el archivo .env con tus configuraciones
#    Si no lo editas, se generarán contraseñas seguras automáticamente
nano .env

# 3. Ejecutar instalador principal
sudo python3 main.py
```

### Importante: Orden de Instalación

1. **Primero**: Ejecuta `sudo ./install.sh`
   - Habilita repositorio EPEL (en RHEL/Rocky Linux)
   - Instala dependencias del sistema (git, wget)
   - Instala pip3 si no está presente
   - Instala dependencias Python
   - **Crea archivo .env desde .env.example**

2. **Segundo**: Edita el archivo `.env` (opcional)
   - Configura URLs personalizadas
   - Configura puertos si los por defecto están ocupados
   - Establece contraseñas personalizadas (o déjalas para auto-generación)

3. **Tercero**: Ejecuta `sudo python3 main.py`
   - Inicia el instalador principal
   - Las contraseñas marcadas como `GENERAR_CONTRASEÑA_SEGURA` se generan automáticamente

## Estructura del Proyecto

```
moodle-docker-installer/
├── main.py                      # Script principal
├── install.sh                   # Script de instalación de dependencias
├── requirements.txt             # Dependencias Python
├── .env.example                 # Plantilla de configuración
├── config/                      # Configuraciones
│   ├── settings.py
│   └── env_template.py
├── core/                        # Modulos principales
│   ├── os_detector.py
│   ├── docker_installer.py
│   ├── directory_manager.py
│   └── moodle_downloader.py
├── docker/                      # Gestion Docker
│   ├── dockerfile_generator.py
│   ├── compose_generator.py
│   ├── network_manager.py
│   └── volume_manager.py
├── nginx/                       # Configuraciones Nginx
│   └── config_generator.py
├── backup/                      # Sistema de backups
│   ├── backup.sh                # Script de respaldo
│   ├── restore.sh               # Script de restauracion
│   ├── send_mail.py             # Notificaciones email
│   ├── backup_manager.py        # Gestor Python
│   ├── scheduler.py             # Programacion cron
│   └── README.md                # Documentacion backups
└── utils/                       # Utilidades
    ├── logger.py
    ├── password_generator.py
    ├── validator.py
    ├── rollback.py
    ├── ssl_manager.py           # Gestor de certificados SSL
    ├── docker_compose_wrapper.py # Wrapper Docker Compose V1/V2
    ├── DOCKER_COMPOSE_COMPATIBILITY.md
    └── SSL_CONFIGURATION.md     # Documentacion SSL
```

## Estructura de Instalacion

Una vez instalado, la estructura en `/opt/docker-project/` sera:

```
/opt/docker-project/
├── .env                         # Variables de entorno
├── docker-compose.yml           # Orquestacion de contenedores
├── nginx/                       # Configuraciones Nginx
│   ├── conf.d/
│   │   ├── testing.conf
│   │   └── production.conf
│   └── ssl/
│       ├── testing.crt
│       └── production.crt
├── moodle/
│   ├── 4.5.5/                   # Codigo fuente Moodle
│   └── Dockerfile
├── testing/
│   ├── moodledata/              # Datos Moodle Testing
│   └── mysql-data/              # Datos MySQL Testing
├── production/
│   ├── moodledata/              # Datos Moodle Produccion
│   └── mysql-data/              # Datos MySQL Produccion
├── logs/
│   ├── testing/
│   ├── production/
│   └── nginx/
└── backups/
    ├── testing/
    └── production/
```

## Uso

### Menu Principal

El script presenta un menu interactivo con las siguientes opciones:

1. **Instalar infraestructura completa**: Instala todo automaticamente
2. **Gestionar ambientes**: Levantar/detener contenedores
3. **Ver logs**: Monitorear logs de servicios
4. **Gestionar backups**: Crear y restaurar backups
5. **Desinstalar todo**: Elimina toda la infraestructura

### Instalacion Completa

La opcion 1 realiza:
- Deteccion de SO
- Instalacion de Docker
- Creacion de estructura de directorios
- Descarga de Moodle 4.5.5
- Generacion de credenciales seguras
- Creacion de Dockerfiles y docker-compose.yml
- Configuracion de Nginx
- Opcion de levantar ambientes

### Gestion de Ambientes

Permite:
- Levantar Testing
- Levantar Produccion
- Detener ambientes
- Reiniciar servicios
- Ver estado de contenedores

### Comandos Docker Manuales

```bash
# Ver estado de contenedores
cd /opt/docker-project
docker-compose ps

# Ver logs
docker-compose logs -f moodle_testing
docker-compose logs -f mysql_production

# Reiniciar servicios
docker-compose restart moodle_testing
docker-compose restart nginx

# Detener todo
docker-compose down

# Levantar todo
docker-compose up -d
```

## Configuracion

### Archivo .env - Configuración del Sistema

El archivo `.env` es **creado automáticamente** por el script `install.sh` desde la plantilla `.env.example`.

#### Generación Automática del .env

Al ejecutar `sudo ./install.sh`, el script:
1. Copia `.env.example` a `.env` si no existe
2. Te informa que puedes editarlo antes de continuar
3. Si no lo editas, el instalador principal generará contraseñas seguras automáticamente

#### Contenido del .env

El archivo contiene todas las configuraciones del sistema:

```bash
# GENERAL
MOODLE_VERSION='4.5.5'
PROJECT_NAME='moodle_infrastructure'

# TESTING ENVIRONMENT
TEST_URL='https://test.moodle.local'
TEST_DB_NAME='moodle_test'
TEST_DB_USER='moodle_test_user'
TEST_DB_PASS='GENERAR_CONTRASEÑA_SEGURA'  # Se auto-genera si no cambias esto
TEST_DB_ROOT_PASS='GENERAR_CONTRASEÑA_SEGURA'
TEST_MOODLE_ADMIN_USER='admin_test'
TEST_MOODLE_ADMIN_PASS='GENERAR_CONTRASEÑA_SEGURA'
TEST_MOODLE_ADMIN_EMAIL='admin@test.moodle.local'
TEST_HTTP_PORT='8080'
TEST_HTTPS_PORT='8443'

# PRODUCTION ENVIRONMENT
PROD_URL='https://moodle.local'
PROD_DB_NAME='moodle_prod'
PROD_DB_USER='moodle_prod_user'
PROD_DB_PASS='GENERAR_CONTRASEÑA_SEGURA'
PROD_DB_ROOT_PASS='GENERAR_CONTRASEÑA_SEGURA'
PROD_MOODLE_ADMIN_USER='admin'
PROD_MOODLE_ADMIN_PASS='GENERAR_CONTRASEÑA_SEGURA'
PROD_MOODLE_ADMIN_EMAIL='admin@moodle.local'
PROD_HTTP_PORT='80'
PROD_HTTPS_PORT='443'

# BACKUP CONFIGURATION
BACKUP_RETENTION_DAYS='7'
BACKUP_EMAIL_TO=''

# SMTP CONFIGURATION
SMTP_SERVER='smtp.gmail.com'
SMTP_PORT='465'
SMTP_USER=''
SMTP_PASSWORD=''

# RESOURCE LIMITS
PHP_MEMORY_LIMIT='512M'
PHP_UPLOAD_MAX_FILESIZE='100M'
...
```

#### Opciones de Configuración

**Opción 1: Auto-generación (Recomendado para pruebas)**
```bash
# No edites el .env, deja los valores por defecto
sudo python3 main.py
# Las contraseñas se generarán automáticamente
```

**Opción 2: Configuración Manual**
```bash
# Edita el .env antes de ejecutar el instalador
nano .env
# Cambia las contraseñas marcadas como GENERAR_CONTRASEÑA_SEGURA
# Personaliza URLs y puertos según necesites
sudo python3 main.py
```

#### Variables Importantes a Personalizar

1. **URLs** - Si tienes dominios reales:
   ```bash
   TEST_URL='https://test.tusitio.com'
   PROD_URL='https://tusitio.com'
   ```

2. **Puertos** - Si los puertos por defecto están ocupados:
   ```bash
   TEST_HTTP_PORT='8080'   # Cambia si 8080 está ocupado
   PROD_HTTP_PORT='80'     # Cambia si 80 está ocupado
   ```

3. **Contraseñas** - Para producción se recomienda establecerlas manualmente:
   ```bash
   PROD_DB_PASS='TuContraseñaSegura123!'
   PROD_DB_ROOT_PASS='OtraContraseñaSegura456!'
   PROD_MOODLE_ADMIN_PASS='AdminPass789!'
   ```

4. **Email (opcional)** - Para notificaciones de backups:
   ```bash
   SMTP_USER='tu-email@gmail.com'
   SMTP_PASSWORD='contraseña-de-aplicacion'
   BACKUP_EMAIL_TO='admin@tusitio.com'
   ```

### Personalizar URLs

1. Editar `/opt/docker-project/.env`
2. Modificar `TEST_URL` y `PROD_URL`
3. Reiniciar contenedores: `docker-compose restart`

### Certificados SSL

**IMPORTANTE**: Los certificados SSL se configuran **automáticamente después de levantar los contenedores**, solo para los ambientes que selecciones.

#### Flujo de Instalación SSL

1. **Durante la instalación inicial**:
   - Se levantan primero los contenedores Docker
   - Luego se configura SSL automáticamente para cada ambiente levantado
   - Solo se generan certificados para los ambientes que selecciones (Testing, Producción, o ambos)

2. **Al levantar un ambiente posteriormente**:
   - Si el ambiente no tiene SSL configurado, se configurará automáticamente
   - Si ya tiene SSL, se mantiene la configuración existente

#### Tipos de Certificados Soportados

1. **Autofirmados** (por defecto)
   - Ideales para desarrollo y testing
   - Se generan automaticamente
   - Los navegadores mostraran advertencia de seguridad

2. **Let's Encrypt** (produccion)
   - Certificados gratuitos y validos
   - Renovacion automatica
   - Requiere dominio publico
   - **Nota**: En Rocky Linux/RHEL, `install.sh` habilita automáticamente el repositorio EPEL. Ver [utils/CERTBOT_ROCKY_LINUX.md](utils/CERTBOT_ROCKY_LINUX.md)

3. **Personalizados**
   - Para certificados comprados o propios
   - Se solicitan las rutas durante la instalacion

#### Configuracion en .env

```bash
# Tipo de certificado SSL
SSL_CERT_TYPE='self-signed'  # self-signed | letsencrypt | custom

# Email para Let's Encrypt (solo si usas letsencrypt)
SSL_LETSENCRYPT_EMAIL='admin@tusitio.com'

# Forzar HTTPS en Moodle
SSL_FORCE_HTTPS='true'
```

#### Solucion de Problemas SSL

**Error de contenido mixto**:
```
Se ha bloqueado la carga del contenido activo mixto "http://..."
```

**Solucion**: El instalador configura automaticamente Moodle para forzar HTTPS y aplica la configuración SSL automáticamente. Si el error persiste:

1. Verificar que la URL en .env use `https://`
2. La configuración SSL se aplica automáticamente al levantar el ambiente
3. Para verificar la configuración SSL aplicada:
   ```bash
   # Ver la configuracion generada
   cat /opt/docker-project/production/moodle_config/ssl_config.php

   # Verificar si está en config.php de Moodle
   docker exec moodle_production grep -A 5 "sslproxy" /var/www/html/config.php
   ```

3. Limpiar cache de Moodle:
   - Via web: Admin > Desarrollo > Limpiar todas las caches
   - Via CLI: `docker exec moodle_production php admin/cli/purge_caches.php`

#### Script Automatico para Aplicar SSL

Se incluye un script que aplica automaticamente la configuracion SSL:

```bash
# Para testing
sudo bash utils/apply_ssl_config.sh testing

# Para produccion
sudo bash utils/apply_ssl_config.sh production
```

El script:
- Verifica que Moodle este instalado
- Aplica la configuracion SSL al config.php
- Limpia el cache automaticamente
- Reinicia el contenedor

Ver documentacion completa: [utils/SSL_CONFIGURATION.md](utils/SSL_CONFIGURATION.md)

## Sistema de Backups

El sistema incluye un gestor completo de respaldos con las siguientes características:

### Funcionalidades
- **Backups manuales** de Testing y Produccion
- **Backups automaticos** programados (cron)
- **Restauracion completa** (BD + archivos)
- **Notificaciones por email** (SMTP)
- **Limpieza automatica** de respaldos antiguos
- **Compresion automatica** (gzip/tar.gz)

### Componentes Respaldados
1. **Base de datos MySQL** - Dump completo comprimido (.sql.gz)
2. **Volumen moodledata** - Archivos de usuarios (.tar.gz)
3. **Logs y metadatos** - Informacion del respaldo

### Uso Rapido

#### Desde el Menu Principal
```bash
sudo python3 main.py
# Opcion 4: Gestionar backups
```

Opciones disponibles:
1. Crear backup manual
2. Listar backups disponibles
3. Restaurar backup
4. Configurar backup automatico
5. Ver tareas programadas
6. Configurar notificaciones por email

#### Desde Linea de Comandos
```bash
# Crear backup manual
bash backup/backup.sh testing
bash backup/backup.sh production

# Restaurar backup
bash backup/restore.sh testing 2024-12-07_10-30-00

# Listar backups disponibles
ls -lh /opt/docker-project/backups/testing/
```

### Configuracion de Email

Editar `/opt/docker-project/.env`:

```bash
# SMTP CONFIGURATION
SMTP_SERVER='smtp.gmail.com'
SMTP_PORT='465'
SMTP_USER='tu-email@gmail.com'
SMTP_PASSWORD='contraseña-de-aplicacion'
SMTP_FROM_NAME='Moodle Backup System'

# BACKUP CONFIGURATION
BACKUP_RETENTION_DAYS='7'
BACKUP_EMAIL_TO='admin@example.com'
```

**Nota para Gmail:** Debes crear una "Contraseña de aplicacion" en:
https://myaccount.google.com/apppasswords

### Programar Backups Automaticos

```bash
# Desde el menu (opcion 4 -> 6 o 7)
# O manualmente:
sudo python3 -c "
from config.settings import Settings
from backup.scheduler import BackupScheduler

settings = Settings()
settings.load_env_file()
scheduler = BackupScheduler(settings)

# Testing: diario a las 2 AM
scheduler.setup_cron('testing', '0 2 * * *')

# Production: diario a las 3 AM
scheduler.setup_cron('production', '0 3 * * *')
"
```

### Estructura de Backups
```
/opt/docker-project/backups/
├── testing/
│   └── 2024-12-07_10-30-00/
│       ├── moodle_test_2024-12-07_10-30-00.sql.gz
│       ├── moodledata_2024-12-07_10-30-00.tar.gz
│       ├── backup.log
│       ├── DB_INFO.txt
│       └── MOODLEDATA_INFO.txt
└── production/
    └── ...
```

### Documentacion Completa
Ver [backup/README.md](backup/README.md) para documentacion detallada del sistema de respaldos.

## Troubleshooting

### Docker no inicia
```bash
sudo systemctl status docker
sudo systemctl start docker
```

### Puerto ocupado
Editar `.env` y cambiar puertos conflictivos

### Ver logs de errores
```bash
cd /opt/docker-project
docker-compose logs --tail=100
```

### Reiniciar desde cero
```bash
sudo python3 main.py
# Opcion 5: Desinstalar todo
# Luego opcion 1: Instalar infraestructura completa
```

## Licencia

MIT

## Autor

**Eduardo Valdés**

Instalador creado para SLEP Andalien Sur

## Notas

- Los certificados SSL por defecto son autofirmados
- Las contraseñas se generan automaticamente
- Los puertos por defecto pueden modificarse en .env
- El sistema detecta automaticamente el SO y adapta los comandos
