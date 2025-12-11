#!/usr/bin/env python3
"""
Moodle Docker Infrastructure Installer
Instalador automatizado de infraestructura Moodle con Docker
Soporta: Ubuntu/Debian, Rocky Linux/RHEL, Arch Linux

Autor: Eduardo Valdés
"""

import sys
import os
from pathlib import Path

# Agregar el directorio actual al path para imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import Logger
from core.os_detector import OSDetector
from core.docker_installer import DockerInstaller
from core.directory_manager import DirectoryManager
from core.moodle_downloader import MoodleDownloader
from docker.compose_generator import ComposeGenerator
from docker.dockerfile_generator import DockerfileGenerator
from nginx.config_generator import NginxConfigGenerator
from config.settings import Settings
from utils.validator import Validator
from utils.rollback import RollbackManager
from utils.docker_compose_wrapper import DockerComposeWrapper
from backup.backup_manager import BackupManager
from backup.scheduler import BackupScheduler
import time

class MoodleDockerInstaller:
    """Clase principal del instalador"""
    
    def __init__(self):
        self.logger = Logger()
        self.settings = Settings()
        self.validator = Validator()
        self.rollback = RollbackManager()
        
    def show_banner(self):
        """Muestra el banner de inicio"""
        banner = """
===============================================================
                                                               
        MOODLE DOCKER INFRASTRUCTURE INSTALLER v1.0            
                                                               
  Instalador automatizado de Moodle con Docker                
  Soporta: Ubuntu/Debian, Rocky/RHEL, Arch Linux              
                                                               
===============================================================
        """
        print(banner)
        
    def show_menu(self):
        """Muestra el menú principal"""
        menu = """
===============================================================
                       MENU PRINCIPAL                          
===============================================================
                                                               
  1. Instalar infraestructura completa                         
                                                               
  2. Gestionar ambientes                                       
     - Levantar/Detener Testing                                
     - Levantar/Detener Produccion                             
     - Ver estado de servicios                                 
                                                               
  3. Ver logs                                                  
                                                               
  4. Gestionar backups                                         
     - Configurar backup automatico                            
     - Ejecutar backup manual                                  
     - Restaurar backup                                        
                                                               
  5. Desinstalar todo                                          
                                                               
  0. Salir                                                     
                                                               
===============================================================
        """
        print(menu)
        
    def full_installation(self):
        """Instalacion completa automatizada"""
        self.logger.info("Iniciando instalacion completa...")
        
        try:
            # 1. Detectar sistema operativo
            self.logger.info("Detectando sistema operativo...")
            os_detector = OSDetector()
            os_info = os_detector.detect()
            self.logger.success(f"Sistema detectado: {os_info['distro']} {os_info['version']}")
            
            # 2. Validar permisos de root
            self.logger.info("Validando permisos...")
            if not self.validator.check_root():
                self.logger.error("Este script requiere permisos de root/sudo")
                return False
            self.logger.success("Permisos validados")
            
            # 3. Instalar Docker si no existe
            self.logger.info("Verificando Docker...")
            docker_installer = DockerInstaller(os_info)
            if not docker_installer.is_installed():
                self.logger.warning("Docker no encontrado. Instalando...")
                if not docker_installer.install():
                    self.logger.error("Error al instalar Docker")
                    return False
                self.logger.success("Docker instalado correctamente")
            else:
                self.logger.success("Docker ya esta instalado")
            
            # 4. Crear estructura de directorios
            self.logger.info("Creando estructura de directorios...")
            dir_manager = DirectoryManager(self.settings.BASE_PATH)
            if not dir_manager.create_structure():
                self.logger.error("Error al crear estructura de directorios")
                return False
            self.logger.success("Estructura de directorios creada")
            
            # 5. Descargar Moodle
            self.logger.info(f"Descargando Moodle {self.settings.MOODLE_VERSION}...")
            moodle_downloader = MoodleDownloader(
                version=self.settings.MOODLE_VERSION,
                target_path=self.settings.MOODLE_PATH
            )
            if not moodle_downloader.download():
                self.logger.error("Error al descargar Moodle")
                return False
            self.logger.success("Moodle descargado correctamente")
            
            # 6. Generar archivos .env
            self.logger.info("Generando archivo .env...")
            if not self.settings.generate_env_file():
                self.logger.error("Error al generar archivo .env")
                return False
            self.logger.success("Archivo .env generado")
            
            # 7. Generar Dockerfiles
            self.logger.info("Generando Dockerfiles...")
            dockerfile_gen = DockerfileGenerator(self.settings)
            if not dockerfile_gen.generate_all():
                self.logger.error("Error al generar Dockerfiles")
                return False
            self.logger.success("Dockerfiles generados")
            
            # 8. Generar docker-compose.yml
            self.logger.info("Generando docker-compose.yml...")
            compose_gen = ComposeGenerator(self.settings)
            if not compose_gen.generate():
                self.logger.error("Error al generar docker-compose.yml")
                return False
            self.logger.success("docker-compose.yml generado")
            
            # 9. Generar configuraciones Nginx (sin SSL todavia)
            self.logger.info("Generando configuraciones Nginx...")
            nginx_gen = NginxConfigGenerator(self.settings)
            if not nginx_gen.generate_all():
                self.logger.error("Error al generar configuraciones Nginx")
                return False
            self.logger.success("Configuraciones Nginx generadas")

            # 10. Preguntar que ambiente levantar
            print("\nQue ambiente deseas levantar?")
            print("1. Testing")
            print("2. Produccion")
            print("3. Ambos")
            print("4. Ninguno (solo instalar)")

            choice = input("\nSelecciona una opcion (1-4): ").strip()

            environments_to_start = []
            if choice in ['1', '3']:
                environments_to_start.append('testing')
            if choice in ['2', '3']:
                environments_to_start.append('production')

            # 11. Levantar contenedores seleccionados
            for env in environments_to_start:
                self.logger.info(f"Levantando ambiente {env.capitalize()}...")
                if not self._start_environment(env):
                    self.logger.error(f"Error al levantar ambiente {env.capitalize()}")
                else:
                    self.logger.success(f"Ambiente {env.capitalize()} iniciado")

            # 12. Configurar SSL solo para los ambientes levantados
            for env in environments_to_start:
                self.logger.info(f"Configurando SSL para {env.capitalize()}...")
                if not nginx_gen.setup_ssl_for_environment(env):
                    self.logger.error(f"Error al configurar SSL para {env.capitalize()}")
                else:
                    self.logger.success(f"SSL configurado para {env.capitalize()}")

                    # Aplicar configuracion SSL a Moodle si el contenedor esta corriendo
                    self._apply_ssl_to_moodle(env)
            
            # Configurar backups automaticos
            self._setup_automatic_backups()

            # Mostrar resumen final
            self._show_installation_summary()

            self.logger.success("\nInstalacion completada exitosamente!")
            return True
            
        except Exception as e:
            self.logger.error(f"Error durante la instalacion: {str(e)}")
            self.logger.info("Ejecutando rollback...")
            self.rollback.execute()
            return False
    
    def _start_environment(self, env_name):
        """Inicia un ambiente especifico"""
        try:
            # Map environment to specific services
            services_map = {
                'testing': 'mysql_testing moodle_testing nginx',
                'production': 'mysql_production moodle_production nginx'
            }

            services = services_map.get(env_name, env_name)
            compose_cmd = DockerComposeWrapper.get_compose_command_string()

            self.logger.info(f"Ejecutando: {compose_cmd} up -d {services}")
            print("Iniciando contenedores Docker...")
            result = DockerComposeWrapper.run_compose_shell(
                f"up -d {services}",
                cwd=self.settings.BASE_PATH
            )

            if result.returncode != 0:
                self.logger.error("Error al iniciar los contenedores Docker")
                return False

            return True
        except Exception as e:
            self.logger.error(f"Error al iniciar ambiente {env_name}: {str(e)}")
            return False

    def _apply_ssl_to_moodle(self, environment):
        """Aplica configuracion SSL a Moodle si ya esta instalado"""
        import subprocess

        try:
            container_name = f"moodle_{environment}"
            ssl_config_file = os.path.join(
                self.settings.BASE_PATH,
                environment,
                'moodle_config',
                'ssl_config.php'
            )

            # Verificar que el archivo de configuracion SSL exista
            if not os.path.exists(ssl_config_file):
                self.logger.warning(f"No se encontro archivo de configuracion SSL para {environment}")
                return False

            # Verificar que el contenedor este corriendo
            check_container = subprocess.run(
                ['docker', 'ps', '--filter', f'name={container_name}', '--format', '{{.Names}}'],
                capture_output=True,
                text=True
            )

            if container_name not in check_container.stdout:
                self.logger.warning(f"Contenedor {container_name} no esta corriendo")
                return False

            # Verificar si Moodle ya esta instalado
            check_config = subprocess.run(
                ['docker', 'exec', container_name, 'test', '-f', '/var/www/html/config.php'],
                capture_output=True
            )

            if check_config.returncode != 0:
                # Moodle aun no esta instalado, la configuracion se aplicara durante la instalacion
                self.logger.info(f"Moodle en {environment} aun no esta instalado")
                self.logger.info("La configuracion SSL se aplicara automaticamente durante la instalacion")
                return True

            # Verificar si la configuracion SSL ya esta aplicada
            check_ssl = subprocess.run(
                ['docker', 'exec', container_name, 'grep', '-q', 'sslproxy', '/var/www/html/config.php'],
                capture_output=True
            )

            if check_ssl.returncode == 0:
                self.logger.info(f"Configuracion SSL ya esta aplicada en {environment}")
                return True

            # Aplicar configuracion SSL
            self.logger.info(f"Aplicando configuracion SSL a Moodle en {environment}...")

            # Copiar archivo al contenedor
            subprocess.run(
                ['docker', 'cp', ssl_config_file, f'{container_name}:/tmp/ssl_config.php'],
                check=True
            )

            # Agregar configuracion al config.php
            subprocess.run(
                ['docker', 'exec', container_name, 'bash', '-c',
                 'cat /tmp/ssl_config.php >> /var/www/html/config.php'],
                check=True
            )

            # Eliminar archivo temporal
            subprocess.run(
                ['docker', 'exec', container_name, 'rm', '/tmp/ssl_config.php'],
                check=True
            )

            # Limpiar cache de Moodle
            subprocess.run(
                ['docker', 'exec', container_name, 'php', '/var/www/html/admin/cli/purge_caches.php'],
                capture_output=True
            )

            # Reiniciar contenedor para aplicar cambios
            subprocess.run(['docker', 'restart', container_name], capture_output=True)

            self.logger.success(f"Configuracion SSL aplicada a Moodle en {environment}")
            return True

        except Exception as e:
            self.logger.warning(f"Error al aplicar SSL a Moodle en {environment}: {str(e)}")
            return False
    
    def _show_installation_summary(self):
        """Muestra resumen de la instalacion"""
        import socket

        # Función auxiliar para obtener IP del host
        def get_host_ip():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
                return ip
            except Exception:
                return "localhost"

        # Determinar URLs a mostrar
        test_url = self.settings.get_env_var('TEST_URL')
        prod_url = self.settings.get_env_var('PROD_URL')

        default_urls = ['https://test.moodle.local', 'https://moodle.local',
                       'http://test.moodle.local', 'http://moodle.local']

        # Si es URL por defecto, mostrar acceso por IP
        if test_url in default_urls or not test_url:
            host_ip = get_host_ip()
            test_http_port = self.settings.get_env_var('TEST_HTTP_PORT')
            test_https_port = self.settings.get_env_var('TEST_HTTPS_PORT')
            test_access = f"http://{host_ip}:{test_http_port} o https://{host_ip}:{test_https_port}"
        else:
            test_access = test_url

        if prod_url in default_urls or not prod_url:
            host_ip = get_host_ip()
            prod_http_port = self.settings.get_env_var('PROD_HTTP_PORT')
            prod_https_port = self.settings.get_env_var('PROD_HTTPS_PORT')
            prod_access = f"http://{host_ip}:{prod_http_port} o https://{host_ip}:{prod_https_port}"
        else:
            prod_access = prod_url

        summary = f"""
===============================================================
                    RESUMEN DE INSTALACION
===============================================================

Ruta de instalacion: {self.settings.BASE_PATH}
Version de Moodle: {self.settings.MOODLE_VERSION}

AMBIENTE TESTING:
Acceso: {test_access}
Puerto HTTP: {self.settings.get_env_var('TEST_HTTP_PORT')}
Puerto HTTPS: {self.settings.get_env_var('TEST_HTTPS_PORT')}

AMBIENTE PRODUCCION:
Acceso: {prod_access}
Puerto HTTP: {self.settings.get_env_var('PROD_HTTP_PORT')}
Puerto HTTPS: {self.settings.get_env_var('PROD_HTTPS_PORT')}

CREDENCIALES:
Las credenciales se encuentran en: {self.settings.BASE_PATH}/.env

PROXIMOS PASOS:
1. Revisar el archivo .env y ajustar las URLs si es necesario
2. Acceder a las URLs mostradas arriba para completar la configuracion de Moodle
3. (Opcional) Configurar DNS/hosts si deseas usar nombres de dominio personalizados

===============================================================
        """
        print(summary)
    
    def manage_environments(self):
        """Menu de gestion de ambientes"""
        while True:
            menu = """
===============================================================
                    GESTION DE AMBIENTES
===============================================================

  1. Levantar Testing
  2. Detener Testing
  3. Levantar Produccion
  4. Detener Produccion
  5. Ver estado de servicios
  6. Reiniciar Testing
  7. Reiniciar Produccion
  
  0. Volver al menu principal

===============================================================
            """
            print(menu)
            choice = input("Selecciona una opcion: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self._manage_environment_action('testing', 'up')
            elif choice == '2':
                self._manage_environment_action('testing', 'down')
            elif choice == '3':
                self._manage_environment_action('production', 'up')
            elif choice == '4':
                self._manage_environment_action('production', 'down')
            elif choice == '5':
                self._show_services_status()
            elif choice == '6':
                self._manage_environment_action('testing', 'restart')
            elif choice == '7':
                self._manage_environment_action('production', 'restart')
            else:
                print("Opcion invalida")
    
    def _manage_environment_action(self, env, action):
        """Ejecuta una accion sobre un ambiente"""
        actions_map = {
            'up': 'up -d',
            'down': 'down',
            'restart': 'restart'
        }

        try:
            self.logger.info(f"Ejecutando {action} en {env}...")

            # Map environment to specific services if necessary
            services_map = {
                'testing': 'mysql_testing moodle_testing',
                'production': 'mysql_production moodle_production'
            }
            target = services_map.get(env, env)

            # Si es 'up', incluir nginx; si es 'down', solo detener servicios del ambiente
            if action == 'up':
                target += ' nginx'

            result = DockerComposeWrapper.run_compose_shell(
                f"{actions_map[action]} {target}",
                cwd=self.settings.BASE_PATH,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                self.logger.success(f"Accion {action} ejecutada exitosamente en {env}")

                # Si es 'up', verificar y configurar SSL si es necesario
                if action == 'up':
                    self._check_and_setup_ssl(env)
            else:
                self.logger.error(f"Error al ejecutar {action} en {env}: {result.stderr}")
        except Exception as e:
            self.logger.error(f"Error: {str(e)}")

    def _check_and_setup_ssl(self, environment):
        """Verifica y configura SSL si no existe para un ambiente"""
        import os

        try:
            ssl_cert_path = os.path.join(
                self.settings.NGINX_PATH,
                'ssl',
                f'{environment}.crt'
            )

            # Verificar si ya existe certificado SSL
            if os.path.exists(ssl_cert_path):
                self.logger.info(f"SSL ya configurado para {environment}")
                return

            # Configurar SSL
            self.logger.info(f"Configurando SSL para {environment}...")
            from nginx.config_generator import NginxConfigGenerator
            nginx_gen = NginxConfigGenerator(self.settings)

            if nginx_gen.setup_ssl_for_environment(environment):
                self.logger.success(f"SSL configurado exitosamente para {environment}")

                # Aplicar configuracion SSL a Moodle
                self._apply_ssl_to_moodle(environment)
            else:
                self.logger.warning(f"No se pudo configurar SSL para {environment}")

        except Exception as e:
            self.logger.warning(f"Error verificando SSL para {environment}: {str(e)}")
    
    def _show_services_status(self):
        """Muestra el estado de los servicios"""
        try:
            result = DockerComposeWrapper.run_compose_shell(
                "ps",
                cwd=self.settings.BASE_PATH,
                capture_output=True,
                text=True
            )
            print("\n" + result.stdout)
        except Exception as e:
            self.logger.error(f"Error al obtener estado: {str(e)}")
    
    def view_logs(self):
        """Menu de visualizacion de logs"""
        while True:
            menu = """
===============================================================
                        VER LOGS
===============================================================

  1. Logs de Testing (todos los servicios)
  2. Logs de Produccion (todos los servicios)
  3. Logs de Testing - Solo Moodle
  4. Logs de Testing - Solo MySQL
  5. Logs de Testing - Solo Nginx
  6. Logs de Produccion - Solo Moodle
  7. Logs de Produccion - Solo MySQL
  8. Logs de Produccion - Solo Nginx

  0. Volver al menu principal

===============================================================
            """
            print(menu)
            choice = input("Selecciona una opcion: ").strip()

            if choice == '0':
                break
            elif choice == '1':
                self._show_logs('testing')
            elif choice == '2':
                self._show_logs('production')
            elif choice == '3':
                self._show_logs('testing', 'moodle_testing')
            elif choice == '4':
                self._show_logs('testing', 'mysql_testing')
            elif choice == '5':
                self._show_logs('testing', 'nginx_testing')
            elif choice == '6':
                self._show_logs('production', 'moodle_production')
            elif choice == '7':
                self._show_logs('production', 'mysql_production')
            elif choice == '8':
                self._show_logs('production', 'nginx_production')
            else:
                print("Opcion invalida")
    
    def _show_logs(self, env, service=None):
        """Muestra logs de un servicio"""
        try:
            service_flag = f" {service}" if service else ""

            print(f"\nMostrando logs (Ctrl+C para salir)...\n")
            DockerComposeWrapper.run_compose_shell(
                f"logs --tail=100 -f{service_flag}",
                cwd=self.settings.BASE_PATH
            )
        except KeyboardInterrupt:
            print("\n")
        except Exception as e:
            self.logger.error(f"Error al mostrar logs: {str(e)}")
    
    def manage_backups(self):
        """Menu de gestion de backups"""
        # Cargar configuración del .env si existe
        self.settings.load_env_file()

        backup_mgr = BackupManager(self.settings)
        scheduler = BackupScheduler(self.settings)

        while True:
            menu = """
===============================================================
                    GESTION DE BACKUPS
===============================================================

  1. Crear backup manual (Testing)
  2. Crear backup manual (Produccion)
  3. Listar backups disponibles
  4. Restaurar backup (Testing)
  5. Restaurar backup (Produccion)

  6. Configurar backup automatico (Testing)
  7. Configurar backup automatico (Produccion)
  8. Ver tareas programadas
  9. Eliminar backup automatico

  10. Configurar notificaciones por email
  11. Ver informacion detallada de un backup

  0. Volver al menu principal

===============================================================
            """
            print(menu)
            choice = input("Selecciona una opcion: ").strip()

            if choice == '0':
                break
            elif choice == '1':
                self._create_backup(backup_mgr, 'testing')
            elif choice == '2':
                self._create_backup(backup_mgr, 'production')
            elif choice == '3':
                self._list_backups(backup_mgr)
            elif choice == '4':
                self._restore_backup(backup_mgr, 'testing')
            elif choice == '5':
                self._restore_backup(backup_mgr, 'production')
            elif choice == '6':
                self._configure_automatic_backup(scheduler, 'testing')
            elif choice == '7':
                self._configure_automatic_backup(scheduler, 'production')
            elif choice == '8':
                self._show_scheduled_backups(scheduler)
            elif choice == '9':
                self._remove_automatic_backup(scheduler)
            elif choice == '10':
                self._configure_email_notifications()
            elif choice == '11':
                self._show_backup_info(backup_mgr)
            else:
                print("Opcion invalida")

    def _create_backup(self, backup_mgr, environment):
        """Crea un backup manual"""
        print(f"\n=== Crear Backup de {environment.upper()} ===")
        print("Este proceso puede tardar varios minutos dependiendo del tamaño de los datos.")

        confirm = input(f"\nCrear backup de {environment}? (s/N): ").strip().lower()
        if confirm != 's':
            print("Backup cancelado")
            return

        self.logger.info(f"Creando backup de {environment}...")
        if backup_mgr.create_backup(environment):
            self.logger.success(f"Backup de {environment} creado exitosamente")
        else:
            self.logger.error(f"Error al crear backup de {environment}")

        input("\nPresiona Enter para continuar...")

    def _list_backups(self, backup_mgr):
        """Lista todos los backups disponibles"""
        print("\n=== Backups Disponibles ===\n")
        backup_mgr.list_backups()
        input("\nPresiona Enter para continuar...")

    def _restore_backup(self, backup_mgr, environment):
        """Restaura un backup"""
        print(f"\n=== Restaurar Backup de {environment.upper()} ===")

        # Listar backups disponibles
        backups = backup_mgr.list_backups(environment)

        if not backups:
            print(f"\nNo hay backups disponibles para {environment}")
            input("\nPresiona Enter para continuar...")
            return

        print("\nIngresa el timestamp del backup a restaurar")
        print("(Ejemplo: 2024-01-15_10-30-00)")
        timestamp = input("\nTimestamp: ").strip()

        if not timestamp:
            print("Timestamp invalido")
            input("\nPresiona Enter para continuar...")
            return

        print("\n*** ADVERTENCIA ***")
        print("Esta operacion ELIMINARA todos los datos actuales")
        print("y los reemplazara con los del backup especificado.")
        print("\nSe recomienda crear un backup antes de restaurar.")

        confirm = input("\nEstas seguro? Escribe 'SI' para confirmar: ").strip()
        if confirm != 'SI':
            print("Restauracion cancelada")
            input("\nPresiona Enter para continuar...")
            return

        self.logger.info(f"Restaurando backup de {environment}: {timestamp}")
        if backup_mgr.restore_backup(environment, timestamp):
            self.logger.success(f"Backup restaurado exitosamente")
        else:
            self.logger.error(f"Error al restaurar backup")

        input("\nPresiona Enter para continuar...")

    def _configure_automatic_backup(self, scheduler, environment):
        """Configura backup automatico"""
        print(f"\n=== Configurar Backup Automatico para {environment.upper()} ===")

        # Mostrar horarios recomendados
        schedules = scheduler.get_recommended_schedules()

        print("\nIngresa la expresion cron o selecciona una opcion:")
        print("Ejemplos de expresiones cron:")
        print("  0 2 * * *     -> Diario a las 2:00 AM")
        print("  0 3 * * 0     -> Semanal los domingos a las 3:00 AM")
        print("  0 */6 * * *   -> Cada 6 horas")

        schedule = input("\nExpresion cron [0 2 * * *]: ").strip()
        if not schedule:
            schedule = '0 2 * * *'

        self.logger.info(f"Configurando backup automatico para {environment}")
        if scheduler.setup_cron(environment, schedule):
            self.logger.success(f"Backup automatico configurado para {environment}")
            print(f"\nEl backup se ejecutara: {schedule}")
        else:
            self.logger.error("Error al configurar backup automatico")

        input("\nPresiona Enter para continuar...")

    def _show_scheduled_backups(self, scheduler):
        """Muestra las tareas programadas"""
        print("\n=== Tareas de Backup Programadas ===\n")
        scheduler.list_scheduled_backups()
        input("\nPresiona Enter para continuar...")

    def _remove_automatic_backup(self, scheduler):
        """Elimina un backup automatico"""
        print("\n=== Eliminar Backup Automatico ===")
        print("\n1. Testing")
        print("2. Produccion")
        print("0. Cancelar")

        choice = input("\nSelecciona el ambiente: ").strip()

        if choice == '1':
            env = 'testing'
        elif choice == '2':
            env = 'production'
        else:
            print("Cancelado")
            input("\nPresiona Enter para continuar...")
            return

        confirm = input(f"\nEliminar backup automatico de {env}? (s/N): ").strip().lower()
        if confirm != 's':
            print("Cancelado")
            input("\nPresiona Enter para continuar...")
            return

        self.logger.info(f"Eliminando backup automatico de {env}")
        if scheduler.remove_cron(env):
            self.logger.success(f"Backup automatico de {env} eliminado")
        else:
            self.logger.error("Error al eliminar backup automatico")

        input("\nPresiona Enter para continuar...")

    def _configure_email_notifications(self):
        """Configura las notificaciones por email"""
        print("\n=== Configurar Notificaciones por Email ===")
        print("\nConfiguracion actual:")
        print(f"  SMTP Server: {self.settings.SMTP_SERVER}")
        print(f"  SMTP Port: {self.settings.SMTP_PORT}")
        print(f"  SMTP User: {self.settings.SMTP_USER or '(no configurado)'}")
        print(f"  Email destino: {self.settings.BACKUP_EMAIL_TO or '(no configurado)'}")

        print("\nDeseas actualizar la configuracion? (s/N): ")
        if input().strip().lower() != 's':
            input("\nPresiona Enter para continuar...")
            return

        print("\nIngresa los nuevos valores (Enter para mantener actual):")

        smtp_server = input(f"SMTP Server [{self.settings.SMTP_SERVER}]: ").strip()
        if smtp_server:
            self.settings.set_env_var('SMTP_SERVER', smtp_server)

        smtp_port = input(f"SMTP Port [{self.settings.SMTP_PORT}]: ").strip()
        if smtp_port:
            self.settings.set_env_var('SMTP_PORT', smtp_port)

        smtp_user = input(f"SMTP User [{self.settings.SMTP_USER}]: ").strip()
        if smtp_user:
            self.settings.set_env_var('SMTP_USER', smtp_user)

        smtp_password = input("SMTP Password (no se mostrara): ").strip()
        if smtp_password:
            self.settings.set_env_var('SMTP_PASSWORD', smtp_password)

        backup_email = input(f"Email destino [{self.settings.BACKUP_EMAIL_TO}]: ").strip()
        if backup_email:
            self.settings.set_env_var('BACKUP_EMAIL_TO', backup_email)

        # Guardar configuracion
        if self.settings.generate_env_file():
            self.logger.success("Configuracion de email actualizada")
            print("\nLa configuracion se ha guardado en .env")
        else:
            self.logger.error("Error al guardar configuracion")

        input("\nPresiona Enter para continuar...")

    def _show_backup_info(self, backup_mgr):
        """Muestra informacion detallada de un backup"""
        print("\n=== Informacion de Backup ===")

        print("\n1. Testing")
        print("2. Produccion")
        env_choice = input("\nSelecciona el ambiente: ").strip()

        if env_choice == '1':
            env = 'testing'
        elif env_choice == '2':
            env = 'production'
        else:
            print("Opcion invalida")
            input("\nPresiona Enter para continuar...")
            return

        # Listar backups
        backups = backup_mgr.list_backups(env)
        if not backups:
            print(f"\nNo hay backups disponibles para {env}")
            input("\nPresiona Enter para continuar...")
            return

        timestamp = input("\nIngresa el timestamp del backup: ").strip()
        if not timestamp:
            print("Timestamp invalido")
            input("\nPresiona Enter para continuar...")
            return

        # Obtener informacion
        info = backup_mgr.get_backup_info(env, timestamp)
        if not info:
            print(f"\nBackup no encontrado: {timestamp}")
            input("\nPresiona Enter para continuar...")
            return

        # Mostrar informacion
        print(f"\n{'='*60}")
        print(f"Ambiente: {info['environment']}")
        print(f"Timestamp: {info['timestamp']}")
        print(f"Ruta: {info['path']}")
        print(f"Tamaño total: {info['size']}")
        print(f"\nArchivos del backup:")
        print(f"{'-'*60}")
        for file_info in info['files']:
            print(f"  {file_info['name']:40s} {file_info['size']:>10s}")
        print(f"{'='*60}")

        input("\nPresiona Enter para continuar...")

    def _setup_automatic_backups(self):
        """Configura backups automaticos durante la instalacion"""
        print("\n" + "="*60)
        print("CONFIGURACION DE BACKUPS AUTOMATICOS")
        print("="*60)
        print("\nDeseas configurar backups automaticos?")
        print("Se recomienda configurar backups diarios para ambos ambientes")

        choice = input("\nConfigurar backups automaticos? (s/N): ").strip().lower()

        if choice != 's':
            print("Backups automaticos no configurados")
            print("Puedes configurarlos despues desde el menu principal (opcion 4)")
            return

        try:
            from backup.scheduler import BackupScheduler

            # Cargar variables de entorno
            self.settings.load_env_file()
            scheduler = BackupScheduler(self.settings)

            self.logger.info("Configurando backups automaticos...")

            # Testing: diario a las 2 AM
            if scheduler.setup_cron('testing', '0 2 * * *'):
                self.logger.success("Backup automatico para Testing: diario a las 2:00 AM")
            else:
                self.logger.warning("No se pudo configurar backup automatico para Testing")

            # Production: diario a las 3 AM
            if scheduler.setup_cron('production', '0 3 * * *'):
                self.logger.success("Backup automatico para Produccion: diario a las 3:00 AM")
            else:
                self.logger.warning("No se pudo configurar backup automatico para Produccion")

            print("\nBackups automaticos configurados exitosamente")
            print("Testing: Diario a las 2:00 AM")
            print("Produccion: Diario a las 3:00 AM")
            print("\nLos backups se guardaran en: /opt/docker-project/backups/")

        except Exception as e:
            self.logger.error(f"Error configurando backups automaticos: {str(e)}")
            print("Puedes configurarlos manualmente despues desde el menu principal")

    def uninstall_all(self):
        """Menu de desinstalacion con opciones granulares"""
        while True:
            menu = """
===============================================================
                    DESINSTALACION
===============================================================

  1. Eliminar solo ambiente Testing
  2. Eliminar solo ambiente Produccion
  3. Eliminar TODO (Testing + Produccion + Infraestructura)

  0. Cancelar

===============================================================
            """
            print(menu)
            choice = input("Selecciona una opcion: ").strip()

            if choice == '0':
                print("Desinstalacion cancelada")
                return
            elif choice == '1':
                self._uninstall_environment('testing')
                break
            elif choice == '2':
                self._uninstall_environment('production')
                break
            elif choice == '3':
                self._uninstall_complete()
                break
            else:
                print("Opcion invalida")

    def _uninstall_environment(self, env):
        """Desinstala un ambiente especifico"""
        import subprocess
        import shutil
        from backup.backup_manager import BackupManager

        env_name = env.upper()

        print(f"\n{'='*60}")
        print(f"DESINSTALACION DE AMBIENTE {env_name}")
        print(f"{'='*60}")
        print(f"\nEsta accion eliminara:")
        print(f"- Contenedores de {env}: mysql_{env} y moodle_{env}")
        print(f"- Volumenes de datos: mysql_{env} y moodledata_{env}")
        print(f"- Directorios locales en /opt/docker-project/{env}/")
        print(f"- Logs de {env}")

        # Ofrecer backup si es produccion
        if env == 'production':
            print(f"\n{'*'*60}")
            print("IMPORTANTE: Estas eliminando el ambiente de PRODUCCION")
            print(f"{'*'*60}")

            backup_choice = input("\nDeseas crear un backup antes de eliminar? (S/n): ").strip().lower()

            if backup_choice != 'n':
                self.logger.info("Creando backup de seguridad antes de eliminar...")
                backup_mgr = BackupManager(self.settings)
                if backup_mgr.create_backup('production'):
                    self.logger.success("Backup de seguridad creado exitosamente")
                else:
                    self.logger.warning("No se pudo crear el backup")
                    continue_choice = input("Continuar sin backup? (s/N): ").strip().lower()
                    if continue_choice != 's':
                        print("Desinstalacion cancelada")
                        return

        confirm = input(f"\nEstas seguro de eliminar {env_name}? Escribe 'SI' para confirmar: ").strip()

        if confirm != 'SI':
            print("Desinstalacion cancelada")
            return

        try:
            # Detener y eliminar contenedores
            self.logger.info(f"Deteniendo contenedores de {env}...")
            DockerComposeWrapper.run_compose_shell(
                f"stop mysql_{env} moodle_{env}",
                cwd=self.settings.BASE_PATH,
                capture_output=True
            )

            DockerComposeWrapper.run_compose_shell(
                f"rm -f mysql_{env} moodle_{env}",
                cwd=self.settings.BASE_PATH,
                capture_output=True
            )

            # Eliminar volumenes
            self.logger.info(f"Eliminando volumenes de {env}...")
            subprocess.run(f"docker volume rm mysql_{env}", shell=True, capture_output=True)
            subprocess.run(f"docker volume rm moodledata_{env}", shell=True, capture_output=True)

            # Eliminar directorios locales
            self.logger.info(f"Eliminando directorios de {env}...")
            env_dir = os.path.join(self.settings.BASE_PATH, env)
            if os.path.exists(env_dir):
                shutil.rmtree(env_dir)

            logs_dir = os.path.join(self.settings.BASE_PATH, 'logs', env)
            if os.path.exists(logs_dir):
                shutil.rmtree(logs_dir)

            self.logger.success(f"Ambiente {env_name} eliminado exitosamente")

        except Exception as e:
            self.logger.error(f"Error durante la desinstalacion de {env}: {str(e)}")

    def _uninstall_complete(self):
        """Desinstala toda la infraestructura"""
        import shutil
        from backup.backup_manager import BackupManager

        print("\n" + "="*60)
        print("DESINSTALACION COMPLETA")
        print("="*60)
        print("\nEsta accion eliminara:")
        print("- TODOS los contenedores Docker (Testing + Produccion + Nginx)")
        print("- TODOS los volumenes y datos")
        print("- La estructura completa en /opt/docker-project")
        print("- Todos los archivos de configuracion")

        # Ofrecer backup de produccion
        print("\n" + "*"*60)
        print("RECOMENDACION: Crear backup de Produccion antes de eliminar")
        print("*"*60)

        backup_choice = input("\nDeseas crear un backup de Produccion? (S/n): ").strip().lower()

        if backup_choice != 'n':
            self.logger.info("Creando backup de Produccion...")
            self.settings.load_env_file()
            backup_mgr = BackupManager(self.settings)
            if backup_mgr.create_backup('production'):
                self.logger.success("Backup de Produccion creado exitosamente")
            else:
                self.logger.warning("No se pudo crear el backup")

        confirm = input("\nEstas COMPLETAMENTE seguro? Escribe 'ELIMINAR TODO' para confirmar: ").strip()

        if confirm != 'ELIMINAR TODO':
            print("Desinstalacion cancelada")
            return

        try:
            self.logger.info("Deteniendo todos los contenedores...")
            DockerComposeWrapper.run_compose_shell(
                "down -v",
                cwd=self.settings.BASE_PATH
            )

            self.logger.info("Eliminando estructura completa...")
            if os.path.exists(self.settings.BASE_PATH):
                shutil.rmtree(self.settings.BASE_PATH)

            self.logger.success("Desinstalacion completa finalizada")

        except Exception as e:
            self.logger.error(f"Error durante la desinstalacion: {str(e)}")
    
    def run(self):
        """Ejecuta el instalador"""
        self.show_banner()
        
        while True:
            self.show_menu()
            choice = input("Selecciona una opcion: ").strip()
            
            if choice == '0':
                print("\nSaliendo... Hasta pronto!")
                sys.exit(0)
            elif choice == '1':
                self.full_installation()
                input("\nPresiona Enter para continuar...")
            elif choice == '2':
                self.manage_environments()
            elif choice == '3':
                self.view_logs()
            elif choice == '4':
                self.manage_backups()
            elif choice == '5':
                self.uninstall_all()
                input("\nPresiona Enter para continuar...")
            else:
                print("Opcion invalida. Intenta de nuevo.")


def main():
    """Funcion principal"""
    try:
        installer = MoodleDockerInstaller()
        installer.run()
    except KeyboardInterrupt:
        print("\n\nInstalacion interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\nError fatal: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
