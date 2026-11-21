"""PATRÓN 2 · OBSERVER.

Antes, `procesar` armaba y "enviaba" el email dentro de la misma función.
Ahora el servicio solo publica un evento y los observadores reaccionan.

Roles (refactoring.guru):
  - Publisher (Subject)      -> PublicadorEventos
  - Subscriber (Observer)    -> Observador
  - Concrete Subscribers     -> NotificadorEmail, NotificadorAuditoria (adaptadores/salida/)
  - Client                   -> composicion.py (decide quién se suscribe)
  - Eventos (datos enviados) -> PrestamoRealizado, LibroDevuelto
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class PrestamoRealizado:
    usuario_nombre: str
    usuario_correo: str
    titulo_libro: str
    vence: datetime


@dataclass(frozen=True)
class LibroDevuelto:
    usuario_nombre: str
    usuario_correo: str
    titulo_libro: str
    multa: int


class Observador(ABC):
    """Subscriber: también es el puerto de salida de las notificaciones."""

    @abstractmethod
    def actualizar(self, evento: object) -> None: ...


class PublicadorEventos:
    """Publisher: mantiene la lista de suscriptores y les avisa."""

    def __init__(self) -> None:
        self._observadores: List[Observador] = []

    def suscribir(self, observador: Observador) -> None:
        if observador not in self._observadores:
            self._observadores.append(observador)

    def cancelar(self, observador: Observador) -> None:
        self._observadores.remove(observador)

    def publicar(self, evento: object) -> None:
        for observador in list(self._observadores):
            observador.actualizar(evento)
