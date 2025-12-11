"""
Directory Manager Module
Crea y gestiona la estructura de directorios del proyecto
"""

import os
import shutil


class DirectoryManager:
    """Gestiona la estructura de directorios"""
    
    def __init__(self, base_path):
        self.base_path = base_path
        self.directories = [
            # Raiz
            base_path,
            
            # Nginx
            os.path.join(base_path, 'nginx'),
            os.path.join(base_path, 'nginx', 'conf.d'),
            os.path.join(base_path, 'nginx', 'ssl'),
            
            # Moodle
            os.path.join(base_path, 'moodle'),
            
            # Testing
            os.path.join(base_path, 'testing'),
            os.path.join(base_path, 'testing', 'moodledata'),
            os.path.join(base_path, 'testing', 'mysql-data'),
            
            # Production
            os.path.join(base_path, 'production'),
            os.path.join(base_path, 'production', 'moodledata'),
            os.path.join(base_path, 'production', 'mysql-data'),
            
            # Logs
            os.path.join(base_path, 'logs'),
            os.path.join(base_path, 'logs', 'testing'),
            os.path.join(base_path, 'logs', 'production'),
            os.path.join(base_path, 'logs', 'nginx'),
            
            # Backups
            os.path.join(base_path, 'backups'),
            os.path.join(base_path, 'backups', 'testing'),
            os.path.join(base_path, 'backups', 'production'),
        ]
    
    def create_structure(self):
        """Crea toda la estructura de directorios"""
        try:
            for directory in self.directories:
                if not os.path.exists(directory):
                    os.makedirs(directory, mode=0o755)
                    print(f"Directorio creado: {directory}")
                else:
                    print(f"Directorio ya existe: {directory}")
            
            # Permisos especiales para moodledata
            self._set_moodledata_permissions()
            
            return True
        except Exception as e:
            print(f"Error creando estructura: {str(e)}")
            return False
    
    def _set_moodledata_permissions(self):
        """Establece permisos para directorios moodledata"""
        moodledata_dirs = [
            os.path.join(self.base_path, 'testing', 'moodledata'),
            os.path.join(self.base_path, 'production', 'moodledata')
        ]

        for directory in moodledata_dirs:
            try:
                os.chmod(directory, 0o755)
                print(f"Permisos 755 aplicados a: {directory}")
            except Exception as e:
                print(f"Error aplicando permisos a {directory}: {str(e)}")
    
    def clean_structure(self):
        """Elimina toda la estructura de directorios"""
        try:
            if os.path.exists(self.base_path):
                shutil.rmtree(self.base_path)
                print(f"Estructura eliminada: {self.base_path}")
                return True
            return False
        except Exception as e:
            print(f"Error eliminando estructura: {str(e)}")
            return False
    
    def verify_structure(self):
        """Verifica que la estructura este completa"""
        missing = []
        for directory in self.directories:
            if not os.path.exists(directory):
                missing.append(directory)
        
        if missing:
            print(f"Directorios faltantes: {len(missing)}")
            for d in missing:
                print(f"  - {d}")
            return False
        
        print("Estructura verificada correctamente")
        return True
