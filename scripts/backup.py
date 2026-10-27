#!/usr/bin/env python3
"""Respaldo del kit hefesto-actas (HedgeDoc 1.12.0 + PostgreSQL).

El .env nunca se copia en claro: al respaldo solo van sus nombres (env.vars) y,
si hay receptor age, el .env cifrado (env.age). El manifiesto lleva las cinco
claves del contrato. Ver docs/CONTRATO-RESPALDO.md.
"""
import datetime
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CONFIG, ROOT, SERVICES, dc, safe_tar  # noqa: E402
from respaldo_contrato import (escribir_manifiesto, ejecutar,  # noqa: E402
                               exportar_env, marcar_fallido)

SOFTWARE = 'hefesto-actas'
VERSION = '1.12.0'
DATABASE = 'postgresql'


def main():
    os.umask(0o077)
    for n in CONFIG:
        if not (ROOT / n).is_file():
            raise SystemExit('Falta ' + n)
    running = dc('ps', '--services', '--status', 'running',
                 capture_output=True, text=True).stdout.split()
    if any(n not in SERVICES for n in running):
        raise SystemExit('Finalizar inicializacion/migraciones antes del backup')
    running = [n for n in SERVICES if n in running]
    p = ROOT / 'backups' / datetime.datetime.now(datetime.timezone.utc).strftime(
        '%Y%m%dT%H%M%S%fZ')
    p.mkdir(parents=True, mode=0o700)
    try:
        dc('stop', '--timeout', '120', 'app')
        if dc('ps', '--services', '--status', 'running', *SERVICES,
               capture_output=True, text=True).stdout.strip():
            raise SystemExit('Servicios activos; no se copia')
        with (p / 'public.dump').open('wb') as f:
            dc('run', '--rm', '--no-deps', '-T', '--entrypoint', 'pg_dump', 'dbtools',
               '--format=custom', '--schema=public', '--no-owner', '--no-acl', stdout=f)
        with (p / 'files.tar.gz').open('wb') as f:
            dc('run', '--rm', '--no-deps', '-T', '--entrypoint', 'tar', 'filetools',
               '-czf', '-', '-C', '/files', '.', stdout=f)
        safe_tar(p / 'files.tar.gz')
        for n in CONFIG:
            dst = p / n
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / n, dst)
        meta = exportar_env(ROOT, p)
        escribir_manifiesto(p, SOFTWARE, VERSION, DATABASE, extra=meta)
    except BaseException:
        marcar_fallido(p, SOFTWARE, VERSION, DATABASE)
        raise
    finally:
        for n in ['app']:
            if n in running:
                dc('start', n)
    print('Respaldo completado:', p)
    print('El .env no viaja en claro: solo env.vars y, si hay receptor age, env.age.')
    return 0


if __name__ == '__main__':
    raise SystemExit(ejecutar(main))
