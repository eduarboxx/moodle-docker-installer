#!/bin/bash
#
# Script para aplicar configuracion SSL a Moodle despues de la instalacion
#

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=================================================================${NC}"
echo -e "${GREEN}  Aplicando configuracion SSL a Moodle Production${NC}"
echo -e "${GREEN}=================================================================${NC}"

# Verificar que el contenedor este corriendo
if ! docker ps | grep -q "moodle_production"; then
    echo -e "${RED}Error: El contenedor moodle_production no esta corriendo${NC}"
    exit 1
fi

# Verificar que Moodle este instalado
if ! docker exec moodle_production test -f /var/www/html/config.php; then
    echo -e "${RED}Error: Moodle aun no esta instalado${NC}"
    echo -e "${YELLOW}Completa la instalacion desde el navegador primero${NC}"
    exit 1
fi

# Verificar si SSL ya esta aplicado
if docker exec moodle_production grep -q "sslproxy" /var/www/html/config.php 2>/dev/null; then
    echo -e "${YELLOW}La configuracion SSL ya esta aplicada${NC}"
    read -p "Deseas reemplazarla? (s/n) [n]: " -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo -e "${GREEN}Operacion cancelada${NC}"
        exit 0
    fi

    # Eliminar configuracion SSL antigua
    docker exec moodle_production bash -c "sed -i '/Configuracion SSL para Moodle/,+20d' /var/www/html/config.php"
fi

# Aplicar configuracion SSL
echo -e "\n${YELLOW}Aplicando configuracion SSL...${NC}"

# Copiar archivo al contenedor
docker cp /opt/docker-project/production/moodle_config/ssl_config.php moodle_production:/tmp/ssl_config.php

# Agregar al config.php
docker exec moodle_production bash -c 'cat /tmp/ssl_config.php >> /var/www/html/config.php'

# Limpiar
docker exec moodle_production rm /tmp/ssl_config.php

echo -e "${GREEN}Configuracion SSL aplicada${NC}"

# Limpiar cache de Moodle
echo -e "\n${YELLOW}Limpiando cache de Moodle...${NC}"
if docker exec moodle_production test -f /var/www/html/admin/cli/purge_caches.php; then
    docker exec moodle_production php /var/www/html/admin/cli/purge_caches.php
    echo -e "${GREEN}Cache limpiado${NC}"
else
    echo -e "${YELLOW}No se pudo limpiar el cache automaticamente${NC}"
    echo -e "${YELLOW}Limpialo manualmente desde: Admin > Desarrollo > Limpiar todas las caches${NC}"
fi

# Reiniciar contenedor
echo -e "\n${YELLOW}Reiniciando contenedor...${NC}"
docker restart moodle_production > /dev/null

echo -e "\n${GREEN}=================================================================${NC}"
echo -e "${GREEN}  Configuracion SSL aplicada exitosamente${NC}"
echo -e "${GREEN}=================================================================${NC}"
echo -e "\n${YELLOW}Pasos siguientes:${NC}"
echo -e "1. Accede a ${GREEN}https://pruebas.edu.idatum.cl${NC}"
echo -e "2. Verifica que no haya errores de contenido mixto"
echo -e "3. Limpia la cache del navegador si es necesario"
echo ""
