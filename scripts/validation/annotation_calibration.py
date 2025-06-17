import json
import random
from datetime import datetime
from typing import Dict, List, Tuple
import hashlib

class AnnotatorCalibrationTool:
    """
    Herramienta para auto-calibración del anotador único en el proyecto Nadia.
    Implementa el proceso de "examen de certificación" personal.
    """
    
    def __init__(self):
        self.control_bank = []
        self.annotation_history = {}
        
    def create_control_bank(self, messages: List[Dict]) -> None:
        """
        Crea el banco de control con mensajes ambiguos/difíciles.
        
        Args:
            messages: Lista de diccionarios con 'id', 'text', y 'notes'
        """
        self.control_bank = messages
        # Mezclar orden para evitar memorización
        random.shuffle(self.control_bank)
        
    def start_calibration_session(self, session_name: str) -> List[Dict]:
        """
        Inicia una sesión de calibración devolviendo mensajes sin etiquetas previas.
        """
        session_messages = []
        
        for msg in self.control_bank:
            # Crear copia limpia sin etiquetas
            clean_msg = {
                'id': msg['id'],
                'text': msg['text'],
                'session': session_name,
                'timestamp': datetime.now().isoformat()
            }
            session_messages.append(clean_msg)
            
        # Guardar orden aleatorio para esta sesión
        order_hash = hashlib.md5(
            ''.join([m['id'] for m in session_messages]).encode()
        ).hexdigest()
        
        self.annotation_history[session_name] = {
            'messages': session_messages,
            'order_hash': order_hash,
            'annotations': {}
        }
        
        return session_messages
    
    def record_annotation(self, session_name: str, message_id: str, 
                         labels: Dict[str, str]) -> None:
        """
        Registra una anotación para análisis posterior.
        
        Args:
            session_name: Nombre de la sesión de calibración
            message_id: ID del mensaje
            labels: Diccionario con dimensión -> etiqueta
        """
        if session_name in self.annotation_history:
            self.annotation_history[session_name]['annotations'][message_id] = labels
    
    def calculate_intra_annotator_agreement(self, session1: str, 
                                           session2: str) -> Dict[str, float]:
        """
        Calcula el acuerdo entre dos sesiones del mismo anotador.
        """
        if session1 not in self.annotation_history or session2 not in self.annotation_history:
            raise ValueError("Sesiones no encontradas")
        
        annotations1 = self.annotation_history[session1]['annotations']
        annotations2 = self.annotation_history[session2]['annotations']
        
        # Encontrar mensajes comunes
        common_messages = set(annotations1.keys()) & set(annotations2.keys())
        
        if not common_messages:
            return {}
        
        # Calcular acuerdo por dimensión
        dimensions = ['primary_intent', 'message_tone', 'safety_level']
        agreement_scores = {}
        
        for dim in dimensions:
            matches = 0
            total = 0
            
            for msg_id in common_messages:
                if dim in annotations1[msg_id] and dim in annotations2[msg_id]:
                    total += 1
                    if annotations1[msg_id][dim] == annotations2[msg_id][dim]:
                        matches += 1
            
            if total > 0:
                agreement_scores[dim] = matches / total
        
        # Acuerdo general
        all_matches = 0
        all_total = 0
        
        for msg_id in common_messages:
            for dim in dimensions:
                if dim in annotations1[msg_id] and dim in annotations2[msg_id]:
                    all_total += 1
                    if annotations1[msg_id][dim] == annotations2[msg_id][dim]:
                        all_matches += 1
        
        agreement_scores['overall'] = all_matches / all_total if all_total > 0 else 0
        
        return agreement_scores
    
    def identify_inconsistencies(self, session1: str, session2: str) -> List[Dict]:
        """
        Identifica casos específicos donde hubo desacuerdo.
        """
        inconsistencies = []
        
        annotations1 = self.annotation_history[session1]['annotations']
        annotations2 = self.annotation_history[session2]['annotations']
        
        common_messages = set(annotations1.keys()) & set(annotations2.keys())
        
        for msg_id in common_messages:
            msg_inconsistencies = {}
            
            # Buscar el texto original
            original_text = None
            for msg in self.control_bank:
                if msg['id'] == msg_id:
                    original_text = msg['text']
                    break
            
            for dim in ['primary_intent', 'message_tone', 'safety_level']:
                if dim in annotations1[msg_id] and dim in annotations2[msg_id]:
                    label1 = annotations1[msg_id][dim]
                    label2 = annotations2[msg_id][dim]
                    
                    if label1 != label2:
                        msg_inconsistencies[dim] = {
                            'session1': label1,
                            'session2': label2
                        }
            
            if msg_inconsistencies:
                inconsistencies.append({
                    'message_id': msg_id,
                    'text': original_text,
                    'disagreements': msg_inconsistencies
                })
        
        return inconsistencies
    
    def generate_calibration_report(self, session1: str, session2: str) -> str:
        """
        Genera un reporte detallado de calibración.
        """
        agreement = self.calculate_intra_annotator_agreement(session1, session2)
        inconsistencies = self.identify_inconsistencies(session1, session2)
        
        report = []
        report.append("=== REPORTE DE AUTO-CALIBRACIÓN ===\n")
        report.append(f"Sesión 1: {session1}")
        report.append(f"Sesión 2: {session2}")
        report.append(f"Mensajes evaluados: {len(self.annotation_history[session1]['annotations'])}\n")
        
        report.append("TASAS DE ACUERDO:")
        for dim, score in agreement.items():
            status = "✓" if score >= 0.9 else "✗"
            report.append(f"  - {dim}: {score:.1%} {status}")
        
        report.append(f"\nESTATUS: {'APROBADO' if agreement.get('overall', 0) >= 0.9 else 'REQUIERE REFINAMIENTO'}")
        
        if inconsistencies:
            report.append(f"\nINCONSISTENCIAS ENCONTRADAS ({len(inconsistencies)} casos):\n")
            
            for i, case in enumerate(inconsistencies[:5], 1):  # Mostrar máx 5
                report.append(f"{i}. Mensaje: \"{case['text']}\"")
                for dim, labels in case['disagreements'].items():
                    report.append(f"   {dim}: {labels['session1']} → {labels['session2']}")
                report.append("")
        
        return '\n'.join(report)


