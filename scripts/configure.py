#!/usr/bin/env python3
import os,secrets
from pathlib import Path
p=Path(__file__).resolve().parents[1]
s=(p/'.env.example').read_text().replace('SESSION_SECRET=REEMPLAZAR','SESSION_SECRET='+secrets.token_hex(32))
fd=os.open(p/'.env',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w') as f:f.write(s)
print('Creado .env; editar dominio, host y clave. Copiar certificado CA en certs/ca.crt.')
