#!/bin/bash

###############################################################################
# Script de Respaldo Automático para Moodle en Docker
# Respalda: Base de datos MySQL + moodledata
# Autor: Eduardo Valdés
###############################################################################

# Configuración de variables
ENVIRONMENT="${1:-testing}"  # testing o production (por defecto testing)
FECHA="$(date +"%Y-%m-%d_%H-%M-%S")"

# Cargar variables desde .env si las variables no están definidas
if [ -z "$BACKUP_BASE_PATH" ] || [ -z "$DB_NAME" ]; then
    ENV_FILE="${ENV_FILE:-/opt/docker-project/.env}"

    if [ -f "$ENV_FILE" ]; then
        # Cargar todas las variables del .env
        set -a
        source "$ENV_FILE"
        set +a

        # Establecer variables específicas según el ambiente
        if [ "$ENVIRONMENT" = "production" ]; then
            DB_NAME="${PROD_DB_NAME}"
            DB_USER="${PROD_DB_USER}"
            DB_PASS="${PROD_DB_PASS}"
            DB_ROOT_PASS="${PROD_DB_ROOT_PASS}"
        else
            DB_NAME="${TEST_DB_NAME}"
            DB_USER="${TEST_DB_USER}"
            DB_PASS="${TEST_DB_PASS}"
            DB_ROOT_PASS="${TEST_DB_ROOT_PASS}"
        fi
    else
        echo "ADVERTENCIA: No se encontró archivo .env en $ENV_FILE"
        echo "Las variables deben estar definidas en el entorno"
    fi
fi

BASE_BACKUP_DIR="${BACKUP_BASE_PATH:-/opt/docker-project/backups}"
BACKUP_DIR="$BASE_BACKUP_DIR/$ENVIRONMENT/$FECHA"
DAYS_TO_KEEP="${BACKUP_RETENTION_DAYS:-7}"

# Nombres de contenedores
MYSQL_CONTAINER="mysql_$ENVIRONMENT"
MOODLE_CONTAINER="moodle_$ENVIRONMENT"

# Archivo de log
LOG_FILE="$BACKUP_DIR/backup.log"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

###############################################################################
# Funciones auxiliares
###############################################################################

log_message() {
    local message="$1"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo -e "${timestamp} - ${message}" | tee -a "$LOG_FILE"
}

log_success() {
    log_message "${GREEN}[OK]${NC} $1"
}

log_error() {
    log_message "${RED}[ERROR]${NC} $1"
}

log_warning() {
    log_message "${YELLOW}[WARNING]${NC} $1"
}

log_info() {
    log_message "[INFO] $1"
}

###############################################################################
# Función para respaldar base de datos MySQL
###############################################################################
backup_mysql_database() {
    log_info "Iniciando respaldo de base de datos MySQL"

    local db_name="${DB_NAME:-moodle}"
    local db_user="${DB_USER:-moodle}"
    local db_pass="${DB_PASS:-moodle}"
    local output_file="$BACKUP_DIR/${db_name}_${FECHA}.sql"

    # Verificar que el contenedor MySQL esté corriendo
    if ! docker ps | grep -q "$MYSQL_CONTAINER"; then
        log_error "El contenedor MySQL ($MYSQL_CONTAINER) no está corriendo"
        return 1
    fi

    log_info "Exportando base de datos: $db_name"

    # Realizar dump de la base de datos
    # Usamos variable MYSQL_PWD para evitar warning de seguridad
    # Agregamos --no-tablespaces para evitar error de privilegios PROCESS
    docker exec -e MYSQL_PWD="$db_pass" "$MYSQL_CONTAINER" mysqldump \
        -u"$db_user" \
        --single-transaction \
        --routines \
        --triggers \
        --events \
        --no-tablespaces \
        "$db_name" > "$output_file" 2>> "$LOG_FILE"

    if [ $? -eq 0 ] && [ -s "$output_file" ]; then
        log_success "Base de datos exportada correctamente"

        # Comprimir el archivo SQL
        log_info "Comprimiendo archivo SQL..."
        gzip "$output_file"

        if [ $? -eq 0 ]; then
            local compressed_file="${output_file}.gz"
            local file_size=$(du -h "$compressed_file" | cut -f1)
            log_success "Base de datos comprimida: $compressed_file ($file_size)"
            echo "$db_name" > "$BACKUP_DIR/DB_INFO.txt"
            echo "Tamaño: $file_size" >> "$BACKUP_DIR/DB_INFO.txt"
            date > "$BACKUP_DIR/FIN_DUMP_DB.log"
            return 0
        else
            log_error "Error al comprimir el archivo SQL"
            return 1
        fi
    else
        log_error "Error al exportar la base de datos"
        return 1
    fi
}

