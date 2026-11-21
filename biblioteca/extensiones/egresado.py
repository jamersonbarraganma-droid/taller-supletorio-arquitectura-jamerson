"""EXTENSIÓN del Strategy: un tipo de usuario NUEVO (egresado).

Este archivo es lo único que se escribe. No se modifica Usuario, ni ServicioPrestamos,
ni ninguna otra política: el decorador registra la nueva estrategia.
"""
from ..dominio.politicas import PoliticaPrestamo, registrar_politica


@registrar_politica
class PoliticaEgresado(PoliticaPrestamo):
    tipo = "egresado"
    plazo_dias = 10
    limite_prestamos = 4
    multa_por_dia = 1500
