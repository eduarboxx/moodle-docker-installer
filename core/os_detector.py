"""
OS Detector Module
Detecta el sistema operativo y su version
"""

import platform
import subprocess


class OSDetector:
    """Detecta el sistema operativo"""
    
    def __init__(self):
        self.os_info = {}
    
    def detect(self):
        """Detecta el sistema operativo y retorna informacion"""
        system = platform.system()
        
        if system == "Linux":
            return self._detect_linux()
        else:
            raise Exception(f"Sistema operativo no soportado: {system}")
    
    def _detect_linux(self):
        """Detecta la distribucion de Linux"""
        try:
            # Intentar usar /etc/os-release primero
            with open('/etc/os-release', 'r') as f:
                os_release = {}
                for line in f:
                    if '=' in line:
                        key, value = line.rstrip().split('=', 1)
                        os_release[key] = value.strip('"')
            
            distro_id = os_release.get('ID', '').lower()
            distro_name = os_release.get('NAME', '')
            version = os_release.get('VERSION_ID', '')
            
            # Normalizar nombres de distribuciones
            if distro_id in ['ubuntu', 'debian']:
                family = 'debian'
            elif distro_id in ['rhel', 'centos', 'rocky', 'almalinux']:
                family = 'rhel'
            elif distro_id in ['arch', 'manjaro']:
                family = 'arch'
            else:
                family = 'unknown'
            
            return {
                'distro': distro_name,
                'distro_id': distro_id,
                'version': version,
                'family': family,
                'package_manager': self._get_package_manager(family)
            }
            
        except Exception as e:
            raise Exception(f"No se pudo detectar la distribucion de Linux: {str(e)}")
    
    def _get_package_manager(self, family):
        """Retorna el gestor de paquetes segun la familia"""
        package_managers = {
            'debian': 'apt',
            'rhel': 'dnf',
            'arch': 'pacman'
        }
        return package_managers.get(family, 'unknown')
    
    def is_supported(self):
        """Verifica si la distribucion es soportada"""
        try:
            info = self.detect()
            return info['family'] in ['debian', 'rhel', 'arch']
        except Exception:
            return False
