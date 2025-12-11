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

echo ""
echo "Instalacion completada!"
echo ""
echo "Para ejecutar el instalador:"
echo "  sudo python3 main.py"
echo ""
