# Sistema de Respaldo y Restauración de Moodle

Sistema completo de backup y restore para Moodle desplegado en contenedores Docker.

## Componentes

### 1. Scripts de Bash

#### backup.sh
Script principal para crear respaldos automáticos.

**Características:**
- Respaldo de base de datos MySQL (dump comprimido)
- Respaldo de volumen moodledata (archivos de usuario)
- Limpieza automática de respaldos antiguos
- Notificaciones por email
- Logs detallados con colores

**Uso:**
```bash
# Respaldar ambiente de testing
bash backup/backup.sh testing

# Respaldar ambiente de producción
bash backup/backup.sh production
```

**Variables de entorno requeridas:**
- `BACKUP_BASE_PATH`: Directorio base para respaldos (default: /opt/moodle-backups)
- `BACKUP_RETENTION_DAYS`: Días de retención de respaldos (default: 7)
- `DB_NAME`: Nombre de la base de datos
- `DB_USER`: Usuario de la base de datos
- `DB_PASS`: Contraseña de la base de datos
- `BACKUP_EMAIL_TO`: Email de destino para notificaciones (opcional)

#### restore.sh
Script para restaurar respaldos.

**Características:**
- Restauración de base de datos MySQL
- Restauración de volumen moodledata
- Confirmación de seguridad antes de restaurar
- Verificación de integridad
- Logs detallados

**Uso:**
```bash
# Listar respaldos disponibles
bash backup/restore.sh testing

# Restaurar un respaldo específico
bash backup/restore.sh testing 2024-01-15_10-30-00
```

**ADVERTENCIA:** La restauración eliminará todos los datos actuales y los reemplazará con los del respaldo.

### 2. Scripts de Python

#### send_mail.py
Envío de notificaciones por email.

**Características:**
- Soporte para múltiples destinatarios
- Archivos adjuntos
- Configuración vía variables de entorno
- Manejo de errores robusto

**Uso desde línea de comandos:**
```bash
python3 backup/send_mail.py "admin@example.com" "Asunto" "Mensaje del correo"
```

**Variables de entorno:**
- `SMTP_SERVER`: Servidor SMTP (default: smtp.gmail.com)
- `SMTP_PORT`: Puerto SMTP (default: 465)
- `SMTP_USER`: Usuario SMTP
- `SMTP_PASSWORD`: Contraseña SMTP
- `SMTP_FROM_NAME`: Nombre del remitente (default: Moodle Backup System)

#### backup_manager.py
Gestor principal de respaldos desde Python.

**Características:**
- Interfaz Python para scripts de bash
- Gestión de variables de entorno
- Listado de respaldos disponibles
- Información detallada de respaldos

**Uso:**
```python
from config.settings import Settings
from backup.backup_manager import BackupManager

settings = Settings()
backup_mgr = BackupManager(settings)

# Crear backup
backup_mgr.create_backup('testing')

# Listar backups
backup_mgr.list_backups('testing')

# Restaurar backup
backup_mgr.restore_backup('testing', '2024-01-15_10-30-00')
```

#### scheduler.py
Programación automática de respaldos usando cron.

**Características:**
- Configuración de tareas cron
- Horarios predefinidos recomendados
- Gestión de múltiples ambientes
- Exportación automática de variables de entorno

**Uso:**
```python
from config.settings import Settings
from backup.scheduler import BackupScheduler

settings = Settings()
scheduler = BackupScheduler(settings)

# Configurar backup diario a las 2 AM
scheduler.setup_cron('testing', '0 2 * * *')

# Ver horarios recomendados
scheduler.get_recommended_schedules()

# Listar tareas programadas
scheduler.list_scheduled_backups()

# Eliminar tarea programada
scheduler.remove_cron('testing')
```

## Configuración

### 1. Configurar variables de entorno SMTP

Editar el archivo `.env` en `/opt/docker-project/`:

```bash
# SMTP CONFIGURATION
SMTP_SERVER='smtp.gmail.com'
SMTP_PORT='465'
SMTP_USER='tu-email@gmail.com'
SMTP_PASSWORD='tu-contraseña-app'
SMTP_FROM_NAME='Moodle Backup System'

# BACKUP CONFIGURATION
BACKUP_RETENTION_DAYS='7'
BACKUP_EMAIL_TO='admin@example.com,admin2@example.com'
```

**Nota para Gmail:** Debes usar una "Contraseña de aplicación" en lugar de tu contraseña normal.
- Ir a: https://myaccount.google.com/apppasswords
- Crear una contraseña de aplicación para "Correo"
- Usar esa contraseña en `SMTP_PASSWORD`

### 2. Dar permisos de ejecución a los scripts

```bash
chmod +x backup/backup.sh
chmod +x backup/restore.sh
chmod +x backup/send_mail.py
```

### 3. Programar respaldos automáticos

Usando Python:
```python
from config.settings import Settings
from backup.scheduler import BackupScheduler

settings = Settings()
settings.load_env_file()  # Cargar configuración del .env

scheduler = BackupScheduler(settings)

# Testing: backup diario a las 2 AM
scheduler.setup_cron('testing', '0 2 * * *')

# Production: backup diario a las 3 AM
scheduler.setup_cron('production', '0 3 * * *')
```

