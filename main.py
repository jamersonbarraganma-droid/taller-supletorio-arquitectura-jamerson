"""Punto de entrada.  python main.py  (menú)   |   python main.py --demo  (recorrido automático)"""
import sys

from biblioteca.adaptadores.entrada.consola import ConsolaBiblioteca
from biblioteca.adaptadores.entrada.demo import ejecutar_demo
from biblioteca.composicion import construir_servicio
from biblioteca.dominio.informe_ia import informe_uso_ia


def main() -> None:
    servicio = construir_servicio()
    if "--demo" in sys.argv:
        ejecutar_demo(servicio)
    elif "--informe-ia" in sys.argv:
        print(informe_uso_ia())
    else:
        ConsolaBiblioteca(servicio).ejecutar()


if __name__ == "__main__":
    main()
