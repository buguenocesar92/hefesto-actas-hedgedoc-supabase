# Hefesto Actas · HedgeDoc 1.12.0 + Supabase
Kit nativo para actas colaborativas en Markdown, historial y exportación. Imagen oficial fijada por digest; PostgreSQL externo y adjuntos persistentes. Sin frontend simulado ni datos de clientes precargados.

## Qué está entregado
Compose para Coolify, configuración TLS con CA, registro cerrado, notas privadas por defecto, scripts de respaldo/restauración, tres plantillas y guía de operación. No incluye conexión desplegada, cuentas creadas ni integración automática con Odoo.

## Arranque
1. Leer docs/INSTALACION.md. Usar un proyecto Supabase dedicado con PostgreSQL 16/17; no una base compartida con aplicaciones anteriores. Conexión directa 5432, no pooler transaccional. El servidor debe poder alcanzar el host, incluida IPv6 si corresponde.
2. `python3 scripts/configure.py`. Editar `.env` y descargar CA real a `certs/ca.crt`. Usar contraseña aleatoria alfanumérica de 32 o más caracteres, la misma en SQL y .env. Nunca subir .env a Git.
3. Ejecutar sql/01-admin.sql con clave real como administrador Supabase. La aplicación utiliza exclusivamente hedgedoc_app.
4. `docker compose config --quiet`
5. `docker compose run --rm --no-deps -T --entrypoint psql dbtools --no-psqlrc -v ON_ERROR_STOP=1 -f /dev/stdin < sql/02-preflight.sql`
6. Configurar proxy HTTPS para app:3000 con WebSocket. `docker compose up -d app`. HedgeDoc ejecuta migraciones nativas al iniciar. Esperar logs sin errores.
7. Crear cuentas desde terminal: `docker compose exec app /hedgedoc/bin/manage_users --add persona@empresa.cl`. La contraseña se solicita de forma oculta. No usar --pass en historial. Probar dos sesiones según docs/ACEPTACION.md.

## Alcance de seguridad
Las notas nuevas son privadas; su propietario puede cambiar los permisos y publicarlas. Desactivar creación anónima no impide leer notas que se hayan hecho públicas. Los archivos subidos se sirven mediante sus URL: no se debe asumir que heredan el permiso privado de la nota. No usar adjuntos confidenciales sin una capa adicional de control comprobada. Para separar clientes, desplegar una instancia/proyecto por cliente.

El login local no ofrece MFA ni recuperación automática de contraseña; el operador usa manage_users --reset. No requiere SMTP. Para MFA, evaluar un proveedor externo mediante la configuración nativa y ensayarlo antes de activarlo.

## Entrega y validación
Se revisaron fuentes oficiales, YAML, sintaxis y guardas locales de integridad/restauración. No hay Docker en el entorno de preparación: falta ejecutar imagen, TLS, migraciones, colaboración, backup y recuperación reales. No se afirma aceptación productiva.

## Despliegue en Coolify (MVP Hefesto)
El compose cumple el contrato del MVP Hefesto para Coolify (servicios sin `profiles` no publican puertos ni toman poderes de host; sin `name:` fijo). Variables nuevas que el operador define en Coolify:

- `DB_NAME` (opcional, defecto `postgres`): nombre de la base dentro del Postgres compartido. Para multi-app, usar `mvp_<slug>`.
- `DB_USER` (opcional, defecto `hedgedoc_app`): rol con el que HedgeDoc conecta. Coincidir con el creado en `sql/01-admin.sql`.
- `DB_SSLMODE` (opcional, defecto `verify-full`): modo SSL de Sequelize. Si se usa algo distinto de `verify-full`/`verify-ca`, la CA deja de ser obligatoria y `ops/config.cjs` no aborta al faltarla.
- `DB_ALLOW_INTERNAL_HOST` (opcional, defecto `false`): permite hosts que no terminen en `.supabase.co`/`.supabase.com`. Útil con bases internas en la misma red Docker; también se acepta implícitamente cuando `DB_SSLMODE=disable`.
- `DB_ALLOW_INSECURE_SSL` (opcional, defecto `false`): exige `true` para activar `DB_SSLMODE=require` (cifrado sin verificación de CA, vulnerable a MITM). Operador debe confirmarlo explícitamente.

Las cuentas se crean tras las migraciones con la CLI nativa:
`docker compose exec app /hedgedoc/bin/manage_users --add persona@empresa.cl`.
