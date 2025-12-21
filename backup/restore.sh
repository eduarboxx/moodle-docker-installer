#!/bin/bash

###############################################################################
# Script de Restauración de Respaldos para Moodle en Docker
# Restaura: Base de datos MySQL + moodledata
# Formatos soportados: .sql.gz (comprimido) y .sql (sin comprimir)
# Autor: Eduardo Valdés
###############################################################################

# Configuración de variables
ENVIRONMENT="${1}"
BACKUP_TIMESTAMP="${2}"

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
BACKUP_DIR="$BASE_BACKUP_DIR/$ENVIRONMENT/$BACKUP_TIMESTAMP"

# Nombres de contenedores
MYSQL_CONTAINER="mysql_$ENVIRONMENT"
MOODLE_CONTAINER="moodle_$ENVIRONMENT"

# Archivo de log
LOG_FILE="/tmp/restore_${ENVIRONMENT}_${BACKUP_TIMESTAMP}.log"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
    log_message "${BLUE}[INFO]${NC} $1"
}

###############################################################################
# Validaciones iniciales
###############################################################################
validate_parameters() {
    if [ -z "$ENVIRONMENT" ]; then
        echo "ERROR: Debe especificar el ambiente (testing o production)"
        echo "Uso: $0 <environment> <backup_timestamp>"
        echo "Ejemplo: $0 testing 2024-01-15_10-30-00"
        exit 1
    fi

    if [ -z "$BACKUP_TIMESTAMP" ]; then
        echo "ERROR: Debe especificar el timestamp del backup"
        echo "Uso: $0 <environment> <backup_timestamp>"
        echo ""
        echo "Backups disponibles para $ENVIRONMENT:"
        list_available_backups
        exit 1
    fi

    if [ ! -d "$BACKUP_DIR" ]; then
        log_error "No existe el directorio de backup: $BACKUP_DIR"
        echo ""
        echo "Backups disponibles para $ENVIRONMENT:"
        list_available_backups
        exit 1
    fi

    log_success "Parámetros validados correctamente"
}

list_available_backups() {
    local env_backup_dir="$BASE_BACKUP_DIR/$ENVIRONMENT"
    if [ -d "$env_backup_dir" ]; then
        ls -1 "$env_backup_dir" | sort -r
    else
        echo "  (no hay backups disponibles)"
    fi
}

###############################################################################
# Confirmación del usuario
###############################################################################
confirm_restore() {
    # Si SKIP_CONFIRMATION está configurada, saltar la confirmación
    # (la confirmación ya fue hecha en la interfaz de Python)
    if [ "${SKIP_CONFIRMATION}" = "yes" ]; then
        log_info "Confirmación omitida (ya confirmado previamente)"
        log_success "Iniciando restauración..."
        return 0
    fi

    log_warning "=========================================="
    log_warning "ADVERTENCIA: RESTAURACIÓN DE RESPALDO"
    log_warning "=========================================="
    log_warning "Ambiente: $ENVIRONMENT"
    log_warning "Backup: $BACKUP_TIMESTAMP"
    log_warning "Esta acción:"
    log_warning "  - ELIMINARÁ todos los datos actuales"
    log_warning "  - Restaurará los datos del backup especificado"
    log_warning "  - Detendrá temporalmente los servicios"
    echo ""
    read -p "¿Está seguro de continuar? (escriba 'SI' en mayúsculas): " confirmation

    if [ "$confirmation" != "SI" ]; then
        log_info "Restauración cancelada por el usuario"
        exit 0
    fi

    log_success "Confirmación recibida, iniciando restauración..."
}

###############################################################################
# Detener servicios
###############################################################################
stop_services() {
    log_info "Deteniendo servicios de Moodle..."

    docker stop "$MOODLE_CONTAINER" 2>> "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log_success "Contenedor Moodle detenido"
        return 0
    else
        log_warning "No se pudo detener el contenedor Moodle (puede que no esté corriendo)"
        return 0
    fi
}

###############################################################################
# Iniciar servicios
###############################################################################
start_services() {
    log_info "Iniciando servicios de Moodle..."

    docker start "$MOODLE_CONTAINER" 2>> "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log_success "Contenedor Moodle iniciado"
        return 0
    else
        log_error "Error al iniciar el contenedor Moodle"
        return 1
    fi
}

