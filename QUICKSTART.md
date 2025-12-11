# Guia Rapida de Uso

## Instalacion

```bash
# Descomprimir
tar -xzf moodle-docker-installer.tar.gz
cd moodle-docker-installer

# Instalar dependencias
sudo ./install.sh

# O manualmente:
sudo pip3 install -r requirements.txt
```

## Uso Basico

```bash
# Ejecutar instalador
sudo python3 main.py
```

## Flujo de Instalacion Completa

1. Ejecutar `sudo python3 main.py`
2. Seleccionar opcion `1` (Instalar infraestructura completa)
3. El script automaticamente:
   - Detecta tu SO
   - Instala Docker si no existe
   - Crea estructura en `/opt/docker-project/`
   - Descarga Moodle 4.5.5
   - Genera contraseñas seguras
   - Crea todos los archivos Docker
   - Configura Nginx
4. Te pregunta que ambiente levantar:
   - Testing (puerto 8080/8443)
   - Produccion (puerto 80/443)
   - Ambos
   - Ninguno (solo instalar)
5. Muestra resumen con credenciales

## Acceder a Moodle

### Testing
```
URL: https://test.moodle.local:8443
Usuario: admin_test
Contraseña: (ver en /opt/docker-project/.env)
```

### Produccion
```
URL: https://moodle.local
Usuario: admin
Contraseña: (ver en /opt/docker-project/.env)
```

NOTA: Debes configurar /etc/hosts o DNS para que apunten a tu servidor

## Comandos Utiles

```bash
# Ver estado
cd /opt/docker-project
docker-compose ps

# Ver logs
docker-compose logs -f

# Reiniciar servicio
docker-compose restart moodle_testing

# Detener todo
docker-compose down

# Levantar todo
docker-compose up -d
```

## Gestion desde el Menu

```bash
sudo python3 main.py
```

Opcion 2: Gestionar ambientes
- Levantar/Detener Testing
- Levantar/Detener Produccion
- Ver estado

Opcion 3: Ver logs
- Logs de Testing
- Logs de Produccion
- Logs de Nginx
- Logs de MySQL

Opcion 4: Backups (en desarrollo)

Opcion 5: Desinstalar todo

## Configuracion DNS

Agregar a /etc/hosts:
```
127.0.0.1 test.moodle.local
127.0.0.1 moodle.local
```

O configurar DNS real apuntando a la IP del servidor

## Personalizar URLs

1. Editar `/opt/docker-project/.env`
2. Cambiar `TEST_URL` y `PROD_URL`
3. Reiniciar: `docker-compose restart`

## Problemas Comunes

### Puerto ocupado
Editar `.env` y cambiar puertos

### Docker no arranca
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Certificados SSL
Los certificados por defecto son autofirmados.
Para produccion, reemplazar en:
`/opt/docker-project/nginx/ssl/`

## Pruebas

```bash
# Ejecutar suite de pruebas
python3 test.py
```

## Proximos Pasos

1. Instalar
2. Configurar DNS/hosts
3. Acceder a Moodle
4. Completar wizard de instalacion de Moodle
5. Configurar backups (cuando Eduardo envie su script lindo)

## Soporte

Para problemas o mejoras, contactar a Eduardo
