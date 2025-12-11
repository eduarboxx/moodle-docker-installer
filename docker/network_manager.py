"""
Network Manager Module
Gestiona las redes Docker
"""

import subprocess


class NetworkManager:
    """Gestiona redes Docker"""
    
    def __init__(self):
        self.networks = [
            'moodle_network_testing',
            'moodle_network_production'
        ]
    
    def create_networks(self):
        """Crea las redes Docker necesarias"""
        for network in self.networks:
            if not self.network_exists(network):
                self._create_network(network)
            else:
                print(f"Red ya existe: {network}")
        return True
    
    def network_exists(self, network_name):
        """Verifica si una red existe"""
        try:
            result = subprocess.run(
                f'docker network ls --filter name={network_name} --format "{{{{.Name}}}}"',
                shell=True,
                capture_output=True,
                text=True
            )
            return network_name in result.stdout
        except Exception:
            return False
    
    def _create_network(self, network_name):
        """Crea una red Docker"""
        try:
            subprocess.run(
                f'docker network create {network_name}',
                shell=True,
                check=True
            )
            print(f"Red creada: {network_name}")
            return True
        except Exception as e:
            print(f"Error creando red {network_name}: {str(e)}")
            return False
    
    def remove_networks(self):
        """Elimina todas las redes"""
        for network in self.networks:
            if self.network_exists(network):
                self._remove_network(network)
        return True
    
    def _remove_network(self, network_name):
        """Elimina una red Docker"""
        try:
            subprocess.run(
                f'docker network rm {network_name}',
                shell=True,
                check=True
            )
            print(f"Red eliminada: {network_name}")
            return True
        except Exception as e:
            print(f"Error eliminando red {network_name}: {str(e)}")
            return False
