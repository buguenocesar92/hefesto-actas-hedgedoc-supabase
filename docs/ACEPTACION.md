# Comprobación obligatoria en el servidor
- `docker compose config --quiet`; preflight devuelve usuario hedgedoc_app y ssl=true. Una CA incorrecta debe hacer fallar la conexión, nunca provocar fallback sin TLS.
- Primer arranque completa migraciones sin errores; reiniciar app conserva actas y adjuntos.
- Crear dos cuentas con CLI, entrar por HTTPS y cerrar sesión. Ventana incógnita no permite crear notas ni registrarse.
- Crear nota privada: segundo usuario y visitante no deben leerla. Cambiar conscientemente permisos para colaboración y probar lectura/escritura con dos navegadores; validar WebSocket.
- Subir una imagen no confidencial, comprobar persistencia, comprobar acceso directo a su URL desde incógnito y documentar el resultado. No vender el sistema como repositorio seguro de adjuntos privados.
- Pegar una plantilla, editar simultáneamente, consultar historial y exportar Markdown/HTML. Restaurar contraseña mediante CLI.
- Respaldo con una nota y una imagen identificables; recuperar en otro servidor/base/volumen vacíos y comprobar ambos. Probar rechazo a backup alterado y destino ocupado.
- Terminar override bootstrap; confirmar que no quedan puertos públicos 8116/3000 y que el proxy renueva HTTPS.
Guardar evidencia, fecha, operador y resultado. Cualquier fallo impide dar por aceptada la instalación.
