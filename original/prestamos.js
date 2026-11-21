// prestamos.js
var prestamos = [];
var libros = [{ id: 1, titulo: "Clean Code", disponible: true },
              { id: 2, titulo: "Design Patterns", disponible: true }];

function procesar(accion, usuario, libroId, fechaDevolucion) {
  if (accion == "prestar") {
    if (!usuario || !usuario.nombre || usuario.nombre.length < 3) { console.log("Error: usuario invalido"); return; }
    if (!libroId || libroId <= 0) { console.log("Error: libro invalido"); return; }
    var libro = null;
    for (var i = 0; i < libros.length; i++) { if (libros[i].id == libroId) libro = libros[i]; }
    if (!libro.disponible) { console.log("Error: libro no disponible"); return; }
    var activos = 0;
    for (var j = 0; j < prestamos.length; j++) {
      if (prestamos[j].usuario == usuario.nombre && prestamos[j].estado == "activo") activos++;
    }
    if (usuario.tipo == "docente" && activos >= 5) { console.log("Error: limite"); return; }
    if (usuario.tipo != "docente" && activos >= 3) { console.log("Error: limite"); return; }
    var dias = 0;
    if (usuario.tipo == "estudiante") dias = 8;
    else if (usuario.tipo == "docente") dias = 15;
    else if (usuario.tipo == "externo") dias = 3;
    var hoy = new Date();
    var vence = new Date(hoy.getTime() + dias * 86400000);
    prestamos.push({ usuario: usuario.nombre, libro: libroId, vence: vence, estado: "activo" });
    libro.disponible = false;
    console.log("EMAIL a " + usuario.correo + ": prestaste " + libro.titulo + ", vence " + vence);
    document.getElementById("res").innerHTML = "<b>Prestamo OK: " + libro.titulo + "</b>";
  } else if (accion == "devolver") {
    if (!usuario || !usuario.nombre || usuario.nombre.length < 3) { console.log("Error: usuario invalido"); return; }
    if (!libroId || libroId <= 0) { console.log("Error: libro invalido"); return; }
    for (var k = 0; k < prestamos.length; k++) {
      var p = prestamos[k];
      if (p.usuario == usuario.nombre && p.libro == libroId && p.estado == "activo") {
        var retraso = Math.ceil((fechaDevolucion - p.vence) / 86400000);
        var multa = 0;
        if (retraso > 0) {
          if (usuario.tipo == "estudiante") multa = retraso * 1000;
          else if (usuario.tipo == "docente") multa = retraso * 500;
          else if (usuario.tipo == "externo") multa = retraso * 2000;
        }
        p.estado = "devuelto";
        for (var m = 0; m < libros.length; m++) { if (libros[m].id == libroId) libros[m].disponible = true; }
        console.log("EMAIL a " + usuario.correo + ": devolviste el libro. Multa: $" + multa);
        document.getElementById("res").innerHTML = "<b>Devolucion OK. Multa: $" + multa + "</b>";
      }
    }
  }
}
