-- Ejecutar como administrador en proyecto Supabase EXCLUSIVO y vacio.
-- Cambiar la clave antes de ejecutar; no compartir capturas.
CREATE ROLE hedgedoc_app LOGIN PASSWORD 'REEMPLAZAR_CON_CLAVE_ALEATORIA';
GRANT CONNECT ON DATABASE postgres TO hedgedoc_app;
GRANT USAGE, CREATE ON SCHEMA public TO hedgedoc_app;
-- No otorgar superusuario ni usar postgres/service_role en la aplicacion.
