'use strict';
const fs = require('fs');
for (const k of ['CMD_DB_HOST','CMD_DB_PASSWORD','CMD_SESSION_SECRET']) {
  if (!process.env[k] || /CAMBIAR|REEMPLAZAR/.test(process.env[k])) throw new Error('Configurar '+k);
}
if (process.env.CMD_SESSION_SECRET.length < 48) throw new Error('Session secret demasiado corto');
if (!process.env.CMD_DB_HOST.endsWith('.supabase.co') && !process.env.CMD_DB_HOST.endsWith('.supabase.com')) throw new Error('Se requiere host Supabase, no URL');
module.exports = {production: {db: {dialectOptions: {ssl: {
  require: true, rejectUnauthorized: true,
  ca: fs.readFileSync('/certs/ca.crt', 'utf8')
}}}}};
