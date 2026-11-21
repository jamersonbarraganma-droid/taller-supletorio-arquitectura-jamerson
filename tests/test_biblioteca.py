import unittest
from datetime import datetime, timedelta

from biblioteca.adaptadores.salida.notificador_auditoria import NotificadorAuditoria
from biblioteca.adaptadores.salida.notificador_email import NotificadorEmail
from biblioteca.adaptadores.salida.repositorio_memoria import RepositorioLibrosMemoria, RepositorioPrestamosMemoria
from biblioteca.aplicacion.servicio_prestamos import ServicioPrestamos
from biblioteca.dominio.entidades import Libro, Usuario
from biblioteca.dominio.errores import (
    LibroInvalido, LibroNoDisponible, LibroNoEncontrado, LimitePrestamosAlcanzado,
    PrestamoNoEncontrado, TipoUsuarioDesconocido, UsuarioInvalido,
)
from biblioteca.dominio.eventos import LibroDevuelto, Observador, PrestamoRealizado, PublicadorEventos
from biblioteca.dominio.informe_ia import informe_uso_ia

AHORA = datetime(2026, 11, 21, 10, 0)


class EspiaObservador(Observador):
    def __init__(self):
        self.eventos = []

    def actualizar(self, evento):
        self.eventos.append(evento)


def crear_servicio(n_libros=6):
    libros = RepositorioLibrosMemoria([Libro(i, f"Libro {i}") for i in range(1, n_libros + 1)])
    publicador = PublicadorEventos()
    espia = EspiaObservador()
    publicador.suscribir(espia)
    servicio = ServicioPrestamos(libros, RepositorioPrestamosMemoria(), publicador, reloj=lambda: AHORA)
    return servicio, espia, publicador


def usuario(tipo, nombre="Ana Gómez"):
    return Usuario.crear(nombre, "ana@correo.com", tipo)


class PruebasStrategy(unittest.TestCase):
    def test_plazo_limite_y_multa_por_tipo(self):
        esperado = {  # tipo: (plazo, límite, multa por día)
            "estudiante": (8, 3, 1000),
            "docente": (15, 5, 500),
            "externo": (3, 3, 2000),
        }
        for tipo, (plazo, limite, multa) in esperado.items():
            with self.subTest(tipo=tipo):
                u = usuario(tipo)
                self.assertEqual(u.fecha_vencimiento(AHORA), AHORA + timedelta(days=plazo))
                self.assertEqual(u.politica.limite_prestamos, limite)
                self.assertEqual(u.multa_por_retraso(2), 2 * multa)
                self.assertEqual(u.multa_por_retraso(0), 0)

    def test_tipo_desconocido(self):
        with self.assertRaises(TipoUsuarioDesconocido):
            usuario("alienigena")

    def test_extension_egresado_sin_modificar_codigo_existente(self):
        from biblioteca.extensiones import egresado  # noqa: F401
        u = usuario("egresado")
        self.assertEqual(u.fecha_vencimiento(AHORA), AHORA + timedelta(days=10))
        self.assertEqual(u.politica.limite_prestamos, 4)
        self.assertEqual(u.multa_por_retraso(2), 3000)


class PruebasPrestar(unittest.TestCase):
    def test_prestar_ok(self):
        servicio, _, _ = crear_servicio()
        p = servicio.prestar(usuario("estudiante"), 1)
        self.assertEqual(p.vence, AHORA + timedelta(days=8))
        self.assertFalse(servicio.consultar_libro(1).disponible)

    def test_libro_no_se_presta_dos_veces(self):
        servicio, _, _ = crear_servicio()
        servicio.prestar(usuario("estudiante"), 1)
        with self.assertRaises(LibroNoDisponible):
            servicio.prestar(usuario("docente", "Pedro Docente"), 1)

    def test_limite_estudiante_3_y_docente_5(self):
        servicio, _, _ = crear_servicio()
        est, doc = usuario("estudiante"), usuario("docente", "Pedro Docente")
        for i in (1, 2, 3):
            servicio.prestar(est, i)
        with self.assertRaises(LimitePrestamosAlcanzado):
            servicio.prestar(est, 4)
        for i in (4, 5, 6):
            servicio.prestar(doc, i)  # el docente puede tener más de 3
        self.assertEqual(len(servicio.listar_prestamos(solo_activos=True)), 6)

    def test_limite_docente_5(self):
        servicio, _, _ = crear_servicio(n_libros=6)
        doc = usuario("docente", "Pedro Docente")
        for i in range(1, 6):
            servicio.prestar(doc, i)
        with self.assertRaises(LimitePrestamosAlcanzado):
            servicio.prestar(doc, 6)

    def test_libro_inexistente_o_invalido(self):
        servicio, _, _ = crear_servicio()
        with self.assertRaises(LibroNoEncontrado):
            servicio.prestar(usuario("estudiante"), 99)
        for malo in (0, -1):
            with self.assertRaises(LibroInvalido):
                servicio.prestar(usuario("estudiante"), malo)

    def test_usuario_invalido(self):
        with self.assertRaises(UsuarioInvalido):
            Usuario.crear("Al", "a@correo.com", "estudiante")


