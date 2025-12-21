# Changelog - Moodle Docker Installer

## [2024-12-21] - Migración de Nginx a Apache

### Modificado
- **Arquitectura de Proxy Reverso** - Cambio fundamental de Nginx a Apache
  - **Eliminado**: Contenedores Docker de Nginx (nginx_testing y nginx_production)
  - **Agregado**: Apache HTTP Server en el HOST como proxy reverso
  - **Beneficio**: Simplificación de la arquitectura, menor consumo de recursos
  - **Puertos**:
    - Testing: Apache escucha en 8080 (HOST) → Moodle en 8081 (contenedor)
    - Production: Apache escucha en 80 (HOST) → Moodle en 8082 (contenedor)

### Agregado
- **apache/vhost_generator.py**: Nuevo módulo para generación de VirtualHosts
  - Detección automática de SO (Debian/Ubuntu, RHEL/Rocky, Arch)
  - Generación de VirtualHosts para Testing y Production
  - Configuración automática de puertos (Listen 8080)
  - Habilitación automática de sitios (a2ensite en Debian/Ubuntu)
  - Recarga automática de Apache tras configuración
  - Soporte multi-distribución con rutas específicas:
    - Debian/Ubuntu: `/etc/apache2/sites-available/`
    - RHEL/Rocky/Arch: `/etc/httpd/conf.d/`

### Modificado
- **main.py**: Integración del generador de VirtualHosts de Apache
  - Import de `ApacheVHostGenerator` (línea 24)
  - Llamada a `apache_gen.generate_all()` durante instalación (línea 159)
  - Comentarios actualizados indicando eliminación de Nginx (líneas 267, 546)

- **docker/compose_generator.py**: Eliminación de servicios Nginx
  - Comentario explícito: "Nginx eliminado - Apache corre en el HOST como proxy reverso" (línea 72)
  - Puertos de Moodle expuestos directamente al HOST:
    - Testing: `8081:80`
    - Production: `8082:80`
  - Simplificación de la configuración de servicios

### Impacto en la Documentación
- URLs de acceso actualizadas en README.md y QUICKSTART.md
- Instrucciones de Apache agregadas (systemctl, logs, certificados SSL)
- Eliminadas referencias a contenedores Nginx
- Agregadas rutas de configuración de Apache según distribución

### Ventajas de la Migración
1. **Menor consumo de recursos**: 2 contenedores menos (nginx_testing y nginx_production)
2. **Gestión simplificada**: Apache se gestiona con systemctl en el HOST
3. **Logs centralizados**: Logs de Apache en ubicaciones estándar del SO
4. **Certificados SSL más fáciles**: certbot-apache disponible en todas las distros
5. **Compatibilidad mejorada**: Apache es estándar en servidores Linux

### Compatibilidad
- Mantiene compatibilidad total con sistema de backups
- Sin cambios en bases de datos ni volúmenes de Moodle
- Migración transparente para instalaciones existentes

---

## [2024-12-10] - Limpieza y Consolidación de Documentación

### Eliminado
- **CAMBIOS_APLICADOS.md**: Archivo de documentación redundante
  - Toda la información histórica consolidada en CHANGELOG.md
  - Mantiene un único punto de verdad para historial de cambios
  - Elimina duplicación de documentación

### Modificado
- **CHANGELOG.md**: Reorganización y consolidación
  - Agregado historial completo desde diciembre 1
  - Estructura cronológica mejorada
  - Sección de autor actualizada con historial de desarrollo

---

## [2024-12-09] - Corrección de Errores y Limpieza de Código

### Corregido
- **backup/backup.sh**: Error en creación de logs
  - **Problema**: Error `tee: No existe el fichero o el directorio` al escribir logs
  - **Causa**: Funciones `log_*()` intentaban escribir en `$LOG_FILE` antes de crear `$BACKUP_DIR`
  - **Solución**: Creación del directorio **antes** de cualquier llamada a funciones de log
  - **Beneficio**: Backups se ejecutan sin errores de escritura

### Eliminado
- **backup/.env.example**: Archivo de configuración redundante
  - Variables ya integradas en `/opt/docker-project/.env`
  - Sistema genera automáticamente todas las variables en `config/settings.py`

