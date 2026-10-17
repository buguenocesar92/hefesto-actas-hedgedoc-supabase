#!/usr/bin/env python3
import os,re,subprocess,sys,tempfile
from pathlib import Path
from common import ROOT,CONFIG,dc,sha,verify
if len(sys.argv)!=3 or sys.argv[2]!='--accept-restored-content':raise SystemExit('Uso: python3 scripts/restore.py /ruta/respaldo --accept-restored-content')
p=verify(sys.argv[1])
for n in CONFIG:
    if n in ['.env','certs/ca.crt']:continue
    if not (ROOT/n).is_file() or sha(ROOT/n)!=sha(p/n):raise SystemExit('Kit/configuracion distinto: '+n)
def secret(path):
    for line in path.read_text().splitlines():
        if line.startswith('SESSION_SECRET='):return line.split('=',1)[1].strip().strip("\"'")
if not secret(ROOT/'.env') or secret(ROOT/'.env')!=secret(p/'.env'):raise SystemExit('Conservar SESSION_SECRET original')
if dc('ps','--services','--status','running',capture_output=True,text=True).stdout.strip():raise SystemExit('Destino debe estar completamente detenido')
dc('run','--rm','--no-deps','-T','--entrypoint','psql','dbtools','--no-psqlrc','-v','ON_ERROR_STOP=1','-Atc',"SELECT current_user")
count=dc('run','--rm','--no-deps','-T','--entrypoint','psql','dbtools','--no-psqlrc','-Atc',"SELECT count(*) FROM pg_tables WHERE schemaname='public'",capture_output=True,text=True).stdout.strip()
if count!='0':raise SystemExit('public no esta vacio; no se sobrescribe')
for folder in ['/files']:
    if dc('run','--rm','--no-deps','-T','--entrypoint','find','filetools',folder,'-mindepth','1','-print','-quit',capture_output=True,text=True).stdout.strip():raise SystemExit('Volumen ocupado: '+folder)
with (p/'public.dump').open('rb') as f:toc=dc('run','--rm','--no-deps','-T','--entrypoint','pg_restore','dbtools','--list',stdin=f,stdout=subprocess.PIPE).stdout.decode()
lines=[s for s in toc.splitlines() if not re.match(r'^\d+;\s+\d+\s+\d+\s+SCHEMA\s+-\s+public(?:\s|$)',s)]
with tempfile.TemporaryDirectory(prefix='hefesto-actas-restore-') as tmp:
    file=Path(tmp)/'restore.list';file.write_text('\n'.join(lines)+'\n');os.chmod(tmp,0o755);os.chmod(file,0o644)
    with (p/'public.dump').open('rb') as f:dc('run','--rm','--no-deps','-T','-v',tmp+':/restore:ro','--entrypoint','pg_restore','dbtools','--exit-on-error','--single-transaction','--no-owner','--no-acl','--use-list=/restore/restore.list','--dbname=postgres',stdin=f)
for name,folder in [('files.tar.gz','/files')]:
    with (p/name).open('rb') as f:dc('run','--rm','--no-deps','-T','--entrypoint','tar','filetools','-xzf','-','-C',folder,stdin=f)

print('Base y adjuntos recuperados; servicios detenidos. Revisar permisos y privacidad antes de iniciar app.')
