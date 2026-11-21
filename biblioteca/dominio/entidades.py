"""Entidades y reglas de negocio. No importa nada externo al dominio."""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from .errores import (
    LibroInvalido,
    LibroNoDisponible,
    LimitePrestamosAlcanzado,
    UsuarioInvalido,
)
from .politicas import PoliticaPrestamo, politica_para

LARGO_MINIMO_NOMBRE = 3
SEGUNDOS_POR_DIA = 86400


def validar_id_libro(libro_id: int) -> None:
    if not isinstance(libro_id, int) or isinstance(libro_id, bool) or libro_id <= 0:
        raise LibroInvalido("El id del libro debe ser un número entero positivo.")


@dataclass(frozen=True)
class Usuario:
    """CONTEXT del patrón Strategy: guarda una política y le delega las reglas variables."""

    nombre: str
    correo: str
    politica: PoliticaPrestamo

    def __post_init__(self) -> None:
        if not self.nombre or len(self.nombre.strip()) < LARGO_MINIMO_NOMBRE:
            raise UsuarioInvalido(f"El nombre del usuario debe tener al menos {LARGO_MINIMO_NOMBRE} caracteres.")

    @classmethod
    def crear(cls, nombre: str, correo: str, tipo: str) -> "Usuario":
        return cls(nombre=nombre, correo=correo, politica=politica_para(tipo))

    @property
    def tipo(self) -> str:
        return self.politica.tipo

    def verificar_puede_prestar(self, prestamos_activos: int) -> None:
        limite = self.politica.limite_prestamos
        if prestamos_activos >= limite:
            raise LimitePrestamosAlcanzado(
                f"{self.nombre} ({self.tipo}) ya tiene {prestamos_activos} préstamos activos; el máximo es {limite}."
            )

    def fecha_vencimiento(self, desde: datetime) -> datetime:
        return desde + timedelta(days=self.politica.plazo_dias)

    def multa_por_retraso(self, dias_retraso: int) -> int:
        return self.politica.calcular_multa(dias_retraso)


@dataclass
class Libro:
    id: int
    titulo: str
    disponible: bool = True

    def verificar_disponible(self) -> None:
        if not self.disponible:
            raise LibroNoDisponible(f'El libro "{self.titulo}" ya está prestado; debe devolverse antes de prestarlo de nuevo.')

    def marcar_prestado(self) -> None:
        self.verificar_disponible()
        self.disponible = False

    def marcar_devuelto(self) -> None:
        self.disponible = True


class EstadoPrestamo(str, Enum):
    ACTIVO = "activo"
    DEVUELTO = "devuelto"


@dataclass
class Prestamo:
    usuario: str
    libro_id: int
    prestado_en: datetime
    vence: datetime
    estado: EstadoPrestamo = EstadoPrestamo.ACTIVO
    devuelto_en: Optional[datetime] = None
    multa: int = 0
    id: Optional[int] = None  # lo asigna el repositorio al guardar

    @classmethod
    def crear(cls, usuario: Usuario, libro: Libro, ahora: datetime) -> "Prestamo":
        return cls(
            usuario=usuario.nombre,
            libro_id=libro.id,
            prestado_en=ahora,
            vence=usuario.fecha_vencimiento(ahora),
        )

    @property
    def esta_activo(self) -> bool:
        return self.estado == EstadoPrestamo.ACTIVO

    def dias_de_retraso(self, fecha_devolucion: datetime) -> int:
        diferencia = (fecha_devolucion - self.vence).total_seconds() / SEGUNDOS_POR_DIA
        return max(0, math.ceil(diferencia))

    def cerrar(self, usuario: Usuario, fecha_devolucion: datetime) -> int:
        """Marca el préstamo como devuelto y devuelve la multa calculada."""
        self.multa = usuario.multa_por_retraso(self.dias_de_retraso(fecha_devolucion))
        self.estado = EstadoPrestamo.DEVUELTO
        self.devuelto_en = fecha_devolucion
        return self.multa
