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

            return result.returncode == 0
        except Exception as e:
            print(f"Error escribiendo crontab: {str(e)}")
            return False

    def _get_env_exports(self, environment):
        """Genera las variables de entorno necesarias para el cron"""
        env_prefix = 'TEST' if environment == 'testing' else 'PROD'

        exports = [
            f"export BACKUP_BASE_PATH='{self.settings.BACKUPS_PATH}'",
            f"export BACKUP_RETENTION_DAYS='{self.settings.BACKUP_RETENTION_DAYS}'",
            f"export DB_NAME='{self.settings.get_env_var(f'{env_prefix}_DB_NAME')}'",
            f"export DB_USER='{self.settings.get_env_var(f'{env_prefix}_DB_USER')}'",
            f"export DB_PASS='{self.settings.get_env_var(f'{env_prefix}_DB_PASS')}'",
            f"export DB_ROOT_PASS='{self.settings.get_env_var(f'{env_prefix}_DB_ROOT_PASS')}'",
        ]

        # Agregar variables de email si están configuradas
        if self.settings.BACKUP_EMAIL_TO:
            exports.append(f"export BACKUP_EMAIL_TO='{self.settings.BACKUP_EMAIL_TO}'")
        if self.settings.SMTP_USER:
            exports.append(f"export SMTP_USER='{self.settings.SMTP_USER}'")
        if self.settings.SMTP_PASSWORD:
            exports.append(f"export SMTP_PASSWORD='{self.settings.SMTP_PASSWORD}'")
        if self.settings.SMTP_SERVER:
            exports.append(f"export SMTP_SERVER='{self.settings.SMTP_SERVER}'")
        if self.settings.SMTP_PORT:
            exports.append(f"export SMTP_PORT='{self.settings.SMTP_PORT}'")

        return ' && '.join(exports)

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
        lines = current_crontab.split('\n')
        new_lines = [line for line in lines if job_id not in line]

        # Preparar comando con exports
        env_exports = self._get_env_exports(environment)
        command = f"{env_exports} && bash {self.backup_script} {environment}"

        # Agregar nueva entrada
        new_entry = f"{schedule} {command} # {job_id}"
        new_lines.append(new_entry)

        # Escribir nuevo crontab
        new_crontab = '\n'.join(new_lines)

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

        # Filtrar líneas que no contengan el job_id
        lines = current_crontab.split('\n')
        new_lines = [line for line in lines if job_id not in line]

        # Verificar si se eliminó algo
        if len(lines) == len(new_lines):
            print(f"No hay backup automatico configurado para {environment}")
            return True

        # Escribir nuevo crontab
        new_crontab = '\n'.join(new_lines)

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

    def get_recommended_schedules(self):
        """
        Muestra horarios recomendados para backups

        Returns:
            Dict con horarios recomendados
        """
        schedules = {
            'daily_2am': {
                'cron': '0 2 * * *',
                'description': 'Diario a las 2:00 AM'
            },
            'daily_3am': {
                'cron': '0 3 * * *',
                'description': 'Diario a las 3:00 AM'
            },
            'weekly_sunday': {
                'cron': '0 2 * * 0',
                'description': 'Semanal los domingos a las 2:00 AM'
            },
            'twice_daily': {
                'cron': '0 2,14 * * *',
                'description': 'Dos veces al día (2:00 AM y 2:00 PM)'
            },
            'every_6_hours': {
                'cron': '0 */6 * * *',
                'description': 'Cada 6 horas'
            }
        }

        print("\nHorarios recomendados para backups:")
        print("-" * 80)
        for key, value in schedules.items():
            print(f"  {key:20s} -> {value['cron']:15s} ({value['description']})")
        print("-" * 80)

        return schedules