class PruebasDevolver(unittest.TestCase):
    def test_devolver_a_tiempo_sin_multa(self):
        servicio, _, _ = crear_servicio()
        u = usuario("estudiante")
        p = servicio.prestar(u, 1)
        servicio.devolver(u, 1, p.vence)
        self.assertEqual(p.multa, 0)
        self.assertTrue(servicio.consultar_libro(1).disponible)

    def test_multa_por_retraso_segun_tipo(self):
        for tipo, por_dia in (("estudiante", 1000), ("docente", 500), ("externo", 2000)):
            with self.subTest(tipo=tipo):
                servicio, _, _ = crear_servicio()
                u = usuario(tipo)
                p = servicio.prestar(u, 1)
                servicio.devolver(u, 1, p.vence + timedelta(days=4))
                self.assertEqual(p.multa, 4 * por_dia)

    def test_fraccion_de_dia_cuenta_como_dia_completo(self):
        servicio, _, _ = crear_servicio()
        u = usuario("estudiante")
        p = servicio.prestar(u, 1)
        servicio.devolver(u, 1, p.vence + timedelta(hours=1))
        self.assertEqual(p.multa, 1000)

    def test_devolver_sin_prestamo(self):
        servicio, _, _ = crear_servicio()
        with self.assertRaises(PrestamoNoEncontrado):
            servicio.devolver(usuario("estudiante"), 1)

    def test_libro_se_puede_prestar_de_nuevo_tras_devolver(self):
        servicio, _, _ = crear_servicio()
        u = usuario("estudiante")
        servicio.prestar(u, 1)
        servicio.devolver(u, 1)
        servicio.prestar(usuario("docente", "Pedro Docente"), 1)


class PruebasObserver(unittest.TestCase):
    def test_se_publican_eventos(self):
        servicio, espia, _ = crear_servicio()
        u = usuario("externo")
        p = servicio.prestar(u, 1)
        servicio.devolver(u, 1, p.vence + timedelta(days=1))
        self.assertIsInstance(espia.eventos[0], PrestamoRealizado)
        self.assertIsInstance(espia.eventos[1], LibroDevuelto)
        self.assertEqual(espia.eventos[1].multa, 2000)

    def test_no_se_publica_nada_si_la_regla_falla(self):
        servicio, espia, _ = crear_servicio()
        with self.assertRaises(LibroNoEncontrado):
            servicio.prestar(usuario("estudiante"), 99)
        self.assertEqual(espia.eventos, [])

    def test_canales_nuevos_sin_modificar_el_servicio(self):
        servicio, _, publicador = crear_servicio()
        salida = []
        publicador.suscribir(NotificadorEmail(salida.append))
        publicador.suscribir(NotificadorAuditoria(salida.append))
        servicio.prestar(usuario("estudiante"), 1)
        self.assertTrue(any(l.startswith("EMAIL a ana@correo.com") for l in salida))
        self.assertTrue(any(l.startswith("AUDITORIA") for l in salida))


class PruebasConvencionCurso(unittest.TestCase):
    def test_informe_uso_ia(self):
        texto = informe_uso_ia()
        self.assertIn("ARQ-ZAF-A", texto)
        self.assertIn("%", texto)


if __name__ == "__main__":
    unittest.main()
