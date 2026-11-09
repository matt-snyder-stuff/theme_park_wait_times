"""Validate two-park SPL against real history without writing fixture events."""
from check_splunk import request
import xml.etree.ElementTree as E
import json
r=E.parse('/opt/splunk/etc/apps/queue_times/default/data/ui/views/trip_builder.xml')
values={'visit_date':'2026-11-04','morning':'7','afternoon':'5','entry_time':'09:00','leave_time':'13:00','transfer':'90','days':'1','morning_rides':'*','afternoon_rides':'*'}
for v in r.findall('.//table'):
    q=v.findtext('search/query')
    for k,value in values.items():q=q.replace('$'+k+'|s$',json.dumps(value))
    raw=request('/servicesNS/admin/queue_times/search/jobs/export',{'search':'search '+q,'earliest_time':'-30d','output_mode':'json'})
    rows=[]
    for line in raw.splitlines():
        item=json.loads(line)
        if item.get('preview'):continue
        for m in item.get('messages',[]):
            if m.get('type') in ('ERROR','FATAL'):raise AssertionError(m)
        if 'result' in item:rows.append(item['result'])
    assert rows and 'Status' not in rows[0],rows
    print(v.findtext('title'),len(rows),'evidence rows',flush=True)
