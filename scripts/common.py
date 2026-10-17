import hashlib,json,subprocess,tarfile
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
CONFIG=['.env','compose.yaml','compose.bootstrap.yaml','ops/config.cjs','certs/ca.crt']
SERVICES=['app']
def dc(*a,**kw):return subprocess.run(['docker','compose','--project-directory',str(ROOT),'-f',str(ROOT/'compose.yaml'),*a],check=True,**kw)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def safe_tar(path):
    names=set();size=0
    with tarfile.open(path,'r|gz') as tf:
        for m in tf:
            n=PurePosixPath(m.name)
            if n.is_absolute() or '..' in n.parts or not(m.isfile() or m.isdir()) or m.mode&0o6000 or str(n) in names:raise SystemExit('Ruta/tipo/modo tar no admitido')
            names.add(str(n));size+=m.size
            if len(names)>2000000 or size>500*1024**3:raise SystemExit('Tar excede limite')
def verify(folder):
    p=Path(folder).resolve();m=json.loads((p/'manifest.json').read_text())
    if (m.get('product'),m.get('version'),m.get('status'))!=('hefesto-actas','1.12.0','completed'):raise SystemExit('Manifest incorrecto')
    if set(m.get('sha256',{}))!=set(CONFIG+['public.dump','files.tar.gz']):raise SystemExit('Lista inesperada')
    for n,digest in m['sha256'].items():
        f=p/n
        if f.is_symlink() or not f.is_file() or p not in f.resolve().parents or sha(f)!=digest:raise SystemExit('Checksum/ruta incorrecto: '+n)
    for n in ['files.tar.gz']:safe_tar(p/n)
    return p
