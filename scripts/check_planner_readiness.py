from check_splunk import request
import json
import xml.etree.ElementTree as ET
r=ET.parse('/opt/splunk/etc/apps/queue_times/default/data/ui/views/disney_world.xml')
for panel in r.findall('.//panel'):
    v=panel.find('./*'); title=v.findtext('title','')
    if not (title.startswith('Opening data') or title.startswith('Opening priorities')):continue
    for days in (['3','1'] if title.startswith('Opening priorities') else ['3']):
        q=v.findtext('search/query').replace('$park|s$','"*"').replace('$ride|s$','"*"').replace('$weekday|s$','"*"').replace('$days|s$',json.dumps(days))
        raw=request('/servicesNS/admin/queue_times/search/jobs/export',{'search':'search '+q,'earliest_time':'-7d','output_mode':'json'})
        rows=[]
        for line in raw.splitlines():
            obj=json.loads(line)
            if obj.get('preview'):continue
            if obj.get('messages'):print(obj['messages'],flush=True)
            if 'result' in obj:rows.append(obj['result'])
        print(title,'days='+days,'rows='+str(len(rows)),json.dumps(rows[:4]),flush=True)
