"""Concrete Subscriber (Observer): "envía" emails (los escribe en consola)."""
from typing import Callable

from ...dominio.eventos import LibroDevuelto, Observador, PrestamoRealizado
from ..formato import pesos


class NotificadorEmail(Observador):
    def __init__(self, escribir: Callable[[str], None] = print) -> None:
        self._escribir = escribir

    def actualizar(self, evento: object) -> None:
        if isinstance(evento, PrestamoRealizado):
            self._escribir(
                f"EMAIL a {evento.usuario_correo}: prestaste {evento.titulo_libro}, "
                f"vence {evento.vence:%Y-%m-%d}"
            )
        elif isinstance(evento, LibroDevuelto):
            self._escribir(
                f"EMAIL a {evento.usuario_correo}: devolviste {evento.titulo_libro}. Multa: {pesos(evento.multa)}"
            )
