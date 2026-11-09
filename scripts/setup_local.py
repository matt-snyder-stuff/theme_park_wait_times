"""Create private local development settings without overwriting existing files."""
from pathlib import Path
import secrets
import shutil
root=Path(__file__).resolve().parents[1]
env=root/'.env'
if not env.exists():
    with env.open('x') as f:
        env.chmod(0o600)
        f.write('SPLUNK_PASSWORD=Atlas!'+secrets.token_urlsafe(24)+'\n')
local=root/'queue_times/local/inputs.conf'
if not local.exists():
    local.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(root/'docker/inputs.conf',local)
print('Local configuration is ready. Credentials remain in .env. Run docker compose up -d.')
