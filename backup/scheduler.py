"""
Scheduler Module
Gestion de tareas programadas para backups usando cron
"""

import os
import subprocess
from pathlib import Path
import tempfile


class BackupScheduler:
    """Gestiona tareas programadas de backups usando crontab"""

    def __init__(self, settings):
        self.settings = settings
        self.script_dir = Path(__file__).parent
        self.backup_script = self.script_dir / 'backup.sh'

    def _get_current_crontab(self):
        """Obtiene el contenido actual del crontab"""
        try:
            result = subprocess.run(
                ['crontab', '-l'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout
            else:
                return ""
        except Exception:
            return ""

    def _write_crontab(self, content):
        """Escribe el contenido al crontab"""
        try:
            # Verificar que crontab esté disponible
            import shutil
            if not shutil.which('crontab'):
                print("Error: El comando 'crontab' no está disponible")
                print("Instala cron/cronie según tu distribución:")
                print("  - Ubuntu/Debian: sudo apt install cron")
                print("  - Rocky/RHEL:    sudo yum install cronie")
                print("  - Arch Linux:    sudo pacman -S cronie")
                return False

            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(content)
                temp_file = f.name

            # Cargar el crontab desde el archivo temporal
            result = subprocess.run(
                ['crontab', temp_file],
                capture_output=True,
                text=True
            )

            # Eliminar archivo temporal
            os.unlink(temp_file)

            if result.returncode != 0 and result.stderr:
                print(f"Error de crontab: {result.stderr}")

            return result.returncode == 0
        except FileNotFoundError:
            print("Error: El comando 'crontab' no está disponible")
            print("Instala cron/cronie según tu distribución")
            return False
        except Exception as e:
            print(f"Error escribiendo crontab: {str(e)}")
            return False

    def _get_env_file_path(self):
        """Obtiene la ruta al archivo .env"""
        # Buscar el .env en el directorio base del proyecto
        env_file = os.path.join(self.settings.BASE_PATH, '.env')
        if os.path.exists(env_file):
            return env_file

        # Fallback: usar la ruta por defecto
        return '/opt/docker-project/.env'

    def setup_cron(self, environment='testing', schedule='0 2 * * *'):
        """
        Configura tarea cron para backups automaticos

        Args:
            environment: 'testing' o 'production'
            schedule: Expresión cron (default: 2 AM diario)

        Returns:
            True si se configuró correctamente
        """
        print(f"\nConfigurando backup automatico para {environment}")
        print(f"Horario: {schedule}")

        if not self.backup_script.exists():
            print(f"Error: Script de backup no encontrado: {self.backup_script}")
            return False

        # Obtener crontab actual
        current_crontab = self._get_current_crontab()

        # Identificador único para esta tarea
        job_id = f"moodle-backup-{environment}"

        # Eliminar entrada anterior si existe
        lines = current_crontab.split('\n') if current_crontab else []
        # Filtrar líneas vacías y la entrada anterior
        new_lines = [line for line in lines if line.strip() and job_id not in line]

        # Preparar comando con ruta al archivo .env
        env_file = self._get_env_file_path()
        command = f"ENV_FILE='{env_file}' bash {self.backup_script} {environment}"

        # Agregar nueva entrada
        new_entry = f"{schedule} {command} # {job_id}"
        new_lines.append(new_entry)

        # Escribir nuevo crontab (debe terminar con newline)
        new_crontab = '\n'.join(new_lines) + '\n'

        if self._write_crontab(new_crontab):
            print(f"Backup automatico configurado exitosamente para {environment}")
            print(f"Comando: {new_entry}")
            return True
        else:
            print("Error configurando crontab")
            return False

    def remove_cron(self, environment):
        """
        Elimina tarea cron de backups

        Args:
            environment: 'testing' o 'production'

        Returns:
            True si se eliminó correctamente
        """
        print(f"\nEliminando backup automatico de {environment}")

        # Obtener crontab actual
        current_crontab = self._get_current_crontab()

        if not current_crontab:
            print("No hay tareas cron configuradas")
            return True

        # Identificador único para esta tarea
        job_id = f"moodle-backup-{environment}"

        # Filtrar líneas que no contengan el job_id y líneas vacías
        lines = current_crontab.split('\n')
        new_lines = [line for line in lines if line.strip() and job_id not in line]

        # Verificar si se eliminó algo
        original_jobs = [line for line in lines if job_id in line]
        if not original_jobs:
            print(f"No hay backup automatico configurado para {environment}")
            return True

        # Escribir nuevo crontab (debe terminar con newline si no está vacío)
        new_crontab = '\n'.join(new_lines) + '\n' if new_lines else ''

        if self._write_crontab(new_crontab):
            print(f"Backup automatico de {environment} eliminado exitosamente")
            return True
        else:
            print("Error eliminando entrada de crontab")
            return False

    def list_scheduled_backups(self):
        """
        Lista las tareas programadas de backups

        Returns:
            True si se listaron correctamente
        """
        try:
            current_crontab = self._get_current_crontab()

            if not current_crontab:
                print("\nNo hay tareas cron configuradas")
                return True

            # Filtrar solo las tareas de moodle-backup
            lines = current_crontab.split('\n')
            backup_lines = [line for line in lines if 'moodle-backup' in line]

            if backup_lines:
                print("\nTareas de backup programadas:")
                print("-" * 80)
                for line in backup_lines:
                    print(f"  {line}")
                print("-" * 80)
            else:
                print("\nNo hay tareas de backup programadas")

            return True
        except Exception as e:
            print(f"Error listando tareas: {str(e)}")
            return False

