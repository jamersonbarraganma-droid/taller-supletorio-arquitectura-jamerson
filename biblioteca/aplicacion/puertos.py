"""PUERTOS DE SALIDA (interfaces) que la aplicación necesita del mundo exterior.

El otro puerto de salida, las notificaciones, es `Observador` (dominio/eventos.py).
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..dominio.entidades import Libro, Prestamo


class RepositorioLibros(ABC):
    @abstractmethod
    def obtener(self, libro_id: int) -> Optional[Libro]: ...

    @abstractmethod
    def guardar(self, libro: Libro) -> None: ...

    @abstractmethod
    def listar(self) -> List[Libro]: ...


class RepositorioPrestamos(ABC):
    @abstractmethod
    def guardar(self, prestamo: Prestamo) -> None: ...

    @abstractmethod
    def buscar_activo(self, usuario_nombre: str, libro_id: int) -> Optional[Prestamo]: ...

    @abstractmethod
    def contar_activos(self, usuario_nombre: str) -> int: ...

    @abstractmethod
    def listar(self, solo_activos: bool = False) -> List[Prestamo]: ...
