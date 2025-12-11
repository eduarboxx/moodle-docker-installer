# Compatibilidad Docker Compose

Este proyecto soporta automáticamente ambas versiones de Docker Compose:
- **Docker Compose V2** (plugin): `docker compose` (recomendado)
- **Docker Compose V1** (standalone): `docker-compose` (legacy)

## ¿Cómo funciona?

El módulo `docker_compose_wrapper.py` detecta automáticamente qué versión está disponible en el sistema y usa el comando correcto.

## Orden de detección

1. Primero intenta usar `docker compose` (V2 plugin)
2. Si no está disponible, intenta `docker-compose` (V1 standalone)
3. Si ninguno está disponible, usa `docker compose` por defecto

## Uso en el código

### Importar el wrapper
```python
from utils.docker_compose_wrapper import DockerComposeWrapper
```

### Obtener el comando como string
```python
compose_cmd = DockerComposeWrapper.get_compose_command_string()
# Retorna: "docker compose" o "docker-compose"
```

### Ejecutar comandos compose
```python
# Método 1: Con shell
result = DockerComposeWrapper.run_compose_shell(
    "up -d",
    cwd="/ruta/al/proyecto"
)

# Método 2: Con lista de argumentos
result = DockerComposeWrapper.run_compose(
    ["up", "-d"],
    cwd="/ruta/al/proyecto"
)
```

### Verificar disponibilidad
```python
if DockerComposeWrapper.is_compose_available():
    print("Docker Compose está disponible")
```

## Archivos actualizados

Los siguientes archivos han sido modificados para usar el wrapper:

- `core/docker_installer.py` - Detección de Docker Compose instalado
- `main.py` - Todos los comandos docker-compose en el instalador principal

## Ventajas

- ✅ Compatibilidad con sistemas que tienen V1 o V2
- ✅ Transición automática entre versiones
- ✅ No requiere cambios manuales
- ✅ Cache del comando detectado para mejor rendimiento
- ✅ Manejo consistente de errores
