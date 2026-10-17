#!/usr/bin/env python3
import datetime,json,os,shutil
from common import ROOT,CONFIG,SERVICES,dc,sha,safe_tar
os.umask(0o077)
for n in CONFIG:
    if not (ROOT/n).is_file():raise SystemExit('Falta '+n)
running=dc('ps','--services','--status','running',capture_output=True,text=True).stdout.split()
if any(n not in SERVICES for n in running):raise SystemExit('Finalizar inicializacion/migraciones antes del backup')
running=[n for n in SERVICES if n in running]
p=ROOT/'backups'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');p.mkdir(parents=True,mode=0o700)
try:
    dc('stop','--timeout','120','app')
    if dc('ps','--services','--status','running',*SERVICES,capture_output=True,text=True).stdout.strip():raise SystemExit('Servicios activos; no se copia')
    with (p/'public.dump').open('wb') as f:dc('run','--rm','--no-deps','-T','--entrypoint','pg_dump','dbtools','--format=custom','--schema=public','--no-owner','--no-acl',stdout=f)
    for name,folder in [('files.tar.gz','/files')]:
        with (p/name).open('wb') as f:dc('run','--rm','--no-deps','-T','--entrypoint','tar','filetools','-czf','-','-C',folder,'.',stdout=f)
        safe_tar(p/name)
    for n in CONFIG:
        dst=p/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,dst)
    files=CONFIG+['public.dump','files.tar.gz']
    (p/'manifest.json').write_text(json.dumps({'product':'hefesto-actas','version':'1.12.0','status':'completed','sha256':{n:sha(p/n) for n in files}},indent=2))
    print('Respaldo completado:',p,'Incluye actas, archivos, cuentas y secretos. Cifrar fuera del servidor.')
finally:
    for n in ['app']:
        if n in running:dc('start',n)
