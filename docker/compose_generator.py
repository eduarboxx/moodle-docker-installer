"""
Docker Compose Generator Module
Genera el archivo docker-compose.yml
"""

import os
import yaml


class ComposeGenerator:
    """Genera archivo docker-compose.yml"""
    
    def __init__(self, settings):
        self.settings = settings
        self.base_path = settings.BASE_PATH
    
    def generate(self):
        """Genera docker-compose.yml completo"""
        try:
            compose_config = self._build_compose_config()
            compose_path = os.path.join(self.base_path, 'docker-compose.yml')
            
            with open(compose_path, 'w') as f:
                yaml.dump(compose_config, f, default_flow_style=False, sort_keys=False)
            
            print(f"docker-compose.yml creado: {compose_path}")
            return True
            
        except Exception as e:
            print(f"Error generando docker-compose.yml: {str(e)}")
            return False
    
    def _build_compose_config(self):
        """Construye la configuracion de docker-compose"""
        config = {
            'version': '3.8',
            'services': {},
            'networks': {
                'testing': {
                    'name': 'testing',
                    'driver': 'bridge'
                },
                'production': {
                    'name': 'production',
                    'driver': 'bridge'
                }
            },
            'volumes': {
                'mysql_testing': {
                    'name': 'mysql_testing'
                },
                'mysql_production': {
                    'name': 'mysql_production'
                },
                'moodledata_testing': {
                    'name': 'moodledata_testing'
                },
                'moodledata_production': {
                    'name': 'moodledata_production'
                }
            }
        }

        # Servicios de Testing
        config['services']['mysql_testing'] = self._build_mysql_service('testing')
        config['services']['moodle_testing'] = self._build_moodle_service('testing')

        # Servicios de Produccion
        config['services']['mysql_production'] = self._build_mysql_service('production')
        config['services']['moodle_production'] = self._build_moodle_service('production')

        # Nginx eliminado - Apache corre en el HOST como proxy reverso

        return config
    
    def _build_mysql_service(self, env):
        """Construye configuracion de MySQL para un ambiente"""
        env_prefix = 'TEST' if env == 'testing' else 'PROD'
        
        return {
            'image': 'mysql:8.0',
            'container_name': f'mysql_{env}',
            'environment': [
                f"MYSQL_ROOT_PASSWORD=${{{env_prefix}_DB_ROOT_PASS}}",
                f"MYSQL_DATABASE=${{{env_prefix}_DB_NAME}}",
                f"MYSQL_USER=${{{env_prefix}_DB_USER}}",
                f"MYSQL_PASSWORD=${{{env_prefix}_DB_PASS}}"
            ],
            'volumes': [
                f'mysql_{env}:/var/lib/mysql',
                f'./logs/{env}:/var/log/mysql'
            ],
            'networks': [
                env
            ],
            'restart': 'unless-stopped',
            'healthcheck': {
                'test': ['CMD', 'mysqladmin', 'ping', '-h', 'localhost'],
                'interval': '10s',
                'timeout': '5s',
                'retries': 5
            }
        }
    
    def _build_moodle_service(self, env):
        """Construye configuracion de Moodle para un ambiente"""
        env_prefix = 'TEST' if env == 'testing' else 'PROD'

        # Puertos expuestos al host para que Apache haga proxy
        # Testing: 8081:80, Production: 8082:80
        host_port = '8081' if env == 'testing' else '8082'

        return {
            'build': {
                'context': './moodle',
                'dockerfile': 'Dockerfile'
            },
            'container_name': f'moodle_{env}',
            'environment': [
                f"MOODLE_DATABASE_TYPE=mysqli",
                f"MOODLE_DATABASE_HOST=mysql_{env}",
                f"MOODLE_DATABASE_NAME=${{{env_prefix}_DB_NAME}}",
                f"MOODLE_DATABASE_USER=${{{env_prefix}_DB_USER}}",
                f"MOODLE_DATABASE_PASSWORD=${{{env_prefix}_DB_PASS}}",
                f"MOODLE_URL=${{{env_prefix}_URL}}"
            ],
            'ports': [
                f'{host_port}:80'
            ],
            'volumes': [
                f'moodledata_{env}:/var/moodledata',
                f'./{env}/www-moodledata:/var/www/moodledata',
                f'./logs/{env}:/var/log/apache2'
            ],
            'networks': [
                env
            ],
            'depends_on': {
                f'mysql_{env}': {
                    'condition': 'service_healthy'
                }
            },
            'restart': 'unless-stopped',
            'healthcheck': {
                'test': ['CMD', 'curl', '-f', 'http://localhost/'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3,
                'start_period': '60s'
            }
        }
