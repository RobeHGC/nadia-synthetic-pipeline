# scripts/setup_pipeline.py
#!/usr/bin/env python3
"""
Script de configuración inicial del pipeline
"""

import os
import json
from pathlib import Path
import sys

def setup_pipeline():
    print("🔧 Configuración inicial del Synthetic Pipeline")
    print("=" * 50)
    
    # Verificar estructura de directorios
    required_dirs = [
        'data/raw',
        'data/anonymized',
        'data/patterns',
        'data/synthetic',
        'data/labeled',
        'outputs/reports',
        'outputs/exports',
        'outputs/checkpoints',
        'logs'
    ]
    
    print("\n📁 Verificando estructura de directorios...")
    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}")
    
    # Configurar archivo de config si no existe
    config_path = Path('config/pipeline_config.json')
    
    if not config_path.exists():
        print("\n⚙️  Creando archivo de configuración...")
        
        # Copiar template
        template_path = Path('config/pipeline_config_template.json')
        if template_path.exists():
            import shutil
            shutil.copy(template_path, config_path)
            print("  ✓ Configuración creada desde template")
        else:
            print("  ❌ No se encontró template de configuración")
            return False
    
    # Verificar dependencias
    print("\n📦 Verificando dependencias...")
    try:
        import pandas
        import spacy
        import openai
        print("  ✓ Dependencias principales instaladas")
    except ImportError as e:
        print(f"  ❌ Falta instalar: {e.name}")
        print("  💡 Ejecuta: pip install -r requirements.txt")
        return False
    
    # Instrucciones finales
    print("\n✅ Setup completado!")
    print("\n📝 Siguientes pasos:")
    print("1. Edita config/pipeline_config.json con tu API key de OpenAI")
    print("2. Coloca tus datos raw en data/raw/")
    print("3. Ejecuta: python scripts/main_pipeline.py")
    
    return True

if __name__ == '__main__':
    success = setup_pipeline()
    sys.exit(0 if success else 1)