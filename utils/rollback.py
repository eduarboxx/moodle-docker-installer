"""
Rollback Module
Sistema de rollback en caso de errores
"""

import os
import shutil
import subprocess


class RollbackManager:
    """Maneja el rollback de cambios en caso de error"""
    
    def __init__(self):
        self.actions = []
        self.base_path = "/opt/docker-project"
    
    def add_action(self, action_type, data):
        """Registra una accion para posible rollback"""
        self.actions.append({
            'type': action_type,
            'data': data
        })
    
    def execute(self):
        """Ejecuta el rollback de todas las acciones"""
        print("\nEjecutando rollback...")
        
        # Revertir en orden inverso
        for action in reversed(self.actions):
            try:
                if action['type'] == 'directory':
                    self._rollback_directory(action['data'])
                elif action['type'] == 'file':
                    self._rollback_file(action['data'])
                elif action['type'] == 'docker':
                    self._rollback_docker(action['data'])
                elif action['type'] == 'package':
                    self._rollback_package(action['data'])
            except Exception as e:
                print(f"Error en rollback de {action['type']}: {str(e)}")
        
        print("Rollback completado")
    
    def _rollback_directory(self, path):
        """Elimina un directorio"""
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"Directorio eliminado: {path}")
    
    def _rollback_file(self, path):
        """Elimina un archivo"""
        if os.path.exists(path):
            os.remove(path)
            print(f"Archivo eliminado: {path}")
    
    def _rollback_docker(self, container_name):
        """Detiene y elimina contenedores Docker"""
        try:
            subprocess.run(
                f"docker stop {container_name} && docker rm {container_name}",
                shell=True,
                capture_output=True
            )
            print(f"Contenedor eliminado: {container_name}")
        except Exception:
            pass
    
    def _rollback_package(self, package_name):
        """No desinstala paquetes (demasiado peligroso)"""
        print(f"Paquete {package_name} no se desinstalara (rollback manual requerido)")
    
    def clear(self):
        """Limpia el registro de acciones"""
        self.actions = []
