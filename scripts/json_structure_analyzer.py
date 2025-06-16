#!/usr/bin/env python3
"""
Script para analizar la estructura real de los archivos JSON
"""

import json
from pathlib import Path
import pprint

def analyze_json_structure(file_path: Path):
    """
    Analiza y muestra la estructura de un archivo JSON
    """
    print(f"\n🔍 Analizando: {file_path.name}")
    print("=" * 60)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Tipo de dato principal
        print(f"📊 Tipo de dato raíz: {type(data)}")
        
        if isinstance(data, dict):
            print(f"📋 Claves del diccionario: {list(data.keys())}")
            
            # Analizar cada clave
            for key, value in data.items():
                print(f"\n  🔹 Clave '{key}':")
                print(f"     - Tipo: {type(value)}")
                
                if isinstance(value, list):
                    print(f"     - Longitud: {len(value)} elementos")
                    if len(value) > 0:
                        print(f"     - Tipo del primer elemento: {type(value[0])}")
                        if isinstance(value[0], dict):
                            print(f"     - Claves del primer elemento: {list(value[0].keys())}")
                            
                elif isinstance(value, dict):
                    print(f"     - Claves: {list(value.keys())}")
                    
                elif isinstance(value, (str, int, float)):
                    print(f"     - Valor: {value}")
        
        elif isinstance(data, list):
            print(f"📋 Lista con {len(data)} elementos")
            if len(data) > 0:
                print(f"🔹 Tipo del primer elemento: {type(data[0])}")
                if isinstance(data[0], dict):
                    print(f"🔹 Claves del primer elemento: {list(data[0].keys())}")
        
        # Mostrar muestra de los primeros elementos
        print(f"\n📄 Muestra de los primeros 2 elementos:")
        if isinstance(data, dict) and any(isinstance(v, list) for v in data.values()):
            # Si es un dict con listas, mostrar las listas
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 0:
                    print(f"\n'{key}' primeros 2 elementos:")
                    for i, item in enumerate(value[:2]):
                        print(f"\nElemento {i}:")
                        pprint.pprint(item, indent=2, width=100)
        elif isinstance(data, list):
            # Si es una lista directa
            for i, item in enumerate(data[:2]):
                print(f"\nElemento {i}:")
                pprint.pprint(item, indent=2, width=100)
        else:
            # Mostrar el objeto completo si es pequeño
            pprint.pprint(data, indent=2, width=100)
                
    except Exception as e:
        print(f"❌ Error al analizar: {str(e)}")


def main():
    """
    Analiza todos los archivos JSON de prueba
    """
    print("🔧 Analizador de estructura JSON")
    
    test_files = [
        "test_case_rapport_success.json",
        "test_case_rapport_fail.json"
    ]
    
    for filename in test_files:
        file_path = Path(f"data/raw/{filename}")
        if file_path.exists():
            analyze_json_structure(file_path)
        else:
            print(f"\n❌ No encontrado: {file_path}")
    
    print("\n✅ Análisis completado")
    print("\n💡 Usa esta información para ajustar el script de inyección de PII")


if __name__ == "__main__":
    main()