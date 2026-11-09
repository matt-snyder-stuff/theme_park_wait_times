"""Check release hygiene without printing secret values."""
from pathlib import Path
import configparser
import tarfile
import xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
c=configparser.ConfigParser();c.read(root/'queue_times/default/app.conf')
package=root/'dist'/('queue_times-'+c['launcher']['version']+'.tar.gz')
errors=[]
secrets=[]
env=root/'.env'
if env.exists():
    for line in env.read_text().splitlines():
        if '=' in line and not line.startswith('#'):
            value=line.split('=',1)[1].strip()
            if len(value)>8:secrets.append(value.encode())
with tarfile.open(package) as archive:
    for member in archive.getmembers():
        parts=Path(member.name).parts
        if 'local' in parts or '__pycache__' in parts or member.name.endswith(('.lic','.pyc')) or any(p.startswith('.') for p in parts):errors.append('Forbidden archive member: '+member.name)
        if member.isfile():
            data=archive.extractfile(member).read()
            if any(secret in data for secret in secrets):errors.append('Credential found in archive member: '+member.name)
for path in root.rglob('*'):
    rel=path.relative_to(root)
    if not path.is_file() or any(p in ('.git','dist','__pycache__','local') for p in rel.parts) or path.name=='.env':continue
    if path.suffix in ('.lic','.pem','.key'):errors.append('Private file in source: '+str(rel));continue
    if any(secret in path.read_bytes() for secret in secrets):errors.append('Credential found in source: '+str(rel))
for path in (root/'queue_times/default/data/ui').rglob('*.xml'):ET.parse(path)
views={p.stem for p in (root/'queue_times/default/data/ui/views').glob('*.xml')}
for view in ET.parse(root/'queue_times/default/data/ui/nav/default.xml').findall('.//view'):
    if view.get('name') not in views|{'search'}:errors.append('Missing navigation target: '+view.get('name'))
assert not errors,'\n'.join(errors)
print('Release checks passed: XML, navigation, package exclusions, local credential scan.')
