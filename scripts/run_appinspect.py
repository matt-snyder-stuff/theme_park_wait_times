"""Run local AppInspect and fail CI on actual findings, not just process exit status."""
from pathlib import Path
import argparse
import configparser
import json
import shutil
import subprocess
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--executable',default=shutil.which('splunk-appinspect'));args=parser.parse_args()
if not args.executable:parser.error('Install splunk-appinspect==4.4.0 or pass --executable.')
c=configparser.ConfigParser();c.read(root/'queue_times/default/app.conf')
package=root/'dist'/('queue_times-'+c['launcher']['version']+'.tar.gz')
report=root/'dist/appinspect.json';log=root/'dist/appinspect.log'
with log.open('w') as output:
    subprocess.run([args.executable,'inspect',str(package),'--mode','precert','--output-file',str(report)],stdout=output,stderr=subprocess.STDOUT,check=True)
data=json.loads(report.read_text());print(json.dumps(data['summary'],indent=2))
if any(data['summary'].get(key,0) for key in ['failure','error']):raise SystemExit('AppInspect failed; inspect dist/appinspect.json and .log.')
print('Local precert checks passed. Warnings/manual review are not certification.')