###############################################################################
# Función para respaldar moodledata
###############################################################################
backup_moodledata() {
    log_info "Iniciando respaldo de moodledata"

    local volume_name="moodledata_${ENVIRONMENT}"
    local output_file="$BACKUP_DIR/moodledata_${FECHA}.tar.gz"

    # Verificar que el volumen existe
    if ! docker volume ls | grep -q "$volume_name"; then
        log_warning "El volumen $volume_name no existe"
        return 1
    fi

    log_info "Comprimiendo volumen: $volume_name"

    # Crear backup del volumen usando un contenedor temporal
    docker run --rm \
        -v "$volume_name":/source:ro \
        -v "$BACKUP_DIR":/backup \
        alpine tar czf "/backup/moodledata_${FECHA}.tar.gz" -C /source . 2>> "$LOG_FILE"

    if [ $? -eq 0 ] && [ -f "$output_file" ]; then
        local file_size=$(du -h "$output_file" | cut -f1)
        log_success "Moodledata respaldado: $output_file ($file_size)"
        echo "Volumen: $volume_name" > "$BACKUP_DIR/MOODLEDATA_INFO.txt"
        echo "Tamaño: $file_size" >> "$BACKUP_DIR/MOODLEDATA_INFO.txt"
        date > "$BACKUP_DIR/FIN_DUMP_MOODLEDATA.log"
        return 0
    else
        log_error "Error al respaldar moodledata"
        return 1
    fi
}

###############################################################################
# Función para limpiar respaldos antiguos
###############################################################################
cleanup_old_backups() {
    log_info "Limpiando respaldos antiguos (manteniendo últimos $DAYS_TO_KEEP días)"

    local env_backup_dir="$BASE_BACKUP_DIR/$ENVIRONMENT"

    if [ ! -d "$env_backup_dir" ]; then
        log_warning "No existe directorio de respaldos para $ENVIRONMENT"
        return 0
    fi

    # Encontrar y eliminar respaldos antiguos
    find "$env_backup_dir" -maxdepth 1 -type d -mtime "+$DAYS_TO_KEEP" -exec rm -rf {} \; 2>> "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log_success "Respaldos antiguos eliminados"
        return 0
    else
        log_warning "Hubo problemas al eliminar respaldos antiguos"
        return 1
    fi
}

###############################################################################
# Función para enviar notificación por email
###############################################################################
send_email_notification() {
    local status="$1"
    local details="$2"

    # Verificar si existe el script de envío de email
    local script_dir="$(dirname "$0")"
    local email_script="$script_dir/send_mail.py"

    if [ ! -f "$email_script" ]; then
        log_warning "Script de email no encontrado: $email_script"
        return 1
    fi

    # Verificar variables de entorno
    if [ -z "$BACKUP_EMAIL_TO" ]; then
        log_warning "No se ha configurado BACKUP_EMAIL_TO"
        return 1
    fi

    local subject="[Backup Moodle] $ENVIRONMENT - $status"
    local message="Respaldo de Moodle $ENVIRONMENT\nFecha: $FECHA\nEstado: $status\n\nDetalles:\n$details"

    python3 "$email_script" "$BACKUP_EMAIL_TO" "$subject" "$message" >> "$LOG_FILE" 2>&1

    if [ $? -eq 0 ]; then
        log_success "Notificación enviada por email"
        return 0
    else
        log_warning "No se pudo enviar la notificación por email"
        return 1
    fi
}

###############################################################################
# Función principal
###############################################################################
main() {
    # Crear directorio de respaldo PRIMERO (antes de cualquier log)
    echo "Creando directorio de respaldo: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"

    if [ $? -ne 0 ]; then
        echo "ERROR: No se pudo crear el directorio de respaldo"
        exit 1
    fi

    # Ahora sí podemos usar las funciones de log
    log_info "=========================================="
    log_info "Iniciando respaldo de Moodle $ENVIRONMENT"
    log_info "=========================================="

    local backup_status="SUCCESS"
    local error_details=""

    # Configurar archivo de inicio
    log_success "Directorio de respaldo creado"
    echo "INICIO RESPALDO MOODLE $ENVIRONMENT" > "$BACKUP_DIR/INICIO.log"
    date >> "$BACKUP_DIR/INICIO.log"

    # Respaldar base de datos
    if ! backup_mysql_database; then
        backup_status="FAILED"
        error_details="${error_details}\n- Error al respaldar base de datos MySQL"
    fi

    # Respaldar moodledata
    if ! backup_moodledata; then
        backup_status="FAILED"
        error_details="${error_details}\n- Error al respaldar moodledata"
    fi

    # Limpiar respaldos antiguos
    cleanup_old_backups

    # Finalizar respaldo
    date > "$BACKUP_DIR/FIN_RESPALDO.log"

    # Resumen del respaldo
    local backup_size=$(du -sh "$BACKUP_DIR" | cut -f1)
    log_info "=========================================="
    log_info "Respaldo completado con estado: $backup_status"
    log_info "Ubicación: $BACKUP_DIR"
    log_info "Tamaño total: $backup_size"
    log_info "=========================================="

    # Enviar notificación
    if [ "$backup_status" = "SUCCESS" ]; then
        send_email_notification "EXITOSO" "Respaldo completado correctamente\nUbicación: $BACKUP_DIR\nTamaño: $backup_size"
    else
        send_email_notification "FALLIDO" "Errores durante el respaldo:$error_details\nUbicación: $BACKUP_DIR"
    fi

    # Retornar código de salida apropiado
    if [ "$backup_status" = "SUCCESS" ]; then
        exit 0
    else
        exit 1
    fi
}

# Ejecutar función principal.
main