# Banco de control de ejemplo para el proyecto Nadia
CONTROL_BANK_EXAMPLES = [
    {
        'id': 'ctrl_001',
        'text': 'Hola preciosa, ¿cuánto cuesta tu contenido?',
        'notes': 'Saludo + transaccional - caso ambiguo clásico'
    },
    {
        'id': 'ctrl_002',
        'text': 'No sé si eres real pero me gustas mucho',
        'notes': 'Hesitación + cumplido'
    },
    {
        'id': 'ctrl_003',
        'text': 'ok',
        'notes': 'Respuesta mínima - tono ambiguo'
    },
    {
        'id': 'ctrl_004',
        'text': 'Eres hermosa pero no pago por esto',
        'notes': 'Cumplido + feedback negativo'
    },
    {
        'id': 'ctrl_005',
        'text': '¿Hablas español? Soy de México',
        'notes': 'Small talk vs personal share'
    },
    {
        'id': 'ctrl_006',
        'text': 'Me divorcie hace poco y busco compañía',
        'notes': 'Personal share con contexto emocional'
    },
    {
        'id': 'ctrl_007',
        'text': '¿Vale la pena pagar? No estoy seguro',
        'notes': 'Hesitación clara sobre transacción'
    },
    {
        'id': 'ctrl_008',
        'text': '😍😍😍 que bella',
        'notes': 'Emojis + cumplido breve'
    },
    {
        'id': 'ctrl_009',
        'text': 'Mejor hablemos aquí, no uso telegram',
        'notes': 'Objeción al funnel'
    },
    {
        'id': 'ctrl_010',
        'text': 'Hola otra vez, ¿me recuerdas?',
        'notes': 'Continuación vs saludo'
    }
]

# Ejemplo de uso
if __name__ == "__main__":
    tool = AnnotatorCalibrationTool()
    
    # Crear banco de control
    tool.create_control_bank(CONTROL_BANK_EXAMPLES)
    
    # Simular primera sesión
    print("=== SESIÓN 1 DE CALIBRACIÓN ===")
    messages_session1 = tool.start_calibration_session("Día 1 - Mañana")
    
    # Simular anotaciones (en la práctica, esto lo harías manualmente)
    sample_annotations_1 = {
        'ctrl_001': {
            'primary_intent': 'TRANSACTIONAL_INQUIRY',
            'message_tone': 'FRIENDLY',
            'safety_level': 'LEVEL_0_SAFE'
        },
        'ctrl_002': {
            'primary_intent': 'HESITATION_OR_OBJECTION',
            'message_tone': 'ENGAGED',
            'safety_level': 'LEVEL_0_SAFE'
        },
        'ctrl_003': {
            'primary_intent': 'SMALL_TALK',
            'message_tone': 'DISMISSIVE',
            'safety_level': 'LEVEL_0_SAFE'
        }
    }
    
    for msg_id, labels in sample_annotations_1.items():
        tool.record_annotation("Día 1 - Mañana", msg_id, labels)
    
    # Simular segunda sesión (día siguiente)
    print("\n=== SESIÓN 2 DE CALIBRACIÓN ===")
    messages_session2 = tool.start_calibration_session("Día 2 - Mañana")
    
    # Simular algunas diferencias
    sample_annotations_2 = {
        'ctrl_001': {
            'primary_intent': 'TRANSACTIONAL_INQUIRY',  # Consistente
            'message_tone': 'FRIENDLY',  # Consistente
            'safety_level': 'LEVEL_0_SAFE'  # Consistente
        },
        'ctrl_002': {
            'primary_intent': 'COMPLIMENT',  # CAMBIÓ! Era HESITATION
            'message_tone': 'ENGAGED',  # Consistente
            'safety_level': 'LEVEL_0_SAFE'  # Consistente
        },
        'ctrl_003': {
            'primary_intent': 'SMALL_TALK',  # Consistente
            'message_tone': 'SKEPTICAL',  # CAMBIÓ! Era DISMISSIVE
            'safety_level': 'LEVEL_0_SAFE'  # Consistente
        }
    }
    
    for msg_id, labels in sample_annotations_2.items():
        tool.record_annotation("Día 2 - Mañana", msg_id, labels)
    
    # Generar reporte
    print("\n" + tool.generate_calibration_report("Día 1 - Mañana", "Día 2 - Mañana"))