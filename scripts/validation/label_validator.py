import pandas as pd
import numpy as np
from sklearn.metrics import cohen_kappa_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

class LabelValidator:
    """
    Herramienta para validar la calidad y consistencia del etiquetado
    en el proyecto Nadia.
    """
    
    def __init__(self):
        self.dimensions = {
            'profile_id': ['PROFILE_1_DIRECTO', 'PROFILE_2_HESITANTE', 'PROFILE_3_DECEPCIONADO'],
            'customer_status': ['PROSPECT', 'LEAD_QUALIFIED', 'CUSTOMER', 'CHURNED'],
            'primary_intent': [
                'GREETING', 'TRANSACTIONAL_INQUIRY', 'RELATIONAL_QUESTION',
                'HESITATION_OR_OBJECTION', 'NEGATIVE_FEEDBACK', 'SMALL_TALK',
                'COMPLIMENT', 'PERSONAL_SHARE', 'FANTASY_ROLEPLAY',
                'TECHNICAL_ISSUE', 'GOODBYE'
            ],
            'rapport_stage': ['ICE_BREAKER', 'RAPPORT_BUILDING', 'DEEP_EMOTION', 
                            'HIGH_INTENT', 'CLOSING'],
            'safety_level': ['LEVEL_0_SAFE', 'LEVEL_1_FLIRT_SAFE', 
                           'LEVEL_2_BORDERLINE', 'LEVEL_3_INAPPROPRIATE']
        }
        
        # Transiciones válidas para rapport_stage
        self.valid_transitions = {
            'ICE_BREAKER': ['RAPPORT_BUILDING', 'CLOSING'],
            'RAPPORT_BUILDING': ['DEEP_EMOTION', 'HIGH_INTENT', 'CLOSING'],
            'DEEP_EMOTION': ['HIGH_INTENT', 'RAPPORT_BUILDING'],
            'HIGH_INTENT': ['CLOSING'],
            'CLOSING': []  # Estado terminal
        }
        
    def validate_consistency(self, annotations_df, annotator_col='annotator'):
        """
        Calcula métricas de consistencia entre anotadores.
        """
        results = {}
        
        # Agrupar por mensaje para comparar anotaciones
        grouped = annotations_df.groupby('message_id')
        
        for dimension in self.dimensions.keys():
            if dimension in annotations_df.columns:
                # Calcular Cohen's Kappa para pares de anotadores
                kappa_scores = []
                
                for msg_id, group in grouped:
                    if len(group) >= 2:
                        annotators = group[annotator_col].unique()
                        if len(annotators) >= 2:
                            ann1_labels = group[group[annotator_col] == annotators[0]][dimension].values
                            ann2_labels = group[group[annotator_col] == annotators[1]][dimension].values
                            
                            if len(ann1_labels) > 0 and len(ann2_labels) > 0:
                                kappa = cohen_kappa_score([ann1_labels[0]], [ann2_labels[0]])
                                kappa_scores.append(kappa)
                
                results[dimension] = {
                    'mean_kappa': np.mean(kappa_scores) if kappa_scores else 0,
                    'min_kappa': np.min(kappa_scores) if kappa_scores else 0,
                    'samples': len(kappa_scores)
                }
        
        return results
    
    def analyze_distribution(self, labels_df):
        """
        Analiza la distribución de etiquetas para identificar desbalances.
        """
        distributions = {}
        
        for dimension in self.dimensions.keys():
            if dimension in labels_df.columns:
                dist = labels_df[dimension].value_counts(normalize=True).to_dict()
                distributions[dimension] = dist
        
        return distributions
    
    def validate_rapport_transitions(self, conversation_df):
        """
        Valida que las transiciones de rapport_stage sean válidas según la FSM.
        """
        invalid_transitions = []
        
        # Ordenar por conversación y timestamp
        sorted_df = conversation_df.sort_values(['conversation_id', 'timestamp'])
        
        for conv_id, conv_data in sorted_df.groupby('conversation_id'):
            stages = conv_data['rapport_stage'].tolist()
            
            for i in range(len(stages) - 1):
                current = stages[i]
                next_stage = stages[i + 1]
                
                if next_stage not in self.valid_transitions.get(current, []):
                    invalid_transitions.append({
                        'conversation_id': conv_id,
                        'position': i,
                        'invalid_transition': f"{current} → {next_stage}"
                    })
        
        return invalid_transitions
    
    def detect_label_conflicts(self, labels_df):
        """
        Detecta conflictos lógicos entre etiquetas
        (ej: NEGATIVE_FEEDBACK con LEVEL_1_FLIRT_SAFE).
        """
        conflicts = []
        
        # Reglas de conflicto
        conflict_rules = [
            {
                'condition': (labels_df['primary_intent'] == 'NEGATIVE_FEEDBACK') & 
                            (labels_df['safety_level'].isin(['LEVEL_1_FLIRT_SAFE', 'LEVEL_0_SAFE'])),
                'description': 'NEGATIVE_FEEDBACK debería tener safety_level más alto'
            },
            {
                'condition': (labels_df['primary_intent'] == 'TRANSACTIONAL_INQUIRY') & 
                            (labels_df['rapport_stage'] == 'DEEP_EMOTION'),
                'description': 'TRANSACTIONAL_INQUIRY es inconsistente con DEEP_EMOTION'
            },
            {
                'condition': (labels_df['safety_level'] == 'LEVEL_3_INAPPROPRIATE') & 
                            (labels_df['rapport_stage'].isin(['HIGH_INTENT', 'DEEP_EMOTION'])),
                'description': 'Contenido inapropiado no debería tener rapport alto'
            }
        ]
        
        for rule in conflict_rules:
            conflicting_rows = labels_df[rule['condition']]
            if len(conflicting_rows) > 0:
                conflicts.append({
                    'rule': rule['description'],
                    'count': len(conflicting_rows),
                    'message_ids': conflicting_rows['message_id'].tolist()
                })
        
        return conflicts
    
    def generate_quality_report(self, labels_df, output_file='label_quality_report.txt'):
        """
        Genera un reporte completo de calidad del etiquetado.
        """
        report = []
        report.append("=== REPORTE DE CALIDAD DE ETIQUETADO ===\n")
        
        # 1. Distribuciones
        report.append("1. DISTRIBUCIÓN DE ETIQUETAS:")
        distributions = self.analyze_distribution(labels_df)
        for dim, dist in distributions.items():
            report.append(f"\n{dim}:")
            for label, pct in sorted(dist.items(), key=lambda x: x[1], reverse=True):
                report.append(f"  - {label}: {pct:.1%}")
        
        # 2. Conflictos
        report.append("\n\n2. CONFLICTOS DETECTADOS:")
        conflicts = self.detect_label_conflicts(labels_df)
        if conflicts:
            for conflict in conflicts:
                report.append(f"\n- {conflict['rule']}")
                report.append(f"  Casos encontrados: {conflict['count']}")
        else:
            report.append("\nNo se detectaron conflictos lógicos ✓")
        
        # 3. Validación de transiciones (si aplica)
        if 'rapport_stage' in labels_df.columns and 'conversation_id' in labels_df.columns:
            report.append("\n\n3. VALIDACIÓN DE TRANSICIONES DE RAPPORT:")
            invalid = self.validate_rapport_transitions(labels_df)
            if invalid:
                report.append(f"\nTransiciones inválidas encontradas: {len(invalid)}")
                for trans in invalid[:5]:  # Mostrar solo las primeras 5
                    report.append(f"  - {trans['invalid_transition']} en conversación {trans['conversation_id']}")
            else:
                report.append("\nTodas las transiciones son válidas ✓")
        
        # Guardar reporte
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print(f"Reporte guardado en: {output_file}")
        return '\n'.join(report)

