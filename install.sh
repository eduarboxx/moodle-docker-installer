#!/bin/bash

# Script de instalacion rapida
# Moodle Docker Infrastructure Installer

set -e

echo "================================================================="
echo "  Moodle Docker Infrastructure Installer - Instalacion Rapida"
echo "================================================================="
echo ""

# Verificar permisos root
if [ "$EUID" -ne 0 ]; then
    echo "Error: Este script debe ejecutarse como root"
    echo "Usa: sudo ./install.sh"
    exit 1
fi

# Verificar Python3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 no esta instalado"
    echo "Instala Python3 primero"
    exit 1
fi

# Habilitar repositorios necesarios segun el sistema operativo
echo "Verificando repositorios del sistema..."
if command -v dnf &> /dev/null; then
    # Sistema basado en RHEL/Rocky/CentOS
    if [ -f /etc/redhat-release ]; then
        echo "Sistema RHEL/Rocky detectado"

        # Verificar si EPEL esta instalado
        if ! rpm -q epel-release &> /dev/null; then
            echo "Instalando repositorio EPEL..."
            dnf install -y epel-release

            # Habilitar CodeReady Builder (CRB) si esta disponible
            if command -v crb &> /dev/null; then
                echo "Habilitando CodeReady Builder (CRB)..."
                crb enable || true
            fi
        else
            echo "EPEL ya esta instalado"
        fi
    fi
fi

# Instalar herramientas necesarias: git y wget
echo "Verificando herramientas necesarias..."
TOOLS_TO_INSTALL=""

if ! command -v git &> /dev/null; then
    TOOLS_TO_INSTALL="$TOOLS_TO_INSTALL git"
fi

if ! command -v wget &> /dev/null; then
    TOOLS_TO_INSTALL="$TOOLS_TO_INSTALL wget"
fi

if [ -n "$TOOLS_TO_INSTALL" ]; then
    echo "Instalando herramientas:$TOOLS_TO_INSTALL"
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y $TOOLS_TO_INSTALL
    elif command -v dnf &> /dev/null; then
        dnf install -y $TOOLS_TO_INSTALL
    elif command -v pacman &> /dev/null; then
        pacman -S --noconfirm $TOOLS_TO_INSTALL
    fi
else
    echo "Git y wget ya estan instalados"
fi

# Instalar pip si no existe
if ! command -v pip3 &> /dev/null; then
    echo "Instalando pip3..."
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y python3-pip
    elif command -v dnf &> /dev/null; then
        dnf install -y python3-pip
    elif command -v pacman &> /dev/null; then
        pacman -S --noconfirm python-pip
    fi
fi

# Instalar dependencias
echo "Instalando dependencias Python..."
pip3 install -r requirements.txt

# Crear archivo .env si no existe
echo ""
if [ ! -f .env ]; then
    echo "Creando archivo de configuracion .env desde .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "Archivo .env creado exitosamente"
        echo ""
        echo "================================================================="
        echo "  IMPORTANTE: Debes editar el archivo .env antes de continuar"
        echo "================================================================="
        echo ""
        echo "El archivo .env contiene las variables de configuracion necesarias."
        echo "Por defecto, las contraseñas estan marcadas como 'GENERAR_CONTRASEÑA_SEGURA'"
        echo ""
        echo "Opciones:"
        echo "  1. Ejecutar el instalador y las contraseñas se generaran automaticamente"
        echo "  2. Editar .env manualmente y establecer tus propias contraseñas"
        echo ""
        echo "Para editar el archivo .env:"
        echo "  nano .env"
        echo "  o"
        echo "  vim .env"
        echo ""
    else
        echo "Error: No se encontro .env.example"
        echo "El archivo .env debe crearse manualmente"
    fi
else
    echo "El archivo .env ya existe, no se sobrescribira"
fi

echo ""
echo "================================================================="
echo "  Instalacion de dependencias completada"
echo "================================================================="
echo ""
echo "PROXIMOS PASOS:"
echo ""
echo "1. (Opcional) Edita el archivo .env con tus configuraciones:"
echo "   nano .env"
echo ""
echo "2. Ejecuta el instalador principal:"
echo "   sudo python3 main.py"
echo ""
echo "Nota: Si no editas el .env, el instalador generara contraseñas"
echo "      seguras automaticamente durante la instalacion."
echo ""
