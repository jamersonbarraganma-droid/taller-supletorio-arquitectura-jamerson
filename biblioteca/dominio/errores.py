"""Errores del dominio: una clase por cada regla de negocio que se puede romper.

Los adaptadores de entrada solo necesitan capturar ErrorDeDominio y mostrar el mensaje.
"""


class ErrorDeDominio(Exception):
    """Base de todos los errores de negocio."""


class UsuarioInvalido(ErrorDeDominio):
    pass


class TipoUsuarioDesconocido(ErrorDeDominio):
    pass


class LibroInvalido(ErrorDeDominio):
    pass


class LibroNoEncontrado(ErrorDeDominio):
    pass


class LibroNoDisponible(ErrorDeDominio):
    pass


class LimitePrestamosAlcanzado(ErrorDeDominio):
    pass


class PrestamoNoEncontrado(ErrorDeDominio):
    pass
