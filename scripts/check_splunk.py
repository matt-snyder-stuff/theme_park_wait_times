"""Run inside the container using Splunk's Python to verify the local app."""
import base64
import json
import os
import ssl
import urllib.parse
import urllib.request

BASE='https://127.0.0.1:8089'
AUTH=base64.b64encode(('admin:'+os.environ['SPLUNK_PASSWORD']).encode()).decode()
def request(path,data=None):
    req=urllib.request.Request(BASE+path,data=urllib.parse.urlencode(data).encode() if data else None,headers={'Authorization':'Basic '+AUTH})
    with urllib.request.urlopen(req,context=ssl._create_unverified_context(),timeout=60) as response:
        return response.read().decode()
import xml.etree.ElementTree as ET
from pathlib import Path
def main():
    app=json.loads(request('/services/apps/local/queue_times?output_mode=json'))['entry'][0]
    print('APP:',app['name'],'version',app['content']['version'])
    print('EVENTS:',request('/services/search/jobs/export',{'search':'search index=queue_times | stats count by sourcetype','earliest_time':'-1h','output_mode':'json'}))
    for path in Path('/opt/splunk/etc/apps/queue_times/default/data/ui/views').glob('*.xml'):
        count=0
        for query in ET.parse(path).findall('.//query'):
            spl='search '+query.text.replace('$park|s$', '\"*\"').replace('$ride|s$', '\"*\"').replace('$weekday|s$', '\"*\"').replace('$days|s$', '\"3\"')
            raw=request('/servicesNS/admin/queue_times/search/jobs/export',{'search':spl,'earliest_time':'-24h','output_mode':'json'})
            for line in raw.splitlines():
                result=json.loads(line)
                if result.get('preview'): continue
                for message in result.get('messages',[]):
                    if message.get('type') in ('ERROR','FATAL'): raise RuntimeError(message)
            count+=1
        print('SEARCHES OK:',path.stem,count)

if __name__ == "__main__":
    main()