- **backup/email_notifier.py**: Módulo obsoleto
  - Contenía TODOs pendientes y nunca fue implementado
  - Sistema usa `send_mail.py` como script funcional para notificaciones
  - Elimina código muerto y confusión

### Actualizado
- **Autoría del proyecto**: Eduardo Valdés
  - `main.py`, `backup/backup.sh`, `backup/restore.sh`
  - `README.md`, `CHANGELOG.md`
  - Reconocimiento apropiado en archivos principales

---

## [2024-12-08] - Mejoras en Gestión y Configuración

### Agregado
- **Configuración automática de backups** (`main.py`)
  - Método `_setup_automatic_backups()` durante instalación
  - Testing: Backup diario a las 2:00 AM
  - Production: Backup diario a las 3:00 AM
  - Opción de configuración posterior desde menú

- **Desinstalación granular** (`main.py`)
  - Opción 1: Eliminar solo Testing
  - Opción 2: Eliminar solo Production
  - Opción 3: Eliminar TODO (infraestructura completa)
  - Backup automático antes de eliminar Production
  - Confirmaciones diferentes por nivel de riesgo

### Modificado
- **Variables de entorno mejoradas** (`config/settings.py`)
  - Auto-start: `AUTO_START_ON_BOOT`, `AUTO_INSTALL_MOODLE`, `AUTO_BACKUP_ON_START`
  - Monitoreo: `MONITORING_ENABLED`, `MONITORING_INTERVAL`
  - Recursos: `MYSQL_MAX_CONNECTIONS`, `PHP_MEMORY_LIMIT`, `PHP_MAX_EXECUTION_TIME`
  - `PHP_UPLOAD_MAX_FILESIZE`, `PHP_POST_MAX_SIZE`

---

## [2024-12-07] - Sistema de Respaldos Completo

### Agregado
- **backup.sh**: Script completo de respaldo para contenedores Docker
  - Respaldo de base de datos MySQL con compresión
  - Respaldo de volumen moodledata
  - Limpieza automática de respaldos antiguos
  - Notificaciones por email
  - Logs detallados con códigos de colores

- **restore.sh**: Script de restauración de respaldos
  - Restauración completa de base de datos
  - Restauración de volumen moodledata
  - Confirmación de seguridad
  - Verificación post-restauración

- **send_mail.py**: Sistema de notificaciones por email
  - Configuración vía variables de entorno
  - Soporte para múltiples destinatarios
  - Archivos adjuntos opcionales
  - Validación de credenciales

- **backup_manager.py**: Gestor Python de respaldos
  - Interfaz Python para scripts bash
  - Gestión completa de respaldos
  - Información detallada de backups
  - Integración con settings

- **scheduler.py**: Programación automática con cron
  - Configuración de tareas cron
  - Horarios predefinidos
  - Gestión por ambiente
  - Exportación automática de variables

### Modificado
- **config/settings.py**: Agregadas variables SMTP y configuración de respaldos
- **main.py**: Implementado menú completo de gestión de backups (11 opciones)

### Documentación
- **backup/README.md**: Documentación completa del sistema de respaldos

---

## [2024-12-05] - Optimización de Infraestructura Docker

### Modificado
- **Nginx unificado** (`docker/compose_generator.py`, `nginx/config_generator.py`)
  - Consolidado de 2 contenedores a 1 contenedor unificado
  - Menor consumo de recursos y gestión simplificada
  - Puertos: Testing (8081/8443), Production (80/443)
  - Conexión a ambas redes Docker simultáneamente
  - Configuraciones separadas: `testing.conf` y `production.conf`

- **Nombres simplificados de recursos Docker** (`docker/compose_generator.py`)
  - Redes: `testing`, `production` (antes: `docker-project_moodle_network_*`)
  - Volúmenes: `mysql_testing`, `moodledata_testing` (antes: `docker-project_*`)
  - Comandos Docker más simples y legibles

---

## [2024-12-03] - Mejoras de Seguridad y Verificaciones

### Modificado
- **Permisos de moodledata** (`core/directory_manager.py`)
  - Cambiados de `777` a `755`
  - Mayor seguridad en producción
  - Mantiene funcionalidad completa

### Verificado
- **Limpieza de emojis en código**
  - Búsqueda exhaustiva en archivos .py, .sh y .md
  - Confirmado: 0 emojis en código fuente
  - Solo caracteres estándar de árbol de directorios (├, │, └)

