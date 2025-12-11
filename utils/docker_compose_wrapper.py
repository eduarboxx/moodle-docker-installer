"""
Docker Compose Wrapper Module
Detecta y usa automaticamente la version correcta de docker compose
"""

import subprocess


class DockerComposeWrapper:
    """Wrapper para usar docker compose o docker-compose automaticamente"""

    _compose_command = None  # Cache del comando detectado

    @classmethod
    def get_compose_command(cls):
        """
        Detecta y retorna el comando correcto de docker compose

        Returns:
            list: Comando como lista (ej: ['docker', 'compose'] o ['docker-compose'])
        """
        if cls._compose_command is not None:
            return cls._compose_command

        # Intentar con docker compose (plugin moderno)
        try:
            result = subprocess.run(
                ['docker', 'compose', 'version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                cls._compose_command = ['docker', 'compose']
                return cls._compose_command
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Intentar con docker-compose (standalone antiguo)
        try:
            result = subprocess.run(
                ['docker-compose', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                cls._compose_command = ['docker-compose']
                return cls._compose_command
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Si no se encuentra ninguno, usar docker compose por defecto
        cls._compose_command = ['docker', 'compose']
        return cls._compose_command

    @classmethod
    def get_compose_command_string(cls):
        """
        Retorna el comando como string para usar en shell

        Returns:
            str: Comando como string (ej: 'docker compose' o 'docker-compose')
        """
        return ' '.join(cls.get_compose_command())

    @classmethod
    def run_compose(cls, args, cwd=None, **kwargs):
        """
        Ejecuta un comando de docker compose

        Args:
            args (list or str): Argumentos para el comando compose
            cwd (str): Directorio de trabajo
            **kwargs: Argumentos adicionales para subprocess.run

        Returns:
            subprocess.CompletedProcess: Resultado de la ejecucion
        """
        compose_cmd = cls.get_compose_command()

        # Si args es string, convertirlo a lista
        if isinstance(args, str):
            args = args.split()

        # Construir comando completo
        full_cmd = compose_cmd + args

        # Ejecutar comando
        return subprocess.run(full_cmd, cwd=cwd, **kwargs)

    @classmethod
    def run_compose_shell(cls, args_str, cwd=None, **kwargs):
        """
        Ejecuta un comando de docker compose usando shell
        Util cuando se necesita usar pipes, redirects, etc.

        Args:
            args_str (str): Argumentos como string
            cwd (str): Directorio de trabajo
            **kwargs: Argumentos adicionales para subprocess.run

        Returns:
            subprocess.CompletedProcess: Resultado de la ejecucion
        """
        compose_cmd_str = cls.get_compose_command_string()
        full_cmd = f"{compose_cmd_str} {args_str}"

        return subprocess.run(full_cmd, shell=True, cwd=cwd, **kwargs)

    @classmethod
    def is_compose_available(cls):
        """
        Verifica si docker compose esta disponible

        Returns:
            bool: True si esta disponible
        """
        try:
            compose_cmd = cls.get_compose_command()
            result = subprocess.run(
                compose_cmd + ['version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    @classmethod
    def reset_cache(cls):
        """Resetea el cache del comando detectado"""
        cls._compose_command = None
