"""
Volume Manager Module
Gestiona los volumenes Docker
"""

import subprocess


class VolumeManager:
    """Gestiona volumenes Docker"""
    
    def __init__(self):
        self.volumes = [
            'mysql_data_testing',
            'mysql_data_production',
            'moodledata_testing',
            'moodledata_production'
        ]
    
    def create_volumes(self):
        """Crea los volumenes Docker necesarios"""
        for volume in self.volumes:
            if not self.volume_exists(volume):
                self._create_volume(volume)
            else:
                print(f"Volumen ya existe: {volume}")
        return True
    
    def volume_exists(self, volume_name):
        """Verifica si un volumen existe"""
        try:
            result = subprocess.run(
                f'docker volume ls --filter name={volume_name} --format "{{{{.Name}}}}"',
                shell=True,
                capture_output=True,
                text=True
            )
            return volume_name in result.stdout
        except Exception:
            return False
    
    def _create_volume(self, volume_name):
        """Crea un volumen Docker"""
        try:
            subprocess.run(
                f'docker volume create {volume_name}',
                shell=True,
                check=True
            )
            print(f"Volumen creado: {volume_name}")
            return True
        except Exception as e:
            print(f"Error creando volumen {volume_name}: {str(e)}")
            return False
    
    def remove_volumes(self):
        """Elimina todos los volumenes"""
        for volume in self.volumes:
            if self.volume_exists(volume):
                self._remove_volume(volume)
        return True
    
    def _remove_volume(self, volume_name):
        """Elimina un volumen Docker"""
        try:
            subprocess.run(
                f'docker volume rm {volume_name}',
                shell=True,
                check=True
            )
            print(f"Volumen eliminado: {volume_name}")
            return True
        except Exception as e:
            print(f"Error eliminando volumen {volume_name}: {str(e)}")
            return False
    
    def backup_volume(self, volume_name, backup_path):
        """Crea un backup de un volumen"""
        try:
            cmd = f"""docker run --rm \\
                -v {volume_name}:/source \\
                -v {backup_path}:/backup \\
                alpine tar czf /backup/{volume_name}.tar.gz -C /source .
            """
            subprocess.run(cmd, shell=True, check=True)
            print(f"Backup creado: {backup_path}/{volume_name}.tar.gz")
            return True
        except Exception as e:
            print(f"Error creando backup de {volume_name}: {str(e)}")
            return False
    
    def restore_volume(self, volume_name, backup_file):
        """Restaura un volumen desde un backup"""
        try:
            cmd = f"""docker run --rm \\
                -v {volume_name}:/target \\
                -v {backup_file}:/backup.tar.gz \\
                alpine sh -c "cd /target && tar xzf /backup.tar.gz"
            """
            subprocess.run(cmd, shell=True, check=True)
            print(f"Volumen restaurado: {volume_name}")
            return True
        except Exception as e:
            print(f"Error restaurando {volume_name}: {str(e)}")
            return False
