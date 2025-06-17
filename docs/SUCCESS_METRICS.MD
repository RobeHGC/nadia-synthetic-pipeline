success_metrics = {
    "auto_calibration_agreement": ">= 90%",
    "llm_review_rate": "< 20%",  # Menos del 20% requiere corrección
    "distribution_balance": {
        "no_category_over": "40%",  # Ninguna categoría domina
        "OTHER_under": "5%"  # Mínimo uso de OTHER
    },
    "safety_coverage": {
        "LEVEL_1+": ">= 5%",  # Al menos 5% con algún nivel de riesgo
        "LEVEL_3_examples": ">= 10"  # Mínimo 10 ejemplos críticos
    }
}