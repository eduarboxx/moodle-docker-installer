# Instalacion de Certbot en Rocky Linux / RHEL

Certbot no esta disponible por defecto en los repositorios de Rocky Linux 9.

**IMPORTANTE**: El script `install.sh` ya habilita automaticamente el repositorio EPEL en sistemas RHEL/Rocky Linux, por lo que solo necesitas instalar certbot despues de ejecutar `./install.sh`.

## Instalacion Rapida (Recomendado)

Despues de ejecutar `sudo ./install.sh`, simplemente instala certbot:

```bash
# EPEL ya esta habilitado por install.sh
sudo dnf install -y certbot

# Verificar instalacion
certbot --version
```

## Opciones Alternativas de Instalacion

Si por alguna razon la instalacion simple no funciona, aqui estan las otras opciones:

### Opcion 1: Usar Snap

Esta es la forma oficial recomendada por Let's Encrypt para Rocky Linux.

```bash
# 1. Instalar snapd
sudo dnf install -y snapd

# 2. Habilitar snapd
sudo systemctl enable --now snapd.socket

# 3. Crear symlink para snap
sudo ln -sf /var/lib/snapd/snap /snap

# 4. Cerrar y abrir sesion, o exportar PATH
export PATH=$PATH:/snap/bin

# 5. Instalar certbot
sudo snap install --classic certbot

# 6. Crear symlink para certbot
sudo ln -sf /snap/bin/certbot /usr/bin/certbot

# 7. Verificar instalacion
certbot --version
```

## Opcion 2: Instalar con pip3 (Alternativa)

```bash
# 1. Actualizar pip
sudo pip3 install --upgrade pip

# 2. Instalar certbot
sudo pip3 install certbot

# 3. Verificar instalacion
certbot --version
```

## Opcion 3: Usar EPEL (Si esta disponible)

```bash
# 1. Habilitar EPEL
sudo dnf install -y epel-release

# 2. Actualizar repositorios
sudo dnf update

# 3. Buscar certbot
sudo dnf search certbot

# 4. Instalar (si esta disponible)
sudo dnf install -y certbot
```

## Opcion 4: No usar Let's Encrypt (Alternativa)

Si no puedes instalar certbot, tienes estas opciones:

### A. Certificado Autofirmado (Desarrollo/Testing)

El instalador de Moodle genera automaticamente certificados autofirmados.

**Configuracion en .env**:
```bash
SSL_CERT_TYPE='self-signed'
```

**Ventajas**:
- No requiere certbot
- Funciona offline
- Gratis

**Desventajas**:
- Advertencia de seguridad en navegadores
- No valido para produccion publica

### B. Certificado Personalizado

Si compras un certificado SSL de otra CA (ej: DigiCert, Comodo):

**Configuracion en .env**:
```bash
SSL_CERT_TYPE='custom'
```

Durante la instalacion, proporciona las rutas a tus archivos:
- Certificado (.crt o .pem)
- Clave privada (.key)

## Uso Despues de Instalar Certbot

Una vez instalado certbot, puedes usarlo con el instalador:

```bash
# Editar .env
nano .env

# Configurar Let's Encrypt
SSL_CERT_TYPE='letsencrypt'
SSL_LETSENCRYPT_EMAIL='tu-email@dominio.com'

# Ejecutar instalador
sudo python3 main.py
```

## Verificar Certbot

```bash
# Verificar version
certbot --version

# Verificar certificados instalados
certbot certificates

# Renovar certificados manualmente
certbot renew --dry-run
```

## Renovacion Automatica

Si instalaste certbot via snap, la renovacion automatica ya esta configurada:

```bash
# Verificar timer de renovacion
systemctl list-timers | grep certbot
```

Si instalaste via pip, agrega un cron job:

```bash
# Editar crontab
crontab -e

# Agregar linea:
0 0,12 * * * certbot renew --quiet --deploy-hook "docker restart nginx"
```

## Referencias

- Documentacion oficial Certbot: https://certbot.eff.org/instructions?ws=other&os=centosrhel9
- Let's Encrypt: https://letsencrypt.org/
- Rocky Linux Docs: https://docs.rockylinux.org/