###############################################################################
# Restaurar base de datos MySQL
###############################################################################
restore_mysql_database() {
    log_info "Restaurando base de datos MySQL..."

    # Buscar archivo SQL (primero comprimido, luego sin comprimir)
    local sql_file=$(find "$BACKUP_DIR" -name "*.sql.gz" | head -n 1)
    local is_compressed=true

    if [ -z "$sql_file" ]; then
        # Si no hay archivo comprimido, buscar archivo .sql sin comprimir
        sql_file=$(find "$BACKUP_DIR" -name "*.sql" | head -n 1)
        is_compressed=false
    fi

    if [ -z "$sql_file" ]; then
        log_error "No se encontró archivo SQL en el backup (buscado: *.sql.gz, *.sql)"
        return 1
    fi

    if [ "$is_compressed" = true ]; then
        log_info "Archivo encontrado (comprimido): $(basename $sql_file)"
    else
        log_info "Archivo encontrado (sin comprimir): $(basename $sql_file)"
    fi

    # Verificar que el contenedor MySQL esté corriendo
    if ! docker ps | grep -q "$MYSQL_CONTAINER"; then
        log_error "El contenedor MySQL ($MYSQL_CONTAINER) no está corriendo"
        return 1
    fi

    local db_name="${DB_NAME:-moodle}"
    local db_user="root"
    local db_pass="${DB_ROOT_PASS}"

    # Restaurar según el formato
    if [ "$is_compressed" = true ]; then
        # Descomprimir, filtrar warnings y restaurar
        log_info "Descomprimiendo y restaurando base de datos..."
        gunzip -c "$sql_file" | grep -v "^mysqldump:" | grep -v "^mysql:" | docker exec -i "$MYSQL_CONTAINER" mysql \
            -u"$db_user" \
            -p"$db_pass" \
            "$db_name" 2>> "$LOG_FILE"
    else
        # Filtrar warnings de mysqldump que puedan estar en el archivo y restaurar
        log_info "Restaurando base de datos..."
        grep -v "^mysqldump:" "$sql_file" | grep -v "^mysql:" | docker exec -i "$MYSQL_CONTAINER" mysql \
            -u"$db_user" \
            -p"$db_pass" \
            "$db_name" 2>> "$LOG_FILE"
    fi

    if [ $? -eq 0 ]; then
        log_success "Base de datos restaurada correctamente"
        return 0
    else
        log_error "Error al restaurar la base de datos"
        return 1
    fi
}

###############################################################################
# Restaurar moodledata
###############################################################################
restore_moodledata() {
    log_info "Restaurando moodledata..."

    # Buscar archivo de moodledata
    local moodledata_file=$(find "$BACKUP_DIR" -name "moodledata_*.tar.gz" | head -n 1)

    if [ -z "$moodledata_file" ]; then
        log_error "No se encontró archivo de moodledata en el backup"
        return 1
    fi

    log_info "Archivo encontrado: $(basename $moodledata_file)"

    local volume_name="moodledata_${ENVIRONMENT}"

    # Verificar que el volumen existe
    if ! docker volume ls | grep -q "$volume_name"; then
        log_error "El volumen $volume_name no existe"
        return 1
    fi

    # Limpiar volumen actual
    log_warning "Eliminando contenido actual de moodledata..."
    docker run --rm \
        -v "$volume_name":/target \
        alpine sh -c "rm -rf /target/*" 2>> "$LOG_FILE"

    # Restaurar desde backup
    log_info "Restaurando contenido de moodledata..."
    docker run --rm \
        -v "$volume_name":/target \
        -v "$BACKUP_DIR":/backup:ro \
        alpine tar xzf "/backup/$(basename $moodledata_file)" -C /target 2>> "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log_success "Moodledata restaurado correctamente"
        return 0
    else
        log_error "Error al restaurar moodledata"
        return 1
    fi
}

###############################################################################
# Verificar restauración
###############################################################################
verify_restore() {
    log_info "Verificando restauración..."

    # Esperar a que los servicios estén listos
    sleep 5

    # Verificar que el contenedor Moodle esté corriendo
    if docker ps | grep -q "$MOODLE_CONTAINER"; then
        log_success "Contenedor Moodle está corriendo"
    else
        log_warning "El contenedor Moodle no está corriendo"
    fi

    # Verificar logs del contenedor
    log_info "Últimas líneas del log de Moodle:"
    docker logs --tail 10 "$MOODLE_CONTAINER" 2>&1 | tee -a "$LOG_FILE"
}

###############################################################################
# Función principal
###############################################################################
main() {
    log_info "=========================================="
    log_info "Restauración de Respaldo de Moodle"
    log_info "=========================================="

    # Validar parámetros
    validate_parameters

    # Confirmar con el usuario
    confirm_restore

    local restore_status="SUCCESS"

    # Detener servicios
    if ! stop_services; then
        log_error "Error al detener servicios"
        restore_status="FAILED"
    fi

    # Restaurar base de datos
    if [ "$restore_status" = "SUCCESS" ]; then
        if ! restore_mysql_database; then
            restore_status="FAILED"
        fi
    fi

    # Restaurar moodledata
    if [ "$restore_status" = "SUCCESS" ]; then
        if ! restore_moodledata; then
            restore_status="FAILED"
        fi
    fi

    # Iniciar servicios
    if ! start_services; then
        log_error "Error al iniciar servicios"
        restore_status="FAILED"
    fi

    # Verificar restauración
    verify_restore

    # Resultado final
    log_info "=========================================="
    if [ "$restore_status" = "SUCCESS" ]; then
        log_success "RESTAURACIÓN COMPLETADA EXITOSAMENTE"
        log_info "Ambiente: $ENVIRONMENT"
        log_info "Backup: $BACKUP_TIMESTAMP"
    else
        log_error "RESTAURACIÓN COMPLETADA CON ERRORES"
        log_info "Revise el log: $LOG_FILE"
    fi
    log_info "=========================================="

    # Retornar código de salida apropiado
    if [ "$restore_status" = "SUCCESS" ]; then
        exit 0
    else
        exit 1
    fi
}

# Ejecutar función principal
main
