"""Convención obligatoria del curso para el Caso A."""

HERRAMIENTA = "Claude Sonnet 5.5 (Anthropic)"
PORCENTAJE_IA = 90  # <- AJÚSTALO a tu realidad; debe coincidir con INFORME_IA.md
CODIGO_CURSO = "ARQ-ZAF-A"


def informe_uso_ia() -> str:
    return (
        f"Herramienta usada: {HERRAMIENTA}. "
        f"Porcentaje estimado de código generado con asistencia de IA: {PORCENTAJE_IA}%. "
        f"Código: {CODIGO_CURSO}"
    )
