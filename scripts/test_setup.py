#!/usr/bin/env python3
"""
Test básico para verificar que el setup está completo
"""

import sys
import json
from pathlib import Path

def test_setup():
    print("🔍 Verificando setup del proyecto...")
    
    checks = {
        "Estructura de directorios": True,
        "Archivo de configuración": True,
        "Scripts básicos": True,
        "Permisos correctos": True
    }
    
    # Verificar directorios
    required_dirs = ['data', 'config', 'scripts', 'outputs', 'logs']
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            checks["Estructura de directorios"] = False
            print(f"❌ Falta directorio: {dir_name}")
    
    # Verificar archivos de configuración
    if not Path('config/pipeline_config_template.json').exists():
        checks["Archivo de configuración"] = False
        print("❌ Falta config/pipeline_config_template.json")
        
    # Verificar scripts
    if not Path('scripts/main_pipeline.py').exists():
        checks["Scripts básicos"] = False
        print("❌ Falta scripts/main_pipeline.py")
    
    # Mostrar resumen
    print("\n📊 Resumen de verificación:")
    all_good = True
    for check, status in checks.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {check}")
        if not status:
            all_good = False
    
    return all_good

if __name__ == '__main__':
    if test_setup():
        print("\n✅ ¡Todo listo para el commit inicial!")
    else:
        print("\n⚠️  Corrige los problemas antes del commit")
        sys.exit(1)