O manualmente editando crontab:
```bash
crontab -e
```

Agregar:
```
# Backup Moodle Testing - Diario 2 AM
0 2 * * * bash /ruta/a/backup/backup.sh testing

# Backup Moodle Production - Diario 3 AM
0 3 * * * bash /ruta/a/backup/backup.sh production
```

## Estructura de Respaldos

Los respaldos se almacenan en:
```
/opt/docker-project/backups/
├── testing/
│   ├── 2024-01-15_10-30-00/
│   │   ├── moodle_test_2024-01-15_10-30-00.sql.gz
│   │   ├── moodledata_2024-01-15_10-30-00.tar.gz
│   │   ├── backup.log
│   │   ├── DB_INFO.txt
│   │   └── MOODLEDATA_INFO.txt
│   └── 2024-01-16_10-30-00/
│       └── ...
└── production/
    └── ...
```

## Componentes del Respaldo

### Base de Datos MySQL
- Formato: SQL comprimido (.sql.gz)
- Incluye: rutinas, triggers, eventos
- Compresión: gzip

### Moodledata
- Formato: Archivo tar comprimido (.tar.gz)
- Contenido: Todos los archivos subidos por usuarios
- Incluye: caché, sesiones, repositorios

## Restauración de Respaldos

### Pasos para restaurar:

1. **Listar respaldos disponibles:**
```bash
bash backup/restore.sh testing
```

2. **Ejecutar restauración:**
```bash
bash backup/restore.sh testing 2024-01-15_10-30-00
```

3. **Confirmar la operación:**
El script pedirá confirmación escribiendo "SI" en mayúsculas.

4. **Verificar:**
El script mostrará los logs y verificará que los servicios estén corriendo.

### Precauciones:
- La restauración ELIMINARÁ todos los datos actuales
- Los contenedores se detendrán temporalmente
- Asegúrate de tener el timestamp correcto del respaldo
- Se recomienda hacer un respaldo antes de restaurar

## Notificaciones por Email

Si las variables SMTP están configuradas, recibirás emails:

**Respaldo exitoso:**
```
Asunto: [Backup Moodle] testing - EXITOSO
Cuerpo:
  Respaldo de Moodle testing
  Fecha: 2024-01-15 10:30:00
  Estado: EXITOSO

  Detalles:
  Respaldo completado correctamente
  Ubicación: /opt/docker-project/backups/testing/2024-01-15_10-30-00
  Tamaño: 1.2G
```

**Respaldo fallido:**
```
Asunto: [Backup Moodle] testing - FALLIDO
Cuerpo:
  Respaldo de Moodle testing
  Fecha: 2024-01-15 10:30:00
  Estado: FALLIDO

  Detalles:
  Errores durante el respaldo:
  - Error al respaldar base de datos MySQL
```

## Limpieza Automática

Los respaldos antiguos se eliminan automáticamente según `BACKUP_RETENTION_DAYS`:
- Se ejecuta en cada respaldo
- Mantiene los últimos N días configurados
- Default: 7 días

Para cambiar:
```bash
# En .env
BACKUP_RETENTION_DAYS='14'  # Mantener 14 días
```

## Logs

Cada respaldo genera un log detallado:
- Ubicación: Dentro del directorio del respaldo
- Nombre: `backup.log`
- Contenido: Timestamps, mensajes de éxito/error, tamaños de archivos

Para ver logs de un respaldo:
```bash
cat /opt/docker-project/backups/testing/2024-01-15_10-30-00/backup.log
```

## Solución de Problemas

### Error: "El contenedor MySQL no está corriendo"
```bash
# Verificar contenedores
docker ps | grep mysql

# Iniciar contenedor
docker start mysql_testing
```

### Error: "No se pudo enviar email"
- Verificar credenciales SMTP en `.env`
- Para Gmail, usar contraseña de aplicación
- Verificar firewall y conexión a internet

### Error: "Permiso denegado"
```bash
# Dar permisos a scripts
chmod +x backup/*.sh
chmod +x backup/*.py
```

### Respaldo muy grande
- Verificar tamaño de moodledata
- Considerar limpiar cache de Moodle
- Aumentar tiempo de ejecución si usa cron

## Mejores Prácticas

1. **Programar respaldos en horarios de baja actividad** (2-4 AM)
2. **Mantener al menos 7 días de respaldos**
3. **Configurar notificaciones por email**
4. **Probar la restauración periódicamente**
5. **Monitorear el espacio en disco**
6. **Guardar respaldos críticos fuera del servidor** (backup remoto)

## Respaldos Remotos (Opcional)

Para copiar respaldos a almacenamiento remoto:

```bash
# Usando rsync
rsync -avz /opt/docker-project/backups/ usuario@servidor-remoto:/backups/moodle/

# Usando AWS S3
aws s3 sync /opt/docker-project/backups/ s3://mi-bucket/moodle-backups/
```

## Soporte

Para reportar problemas o solicitar mejoras, contactar al administrador del sistema.
