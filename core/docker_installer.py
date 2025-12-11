"""
Docker Installer Module
Instala Docker y Docker Compose en diferentes distribuciones
"""

import subprocess
import time


class DockerInstaller:
    """Instala Docker y Docker Compose"""
    
    def __init__(self, os_info):
        self.os_info = os_info
        self.family = os_info['family']
        self.package_manager = os_info['package_manager']
    
    def is_installed(self):
        """Verifica si Docker esta instalado"""
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # Verificar Docker Compose tambien
                result_compose = subprocess.run(
                    ['docker-compose', '--version'],
                    capture_output=True,
                    text=True
                )
                return result_compose.returncode == 0
            return False
        except FileNotFoundError:
            return False
    
    def install(self):
        """Instala Docker segun la distribucion"""
        print("Instalando Docker...")
        
        if self.family == 'debian':
            return self._install_debian()
        elif self.family == 'rhel':
            return self._install_rhel()
        elif self.family == 'arch':
            return self._install_arch()
        else:
            print(f"Familia de SO no soportada: {self.family}")
            return False
    
    def _install_debian(self):
        """Instala Docker en Debian/Ubuntu"""
        commands = [
            # Actualizar repositorios
            'apt-get update',
            
            # Instalar dependencias
            'apt-get install -y ca-certificates curl gnupg lsb-release',
            
            # Agregar GPG key de Docker
            'install -m 0755 -d /etc/apt/keyrings',
            'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg',
            'chmod a+r /etc/apt/keyrings/docker.gpg',
            
            # Agregar repositorio
            '''echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null''',
            
            # Instalar Docker
            'apt-get update',
            'apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin',
            
            # Iniciar servicio
            'systemctl start docker',
            'systemctl enable docker'
        ]
        
        return self._execute_commands(commands)
    
    def _install_rhel(self):
        """Instala Docker en RHEL/Rocky/CentOS"""
        commands = [
            # Instalar dependencias
            'dnf install -y dnf-plugins-core',
            
            # Agregar repositorio
            'dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo',
            
            # Instalar Docker
            'dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin',
            
            # Iniciar servicio
            'systemctl start docker',
            'systemctl enable docker'
        ]
        
        return self._execute_commands(commands)
    
    def _install_arch(self):
        """Instala Docker en Arch Linux"""
        commands = [
            # Actualizar sistema
            'pacman -Syu --noconfirm',
            
            # Instalar Docker
            'pacman -S --noconfirm docker docker-compose',
            
            # Iniciar servicio
            'systemctl start docker',
            'systemctl enable docker'
        ]
        
        return self._execute_commands(commands)
    
    def _execute_commands(self, commands):
        """Ejecuta una lista de comandos"""
        for cmd in commands:
            print(f"\nEjecutando: {cmd[:60]}...")
            print("-" * 60)
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    text=True,
                    timeout=300
                )

                if result.returncode != 0:
                    print(f"\n[ERROR] El comando falló con código: {result.returncode}")
                    return False

                print("-" * 60)
                time.sleep(1)
            except subprocess.TimeoutExpired:
                print(f"\n[ERROR] Timeout ejecutando: {cmd}")
                return False
            except Exception as e:
                print(f"\n[ERROR] Excepción: {str(e)}")
                return False

        # Verificar instalacion
        time.sleep(3)
        if self.is_installed():
            print("\n" + "=" * 60)
            print("Docker instalado correctamente")
            print("=" * 60)
            return True
        else:
            print("\n" + "=" * 60)
            print("Docker no se instalo correctamente")
            print("=" * 60)
            return False
    
    def add_user_to_docker_group(self, username):
        """Agrega un usuario al grupo docker"""
        try:
            subprocess.run(
                f'usermod -aG docker {username}',
                shell=True,
                check=True
            )
            print(f"Usuario {username} agregado al grupo docker")
            return True
        except Exception as e:
            print(f"Error agregando usuario a grupo docker: {str(e)}")
            return False
