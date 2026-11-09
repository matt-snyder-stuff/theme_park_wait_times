"""Run via Splunk Python in Docker; verify selected new workflows on real data."""
from check_splunk import request
import json
import xml.etree.ElementTree as ET
from pathlib import Path
for name in ['start_here','park_planner','disney_world','research_guide','setup_guide']:
    doc=json.loads(request('/servicesNS/admin/queue_times/data/ui/views/'+name+'?output_mode=json'))
    assert doc.get('entry'),name
    print('VIEW OK:',name,flush=True)
    root=ET.parse('/opt/splunk/etc/apps/queue_times/default/data/ui/views/'+name+'.xml')
    for panel in root.findall('.//panel'):
        v=panel.find('./*');s=v.find('search');title=v.findtext('title','')
        if s is None or not (name=='start_here' or title.startswith(('Opening priorities','Live ride board','Opening data readiness'))):continue
        q=s.findtext('query').replace('$park|s$','"6"').replace('$ride|s$','"*"').replace('$weekday|s$','"*"').replace('$days|s$','"3"')
        earliest=s.findtext('earliest').replace('$window.earliest$','-7d')
        raw=request('/servicesNS/admin/queue_times/search/jobs/export',{'search':'search '+q,'earliest_time':earliest,'output_mode':'json'})
        count=0
        for line in raw.splitlines():
            item=json.loads(line)
            if item.get('preview'):continue
            for message in item.get('messages',[]):
                if message.get('type') in ('ERROR','FATAL'):raise AssertionError(message)
            if 'result' in item:count+=1
        print('SEARCH OK:',name,title,'rows='+str(count),flush=True)
