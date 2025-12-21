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
   - Configura Apache VirtualHosts en el HOST
4. Te pregunta que ambiente levantar:
   - Testing (acceso vía Apache puerto 8080)
   - Produccion (acceso vía Apache puerto 80)
   - Ambos
   - Ninguno (solo instalar)
5. Muestra resumen con credenciales

## Acceder a Moodle

### Testing
```
URL via Apache: http://localhost:8080 o http://IP-del-servidor:8080
URL directa: http://localhost:8081
Usuario: admin_test
Contraseña: (ver en /opt/docker-project/.env)
```

### Produccion
```
URL via Apache: http://localhost o http://IP-del-servidor
URL directa: http://localhost:8082
Usuario: admin
Contraseña: (ver en /opt/docker-project/.env)
```

NOTA: Apache corre en el HOST como proxy reverso a los contenedores Docker

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
- Logs de Testing (Moodle y MySQL)
- Logs de Produccion (Moodle y MySQL)
- Logs de Apache en /var/log/apache2/ o /var/log/httpd/

Opcion 4: Gestionar backups
- Crear backup manual
- Restaurar backup
- Configurar backup automatico
- Ver tareas programadas

Opcion 5: Desinstalar todo

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

### Apache no arranca
```bash
sudo systemctl start apache2    # Debian/Ubuntu
sudo systemctl start httpd      # RHEL/Rocky/Arch
```

### Ver logs de Apache
```bash
sudo tail -f /var/log/apache2/moodle-testing-error.log     # Debian/Ubuntu
sudo tail -f /var/log/httpd/moodle-production-error.log    # RHEL/Rocky/Arch
```

## Pruebas

```bash
# Ejecutar suite de pruebas
python3 test.py
```

## Proximos Pasos

1. Instalar
2. Acceder a Moodle via Apache (http://localhost:8080 para Testing)
3. Completar wizard de instalacion web de Moodle
4. Configurar backups automaticos desde el menu (opcion 4)
5. (Opcional) Configurar SSL con certbot para produccion

## Soporte

Para problemas o mejoras, contactar a Eduardo
