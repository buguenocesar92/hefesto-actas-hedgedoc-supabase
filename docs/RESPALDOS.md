# Respaldo y recuperación
Ejecutar desde host con Python y Docker: `python3 scripts/backup.py`. Detiene app, obtiene pg_dump de public y tar del volumen uploads; copia configuración, secretos y CA. Solo marca completed si todos terminan; reinicia la app si antes estaba activa, incluso ante un fallo de copia. La pausa impide ediciones mientras se obtiene el conjunto coherente. No cubre configuración del proyecto Supabase, roles, políticas fuera de public, proveedor de identidad o proxy TLS.

`python3 scripts/check_backup.py backups/FECHA` verifica lista exacta, SHA256 y seguridad de rutas del tar. Un checksum no autentica una copia frente a un atacante que puede cambiar también el manifiesto. Cifrar y guardar fuera del servidor; restringir acceso, definir retención y ensayar recuperación periódica. Los backups contienen documentos, hashes de cuentas, adjuntos y secreto de sesión.

Restaurar en un servidor de ensayo nuevo: mismo kit/configuración y versión, nueva base dedicada con public vacío, rol creado y volumen uploads vacío. Crear .env de destino con el SESSION_SECRET original; cambiar solo host/clave/CA necesarios. Conservar los archivos del kit idénticos al respaldo. No iniciar app antes de restaurar.

`python3 scripts/restore.py /ruta/respaldo --accept-restored-content`

El script verifica checksums y tar antes de escribir, exige servicios detenidos, base/volumen vacíos y secreto original. No ejecuta DROP ni sobrescribe una instalación ocupada. Restaura public en transacción, después archivos, y deja la app detenida. Si falla la fase de archivos tras completar la base, considerar el destino incompleto y repetir sobre otro destino vacío; no hay transacción distribuida entre DB y volumen.

Al iniciar app el entrypoint oficial corrige propietario de uploads. Antes del ensayo, restringir salida del entorno permitiendo DNS y el endpoint Supabase: una red Docker internal impediría también conectarse a la base. No se suministra una supuesta red aislada incompatible con PostgreSQL externo. Usar hostname de ensayo y comprobar permisos de notas y archivos: una copia puede recuperar contenido eliminado o permisos públicos antiguos. Al migrar dominio revisar enlaces absolutos en las actas.
