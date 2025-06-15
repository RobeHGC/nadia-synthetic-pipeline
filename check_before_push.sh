#!/bin/bash
echo "🔍 Verificando seguridad antes de push..."

# Lista de archivos que NUNCA deben estar en el repo
FORBIDDEN_FILES=(
    "config/pipeline_config.json"
    "config/.env"
    "data/raw/*.json"
    "data/raw/*.csv"
    "data/anonymized/*.json"
    "*.key"
    "*.pem"
)

# Verificar cada archivo
SAFE=true
for pattern in "${FORBIDDEN_FILES[@]}"; do
    if git ls-files | grep -q "$pattern"; then
        echo "❌ PELIGRO: Encontrado $pattern en git!"
        SAFE=false
    fi
done

# Verificar que no hay API keys en el código
if grep -r "sk-" scripts/ 2>/dev/null | grep -v "YOUR_.*_KEY"; then
    echo "❌ PELIGRO: Posible API key encontrada!"
    SAFE=false
fi

if [ "$SAFE" = true ]; then
    echo "✅ Verificación pasada - seguro para push"
else
    echo "🛑 NO HAGAS PUSH - Corrige los problemas primero"
    exit 1
fi
