'use strict';
const fs = require('fs');
for (const k of ['CMD_DB_HOST','CMD_DB_PASSWORD','CMD_SESSION_SECRET']) {
  if (!process.env[k] || /CAMBIAR|REEMPLAZAR/.test(process.env[k])) throw new Error('Configurar '+k);
}
if (process.env.CMD_SESSION_SECRET.length < 48) throw new Error('Session secret demasiado corto');
// CMD_DB_SSLMODE: solo valores conocidos; lo demas se rechaza para no degradar
// la verificacion de CA por accidente.
const sslMode = (process.env.CMD_DB_SSLMODE || 'verify-full').toLowerCase();
const knownModes = ['disable', 'require', 'verify-ca', 'verify-full'];
if (!knownModes.includes(sslMode)) throw new Error('CMD_DB_SSLMODE invalido: ' + process.env.CMD_DB_SSLMODE);
// Hospedaje interno permitido si: el host es Supabase, o DB_ALLOW_INTERNAL_HOST=true,
// o sslmode=disable (plan: base sin TLS en red Docker interna).
const hostIsSupabase = process.env.CMD_DB_HOST.endsWith('.supabase.co') || process.env.CMD_DB_HOST.endsWith('.supabase.com');
const allowInternal = process.env.DB_ALLOW_INTERNAL_HOST === 'true' || sslMode === 'disable';
if (!hostIsSupabase && !allowInternal) throw new Error('Se requiere host Supabase, no URL');
const ssl = {};
if (sslMode === 'verify-full' || sslMode === 'verify-ca') {
  ssl.require = true;
  ssl.rejectUnauthorized = true;
  ssl.ca = fs.readFileSync('/certs/ca.crt', 'utf8');
} else if (sslMode === 'require') {
  // Cifrado sin verificacion de CA: vulnerable a MITM; exige opt-in explicita.
  if (process.env.DB_ALLOW_INSECURE_SSL !== 'true') {
    throw new Error('CMD_DB_SSLMODE=require desactiva la verificacion de CA; usar DB_ALLOW_INSECURE_SSL=true para confirmarlo');
  }
  ssl.require = true;
  ssl.rejectUnauthorized = false;
} else {
  ssl.require = false;
}
module.exports = {production: {db: {dialectOptions: {ssl}}}};
