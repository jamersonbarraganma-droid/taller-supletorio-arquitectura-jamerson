"""ADAPTADOR DE ENTRADA (consola). Solo lee, llama al caso de uso y muestra.

No contiene reglas de negocio: todo error de negocio llega como ErrorDeDominio.
"""
from datetime import datetime
from typing import Callable

from ...aplicacion.servicio_prestamos import ServicioPrestamos
from ...dominio.entidades import Usuario
from ...dominio.errores import ErrorDeDominio
from ...dominio.politicas import tipos_disponibles
from ..formato import pesos

MENU = """
=== Biblioteca ===
1. Prestar un libro
2. Devolver un libro
3. Consultar un libro
4. Listar libros
5. Listar préstamos
0. Salir"""


class ConsolaBiblioteca:
    def __init__(self, servicio: ServicioPrestamos, entrada: Callable[[str], str] = input,
                 salida: Callable[[str], None] = print) -> None:
        self._servicio = servicio
        self._entrada = entrada
        self._salida = salida

    def ejecutar(self) -> None:
        acciones = {
            "1": self._prestar, "2": self._devolver, "3": self._consultar,
            "4": self._listar_libros, "5": self._listar_prestamos,
        }
        while True:
            self._salida(MENU)
            opcion = self._entrada("Opción: ").strip()
            if opcion == "0":
                return
            accion = acciones.get(opcion)
            if accion is None:
                self._salida("Opción no válida.")
                continue
            try:
                accion()
            except ErrorDeDominio as error:
                self._salida(f"Error: {error}")
            except ValueError as error:
                self._salida(f"Dato inválido: {error}")

    # --- lectura de datos --------------------------------------------------------
    def _leer_usuario(self) -> Usuario:
        nombre = self._entrada("Nombre: ")
        correo = self._entrada("Correo: ")
        tipo = self._entrada(f"Tipo ({', '.join(tipos_disponibles())}): ")
        return Usuario.crear(nombre, correo, tipo)

    def _leer_libro_id(self) -> int:
        return int(self._entrada("Id del libro: "))

    # --- acciones ----------------------------------------------------------------
    def _prestar(self) -> None:
        prestamo = self._servicio.prestar(self._leer_usuario(), self._leer_libro_id())
        self._salida(f"Préstamo OK. Vence el {prestamo.vence:%Y-%m-%d}.")

    def _devolver(self) -> None:
        usuario, libro_id = self._leer_usuario(), self._leer_libro_id()
        texto = self._entrada("Fecha de devolución AAAA-MM-DD (Enter = hoy): ").strip()
        fecha = datetime.fromisoformat(texto) if texto else None
        prestamo = self._servicio.devolver(usuario, libro_id, fecha)
        self._salida(f"Devolución OK. Multa: {pesos(prestamo.multa)}")

    def _consultar(self) -> None:
        libro = self._servicio.consultar_libro(self._leer_libro_id())
        estado = "disponible" if libro.disponible else "prestado"
        self._salida(f"#{libro.id} {libro.titulo}: {estado}")

    def _listar_libros(self) -> None:
        for libro in self._servicio.listar_libros():
            estado = "disponible" if libro.disponible else "prestado"
            self._salida(f"#{libro.id} {libro.titulo} - {estado}")

    def _listar_prestamos(self) -> None:
        prestamos = self._servicio.listar_prestamos()
        if not prestamos:
            self._salida("No hay préstamos registrados.")
        for p in prestamos:
            self._salida(f"#{p.id} {p.usuario} | libro {p.libro_id} | {p.estado.value} | vence {p.vence:%Y-%m-%d} | multa {pesos(p.multa)}")