# Ejemplo de uso
if __name__ == "__main__":
    # Simular datos de ejemplo
    np.random.seed(42)
    
    # Crear dataset de prueba
    n_messages = 200
    sample_data = {
        'message_id': range(n_messages),
        'conversation_id': np.repeat(range(40), 5),  # 40 conversaciones de 5 mensajes
        'timestamp': pd.date_range('2024-01-01', periods=n_messages, freq='1min'),
        'primary_intent': np.random.choice(
            ['GREETING', 'RELATIONAL_QUESTION', 'SMALL_TALK', 'HESITATION_OR_OBJECTION'], 
            n_messages, p=[0.1, 0.4, 0.3, 0.2]
        ),
        'safety_level': np.random.choice(
            ['LEVEL_0_SAFE', 'LEVEL_1_FLIRT_SAFE', 'LEVEL_2_BORDERLINE'], 
            n_messages, p=[0.7, 0.25, 0.05]
        ),
        'rapport_stage': np.random.choice(
            ['ICE_BREAKER', 'RAPPORT_BUILDING', 'DEEP_EMOTION'], 
            n_messages, p=[0.3, 0.5, 0.2]
        )
    }
    
    df = pd.DataFrame(sample_data)
    
    # Validar
    validator = LabelValidator()
    report = validator.generate_quality_report(df)
    print("\n" + report)