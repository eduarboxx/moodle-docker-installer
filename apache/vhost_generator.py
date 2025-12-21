"""
Apache VirtualHost Generator Module
Genera configuraciones de Apache VirtualHost para proxy reverso a contenedores Moodle
"""

import os
import socket
import platform


class ApacheVHostGenerator:
    """Genera VirtualHosts de Apache para Moodle"""

    def __init__(self, settings):
        self.settings = settings
        self.os_type = self._detect_os()

    def _detect_os(self):
        """Detecta el sistema operativo"""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                if 'ubuntu' in content or 'debian' in content:
                    return 'debian'
                elif 'rocky' in content or 'rhel' in content or 'centos' in content or 'fedora' in content:
                    return 'rhel'
                elif 'arch' in content:
                    return 'arch'
        except:
            pass
        return 'unknown'

    def _get_host_ip(self):
        """Obtiene la IP del host"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "localhost"

    def _get_log_dir(self):
        """Retorna el directorio de logs según el SO"""
        if self.os_type == 'debian':
            return '${APACHE_LOG_DIR}'
        else:  # rhel, arch
            return '/var/log/httpd'

    def _get_vhost_dir(self):
        """Retorna el directorio para VirtualHosts según el SO"""
        if self.os_type == 'debian':
            return '/etc/apache2/sites-available'
        elif self.os_type == 'rhel':
            return '/etc/httpd/conf.d'
        elif self.os_type == 'arch':
            return '/etc/httpd/conf/extra'
        else:
            return '/etc/apache2/sites-available'  # fallback

    def generate_testing_vhost(self):
        """Genera VirtualHost para ambiente de testing"""
        log_dir = self._get_log_dir()

        vhost_content = f"""# Moodle Testing Environment VirtualHost
<VirtualHost *:8080>
    # No ServerName - acepta requests de cualquier IP/hostname

    ProxyPreserveHost On
    ProxyPass / http://localhost:8081/
    ProxyPassReverse / http://localhost:8081/

    # Headers para que Moodle conozca el protocolo y puerto original
    RequestHeader set X-Forwarded-Proto "http"
    RequestHeader set X-Forwarded-Port "8080"

    <Proxy *>
        Order deny,allow
        Allow from all
    </Proxy>

    ErrorLog {log_dir}/moodle-testing-error.log
    CustomLog {log_dir}/moodle-testing-access.log combined
</VirtualHost>
"""

        vhost_dir = self._get_vhost_dir()
        vhost_path = os.path.join(vhost_dir, 'moodle-testing.conf')

        try:
            os.makedirs(vhost_dir, exist_ok=True)
            with open(vhost_path, 'w') as f:
                f.write(vhost_content)
            print(f"VirtualHost Testing creado: {vhost_path}")
            return vhost_path
        except PermissionError:
            print(f"ERROR: Se requieren permisos de root para escribir en {vhost_dir}")
            print(f"Ejecuta el instalador con sudo")
            return None
        except Exception as e:
            print(f"Error creando VirtualHost Testing: {str(e)}")
            return None

    def generate_production_vhost(self):
        """Genera VirtualHost para ambiente de producción"""
        log_dir = self._get_log_dir()

        vhost_content = f"""# Moodle Production Environment VirtualHost
<VirtualHost *:80>
    # No ServerName - acepta requests de cualquier IP/hostname

    ProxyPreserveHost On
    ProxyPass / http://localhost:8082/
    ProxyPassReverse / http://localhost:8082/

    # Headers para que Moodle conozca el protocolo original
    RequestHeader set X-Forwarded-Proto "http"

    <Proxy *>
        Order deny,allow
        Allow from all
    </Proxy>

    ErrorLog {log_dir}/moodle-production-error.log
    CustomLog {log_dir}/moodle-production-access.log combined
