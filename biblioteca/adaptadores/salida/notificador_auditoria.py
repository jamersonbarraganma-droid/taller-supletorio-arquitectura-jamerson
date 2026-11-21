"""EXTENSIÓN del Observer: un canal NUEVO (bitácora de auditoría).

Se agregó sin modificar PublicadorEventos, ServicioPrestamos ni NotificadorEmail.
"""
from typing import Callable

from ...dominio.eventos import LibroDevuelto, Observador, PrestamoRealizado
from ..formato import pesos


class NotificadorAuditoria(Observador):
    def __init__(self, escribir: Callable[[str], None] = print) -> None:
        self._escribir = escribir

    def actualizar(self, evento: object) -> None:
        if isinstance(evento, PrestamoRealizado):
            self._escribir(f"AUDITORIA: préstamo | {evento.usuario_nombre} | {evento.titulo_libro}")
        elif isinstance(evento, LibroDevuelto):
            self._escribir(
                f"AUDITORIA: devolución | {evento.usuario_nombre} | {evento.titulo_libro} | multa {pesos(evento.multa)}"
            )