---

## [2024-12-01] - Correcciones Post-Integración

### Corregido
- **Rutas de backups** (`backup/backup.sh`, `backup/restore.sh`)
  - Actualizada ruta de `/opt/moodle-backups` a `/opt/docker-project/backups`
  - Backups se almacenan en ubicación correcta dentro del proyecto
  - Consistencia en toda la estructura

---

## Características del Sistema de Respaldos

### Componentes Respaldados
1. **Base de datos MySQL** (.sql.gz)
   - Dump completo comprimido
   - Incluye rutinas, triggers y eventos

2. **Volumen moodledata** (.tar.gz)
   - Archivos subidos por usuarios
   - Caché y datos temporales

3. **Metadatos**
   - Logs de respaldo
   - Información de tamaños
   - Timestamps

### Funcionalidades

#### Respaldos
- Respaldo manual por ambiente
- Respaldo automático programado (cron)
- Compresión automática
- Limpieza automática de respaldos antiguos
- Notificaciones por email

#### Restauración
- Restauración completa (BD + archivos)
- Confirmación de seguridad
- Verificación post-restauración
- Logs detallados

#### Gestión
- Listar respaldos disponibles
- Información detallada de cada respaldo
- Configuración de email desde menú
- Gestión de tareas programadas

### Uso desde el Menú Principal

```
4. Gestionar backups
   1. Crear backup manual (Testing)
   2. Crear backup manual (Produccion)
   3. Listar backups disponibles
   4. Restaurar backup (Testing)
   5. Restaurar backup (Produccion)
   6. Configurar backup automatico (Testing)
   7. Configurar backup automatico (Produccion)
   8. Ver tareas programadas
   9. Eliminar backup automatico
   10. Configurar notificaciones por email
   11. Ver informacion detallada de un backup
```

### Uso desde Línea de Comandos

#### Crear respaldo:
```bash
bash backup/backup.sh testing
bash backup/backup.sh production
```

#### Restaurar respaldo:
```bash
bash backup/restore.sh testing 2024-12-07_10-30-00
bash backup/restore.sh production 2024-12-07_10-30-00
```

#### Enviar notificación:
```bash
python3 backup/send_mail.py "admin@example.com" "Asunto" "Mensaje"
```

### Configuración Requerida

#### Variables de entorno en .env:
```bash
# Respaldos
BACKUP_RETENTION_DAYS='7'
BACKUP_EMAIL_TO='admin@example.com'

# SMTP
SMTP_SERVER='smtp.gmail.com'
SMTP_PORT='465'
SMTP_USER='tu-email@gmail.com'
SMTP_PASSWORD='contraseña-de-aplicacion'
SMTP_FROM_NAME='Moodle Backup System'
```

### Estructura de Respaldos
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

---

## Próximas Mejoras (Futuro)

- [ ] Respaldo incremental
- [ ] Sincronización con almacenamiento remoto (S3, rsync)
- [ ] Dashboard web de respaldos
- [ ] Verificación de integridad de respaldos
- [ ] Compresión multi-thread
- [ ] Respaldo diferencial
- [ ] Reportes periódicos por email
- [ ] API REST para gestión de respaldos

---

## Notas de Seguridad

- Las contraseñas se manejan mediante variables de entorno
- Los scripts validan credenciales antes de ejecutar
- La restauración requiere confirmación explícita
- Los logs no contienen información sensible
- Permisos apropiados en archivos de respaldo

---

## Compatibilidad

- Ubuntu/Debian
- Rocky Linux/RHEL
- Arch Linux
- Docker 20.10+
- Python 3.6+
- Bash 4.0+

---

## Autor

**Eduardo Valdés**

Moodle Docker Installer con Sistema de Respaldos Integrado

**Historial de Desarrollo:**
- 2024-12-01: Correcciones Post-Integración
- 2024-12-03: Mejoras de Seguridad y Verificaciones
- 2024-12-05: Optimización de Infraestructura Docker
- 2024-12-07: Sistema de Respaldos Completo
- 2024-12-08: Mejoras en Gestión y Configuración
- 2024-12-09: Corrección de Errores y Limpieza de Código
- 2024-12-10: Limpieza y Consolidación de Documentación
