#!/bin/bash
#
# Script para arreglar Moodle Production y aplicar SSL
#

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=================================================================${NC}"
echo -e "${GREEN}  Reparando instalacion de Moodle Production${NC}"
echo -e "${GREEN}=================================================================${NC}"

# 1. Regenerar Dockerfile con fix de moodledata
echo -e "\n${YELLOW}1. Regenerando Dockerfile de Moodle...${NC}"
cd "/mnt/Archivos/Kakaroto/Documentos/Ciisa/2año/Proyecto /moodle-docker-installer"
python3 -c "
from config.settings import Settings
from docker.dockerfile_generator import DockerfileGenerator

settings = Settings()
dockerfile_gen = DockerfileGenerator(settings)
dockerfile_gen.generate_moodle_dockerfile()
print('Dockerfile regenerado')
"

# 2. Detener y eliminar contenedor de Moodle production
echo -e "\n${YELLOW}2. Deteniendo contenedor actual...${NC}"
cd /opt/docker-project
docker-compose stop moodle_production || true
docker-compose rm -f moodle_production || true

# 3. Eliminar volumen de datos (ESTO BORRARÁ TODOS LOS DATOS)
echo -e "\n${RED}ADVERTENCIA: Se eliminará el volumen de datos de Moodle${NC}"
read -p "Deseas continuar? (s/n) [s]: " -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    docker volume rm moodledata_production || true
    echo -e "${GREEN}Volumen eliminado${NC}"
fi

# 4. Rebuild imagen de Moodle
echo -e "\n${YELLOW}3. Reconstruyendo imagen de Moodle...${NC}"
docker-compose build --no-cache moodle_production

# 5. Levantar contenedor
echo -e "\n${YELLOW}4. Levantando contenedor de Moodle production...${NC}"
docker-compose up -d moodle_production

# 6. Esperar a que esté listo
echo -e "\n${YELLOW}5. Esperando a que Moodle esté listo...${NC}"
sleep 10

# 7. Verificar estado
echo -e "\n${YELLOW}6. Verificando estado de contenedores...${NC}"
docker-compose ps

echo -e "\n${GREEN}=================================================================${NC}"
echo -e "${GREEN}  Reparacion completada${NC}"
echo -e "${GREEN}=================================================================${NC}"
echo -e "\n${YELLOW}Proximos pasos:${NC}"
echo -e "1. Accede a ${GREEN}https://pruebas.edu.idatum.cl${NC}"
echo -e "2. Completa la instalacion de Moodle"
echo -e "   ${YELLOW}IMPORTANTE:${NC} En 'Data directory' pon: ${GREEN}/var/moodledata${NC}"
echo -e "   ${YELLOW}IMPORTANTE:${NC} En 'Web address' pon: ${GREEN}https://pruebas.edu.idatum.cl${NC}"
echo -e "3. Despues de completar la instalacion, ejecuta:"
echo -e "   ${GREEN}sudo bash utils/apply_ssl_to_moodle.sh${NC}"
echo ""