</VirtualHost>
"""

        vhost_dir = self._get_vhost_dir()
        vhost_path = os.path.join(vhost_dir, 'moodle-production.conf')

        try:
            with open(vhost_path, 'w') as f:
                f.write(vhost_content)
            print(f"VirtualHost Production creado: {vhost_path}")
            return vhost_path
        except PermissionError:
            print(f"ERROR: Se requieren permisos de root para escribir en {vhost_dir}")
            print(f"Ejecuta el instalador con sudo")
            return None
        except Exception as e:
            print(f"Error creando VirtualHost Production: {str(e)}")
            return None

    def enable_sites(self):
        """Habilita los sitios (solo en Debian/Ubuntu con a2ensite)"""
        if self.os_type == 'debian':
            import subprocess
            try:
                subprocess.run(['a2ensite', 'moodle-testing.conf'], check=True)
                print("Sitio moodle-testing habilitado")
                subprocess.run(['a2ensite', 'moodle-production.conf'], check=True)
                print("Sitio moodle-production habilitado")
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error habilitando sitios: {e}")
                return False
        else:
            # En RHEL/Arch los archivos en conf.d o conf/extra se cargan automáticamente
            print("VirtualHosts configurados (se cargarán automáticamente)")
            return True

    def configure_ports(self):
        """Configura Apache para escuchar en puerto 8080"""
        if self.os_type == 'debian':
            ports_file = '/etc/apache2/ports.conf'
        elif self.os_type == 'rhel':
            ports_file = '/etc/httpd/conf/httpd.conf'
        elif self.os_type == 'arch':
            ports_file = '/etc/httpd/conf/httpd.conf'
        else:
            return False

        try:
            # Leer archivo actual
            with open(ports_file, 'r') as f:
                content = f.read()

            # Verificar si ya tiene Listen 8080
            if 'Listen 8080' not in content:
                # Agregar Listen 8080
                if self.os_type == 'debian':
                    # Buscar línea "Listen 80" y agregar después
                    lines = content.split('\n')
                    new_lines = []
                    for line in lines:
                        new_lines.append(line)
                        if line.strip().startswith('Listen 80'):
                            new_lines.append('Listen 8080')
                    content = '\n'.join(new_lines)
                else:
                    # En RHEL/Arch agregar al final
                    content += '\nListen 8080\n'

                # Escribir archivo
                with open(ports_file, 'w') as f:
                    f.write(content)

                print(f"Puerto 8080 agregado a {ports_file}")
            else:
                print(f"Puerto 8080 ya configurado en {ports_file}")

            return True
        except PermissionError:
            print(f"ERROR: Se requieren permisos de root para modificar {ports_file}")
            return False
        except Exception as e:
            print(f"Error configurando puertos: {str(e)}")
            return False

    def reload_apache(self):
        """Recarga la configuración de Apache"""
        import subprocess

        service_name = 'apache2' if self.os_type == 'debian' else 'httpd'

        try:
            subprocess.run(['systemctl', 'reload', service_name], check=True)
            print(f"Apache ({service_name}) recargado exitosamente")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error recargando Apache: {e}")
            print(f"Intenta manualmente: sudo systemctl reload {service_name}")
            return False

    def generate_all(self):
        """Genera todos los VirtualHosts y configura Apache"""
        print("\n=== Configurando Apache VirtualHosts ===\n")

        host_ip = self._get_host_ip()
        print(f"IP del host detectada: {host_ip}")
        print(f"Sistema operativo detectado: {self.os_type}")

        # Generar VirtualHosts
        testing_path = self.generate_testing_vhost()
        production_path = self.generate_production_vhost()

        if not testing_path or not production_path:
            return False

        # Configurar puerto 8080
        if not self.configure_ports():
            print("ADVERTENCIA: No se pudo configurar puerto 8080 automáticamente")
            print("Configúralo manualmente según tu distribución")

        # Habilitar sitios (solo Debian/Ubuntu)
        self.enable_sites()

        # Recargar Apache
        self.reload_apache()

        print("\n=== Configuración de Apache completada ===")
        print(f"\nAccede a Moodle Testing en:")
        print(f"  - http://localhost:8080")
        print(f"  - http://{host_ip}:8080")
        print(f"\nAccede a Moodle Production en:")
        print(f"  - http://localhost")
        print(f"  - http://{host_ip}")

        return True
