from check_splunk import request
import json
import xml.etree.ElementTree as ET
from pathlib import Path

def run(label,q,earliest='-7d'):
    raw=request('/servicesNS/admin/queue_times/search/jobs/export',{'search':'search '+q,'earliest_time':earliest,'output_mode':'json'})
    rows=[];messages=[]
    for line in raw.splitlines():
        obj=json.loads(line)
        if obj.get('preview'): continue
        if 'result' in obj: rows.append(obj['result'])
        messages.extend(obj.get('messages',[]))
    print(json.dumps(dict(label=label,rows=len(rows),sample=rows[:3],messages=messages)),flush=True)
run('collection','index=queue_times | stats count max(_time) as last_time by sourcetype','-30m')
run('Disney daily coverage','index=queue_times sourcetype=queue_times:ride park_id IN (5,6,7,8) | `queue_times_observed_day` | stats count sum(open) as open_samples max(complete_day) as eligible min(first_open) as first_open max(last_open) as last_open min(first_sample) as first_sample max(last_sample) as last_sample by park_name park_local_date')
for path in Path('/opt/splunk/etc/apps/queue_times/default/data/ui/views').glob('*.xml'):
    root=ET.parse(path)
    for panel in root.findall('.//panel'):
        for s in panel.findall('./*/search'):
            q=s.findtext('query')
            q=q.replace('$park|s$','"*"').replace('$ride|s$','"*"').replace('$weekday|s$','"*"').replace('$days|s$','"3"')
            earliest=s.findtext('earliest').replace('$window.earliest$','-7d')
            run(path.stem+': '+panel.find('./*').findtext('title',''),q,earliest)
