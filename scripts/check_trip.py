"""Validate two-park SPL against real history without writing fixture events."""
from check_splunk import request
import xml.etree.ElementTree as E
import json
r=E.parse('/opt/splunk/etc/apps/queue_times/default/data/ui/views/trip_builder.xml')
values={'visit_date':'2026-11-04','morning':'7','afternoon':'5','entry_time':'09:00','leave_time':'13:00','transfer':'90','days':'1','morning_rides':'*','afternoon_rides':'*'}
for v in r.findall('.//table'):
    q=v.findtext('search/query')
    for k,value in values.items():q=q.replace('$'+k+'|s$',json.dumps(value))
    raw=request('/servicesNS/admin/queue_times/search/jobs/export',{'search':'search '+q,'earliest_time':'-60d','output_mode':'json'})
    rows=[]
    for line in raw.splitlines():
        item=json.loads(line)
        if item.get('preview'):continue
        for m in item.get('messages',[]):
            if m.get('type') in ('ERROR','FATAL'):raise AssertionError(m)
        if 'result' in item:rows.append(item['result'])
    assert rows and 'Status' not in rows[0],rows
    if v.findtext('title').startswith('Second'):
        for row in rows:
            hour,minute=map(int,row['Arrival_window'].split('–')[0].split(':'))
            assert hour*60+minute>=14*60+30,row
    print(v.findtext('title'),len(rows),'evidence rows',flush=True)
# Regression: fully unavailable mornings must count against availability,
# even though they cannot contribute an open-wait comparison.
first=r.find('.//table/search/query').text
suffix=' | stats median(early_wait)'+first.split(' | stats median(early_wait)',1)[1]
suffix=suffix.replace('$days|s$','"1"')
fixture=[]
for day,available in [('2026-10-28',True),('2026-11-04',False)]:
    for n in range(2):
        row={'park_name':'Fixture','ride_name':'Ride','park_local_date':day,'early_open':100 if available else 0}
        if available:row['early_wait']=5
        fixture.append(row)
        fixture.append({'park_name':'Fixture','ride_name':'Ride','park_local_date':day,'later_wait':20})
raw=json.dumps({'events':fixture},separators=(',',':'))
q='| makeresults | eval _raw='+json.dumps(raw)+' | spath path=events{} output=event | mvexpand event | spath input=event'+suffix
response=request('/servicesNS/admin/queue_times/search/jobs/export',{'search':q,'output_mode':'json'})
rows=[x['result'] for line in response.splitlines() if not (x:=json.loads(line)).get('preview') and 'result' in x]
assert len(rows)==1 and float(rows[0]['Early_open_pct'])==50 and rows[0]['Days']=='1',rows
print('QA regression passed: closed mornings reduce early availability to 50%, not 100%.',flush=True)
