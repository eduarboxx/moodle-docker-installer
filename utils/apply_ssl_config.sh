#!/bin/bash
#
# Script para aplicar configuracion SSL al config.php de Moodle
# Uso: ./apply_ssl_config.sh [testing|production]
#

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funcion para imprimir mensajes
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Verificar argumento
if [ -z "$1" ]; then
    print_message "$RED" "Error: Debes especificar el ambiente (testing o production)"
    echo "Uso: $0 [testing|production]"
    exit 1
fi

ENVIRONMENT=$1

# Validar ambiente
if [ "$ENVIRONMENT" != "testing" ] && [ "$ENVIRONMENT" != "production" ]; then
    print_message "$RED" "Error: Ambiente invalido. Usa 'testing' o 'production'"
    exit 1
fi

# Rutas
BASE_PATH="/opt/docker-project"
SSL_CONFIG_FILE="$BASE_PATH/$ENVIRONMENT/moodle_config/ssl_config.php"
CONTAINER_NAME="moodle_$ENVIRONMENT"

# Verificar que exista el archivo de configuracion SSL
if [ ! -f "$SSL_CONFIG_FILE" ]; then
    print_message "$RED" "Error: No se encuentra el archivo de configuracion SSL:"
    print_message "$RED" "  $SSL_CONFIG_FILE"
    print_message "$YELLOW" "\nEjecuta primero la instalacion para generar los archivos de configuracion."
    exit 1
fi

# Verificar que el contenedor este corriendo
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    print_message "$RED" "Error: El contenedor $CONTAINER_NAME no esta corriendo"
    print_message "$YELLOW" "Inicialo con: docker start $CONTAINER_NAME"
    exit 1
fi

print_message "$GREEN" "==================================================================="
print_message "$GREEN" "  Aplicando configuracion SSL a Moodle - Ambiente: $ENVIRONMENT"
print_message "$GREEN" "==================================================================="

# Verificar si Moodle ya esta instalado
MOODLE_CONFIG="/var/www/html/config.php"
if docker exec "$CONTAINER_NAME" test -f "$MOODLE_CONFIG"; then
    print_message "$YELLOW" "\nMoodle ya esta instalado. Aplicando configuracion SSL..."

    # Verificar si la configuracion SSL ya esta aplicada
    if docker exec "$CONTAINER_NAME" grep -q "sslproxy" "$MOODLE_CONFIG" 2>/dev/null; then
        print_message "$YELLOW" "\nLa configuracion SSL ya esta presente en config.php"
        read -p "Deseas reemplazarla? (s/n) [n]: " -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            print_message "$GREEN" "Operacion cancelada."
            exit 0
        fi

        # Eliminar configuracion SSL antigua
        docker exec "$CONTAINER_NAME" bash -c "sed -i '/Configuracion SSL para Moodle/,+20d' $MOODLE_CONFIG"
    fi

    # Copiar archivo de configuracion al contenedor
    docker cp "$SSL_CONFIG_FILE" "$CONTAINER_NAME:/tmp/ssl_config.php"

    # Aplicar configuracion
    docker exec "$CONTAINER_NAME" bash -c "cat /tmp/ssl_config.php >> $MOODLE_CONFIG"
    docker exec "$CONTAINER_NAME" rm /tmp/ssl_config.php

    print_message "$GREEN" "\nConfiguracion SSL aplicada exitosamente!"

    # Limpiar cache de Moodle
    print_message "$YELLOW" "\nLimpiando cache de Moodle..."
    if docker exec "$CONTAINER_NAME" test -f /var/www/html/admin/cli/purge_caches.php; then
        docker exec "$CONTAINER_NAME" php /var/www/html/admin/cli/purge_caches.php
        print_message "$GREEN" "Cache limpiado exitosamente!"
    else
        print_message "$YELLOW" "No se pudo limpiar el cache automaticamente."
        print_message "$YELLOW" "Limpialo manualmente desde: Admin > Desarrollo > Limpiar todas las caches"
    fi

    # Reiniciar contenedor
    print_message "$YELLOW" "\nReiniciando contenedor..."
    docker restart "$CONTAINER_NAME" > /dev/null

    print_message "$GREEN" "\n==================================================================="
    print_message "$GREEN" "  Configuracion SSL aplicada correctamente!"
    print_message "$GREEN" "==================================================================="
    print_message "$GREEN" "\nPasos siguientes:"
    print_message "$GREEN" "1. Accede a tu sitio Moodle con HTTPS"
    print_message "$GREEN" "2. Verifica que no haya errores de contenido mixto"
    print_message "$GREEN" "3. Si usas certificado autofirmado, acepta la excepcion en el navegador"

else
    print_message "$YELLOW" "\nMoodle aun no esta instalado."
    print_message "$YELLOW" "La configuracion SSL se aplicara automaticamente durante la instalacion."
    print_message "$YELLOW" "\nO puedes aplicarla manualmente despues de instalar Moodle con:"
    print_message "$YELLOW" "  docker exec $CONTAINER_NAME bash -c 'cat $SSL_CONFIG_FILE >> $MOODLE_CONFIG'"
fi

echo ""
