"""ADAPTADORES DE SALIDA: implementan los puertos guardando todo en memoria."""
from typing import Dict, List, Optional

from ...aplicacion.puertos import RepositorioLibros, RepositorioPrestamos
from ...dominio.entidades import Libro, Prestamo


class RepositorioLibrosMemoria(RepositorioLibros):
    def __init__(self, libros: Optional[List[Libro]] = None) -> None:
        self._libros: Dict[int, Libro] = {l.id: l for l in (libros or [])}

    def obtener(self, libro_id: int) -> Optional[Libro]:
        return self._libros.get(libro_id)

    def guardar(self, libro: Libro) -> None:
        self._libros[libro.id] = libro

    def listar(self) -> List[Libro]:
        return sorted(self._libros.values(), key=lambda l: l.id)


class RepositorioPrestamosMemoria(RepositorioPrestamos):
    def __init__(self) -> None:
        self._prestamos: Dict[int, Prestamo] = {}
        self._siguiente_id = 1

    def guardar(self, prestamo: Prestamo) -> None:
        if prestamo.id is None:
            prestamo.id = self._siguiente_id
            self._siguiente_id += 1
        self._prestamos[prestamo.id] = prestamo

    def buscar_activo(self, usuario_nombre: str, libro_id: int) -> Optional[Prestamo]:
        for p in self._prestamos.values():
            if p.esta_activo and p.usuario == usuario_nombre and p.libro_id == libro_id:
                return p
        return None

    def contar_activos(self, usuario_nombre: str) -> int:
        return sum(1 for p in self._prestamos.values() if p.esta_activo and p.usuario == usuario_nombre)

    def listar(self, solo_activos: bool = False) -> List[Prestamo]:
        todos = list(self._prestamos.values())
        return [p for p in todos if p.esta_activo] if solo_activos else todos
