"""PATRÓN 1 · STRATEGY.

Cada tipo de usuario tiene su propia política (plazo, límite y multa).
Antes esto eran tres cadenas if/else repartidas por la función `procesar`.

Roles (refactoring.guru):
  - Strategy            -> PoliticaPrestamo
  - Concrete Strategies -> PoliticaEstudiante, PoliticaDocente, PoliticaExterno
  - Context             -> Usuario (en entidades.py)
  - Client              -> Usuario.crear(), que elige la estrategia con politica_para()
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Type

from .errores import TipoUsuarioDesconocido


class PoliticaPrestamo(ABC):
    """Strategy: lo que cambia según el tipo de usuario."""

    @property
    @abstractmethod
    def tipo(self) -> str: ...

    @property
    @abstractmethod
    def plazo_dias(self) -> int: ...

    @property
    @abstractmethod
    def limite_prestamos(self) -> int: ...

    @property
    @abstractmethod
    def multa_por_dia(self) -> int: ...

    def calcular_multa(self, dias_retraso: int) -> int:
        """Una política puede sobrescribir esto si su multa no es lineal."""
        return max(0, dias_retraso) * self.multa_por_dia


# ---- Registro de estrategias -------------------------------------------------
# Agregar un tipo de usuario = escribir una clase nueva y decorarla.
# No hay que tocar ningún if/else.
_REGISTRO: Dict[str, PoliticaPrestamo] = {}


def registrar_politica(clase: Type[PoliticaPrestamo]) -> Type[PoliticaPrestamo]:
    """Decorador: instancia la política y la guarda por su tipo."""
    politica = clase()
    _REGISTRO[politica.tipo] = politica
    return clase


def politica_para(tipo: str) -> PoliticaPrestamo:
    clave = (tipo or "").strip().lower()
    if clave not in _REGISTRO:
        validos = ", ".join(sorted(_REGISTRO))
        raise TipoUsuarioDesconocido(f'Tipo de usuario "{tipo}" no reconocido. Válidos: {validos}.')
    return _REGISTRO[clave]


def tipos_disponibles() -> List[str]:
    return sorted(_REGISTRO)


# ---- Estrategias concretas (valores del enunciado) ---------------------------
@registrar_politica
class PoliticaEstudiante(PoliticaPrestamo):
    tipo = "estudiante"
    plazo_dias = 8
    limite_prestamos = 3
    multa_por_dia = 1000


@registrar_politica
class PoliticaDocente(PoliticaPrestamo):
    tipo = "docente"
    plazo_dias = 15
    limite_prestamos = 5
    multa_por_dia = 500


@registrar_politica
class PoliticaExterno(PoliticaPrestamo):
    tipo = "externo"
    plazo_dias = 3
    limite_prestamos = 3
    multa_por_dia = 2000
