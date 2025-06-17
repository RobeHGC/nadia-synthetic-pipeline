import json
import pandas as pd
from typing import Dict, List, Tuple
import re
from collections import Counter

class LLMAnnotationQualityChecker:
    """
    Herramienta para revisar rápidamente la calidad del trabajo del LLM anotador.
    Identifica patrones problemáticos y casos que requieren revisión humana.
    """
    
    def __init__(self):
        self.quality_issues = []
        self.statistics = {}
        
    def load_annotations(self, json_file_path: str) -> List[Dict]:
        """Carga las anotaciones generadas por el LLM."""
        with open(json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def check_response_quality(self, response: Dict) -> List[str]:
        """Verifica la calidad de las respuestas generadas de Nadia."""
        issues = []
        text = response.get('text', '')
        
        # Verificar longitud
        sentences = len(re.split(r'[.!?]+', text.strip()))
        if sentences > 3:
            issues.append("Respuesta muy larga (>3 oraciones)")
        
        # Contar emojis
        emoji_count = len(re.findall(r'[😀-🙏🌀-🗿💀-🫶]', text))
        if emoji_count > 2:
            issues.append(f"Demasiados emojis ({emoji_count})")
        
        # Verificar menciones prohibidas
        forbidden_patterns = [
            (r'\$\d+', "Menciona precio específico"),
            (r'fanvue|onlyfans', "Menciona plataforma explícitamente"),
            (r'prometo|garantizo', "Hace promesas"),
            (r'amor|cariño|bebé', "Demasiado íntimo para etapa inicial")
        ]
        
        for pattern, issue in forbidden_patterns:
            if re.search(pattern, text.lower()):
                issues.append(issue)
        
        # Verificar tono
        if text.endswith('?') and text.count('?') > 1:
            issues.append("Demasiadas preguntas")
            
        return issues
    
    def check_annotation_consistency(self, annotation: Dict) -> List[str]:
        """Verifica consistencia lógica entre etiquetas."""
        issues = []
        
        intent = annotation.get('primary_intent', '')
        tone = annotation.get('message_tone', '')
        safety = annotation.get('safety_level', '')
        
        # Reglas de consistencia
        if intent == 'NEGATIVE_FEEDBACK' and tone == 'FRIENDLY':
            issues.append("Inconsistencia: NEGATIVE_FEEDBACK no debería ser FRIENDLY")
            
        if intent == 'COMPLIMENT' and tone == 'FRUSTRATED':
            issues.append("Inconsistencia: COMPLIMENT no debería ser FRUSTRATED")
            
        if safety == 'LEVEL_3_INAPPROPRIATE' and tone in ['FRIENDLY', 'ENGAGED']:
            issues.append("Inconsistencia: Contenido inapropiado con tono positivo")
            
        if intent == 'TRANSACTIONAL_INQUIRY' and annotation.get('confidence', 1) < 0.7:
            issues.append("Baja confianza en pregunta transaccional")
            
        return issues
    
    def analyze_distribution(self, annotations: List[Dict]) -> Dict:
        """Analiza la distribución de etiquetas para detectar sesgos."""
        intent_counts = Counter()
        tone_counts = Counter()
        safety_counts = Counter()
        
        for item in annotations:
            ann = item['annotations']
            intent_counts[ann['primary_intent']] += 1
            tone_counts[ann['message_tone']] += 1
            safety_counts[ann['safety_level']] += 1
        
        total = len(annotations)
        
        distributions = {
            'primary_intent': {k: v/total for k, v in intent_counts.items()},
            'message_tone': {k: v/total for k, v in tone_counts.items()},
            'safety_level': {k: v/total for k, v in safety_counts.items()}
        }
        
        # Detectar anomalías
        anomalies = []
        
        # ¿Demasiados OTHER?
        if 'OTHER' in intent_counts and intent_counts['OTHER'] / total > 0.05:
            anomalies.append(f"Alta proporción de OTHER: {intent_counts['OTHER']/total:.1%}")
        
        # ¿Distribución sospechosa?
        if len(intent_counts) < 5:
            anomalies.append("Poca variedad en intenciones (sesgo potencial)")
            
        # ¿Demasiado seguro?
        if safety_counts.get('LEVEL_0_SAFE', 0) / total > 0.95:
            anomalies.append("Posible sub-clasificación de riesgos de seguridad")
        
        return {
            'distributions': distributions,
            'anomalies': anomalies,
            'total_messages': total
        }
    
    def identify_review_candidates(self, annotations: List[Dict]) -> List[Dict]:
        """Identifica mensajes que requieren revisión humana prioritaria."""
        review_needed = []
        
        for item in annotations:
            ann = item['annotations']
            response = item.get('ideal_nadia_response', {})
            
            reasons = []
            
            # Baja confianza
            if ann.get('confidence', 1) < 0.8:
                reasons.append(f"Baja confianza: {ann['confidence']}")
            
            # Problemas de consistencia
            consistency_issues = self.check_annotation_consistency(ann)
            if consistency_issues:
                reasons.extend(consistency_issues)
            
            # Problemas en respuesta
            response_issues = self.check_response_quality(response)
            if response_issues:
                reasons.extend(response_issues)
            
            # Casos de seguridad críticos
            if ann['safety_level'] in ['LEVEL_2_BORDERLINE', 'LEVEL_3_INAPPROPRIATE']:
                reasons.append("Requiere revisión de seguridad")
            
            # Intenciones complejas
            if ann['primary_intent'] in ['HESITATION_OR_OBJECTION', 'NEGATIVE_FEEDBACK']:
                reasons.append("Intención sensible que requiere validación")
            
            if reasons:
                review_needed.append({
                    'message_id': item['message_id'],
                    'text': item.get('original_text', 'N/A'),
                    'annotations': ann,
                    'response': response.get('text', ''),
                    'review_reasons': reasons
                })
        
        # Ordenar por número de problemas (más problemas primero)
        review_needed.sort(key=lambda x: len(x['review_reasons']), reverse=True)
        
        return review_needed
    
    def generate_review_report(self, annotations: List[Dict], 
                              output_file: str = 'llm_review_report.md') -> str:
        """Genera un reporte markdown para revisión humana eficiente."""
        distribution_analysis = self.analyze_distribution(annotations)
        review_candidates = self.identify_review_candidates(annotations)
        
        report = []
        report.append("# Reporte de Revisión de Anotaciones LLM\n")
        report.append(f"**Total de mensajes procesados**: {len(annotations)}\n")
        
        # Resumen ejecutivo
        report.append("## Resumen Ejecutivo\n")
        report.append(f"- **Mensajes que requieren revisión**: {len(review_candidates)} ({len(review_candidates)/len(annotations)*100:.1f}%)")
        
        if distribution_analysis['anomalies']:
            report.append("- **Anomalías detectadas**:")
            for anomaly in distribution_analysis['anomalies']:
                report.append(f"  - ⚠️ {anomaly}")
        else:
            report.append("- ✅ No se detectaron anomalías en la distribución")
        
        # Distribuciones
        report.append("\n## Distribución de Etiquetas\n")
        for dimension, dist in distribution_analysis['distributions'].items():
            report.append(f"### {dimension}")
            sorted_dist = sorted(dist.items(), key=lambda x: x[1], reverse=True)
            for label, pct in sorted_dist:
                bar = "█" * int(pct * 20)
                report.append(f"- {label}: {bar} {pct:.1%}")
            report.append("")
        
        # Casos prioritarios para revisión
        report.append("\n## Casos Prioritarios para Revisión\n")
        
        # Agrupar por tipo de problema
        by_issue_type = {}
        for candidate in review_candidates[:20]:  # Top 20
            for reason in candidate['review_reasons']:
                issue_type = reason.split(':')[0]
                if issue_type not in by_issue_type:
                    by_issue_type[issue_type] = []
                by_issue_type[issue_type].append(candidate)
        
        for issue_type, cases in by_issue_type.items():
            report.append(f"### {issue_type}\n")
            
            for case in cases[:3]:  # Máximo 3 ejemplos por tipo
                report.append(f"**Mensaje**: \"{case['text']}\"")
                report.append(f"- **Anotaciones LLM**: {case['annotations']['primary_intent']} | "
                            f"{case['annotations']['message_tone']} | "
                            f"{case['annotations']['safety_level']}")
                report.append(f"- **Respuesta propuesta**: \"{case['response']}\"")
                report.append(f"- **Problemas**: {', '.join(case['review_reasons'])}")
                report.append("")
        
        # Recomendaciones
        report.append("\n## Recomendaciones\n")
        
        if len(review_candidates) / len(annotations) > 0.2:
            report.append("1. **Alta tasa de revisión necesaria** - Considera refinar el prompt del LLM")
        
        if 'OTHER' in distribution_analysis['distributions']['primary_intent']:
            other_pct = distribution_analysis['distributions']['primary_intent']['OTHER']
            if other_pct > 0.05:
                report.append(f"2. **Reducir categoría OTHER** ({other_pct:.1%}) - Revisa estos casos para identificar nuevas categorías")
        
        safety_dist = distribution_analysis['distributions']['safety_level']
        if safety_dist.get('LEVEL_0_SAFE', 0) > 0.95:
            report.append("3. **Revisar clasificación de seguridad** - Posible sub-detección de contenido sensible")
        
        # Guardar reporte
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        return '\n'.join(report)
    
    def export_for_correction(self, review_candidates: List[Dict], 
                             output_file: str = 'messages_for_correction.jsonl') -> None:
        """Exporta los casos problemáticos en formato fácil de corregir."""
        with open(output_file, 'w', encoding='utf-8') as f:
            for candidate in review_candidates:
                # Formato simplificado para corrección rápida
                correction_format = {
                    'message_id': candidate['message_id'],
                    'text': candidate['text'],
                    'llm_annotations': candidate['annotations'],
                    'llm_response': candidate['response'],
                    'issues': candidate['review_reasons'],
                    'human_corrections': {
                        'primary_intent': None,
                        'message_tone': None,
                        'safety_level': None,
                        'ideal_response': None,
                        'notes': None
                    }
                }
                f.write(json.dumps(correction_format, ensure_ascii=False) + '\n')


# Script de ejemplo para procesar un batch
def process_llm_batch(input_file: str, output_dir: str = './review_output'):
    """
    Procesa un batch de anotaciones del LLM y genera todos los reportes necesarios.
    """
    import os
    
    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)
    
    # Inicializar el validador
    checker = LLMAnnotationQualityChecker()
    
    # Cargar anotaciones
    print(f"Cargando anotaciones de {input_file}...")
    annotations = checker.load_annotations(input_file)
    print(f"Cargadas {len(annotations)} anotaciones")
    
    # Generar análisis
    print("\nAnalizando calidad...")
    distribution = checker.analyze_distribution(annotations)
    review_candidates = checker.identify_review_candidates(annotations)
    
    print(f"\nEncontrados {len(review_candidates)} mensajes que requieren revisión")
    
    # Generar reportes
    print("\nGenerando reportes...")
    
    # 1. Reporte principal
    report_path = os.path.join(output_dir, 'review_report.md')
    checker.generate_review_report(annotations, report_path)
    print(f"✓ Reporte de revisión: {report_path}")
    
    # 2. Exportar para corrección
    corrections_path = os.path.join(output_dir, 'for_correction.jsonl')
    checker.export_for_correction(review_candidates, corrections_path)
    print(f"✓ Mensajes para corrección: {corrections_path}")
    
    # 3. Estadísticas rápidas
    stats_path = os.path.join(output_dir, 'quick_stats.json')
    with open(stats_path, 'w') as f:
        json.dump({
            'total_messages': len(annotations),
            'messages_needing_review': len(review_candidates),
            'review_rate': len(review_candidates) / len(annotations),
            'distributions': distribution['distributions'],
            'anomalies': distribution['anomalies']
        }, f, indent=2)
    print(f"✓ Estadísticas: {stats_path}")
    
    print(f"\n¡Proceso completado! Revisa los archivos en {output_dir}")


if __name__ == "__main__":
    # Ejemplo de uso
    process_llm_batch('llm_annotations_batch1.json', './review_batch1')