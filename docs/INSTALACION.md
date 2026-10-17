# Instalación y Coolify
Recursos iniciales orientativos: 2 vCPU, 2 GB RAM y espacio para adjuntos/respaldo; ajustar con medición. Se necesita Docker Compose v2 y Python 3.11+ en el host para los scripts.

En Coolify usar el repositorio privado con compose.yaml, montar ops y certs, introducir las variables .env, conservar el volumen uploads y asignar https://actas.tudominio.cl al servicio app, puerto interno 3000. Configurar WebSocket y timeouts para sesiones colaborativas largas. No publicar dbtools ni filetools. Certificado público y renovación pertenecen al proxy de Coolify. Evitar dos proxies TLS encadenados.

La imagen oficial entra como root para ajustar permisos de uploads y usa gosu para ejecutar HedgeDoc como hedgedoc. Se conserva su entrypoint; no forzar user ni no-new-privileges sin verificar el arranque. La CA pública está montada solo lectura. El módulo config.cjs utiliza dialectOptions.ssl de Sequelize con rejectUnauthorized=true; no se usa sslmode ambiguo en URL ni NODE_TLS_REJECT_UNAUTHORIZED=0.

El host Supabase debe ser el endpoint directo del proyecto; si no hay ruta IPv6, contratar/configurar conectividad compatible o preparar y validar una adaptación al pooler en modo sesión. Este kit no adapta automáticamente el usuario a poolers. No exponer PostgreSQL adicional local.

Primera inicialización opcional por túnel: ejecutar `docker compose -f compose.yaml -f compose.bootstrap.yaml up -d app` en servidor; desde tu equipo `ssh -N -L 3000:127.0.0.1:8116 usuario@servidor`, abrir http://localhost:3000. La aplicación sigue escuchando 3000, el puerto 8116 queda solo en loopback remoto. Finalizar con `docker compose -f compose.yaml -f compose.bootstrap.yaml down` sin -v; iniciar luego solo compose.yaml para eliminar el puerto temporal. No usar override HTTP en producción.

La creación de cuentas se hace después de migraciones. No hay administrador global de clientes prometido por el kit. Restablecimiento nativo: `docker compose exec app /hedgedoc/bin/manage_users --reset persona@empresa.cl`. No borrar usuarios como sustituto de revocar acceso a documentos sin revisar propiedad de notas.

Supabase contiene contenido completo de notas e historial. No publicar las tablas por REST, no entregar anon/service_role al navegador. Mantener proyecto, credenciales y copias bajo control del operador; para una instancia sensible revisar Data API, acceso a public y política del proyecto desde su panel. No usar el SQL en una base con tablas de otro producto.
