"""Recorrido automático para mostrar todo funcionando (útil para el video)."""
from datetime import timedelta

from ...aplicacion.servicio_prestamos import ServicioPrestamos
from ...dominio.entidades import Usuario
from ...dominio.errores import ErrorDeDominio
from ..formato import pesos


def _intentar(descripcion: str, accion):
    print(f"\n--- {descripcion}")
    try:
        return accion()
    except ErrorDeDominio as error:
        print(f"Error de negocio ({type(error).__name__}): {error}")


def ejecutar_demo(servicio: ServicioPrestamos) -> None:
    ana = Usuario.crear("Ana Gómez", "ana@correo.com", "estudiante")
    luis = Usuario.crear("Luis Pérez", "luis@correo.com", "externo")
    marta = Usuario.crear("Marta Ríos", "marta@correo.com", "egresado")  # tipo de la extensión

    _intentar("Ana (estudiante) presta el libro 1", lambda: servicio.prestar(ana, 1))
    _intentar("Alguien intenta prestar el libro 1 otra vez", lambda: servicio.prestar(luis, 1))
    _intentar("Libro que no existe (id 99)", lambda: servicio.prestar(ana, 99))
    for libro_id in (2, 3, 4):
        extra = " (4.º préstamo activo: supera el límite de 3)" if libro_id == 4 else ""
        _intentar(f"Ana presta el libro {libro_id}{extra}", lambda i=libro_id: servicio.prestar(ana, i))
    prestamo_luis = _intentar("Luis (externo) presta el libro 5", lambda: servicio.prestar(luis, 5))
    _intentar("Marta (egresado, tipo nuevo) intenta prestar el libro 1 (todavía ocupado)", lambda: servicio.prestar(marta, 1))
    _intentar("Ana devuelve el libro 1 a tiempo", lambda: servicio.devolver(ana, 1))
    if prestamo_luis:
        tarde = prestamo_luis.vence + timedelta(days=5)
        _intentar("Luis devuelve el libro 5 con 5 días de retraso (externo: $2.000/día)",
                  lambda: servicio.devolver(luis, 5, tarde))
    _intentar("Luis intenta devolver un libro que no tiene", lambda: servicio.devolver(luis, 2))
    _intentar("Marta (egresado) presta el libro 1", lambda: servicio.prestar(marta, 1))

    print("\n--- Libros")
    for libro in servicio.listar_libros():
        print(f"#{libro.id} {libro.titulo}: {'disponible' if libro.disponible else 'prestado'}")
    print("\n--- Préstamos")
    for p in servicio.listar_prestamos():
        print(f"#{p.id} {p.usuario} | libro {p.libro_id} | {p.estado.value} | multa {pesos(p.multa)}")
