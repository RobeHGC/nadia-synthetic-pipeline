#!/usr/bin/env python3
"""
Script para inyectar PII falsa en conversaciones JSON para testing del anonymizer
Versión adaptada para estructura de mensajes individuales en inglés/español
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Banco de PII falsa pero realista - VERSIÓN BILINGÜE
FAKE_NAMES = [
    # Nombres en inglés
    "John Smith", "Mary Johnson", "David Brown", "Jennifer Davis",
    "Michael Wilson", "Sarah Miller", "Robert Taylor", "Lisa Anderson",
    "Dr. James Thompson", "Dr. Emily White", "Andrew Martinez", "Jessica Garcia",
    # Nombres en español
    "Juan Pérez", "María García", "Carlos López", "Ana Martínez",
    "Pedro Sánchez", "Laura Rodríguez", "Dr. Miguel Hernández", "Dra. Isabel González"
]

FAKE_EMAILS = [
    "john.smith@gmail.com", "test.user@email.com", "patient.new@hotmail.com",
    "mary.johnson@yahoo.com", "contact@healthclinic.com", "info@medical-center.org",
    "david_brown_88@outlook.com", "appointments@doctoroffice.com",
    "usuario123@gmail.com", "maria.garcia@yahoo.mx", "consultas@clinica-salud.mx"
]

FAKE_PHONES = [
    # Formatos USA
    "555-123-4567", "(212) 555-0123", "+1 212 555 9876", "212.555.9876",
    "Call me at: 555-4321", "Cell: 212-555-4567", "2125554567",
    # Formatos México
    "+52 867 123 4567", "867-555-0123", "WhatsApp: +52 867 999 8888"
]

FAKE_SOCIALS = [
    "@john_smith_official", "@healthyliving", "IG: @fitness_guru", "@dr_wilson_md",
    "Instagram: @medical_updates", "Twitter: @health_tips", "@user12345",
    "FB: Mary Johnson", "Snap: david_brown88", "@maria_garcia_mx"
]

FAKE_ADDRESSES = [
    # Direcciones USA
    "123 Main Street, Apt 4B", "456 Park Avenue, NY 10001",
    "789 Oak Drive, Suite 200", "321 Elm Street, Boston MA",
    # Direcciones México
    "Calle Principal 123, Col. Centro", "Av. Universidad #456, CP 25000"
]

# Patrones de inserción de PII - BILINGÜE
PII_PATTERNS_EN = [
    # Presentación formal
    "Hi, I'm {name}, you can reach me at {phone} or email me at {email}",
    "My name is {name}. Feel free to text me at {phone}",
    
    # Compartir contacto
    "My email is {email}, I'm also on {social}",
    "You can find me on {social} or call {phone}",
    
    # Referencia a otra persona
    "{name} told me to contact you. Their number is {phone}",
    "I got your info from {name}, they said to email {email}",
    
    # Dirección
    "You can visit us at {address}. Ask for {name}",
    "Our office is at {address}, email: {email}",
    
    # Múltiple PII
    "I'm {name}, cell: {phone}, email: {email}, follow me {social}",
    "Contact {name} at {phone} or {email} for appointments"
]

PII_PATTERNS_ES = [
    # Presentación formal
    "Hola, soy {name}, pueden contactarme al {phone} o escribirme a {email}",
    "Mi nombre es {name}. Me pueden llamar al {phone}",
    
    # Compartir contacto
    "Mi correo es {email}, también estoy en {social}",
    "Me encuentran en {social} o al teléfono {phone}",
    
    # Referencia a otra persona
    "{name} me dijo que los contactara. Su teléfono es {phone}",
    
    # Dirección
    "Pueden visitarnos en {address}. Pregunten por {name}",
    
    # Múltiple PII
    "Soy {name}, cel: {phone}, email: {email}, síganme en {social}"
]


def detect_language(text: str) -> str:
    """
    Detecta el idioma del texto de manera simple
    """
    spanish_indicators = ['hola', 'que', 'como', 'estas', 'gracias', 'por', 'para', 'con', 'los', 'las']
    text_lower = text.lower()
    spanish_count = sum(1 for word in spanish_indicators if word in text_lower)
    return 'es' if spanish_count >= 2 else 'en'


def inject_pii_into_message(message: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, List[str]]]:
    """
    Inyecta PII falsa en un mensaje y retorna qué PII se agregó
    """
    pii_added = {
        "names": [],
        "emails": [],
        "phones": [],
        "socials": [],
        "addresses": []
    }
    
    # No agregar PII a mensajes vacíos o con contenido multimedia
    if not message.get("text") or message.get("has_photo") or message.get("has_gif"):
        return message, pii_added
    
    # 25% de probabilidad de agregar PII
    if random.random() < 0.25:
        # Detectar idioma del mensaje
        lang = detect_language(message["text"])
        patterns = PII_PATTERNS_ES if lang == 'es' else PII_PATTERNS_EN
        pattern = random.choice(patterns)
        
        # Llenar el patrón con datos falsos
        replacements = {}
        
        if "{name}" in pattern:
            # Seleccionar nombres apropiados según idioma
            names_pool = [n for n in FAKE_NAMES if (lang == 'es' and any(x in n for x in ['Juan', 'María', 'Carlos', 'Ana', 'Pedro', 'Laura', 'Miguel', 'Isabel'])) or 
                         (lang == 'en' and not any(x in n for x in ['Juan', 'María', 'Carlos', 'Ana', 'Pedro', 'Laura', 'Miguel', 'Isabel']))]
            if not names_pool:
                names_pool = FAKE_NAMES
            name = random.choice(names_pool)
            replacements["{name}"] = name
            pii_added["names"].append(name)
            
        if "{email}" in pattern:
            email = random.choice(FAKE_EMAILS)
            replacements["{email}"] = email
            pii_added["emails"].append(email)
            
        if "{phone}" in pattern:
            phone = random.choice(FAKE_PHONES)
            replacements["{phone}"] = phone
            pii_added["phones"].append(phone)
            
        if "{social}" in pattern:
            social = random.choice(FAKE_SOCIALS)
            replacements["{social}"] = social
            pii_added["socials"].append(social)
            
        if "{address}" in pattern:
            addresses_pool = FAKE_ADDRESSES[:4] if lang == 'en' else FAKE_ADDRESSES[4:]
            address = random.choice(addresses_pool)
            replacements["{address}"] = address
            pii_added["addresses"].append(address)
        
        # Aplicar reemplazos
        pii_text = pattern
        for placeholder, value in replacements.items():
            pii_text = pii_text.replace(placeholder, value)
        
        # Insertar en el mensaje original
        # 50% al inicio, 50% al final
        if random.random() < 0.5:
            message["text"] = f"{pii_text}. {message['text']}"
        else:
            message["text"] = f"{message['text']} {pii_text}"
        
        # Agregar metadata para testing
        message["_test_pii_added"] = pii_added
    
    return message, pii_added


def process_conversation_file(input_path: Path, output_path: Path) -> Dict[str, Any]:
    """
    Procesa un archivo JSON de conversaciones agregando PII falsa
    """
    print(f"  📖 Leyendo {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Manejar estructura: array de conversaciones con messages
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and "messages" in data[0]:
        # Es un array de conversaciones
        conversations = data
        total_messages = sum(len(conv.get("messages", [])) for conv in conversations)
        print(f"  📊 Procesando {len(conversations)} conversaciones con {total_messages} mensajes en total...")
    elif isinstance(data, dict) and "messages" in data:
        # Es una sola conversación
        conversations = [data]
        total_messages = len(data["messages"])
        print(f"  📊 Procesando 1 conversación con {total_messages} mensajes...")
    else:
        raise ValueError(f"Estructura no reconocida: {type(data)}")
    
    # Estadísticas de PII agregada
    total_pii = {
        "names": [],
        "emails": [],
        "phones": [],
        "socials": [],
        "addresses": []
    }
    
    messages_with_pii = 0
    
    # Procesar cada conversación
    for conv in conversations:
        messages = conv.get("messages", [])
        for i, message in enumerate(messages):
            modified_message, pii_added = inject_pii_into_message(message.copy())
            
            # Actualizar mensaje en su lugar
            messages[i] = modified_message
            
            # Si se agregó PII, acumular estadísticas
            if any(pii_added[key] for key in pii_added):
                messages_with_pii += 1
                for key in total_pii:
                    total_pii[key].extend(pii_added[key])
    
    # Guardar archivo modificado con la misma estructura
    print(f"  💾 Guardando archivo con PII en {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Generar reporte
    report = {
        "file": str(input_path.name),
        "output": str(output_path.name),
        "total_conversations": len(conversations),
        "total_messages": total_messages,
        "messages_with_pii": messages_with_pii,
        "pii_statistics": {
            key: len(set(values)) for key, values in total_pii.items()
        },
        "pii_details": {
            key: list(set(values)) for key, values in total_pii.items()
        },
        "timestamp": datetime.now().isoformat()
    }
    
    return report


def main():
    """
    Procesa los archivos de test agregando PII falsa
    """
    print("🔧 Preparando casos de prueba con PII falsa...")
    print("=" * 60)
    
    # Archivos a procesar
    test_files = [
        "test_case_rapport_success.json",
        "test_case_rapport_fail.json"
    ]
    
    reports = []
    
    # Crear directorio si no existe
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    
    for filename in test_files:
        input_path = Path(f"data/raw/{filename}")
        output_path = Path(f"data/raw/{filename.replace('.json', '_with_pii.json')}")
        
        if input_path.exists():
            print(f"\n📄 Procesando: {filename}")
            try:
                report = process_conversation_file(input_path, output_path)
                reports.append(report)
                
                print(f"\n✅ PII agregada exitosamente:")
                print(f"   - Mensajes procesados: {report['total_messages']}")
                print(f"   - Mensajes con PII: {report['messages_with_pii']}")
                print(f"   - Porcentaje con PII: {report['messages_with_pii']/report['total_messages']*100:.1f}%")
                
                print(f"\n📊 Tipos de PII agregada:")
                for pii_type, count in report["pii_statistics"].items():
                    if count > 0:
                        print(f"   - {pii_type}: {count} únicos")
                        
            except Exception as e:
                print(f"❌ Error procesando {filename}: {str(e)}")
                continue
        else:
            print(f"❌ No encontrado: {input_path}")
            print(f"   Por favor, coloca el archivo en: data/raw/")
    
    # Guardar reporte consolidado
    if reports:
        report_path = Path("data/raw/pii_injection_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                "generator": "PII Test Injector v1.0",
                "timestamp": datetime.now().isoformat(),
                "files_processed": len(reports),
                "reports": reports
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Reporte consolidado guardado en: {report_path}")
    
    print("\n✅ ¡Archivos listos para testing del anonymizer!")
    print("\n📝 Próximo paso: Desarrollar scripts/anonymizer.py")


if __name__ == "__main__":
    main()