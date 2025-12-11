"""
SSL Certificate Manager Module
Gestiona la creacion y configuracion de certificados SSL
"""

import os
import subprocess
from pathlib import Path


class SSLManager:
    """Gestiona certificados SSL para los ambientes"""

    def __init__(self, settings):
        self.settings = settings
        self.ssl_path = os.path.join(settings.NGINX_PATH, 'ssl')
        os.makedirs(self.ssl_path, exist_ok=True)

    def setup_certificates(self):
        """Configura certificados SSL para ambos ambientes"""
        print("\n" + "="*60)
        print("CONFIGURACION DE CERTIFICADOS SSL")
        print("="*60)

        # Generar certificados para testing y production
        for env in ['testing', 'production']:
            self._setup_environment_cert(env)

        return True

    def setup_certificates_for_env(self, environment):
        """Configura certificados SSL para un ambiente especifico"""
        print("\n" + "="*60)
        print(f"CONFIGURACION DE CERTIFICADOS SSL PARA {environment.upper()}")
        print("="*60)

        return self._setup_environment_cert(environment)

    def _setup_environment_cert(self, env):
        """Configura certificado SSL para un ambiente especifico"""
        env_prefix = 'TEST' if env == 'testing' else 'PROD'
        url = self.settings.get_env_var(f'{env_prefix}_URL', '')

        # Extraer dominio de la URL
        domain = url.replace('https://', '').replace('http://', '').split(':')[0]

        cert_file = os.path.join(self.ssl_path, f'{env}.crt')
        key_file = os.path.join(self.ssl_path, f'{env}.key')

        # Si ya existen certificados, preguntar si reemplazar
        if os.path.exists(cert_file) and os.path.exists(key_file):
            print(f"\nCertificados SSL para {env} ya existen")
            replace = input(f"Deseas reemplazarlos? (s/n) [n]: ").strip().lower()
            if replace != 's':
                print(f"Manteniendo certificados existentes para {env}")
                return True

        # Verificar si es un dominio real o local
        is_real_domain = self._is_real_domain(domain)

        if is_real_domain:
            print(f"\nDominio detectado: {domain}")
            print("Opciones de certificado SSL:")
            print("1. Certificado autofirmado (desarrollo/testing)")
            print("2. Let's Encrypt (produccion - requiere dominio publico)")
            print("3. Certificado personalizado (proporcionare mis propios archivos)")

            choice = input("Selecciona una opcion [1]: ").strip() or "1"

            if choice == "2":
                return self._setup_letsencrypt(env, domain)
            elif choice == "3":
                return self._setup_custom_cert(env)
            else:
                return self._generate_self_signed_cert(env, domain)
        else:
            # Dominio local, usar autofirmado
            print(f"\nGenerando certificado autofirmado para {env} ({domain})...")
            return self._generate_self_signed_cert(env, domain)

    def _is_real_domain(self, domain):
        """Verifica si es un dominio real o uno local"""
        local_domains = [
            'localhost',
            'moodle.local',
            'test.moodle.local',
            '127.0.0.1'
        ]

        # Si contiene .local o es localhost, es local
        if '.local' in domain or domain in local_domains:
            return False

        # Si es una IP, es local
        if domain.replace('.', '').isdigit():
            return False

        return True

    def _generate_self_signed_cert(self, env, domain):
        """Genera un certificado SSL autofirmado"""
        cert_file = os.path.join(self.ssl_path, f'{env}.crt')
        key_file = os.path.join(self.ssl_path, f'{env}.key')

        try:
            # Generar certificado autofirmado valido por 365 dias
            cmd = [
                'openssl', 'req', '-x509', '-nodes',
                '-days', '365',
                '-newkey', 'rsa:2048',
                '-keyout', key_file,
                '-out', cert_file,
                '-subj', f'/C=CL/ST=Chile/L=Santiago/O=Moodle/CN={domain}',
                '-addext', f'subjectAltName=DNS:{domain},DNS:*.{domain}'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                # Establecer permisos correctos
                os.chmod(key_file, 0o600)
                os.chmod(cert_file, 0o644)
                print(f"Certificado autofirmado generado para {env}")
                print(f"  Certificado: {cert_file}")
                print(f"  Clave privada: {key_file}")
                return True
            else:
                print(f"Error generando certificado autofirmado: {result.stderr}")
                return False

        except Exception as e:
            print(f"Error generando certificado SSL: {str(e)}")
            return False

    def _setup_letsencrypt(self, env, domain):
        """Configura certificado de Let's Encrypt usando certbot"""
        print(f"\nConfigurando Let's Encrypt para {domain}...")
        print("\nRequisitos:")
        print("- El dominio debe apuntar a esta maquina")
        print("- El puerto 80 debe estar accesible desde internet")
        print("- Certbot debe estar instalado")

        # Verificar si certbot esta instalado
        if not self._check_certbot():
            print("\nCertbot no esta instalado.")
            install = input("Deseas instalarlo ahora? (s/n) [s]: ").strip().lower()
            if install != 'n':
                if not self._install_certbot():
                    print("No se pudo instalar certbot. Usando certificado autofirmado.")
                    return self._generate_self_signed_cert(env, domain)
            else:
                print("Usando certificado autofirmado.")
                return self._generate_self_signed_cert(env, domain)

        # Email para notificaciones de Let's Encrypt
        email = input("Email para notificaciones de Let's Encrypt: ").strip()
        if not email:
            print("Email requerido para Let's Encrypt. Usando certificado autofirmado.")
            return self._generate_self_signed_cert(env, domain)

        try:
            # Detener nginx temporalmente para liberar puerto 80
            print("\nSolicitando certificado de Let's Encrypt...")
            print("Esto puede tomar unos minutos...")

            cmd = [
                'certbot', 'certonly',
                '--standalone',
                '-d', domain,
                '--non-interactive',
                '--agree-tos',
                '--email', email,
                '--preferred-challenges', 'http'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                # Copiar certificados de Let's Encrypt a nuestra ubicacion
                le_cert = f'/etc/letsencrypt/live/{domain}/fullchain.pem'
                le_key = f'/etc/letsencrypt/live/{domain}/privkey.pem'

                cert_file = os.path.join(self.ssl_path, f'{env}.crt')
                key_file = os.path.join(self.ssl_path, f'{env}.key')

                # Crear enlaces simbolicos
                if os.path.exists(le_cert) and os.path.exists(le_key):
                    subprocess.run(['ln', '-sf', le_cert, cert_file])
                    subprocess.run(['ln', '-sf', le_key, key_file])

                    print(f"Certificado de Let's Encrypt configurado para {env}")
                    print(f"  Certificado: {cert_file} -> {le_cert}")
                    print(f"  Clave privada: {key_file} -> {le_key}")

                    # Configurar renovacion automatica
                    self._setup_certbot_renewal()

                    return True
                else:
                    print("Error: No se encontraron los certificados de Let's Encrypt")
                    return self._generate_self_signed_cert(env, domain)
            else:
                print(f"Error obteniendo certificado de Let's Encrypt: {result.stderr}")
                print("Usando certificado autofirmado.")
                return self._generate_self_signed_cert(env, domain)

        except Exception as e:
            print(f"Error configurando Let's Encrypt: {str(e)}")
            print("Usando certificado autofirmado.")
            return self._generate_self_signed_cert(env, domain)

    def _setup_custom_cert(self, env):
        """Configura un certificado SSL personalizado"""
        print(f"\nConfiguración de certificado personalizado para {env}")
        print("Proporciona las rutas a tus archivos de certificado:")

        cert_source = input("Ruta al archivo de certificado (.crt/.pem): ").strip()
        key_source = input("Ruta al archivo de clave privada (.key): ").strip()

        if not cert_source or not key_source:
            print("Rutas requeridas. Usando certificado autofirmado.")
            return self._generate_self_signed_cert(env, "custom.domain")

        if not os.path.exists(cert_source):
            print(f"Error: No se encuentra el archivo de certificado: {cert_source}")
            return False

        if not os.path.exists(key_source):
            print(f"Error: No se encuentra el archivo de clave privada: {key_source}")
            return False

        try:
            cert_file = os.path.join(self.ssl_path, f'{env}.crt')
            key_file = os.path.join(self.ssl_path, f'{env}.key')

            # Copiar archivos
            subprocess.run(['cp', cert_source, cert_file], check=True)
            subprocess.run(['cp', key_source, key_file], check=True)

            # Establecer permisos
            os.chmod(key_file, 0o600)
            os.chmod(cert_file, 0o644)

            print(f"Certificado personalizado configurado para {env}")
            print(f"  Certificado: {cert_file}")
            print(f"  Clave privada: {key_file}")
            return True

        except Exception as e:
            print(f"Error configurando certificado personalizado: {str(e)}")
            return False

    def _check_certbot(self):
        """Verifica si certbot esta instalado"""
        try:
            result = subprocess.run(['certbot', '--version'],
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _install_certbot(self):
        """Instala certbot"""
        print("\nInstalando certbot...")

        try:
            # Detectar sistema operativo
            if os.path.exists('/etc/debian_version'):
                # Debian/Ubuntu
                print("Instalando certbot en Debian/Ubuntu...")
                subprocess.run(['apt-get', 'update'], check=True)
                subprocess.run(['apt-get', 'install', '-y', 'certbot'], check=True)

            elif os.path.exists('/etc/redhat-release'):
                # RHEL/Rocky/CentOS
                print("Instalando certbot en RHEL/Rocky Linux...")

                # Verificar version de RHEL/Rocky
                with open('/etc/redhat-release', 'r') as f:
                    release = f.read().lower()

                # Habilitar EPEL si no esta habilitado
                print("Habilitando repositorio EPEL...")
                if 'rocky' in release or 'centos' in release:
                    subprocess.run(['dnf', 'install', '-y', 'epel-release'], check=False)

                # Intentar instalar certbot desde EPEL
                result = subprocess.run(['dnf', 'install', '-y', 'certbot'],
                                      capture_output=True, text=True)

                if result.returncode != 0:
                    # Si falla, intentar instalar via snap
                    print("Certbot no disponible via DNF, intentando con snapd...")

                    # Instalar snapd
                    subprocess.run(['dnf', 'install', '-y', 'snapd'], check=False)
                    subprocess.run(['systemctl', 'enable', '--now', 'snapd.socket'], check=False)
                    subprocess.run(['ln', '-sf', '/var/lib/snapd/snap', '/snap'], check=False)

                    # Esperar a que snapd se inicialice
                    import time
                    print("Esperando inicializacion de snapd...")
                    time.sleep(5)

                    # Instalar certbot via snap
                    result = subprocess.run(['snap', 'install', '--classic', 'certbot'],
                                          capture_output=True, text=True)

                    if result.returncode == 0:
                        # Crear symlink
                        subprocess.run(['ln', '-sf', '/snap/bin/certbot', '/usr/bin/certbot'],
                                     check=False)
                        print("Certbot instalado via snap")
                    else:
                        print("\nNo se pudo instalar certbot automaticamente.")
                        print("Puedes instalarlo manualmente con:")
                        print("  sudo dnf install epel-release")
                        print("  sudo dnf install certbot")
                        print("\nO usar pip:")
                        print("  sudo pip3 install certbot")
                        return False

            elif os.path.exists('/etc/arch-release'):
                # Arch Linux
                subprocess.run(['pacman', '-S', '--noconfirm', 'certbot'], check=True)
            else:
                print("Sistema operativo no soportado para instalacion automatica de certbot")
                print("\nPuedes intentar instalarlo con pip:")
                print("  sudo pip3 install certbot certbot-apache")

                install_pip = input("\nDeseas intentar instalar con pip? (s/n) [s]: ").strip().lower()
                if install_pip != 'n':
                    subprocess.run(['pip3', 'install', 'certbot'], check=True)
                else:
                    return False

            print("Certbot instalado exitosamente")
            return True

        except Exception as e:
            print(f"Error instalando certbot: {str(e)}")
            print("\nComo alternativa, puedes:")
            print("1. Usar certificado autofirmado (selecciona opcion 1)")
            print("2. Usar certificado personalizado (selecciona opcion 3)")
            print("3. Instalar certbot manualmente luego ejecutar nuevamente")
            return False

    def _setup_certbot_renewal(self):
        """Configura la renovacion automatica de certificados"""
        try:
            # Verificar si el cron job ya existe
            result = subprocess.run(['crontab', '-l'],
                                  capture_output=True, text=True)

            renewal_cmd = '0 0,12 * * * certbot renew --quiet --deploy-hook "docker restart nginx"'

            if renewal_cmd not in result.stdout:
                # Agregar cron job para renovacion
                current_crontab = result.stdout if result.returncode == 0 else ""
                new_crontab = current_crontab + "\n" + renewal_cmd + "\n"

                subprocess.run(['crontab', '-'],
                             input=new_crontab.encode(),
                             check=True)

                print("\nRenovacion automatica de certificados configurada")
                print("Los certificados se renovaran automaticamente cada 12 horas")

        except Exception as e:
            print(f"Advertencia: No se pudo configurar renovacion automatica: {str(e)}")
            print("Deberas renovar los certificados manualmente con: certbot renew")

    def generate_moodle_config_snippet(self, env):
        """Genera snippet de configuracion para config.php de Moodle"""
        env_prefix = 'TEST' if env == 'testing' else 'PROD'
        url = self.settings.get_env_var(f'{env_prefix}_URL', '')

        # Asegurar que la URL use HTTPS
        if not url.startswith('https://'):
            url = url.replace('http://', 'https://')

        config = f"""
// Forzar SSL/HTTPS
$CFG->wwwroot = '{url}';
$CFG->sslproxy = true;
$CFG->admin = 'admin';

// Configuracion de sesiones seguras
@ini_set('session.cookie_secure', 'on');
@ini_set('session.cookie_httponly', 'on');
@ini_set('session.cookie_samesite', 'Lax');

// Forzar conexion segura
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] == 'https') {{
    $_SERVER['HTTPS'] = 'on';
}}
"""

        return config

    def create_moodle_config_file(self, env):
        """Crea archivo de configuracion inicial para Moodle"""
        env_prefix = 'TEST' if env == 'testing' else 'PROD'

        config_dir = os.path.join(self.settings.BASE_PATH, env, 'moodle_config')
        os.makedirs(config_dir, exist_ok=True)

        config_file = os.path.join(config_dir, 'ssl_config.php')

        with open(config_file, 'w') as f:
            f.write("<?php\n")
            f.write("// Configuracion SSL para Moodle - Ambiente: " + env + "\n")
            f.write(self.generate_moodle_config_snippet(env))
            f.write("\n")

        print(f"Archivo de configuracion SSL creado: {config_file}")
        print(f"IMPORTANTE: Este codigo debe agregarse al config.php de Moodle en {env}")

        return config_file
