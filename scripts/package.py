"""Build a code-only Splunk archive; exclude runtime configuration and secrets."""
from pathlib import Path
import configparser
import tarfile
root=Path(__file__).resolve().parents[1]
app=root/'queue_times'
config=configparser.ConfigParser();config.read(app/'default/app.conf')
version=config['launcher']['version']
out=root/'dist'/('queue_times-'+version+'.tar.gz');out.parent.mkdir(exist_ok=True)
allowed={'bin','default','metadata','README','appserver'}
with tarfile.open(out,'w:gz') as archive:
    for path in sorted(app.rglob('*')):
        rel=path.relative_to(app)
        if not path.is_file() or path.is_symlink() or rel.parts[0] not in allowed:continue
        if '__pycache__' in rel.parts or path.suffix in ('.pyc','.pyo','.lic') or any(p.startswith('.') for p in rel.parts):continue
        archive.add(path,arcname='queue_times/'+str(rel))
print(out)
