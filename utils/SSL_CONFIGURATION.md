# Configuracion SSL para Moodle Docker Installer

Este documento explica la configuracion de certificados SSL y como solucionar problemas de contenido mixto (mixed content).

## Problema de Contenido Mixto

El error "Se ha bloqueado la carga del contenido activo mixto" ocurre cuando:
- Tu sitio Moodle se carga por HTTPS
- Pero intenta cargar recursos (CSS, JS, imagenes) por HTTP

Este instalador soluciona automaticamente este problema configurando SSL correctamente.

## Tipos de Certificados SSL

El sistema soporta tres tipos de certificados SSL:

### 1. Certificados Autofirmados (Desarrollo/Testing)

**Uso recomendado**: Desarrollo local y ambientes de testing

**Configuracion en .env**:
```bash
SSL_CERT_TYPE='self-signed'
```

**Ventajas**:
- Generacion automatica
- No requiere configuracion adicional
- Funciona offline

**Desventajas**:
- Los navegadores mostraran advertencia de seguridad
- No valido para produccion publica

### 2. Let's Encrypt (Produccion)

**Uso recomendado**: Ambientes de produccion con dominio publico

**Configuracion en .env**:
```bash
SSL_CERT_TYPE='letsencrypt'
SSL_LETSENCRYPT_EMAIL='tu-email@dominio.com'
```

**Requisitos**:
- Dominio publico que apunte a tu servidor
- Puerto 80 accesible desde internet
- Certbot instalado (el instalador puede hacerlo automaticamente)

**Ventajas**:
- Certificados gratuitos y validos
- Renovacion automatica
- Reconocido por todos los navegadores

**Desventajas**:
- Requiere dominio publico
- Requiere acceso a puerto 80 desde internet

### 3. Certificados Personalizados

**Uso recomendado**: Cuando ya tienes certificados de otra CA

**Configuracion en .env**:
```bash
SSL_CERT_TYPE='custom'
```

Durante la instalacion se te pediran las rutas a tus archivos .crt y .key

## Configuracion de HTTPS en Moodle

El sistema configura automaticamente Moodle para usar HTTPS correctamente:

**Configuracion aplicada**:
```php
// Forzar SSL/HTTPS
$CFG->wwwroot = 'https://tu-dominio.com';
$CFG->sslproxy = true;

// Configuracion de sesiones seguras
@ini_set('session.cookie_secure', 'on');
@ini_set('session.cookie_httponly', 'on');
@ini_set('session.cookie_samesite', 'Lax');

// Forzar conexion segura
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] == 'https') {
    $_SERVER['HTTPS'] = 'on';
}
```

## Archivos de Configuracion SSL

Despues de la instalacion encontraras:

```
/opt/docker-project/
├── nginx/
│   └── ssl/
│       ├── testing.crt       # Certificado testing
│       ├── testing.key       # Clave privada testing
│       ├── production.crt    # Certificado produccion
│       └── production.key    # Clave privada produccion
├── testing/
│   └── moodle_config/
│       └── ssl_config.php    # Config SSL para testing
└── production/
    └── moodle_config/
        └── ssl_config.php    # Config SSL para produccion
```

## Aplicar Configuracion SSL a Moodle

Despues de la instalacion de Moodle, debes agregar la configuracion SSL:

### Metodo 1: Manual

1. Acceder al contenedor de Moodle:
```bash
docker exec -it moodle_production bash
```

2. Editar el archivo config.php de Moodle:
```bash
nano /var/www/html/config.php
```

3. Agregar las lineas del archivo ssl_config.php generado
```bash
cat /opt/docker-project/production/moodle_config/ssl_config.php
```

4. Reiniciar el contenedor:
```bash
docker restart moodle_production
```

### Metodo 2: Script Automatico (Recomendado)

Crear un script que se ejecute durante el arranque del contenedor:

1. Modificar el Dockerfile de Moodle para incluir:
```dockerfile
COPY production/moodle_config/ssl_config.php /etc/moodle/ssl_config.php
```

2. En el entrypoint del contenedor, agregar al config.php:
```bash
cat /etc/moodle/ssl_config.php >> /var/www/html/config.php
```

## Solucion de Problemas

### Error: "Contenido mixto bloqueado"

**Causa**: Moodle esta cargando recursos por HTTP en lugar de HTTPS

**Solucion**:
1. Verificar que `$CFG->sslproxy = true;` este en config.php
2. Verificar que `$CFG->wwwroot` use `https://`
3. Limpiar cache de Moodle:
   - Admin > Desarrollo > Limpiar todas las caches
   - O via CLI: `php admin/cli/purge_caches.php`

### Error: "Certificado no valido" con Let's Encrypt

**Posibles causas**:
- El dominio no apunta correctamente al servidor
- El puerto 80 esta bloqueado por firewall
- Certbot no pudo validar el dominio

**Solucion**:
1. Verificar DNS:
```bash
dig tu-dominio.com
```

2. Verificar puerto 80:
```bash
nc -zv tu-dominio.com 80
```

3. Revisar logs de certbot:
```bash
tail -f /var/log/letsencrypt/letsencrypt.log
```

### Renovacion de Certificados Let's Encrypt

Los certificados de Let's Encrypt son validos por 90 dias y se renuevan automaticamente.

**Verificar renovacion automatica**:
```bash
crontab -l | grep certbot
```

**Renovar manualmente**:
```bash
certbot renew
docker restart nginx
```

**Verificar expiracion**:
```bash
certbot certificates
```

## Variables de Entorno

Todas las variables SSL disponibles en `.env`:

```bash
# Tipo de certificado SSL
SSL_CERT_TYPE='self-signed'         # self-signed | letsencrypt | custom

# Email para Let's Encrypt
SSL_LETSENCRYPT_EMAIL='admin@dominio.com'

# Forzar HTTPS en Moodle
SSL_FORCE_HTTPS='true'              # true | false

# URLs (deben usar https://)
TEST_URL='https://test.moodle.local'
PROD_URL='https://moodle.local'
```

## Mejores Practicas

### Para Desarrollo/Testing
- Usar certificados autofirmados
- Agregar excepcion de seguridad en el navegador
- No compartir el sitio publicamente

### Para Produccion
- Usar Let's Encrypt para dominios publicos
- Configurar renovacion automatica
- Monitorear expiracion de certificados
- Hacer backup de certificados personalizados

### Seguridad Adicional
- Forzar HSTS (HTTP Strict Transport Security)
- Configurar Content Security Policy (CSP)
- Actualizar regularmente certificados
- Usar TLS 1.2 o superior solamente

## Referencias

- Documentacion oficial Moodle SSL: https://docs.moodle.org/en/HTTPS
- Let's Encrypt: https://letsencrypt.org/
- Certbot: https://certbot.eff.org/
- SSL Labs Test: https://www.ssllabs.com/ssltest/
