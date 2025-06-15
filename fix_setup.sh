#!/bin/bash
echo "🔧 Reparando setup del proyecto..."

# 1. Asegurar que .gitignore está bien configurado
if ! grep -q "config/pipeline_config.json" .gitignore 2>/dev/null; then
    echo "config/pipeline_config.json" >> .gitignore
fi

if ! grep -q "data/raw/" .gitignore 2>/dev/null; then
    echo "data/raw/*" >> .gitignore
    echo "!data/raw/.gitkeep" >> .gitignore
fi

# 2. Verificar permisos
chmod 600 config/pipeline_config.json 2>/dev/null || true
chmod 700 data/raw

# 3. Crear archivos .gitkeep faltantes
touch data/raw/.gitkeep
touch data/anonymized/.gitkeep
touch data/patterns/.gitkeep
touch data/synthetic/.gitkeep
touch data/labeled/.gitkeep
touch outputs/reports/.gitkeep
touch outputs/exports/.gitkeep
touch outputs/checkpoints/.gitkeep
touch logs/.gitkeep

echo "✅ Reparación completada"
