#!/usr/bin/env python3
"""
Test Suite
Pruebas basicas de funcionalidad
"""

import sys
import os

# Agregar directorio al path
sys.path.insert(0, os.path.dirname(__file__))

from core.os_detector import OSDetector
from utils.password_generator import PasswordGenerator
from utils.validator import Validator
from config.settings import Settings


def test_os_detection():
    """Prueba deteccion de SO"""
    print("\n=== Test: Deteccion de SO ===")
    detector = OSDetector()
    try:
        os_info = detector.detect()
        print(f"Distribucion: {os_info['distro']}")
        print(f"Version: {os_info['version']}")
        print(f"Familia: {os_info['family']}")
        print(f"Gestor de paquetes: {os_info['package_manager']}")
        print("OK")
        return True
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


def test_password_generation():
    """Prueba generacion de contraseñas"""
    print("\n=== Test: Generacion de Contraseñas ===")
    pg = PasswordGenerator()
    
    for i in range(5):
        password = pg.generate()
        print(f"Contraseña {i+1}: {password}")
    
    print("OK")
    return True


def test_validator():
    """Prueba validaciones"""
    print("\n=== Test: Validaciones ===")
    validator = Validator()
    
    print(f"Root: {validator.check_root()}")
    print(f"Espacio en disco: {validator.check_disk_space('/opt')}")
    print(f"Internet: {validator.check_internet_connection()}")
    print(f"Puerto 8080 disponible: {validator.check_port_available(8080)}")
    
    print("OK")
    return True


def test_settings():
    """Prueba configuraciones"""
    print("\n=== Test: Settings ===")
    settings = Settings()
    
    print(f"Base path: {settings.BASE_PATH}")
    print(f"Moodle version: {settings.MOODLE_VERSION}")
    print(f"Moodle path: {settings.MOODLE_PATH}")
    print(f"Testing URL: {settings.get_env_var('TEST_URL')}")
    print(f"Production URL: {settings.get_env_var('PROD_URL')}")
    
    print("OK")
    return True


def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*60)
    print("EJECUTANDO PRUEBAS")
    print("="*60)
    
    tests = [
        test_os_detection,
        test_password_generation,
        test_validator,
        test_settings
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\nERROR en {test.__name__}: {str(e)}")
            results.append(False)
    
    print("\n" + "="*60)
    print(f"RESULTADOS: {sum(results)}/{len(results)} pruebas pasadas")
    print("="*60 + "\n")
    
    return all(results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
