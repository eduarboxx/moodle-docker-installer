"""
Moodle Downloader Module
Descarga y extrae Moodle desde el sitio oficial
"""

import os
import subprocess
import zipfile
import requests
from pathlib import Path


class MoodleDownloader:
    """Descarga Moodle desde la pagina oficial"""
    
    def __init__(self, version, target_path):
        self.version = version
        self.target_path = target_path
        self.filename = f"moodle-{version}.zip"
        self.download_url = self._get_download_url()
    
    def _get_download_url(self):
        """Construye la URL de descarga"""
        # URL Moodle para version 4.5
        return "https://download.moodle.org/download.php/direct/stable405/moodle-latest-405.zip" 
    
    def download(self):
        """Descarga y extrae Moodle"""
        try:
            # Crear directorio padre si no existe
            parent_dir = os.path.dirname(self.target_path)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir, mode=0o755)
            
            # Verificar si ya esta descargado
            if os.path.exists(self.target_path) and os.listdir(self.target_path):
                print(f"Moodle ya existe en: {self.target_path}")
                return True
            
            # Descargar archivo
            temp_file = os.path.join('/tmp', self.filename)
            print(f"Descargando Moodle {self.version}...")
            print(f"URL: {self.download_url}")
            
            if not self._download_file(self.download_url, temp_file):
                return False
            
            # Extraer archivo
            print(f"Extrayendo Moodle...")
            if not self._extract_zip(temp_file, parent_dir):
                return False
            
            # Renombrar directorio si es necesario
            extracted_dir = os.path.join(parent_dir, 'moodle')
            if os.path.exists(extracted_dir) and extracted_dir != self.target_path:
                os.rename(extracted_dir, self.target_path)
            
            # Limpiar archivo temporal
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            print(f"Moodle descargado en: {self.target_path}")
            return True
            
        except Exception as e:
            print(f"Error descargando Moodle: {str(e)}")
            return False
    
    def _download_file(self, url, destination):
        """Descarga un archivo usando wget"""
        try:
            cmd = f'wget -O {destination} "{url}" --progress=bar:force 2>&1'
            result = subprocess.run(cmd, shell=True, capture_output=False)
            return result.returncode == 0
        except Exception as e:
            print(f"\nError descargando archivo: {str(e)}")
            return False

    def verify_download(self):
        """Verifica que Moodle se haya descargado correctamente"""
        if not os.path.exists(self.target_path):
            return False
        
        # Verificar archivos clave de Moodle
        key_files = [
            'config-dist.php',
            'version.php',
            'index.php',
            'lib',
            'admin'
        ]
        
        for file in key_files:
            if not os.path.exists(os.path.join(self.target_path, file)):
                print(f"Archivo/directorio faltante: {file}")
                return False
        
        print("Descarga de Moodle verificada correctamente")
        return True

    def _extract_zip(self, zip_path, extract_path):
        """Extrae un archivo zip"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            return True
        except Exception as e:
            print(f"Error extrayendo archivo: {str(e)}")
            return False