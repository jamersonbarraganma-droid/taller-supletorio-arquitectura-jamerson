"""CASOS DE USO. Orquestan el dominio y los puertos; las reglas viven en el dominio."""
from datetime import datetime
from typing import Callable, List, Optional

from ..dominio.entidades import Libro, Prestamo, Usuario, validar_id_libro
from ..dominio.errores import LibroNoEncontrado, PrestamoNoEncontrado
from ..dominio.eventos import LibroDevuelto, PrestamoRealizado, PublicadorEventos
from .puertos import RepositorioLibros, RepositorioPrestamos


class ServicioPrestamos:
    def __init__(
        self,
        libros: RepositorioLibros,
        prestamos: RepositorioPrestamos,
        publicador: PublicadorEventos,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._libros = libros
        self._prestamos = prestamos
        self._publicador = publicador
        self._reloj = reloj  # inyectable para poder probar fechas

    # --- crear -----------------------------------------------------------------
    def prestar(self, usuario: Usuario, libro_id: int) -> Prestamo:
        libro = self._obtener_libro(libro_id)
        libro.verificar_disponible()
        usuario.verificar_puede_prestar(self._prestamos.contar_activos(usuario.nombre))

        prestamo = Prestamo.crear(usuario, libro, self._reloj())
        libro.marcar_prestado()
        self._prestamos.guardar(prestamo)
        self._libros.guardar(libro)

        self._publicador.publicar(
            PrestamoRealizado(usuario.nombre, usuario.correo, libro.titulo, prestamo.vence)
        )
        return prestamo

    # --- cierre ----------------------------------------------------------------
    def devolver(self, usuario: Usuario, libro_id: int, fecha_devolucion: Optional[datetime] = None) -> Prestamo:
        libro = self._obtener_libro(libro_id)
        prestamo = self._prestamos.buscar_activo(usuario.nombre, libro_id)
        if prestamo is None:
            raise PrestamoNoEncontrado(
                f'{usuario.nombre} no tiene un préstamo activo del libro "{libro.titulo}".'
            )

        multa = prestamo.cerrar(usuario, fecha_devolucion or self._reloj())
        libro.marcar_devuelto()
        self._prestamos.guardar(prestamo)
        self._libros.guardar(libro)

        self._publicador.publicar(LibroDevuelto(usuario.nombre, usuario.correo, libro.titulo, multa))
        return prestamo

    # --- consultar y listar ----------------------------------------------------
    def consultar_libro(self, libro_id: int) -> Libro:
        return self._obtener_libro(libro_id)

    def listar_libros(self) -> List[Libro]:
        return self._libros.listar()

    def listar_prestamos(self, solo_activos: bool = False) -> List[Prestamo]:
        return self._prestamos.listar(solo_activos)

    # --- interno ---------------------------------------------------------------
    def _obtener_libro(self, libro_id: int) -> Libro:
        validar_id_libro(libro_id)
        libro = self._libros.obtener(libro_id)
        if libro is None:
            raise LibroNoEncontrado(f"No existe un libro con id {libro_id}.")
        return libro
