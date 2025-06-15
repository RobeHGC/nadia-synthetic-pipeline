# scripts/main_pipeline.py
#!/usr/bin/env python3
"""
Pipeline principal - Orquesta todo el proceso
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.anonymizer import HybridAnonymizer
from scripts.pattern_analyzer import PatternAnalyzer
from scripts.prompt_generator import PromptGenerator
from scripts.synthetic_generator import SyntheticGenerator
from scripts.quality_validator import QualityValidator
from scripts.label_prep import LabelStudioPrep

class SyntheticPipeline:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.results = {}
        
    def _load_config(self, config_path: str) -> Dict:
        """Carga configuración del pipeline"""
        with open(config_path, 'r') as f:
            return json.load(f)
            
    def setup_logging(self):
        """Configura sistema de logging"""
        log_file = f"logs/pipeline_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('SyntheticPipeline')
        
    def run(self):
        """Ejecuta el pipeline completo"""
        self.logger.info("🚀 Iniciando Synthetic Pipeline v1.0")
        
        try:
            # Step 1: Anonimización
            self.logger.info("Step 1/5: Anonimización de datos")
            anonymized_data = self.run_anonymization()
            
            # Step 2: Análisis de patrones
            self.logger.info("Step 2/5: Análisis de patrones")
            patterns = self.run_pattern_analysis(anonymized_data)
            
            # Step 3: Generación de prompts
            self.logger.info("Step 3/5: Generación de prompts")
            prompts = self.run_prompt_generation(patterns)
            
            # Step 4: Generación sintética
            self.logger.info("Step 4/5: Generación de datos sintéticos")
            synthetic_data = self.run_synthetic_generation(prompts)
            
            # Step 5: Preparación para etiquetado
            self.logger.info("Step 5/5: Preparación para Label Studio")
            self.prepare_for_labeling(synthetic_data)
            
            # Generar reporte final
            self.generate_final_report()
            
        except Exception as e:
            self.logger.error(f"❌ Error en pipeline: {str(e)}")
            raise
            
    def run_anonymization(self):
        """Ejecuta módulo de anonimización"""
        anonymizer = HybridAnonymizer(self.config['anonymization'])
        
        # Procesar archivos raw
        raw_files = list(Path(self.config['data_sources']['raw_data_path']).glob(
            self.config['data_sources']['file_pattern']
        ))
        
        self.logger.info(f"Encontrados {len(raw_files)} archivos para procesar")
        
        anonymized_data = []
        for file_path in raw_files:
            result = anonymizer.process_file(file_path)
            anonymized_data.extend(result['conversations'])
            
        # Guardar resultado
        output_path = Path('data/anonymized/anonymized_conversations.json')
        with open(output_path, 'w') as f:
            json.dump(anonymized_data, f, indent=2)
            
        self.results['anonymization'] = {
            'files_processed': len(raw_files),
            'conversations_anonymized': len(anonymized_data),
            'output_file': str(output_path)
        }
        
        return anonymized_data
        
    def generate_final_report(self):
        """Genera reporte ejecutivo"""
        report = {
            'pipeline_run': {
                'version': self.config['pipeline']['version'],
                'timestamp': datetime.now().isoformat(),
                'status': 'completed'
            },
            'results': self.results,
            'next_steps': [
                'Review generated synthetic conversations',
                'Import to Label Studio',
                'Begin annotation process'
            ]
        }
        
        report_path = f"outputs/reports/pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.logger.info(f"✅ Pipeline completado. Reporte: {report_path}")

def main():
    parser = argparse.ArgumentParser(description='Synthetic Data Pipeline')
    parser.add_argument(
        '--config',
        default='config/pipeline_config.json',
        help='Path to pipeline configuration'
    )
    
    args = parser.parse_args()
    
    # Verificar que existe el config
    if not Path(args.config).exists():
        print(f"❌ Error: No se encuentra {args.config}")
        print("💡 Copia config/pipeline_config_template.json y configura tus API keys")
        sys.exit(1)
    
    # Ejecutar pipeline
    pipeline = SyntheticPipeline(args.config)
    pipeline.run()

if __name__ == '__main__':
    main()