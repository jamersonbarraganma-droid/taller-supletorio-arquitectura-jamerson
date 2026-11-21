"""Formato de presentación compartido por los adaptadores."""


def pesos(valor: int) -> str:
    return "$" + f"{valor:,}".replace(",", ".")
