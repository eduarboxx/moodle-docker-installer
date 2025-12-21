"""
Backup Manager Module
Gestion de backups automaticos de Moodle
Integrado con scripts de backup y restore
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path


class BackupManager:
    """Gestiona backups de Moodle y MySQL usando scripts de shell"""

    def __init__(self, settings):
        self.settings = settings
        self.backup_path = settings.BACKUPS_PATH
        self.script_dir = Path(__file__).parent
        self.backup_script = self.script_dir / 'backup.sh'
        self.restore_script = self.script_dir / 'restore.sh'

    def _prepare_env_vars(self, environment):
        """Prepara variables de entorno para los scripts"""
        env_vars = os.environ.copy()

        # Solo pasar la ruta al archivo .env
        env_file = os.path.join(self.settings.BASE_PATH, '.env')
        if os.path.exists(env_file):
            env_vars['ENV_FILE'] = env_file
        else:
            # Fallback a la ruta por defecto
            env_vars['ENV_FILE'] = '/opt/docker-project/.env'

        return env_vars

    def create_backup(self, environment='testing'):
        """
        Crea un backup completo de un ambiente usando el script backup.sh

        Args:
            environment: 'testing' o 'production'

        Returns:
            True si el backup fue exitoso, False en caso contrario
        """
        print(f"\nCreando backup de {environment}...")

        if not self.backup_script.exists():
            print(f"Error: Script de backup no encontrado: {self.backup_script}")
            return False

        try:
            env_vars = self._prepare_env_vars(environment)

            # Ejecutar script de backup sin capturar output para mostrar en tiempo real
            # Esto permite que el usuario vea el progreso mientras se ejecuta
            result = subprocess.run(
                ['bash', str(self.backup_script), environment],
                env=env_vars,
                text=True
            )

            if result.returncode == 0:
                print(f"\nBackup de {environment} completado exitosamente")
                return True
            else:
                print(f"\nError en backup de {environment}")
                return False

        except Exception as e:
            print(f"Error ejecutando backup: {str(e)}")
            return False

    def restore_backup(self, environment, backup_timestamp):
        """
        Restaura un backup usando el script restore.sh

        Args:
            environment: 'testing' o 'production'
            backup_timestamp: Timestamp del backup a restaurar (ej: 2024-01-15_10-30-00)

        Returns:
            True si la restauración fue exitosa, False en caso contrario
        """
        print(f"\nRestaurando backup de {environment}: {backup_timestamp}")

        if not self.restore_script.exists():
            print(f"Error: Script de restore no encontrado: {self.restore_script}")
            return False

        # Verificar que el backup existe
        backup_dir = os.path.join(self.backup_path, environment, backup_timestamp)
        if not os.path.exists(backup_dir):
            print(f"Error: Backup no encontrado: {backup_dir}")
            return False

        try:
            env_vars = self._prepare_env_vars(environment)
            # Saltar confirmación en el script de bash ya que se hizo en Python
            env_vars['SKIP_CONFIRMATION'] = 'yes'

            # Ejecutar script de restore sin capturar output para mostrar en tiempo real
            # Esto permite que el usuario vea el progreso mientras se ejecuta
            result = subprocess.run(
                ['bash', str(self.restore_script), environment, backup_timestamp],
                env=env_vars,
                text=True
            )

            if result.returncode == 0:
                print(f"\nRestauración de {environment} completada exitosamente")
                return True
            else:
                print(f"\nError en restauración de {environment}")
                return False

        except Exception as e:
            print(f"Error ejecutando restore: {str(e)}")
            return False

    def list_backups(self, environment=None):
        """
        Lista los backups disponibles

        Args:
            environment: 'testing', 'production' o None para listar ambos

        Returns:
            Lista de timestamps de backups disponibles
        """
        if environment:
            backup_dir = os.path.join(self.backup_path, environment)
            if not os.path.exists(backup_dir):
                print(f"No hay backups para {environment}")
                return []

            backups = sorted(os.listdir(backup_dir), reverse=True)
            print(f"\nBackups disponibles de {environment}:")
            for i, backup in enumerate(backups, 1):
                backup_path = os.path.join(backup_dir, backup)
                size = self._get_dir_size(backup_path)
                print(f"  {i}. {backup} ({size})")
            return backups
        else:
            # Listar ambos ambientes
            testing_backups = self.list_backups('testing')
            production_backups = self.list_backups('production')
            return {'testing': testing_backups, 'production': production_backups}

    def _get_dir_size(self, path):
        """Obtiene el tamaño de un directorio en formato legible"""
        try:
            result = subprocess.run(
                ['du', '-sh', path],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.split()[0]
        except:
            pass
        return 'N/A'

    def clean_old_backups(self, environment, keep_last=None):
        """
        Elimina backups antiguos
        La limpieza se realiza automáticamente por el script de backup
        basándose en BACKUP_RETENTION_DAYS

        Args:
            environment: 'testing' o 'production'
            keep_last: Número de backups a mantener (ignorado, usa BACKUP_RETENTION_DAYS)
        """
        print(f"\nLimpieza de backups antiguos de {environment}")
        print(f"Los backups se mantienen por {self.settings.BACKUP_RETENTION_DAYS} días")
        print("La limpieza se ejecuta automáticamente durante el backup")
        return True

    def get_backup_info(self, environment, backup_timestamp):
        """
        Obtiene información detallada de un backup

        Args:
            environment: 'testing' o 'production'
            backup_timestamp: Timestamp del backup

        Returns:
            Dict con información del backup o None si no existe
        """
        backup_dir = os.path.join(self.backup_path, environment, backup_timestamp)
        if not os.path.exists(backup_dir):
            return None

        info = {
            'environment': environment,
            'timestamp': backup_timestamp,
            'path': backup_dir,
            'size': self._get_dir_size(backup_dir),
            'files': []
        }

        # Listar archivos del backup
        for file in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, file)
            file_size = self._get_dir_size(file_path) if os.path.isfile(file_path) else 'N/A'
            info['files'].append({
                'name': file,
                'size': file_size
            })

        return info
