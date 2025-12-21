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

# Instalar herramientas necesarias: git, wget y Apache
echo "Verificando herramientas necesarias..."
TOOLS_TO_INSTALL=""

if ! command -v git &> /dev/null; then
    TOOLS_TO_INSTALL="$TOOLS_TO_INSTALL git"
fi

if ! command -v wget &> /dev/null; then
    TOOLS_TO_INSTALL="$TOOLS_TO_INSTALL wget"
fi

# Detectar e instalar Apache según el SO
APACHE_INSTALLED=false
if command -v apache2 &> /dev/null || command -v httpd &> /dev/null; then
    echo "Apache ya esta instalado"
    APACHE_INSTALLED=true
fi

if [ "$APACHE_INSTALLED" = false ]; then
    echo "Instalando Apache..."
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        TOOLS_TO_INSTALL="$TOOLS_TO_INSTALL apache2"
    elif command -v dnf &> /dev/null; then
        # Rocky/RHEL/CentOS/Fedora
        TOOLS_TO_INSTALL="$TOOLS_TO_INSTALL httpd"
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        TOOLS_TO_INSTALL="$TOOLS_TO_INSTALL apache"
    fi
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
    echo "Git, wget y Apache ya estan instalados"
fi

# Habilitar módulos de Apache necesarios
echo "Habilitando modulos de Apache..."
if command -v a2enmod &> /dev/null; then
    # Ubuntu/Debian
    a2enmod proxy proxy_http headers rewrite ssl 2>/dev/null || true
    echo "Modulos de Apache habilitados (Debian/Ubuntu)"
elif command -v httpd &> /dev/null; then
    # Rocky/RHEL/Arch - los módulos se cargan desde archivos de configuración
    echo "Modulos de Apache se configuraran automaticamente (RHEL/Arch)"
fi

# Iniciar y habilitar Apache
echo "Iniciando Apache..."
if command -v apache2 &> /dev/null; then
    # Ubuntu/Debian
    systemctl enable apache2 2>/dev/null || true
    systemctl start apache2 2>/dev/null || true
    echo "Apache (apache2) iniciado y habilitado"
elif command -v httpd &> /dev/null; then
    # Rocky/RHEL/Arch
    systemctl enable httpd 2>/dev/null || true
    systemctl start httpd 2>/dev/null || true
    echo "Apache (httpd) iniciado y habilitado"
fi

# Verificar e instalar cron/cronie (necesario para backups automaticos)
echo "Verificando instalacion de cron..."
CRON_INSTALLED=false
if command -v crontab &> /dev/null; then
    echo "Cron ya esta instalado"
    CRON_INSTALLED=true
fi

if [ "$CRON_INSTALLED" = false ]; then
    echo "Instalando cron para backups automaticos..."
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        apt-get install -y cron
        systemctl enable cron 2>/dev/null || true
        systemctl start cron 2>/dev/null || true
        echo "Cron instalado y habilitado"
    elif command -v dnf &> /dev/null; then
        # Rocky/RHEL/CentOS/Fedora
        dnf install -y cronie
        systemctl enable crond 2>/dev/null || true
        systemctl start crond 2>/dev/null || true
        echo "Cronie instalado y habilitado"
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        pacman -S --noconfirm cronie
        systemctl enable cronie 2>/dev/null || true
        systemctl start cronie 2>/dev/null || true
        echo "Cronie instalado y habilitado"
    else
        echo "ADVERTENCIA: No se pudo instalar cron automaticamente"
        echo "Los backups automaticos no estaran disponibles hasta que instales cron manualmente"
    fi
else
    # Verificar que el servicio cron este activo
    echo "Verificando servicio cron..."
    if command -v systemctl &> /dev/null; then
        if systemctl is-active --quiet cron 2>/dev/null; then
            echo "Servicio cron esta activo"
        elif systemctl is-active --quiet crond 2>/dev/null; then
            echo "Servicio crond esta activo"
        elif systemctl is-active --quiet cronie 2>/dev/null; then
            echo "Servicio cronie esta activo"
        else
            # Intentar iniciar el servicio
            echo "Iniciando servicio cron..."
            systemctl start cron 2>/dev/null || \
            systemctl start crond 2>/dev/null || \
            systemctl start cronie 2>/dev/null || \
            echo "ADVERTENCIA: No se pudo iniciar el servicio cron"
        fi
    fi
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
