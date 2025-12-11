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

# Instalar dependencias Python
pip3 install -r requirements.txt

# Ejecutar instalador
sudo python3 main.py
```

## Estructura del Proyecto

```
moodle-docker-installer/
├── main.py                      # Script principal
├── requirements.txt             # Dependencias Python
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
    └── rollback.py
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

### Variables de Entorno

El archivo `.env` contiene todas las configuraciones:

```bash
# URLs
TEST_URL=https://test.moodle.local
PROD_URL=https://moodle.local

# Puertos
TEST_HTTP_PORT=8080
TEST_HTTPS_PORT=8443
PROD_HTTP_PORT=80
PROD_HTTPS_PORT=443

# Credenciales (generadas automaticamente)
TEST_DB_NAME=moodle_test
TEST_DB_USER=moodle_test_user
TEST_DB_PASS=XXXXXXXX
...
```

### Personalizar URLs

1. Editar `/opt/docker-project/.env`
2. Modificar `TEST_URL` y `PROD_URL`
3. Reiniciar contenedores: `docker-compose restart`

### Certificados SSL

Por defecto se generan certificados autofirmados. Para usar certificados reales:

1. Colocar certificados en `/opt/docker-project/nginx/ssl/`
2. Actualizar rutas en `/opt/docker-project/nginx/conf.d/*.conf`
3. Reiniciar Nginx: `docker-compose restart nginx`

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
