"""COMPOSITION ROOT: el único lugar donde se eligen las piezas concretas.

Cambiar de repositorio, agregar un canal de notificación o activar un tipo de usuario
nuevo se hace aquí, con una línea, sin tocar dominio ni aplicación.
"""
from typing import Callable

from .adaptadores.salida.notificador_auditoria import NotificadorAuditoria
from .adaptadores.salida.notificador_email import NotificadorEmail
from .adaptadores.salida.repositorio_memoria import RepositorioLibrosMemoria, RepositorioPrestamosMemoria
from .aplicacion.servicio_prestamos import ServicioPrestamos
from .dominio.entidades import Libro
from .dominio.eventos import PublicadorEventos
from .extensiones import egresado  # noqa: F401  (registra el tipo "egresado")


def construir_servicio(escribir: Callable[[str], None] = print) -> ServicioPrestamos:
    libros = RepositorioLibrosMemoria([
        Libro(1, "Clean Code"),
        Libro(2, "Design Patterns"),
        Libro(3, "Refactoring"),
        Libro(4, "The Pragmatic Programmer"),
        Libro(5, "Clean Architecture"),
    ])
    prestamos = RepositorioPrestamosMemoria()

    publicador = PublicadorEventos()
    publicador.suscribir(NotificadorEmail(escribir))
    publicador.suscribir(NotificadorAuditoria(escribir))  # canal agregado como extensión

    return ServicioPrestamos(libros, prestamos, publicador)
