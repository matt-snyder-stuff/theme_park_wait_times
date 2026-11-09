"""Run in Splunk's container; synthetic records stay in search, never indexed."""
import json
from datetime import datetime, timezone
from check_splunk import request

start=datetime(2026,11,1,9,tzinfo=timezone.utc).timestamp()
events=[]
def add(ride,minute,is_open):
    epoch=start+minute*60
    events.append(dict(park_id=999,park_name='Fixture Park',ride_id=ride,ride_name='Ride '+str(ride),
      observed_at=epoch,is_open='true' if is_open else 'false',wait_time=10,
      park_local_date='2026-11-01',park_local_hour=datetime.fromtimestamp(epoch,timezone.utc).strftime('%H'),
      park_local_time=datetime.fromtimestamp(epoch,timezone.utc).isoformat(),park_day_end=start+15*3600))
for minute in range(-5,186,5):
    add(1,minute,0<=minute<=180)
    add(4,minute,True)  # An always-open show must not define park hours.
for minute,state in [(0,1),(5,0),(10,0),(15,1),(20,1),(25,0),(30,1)]: add(2,minute,state)
for minute,state in [(0,1),(5,0),(30,0),(35,1)]: add(3,minute,state)
raw=json.dumps({'events':events},separators=(',',':'))
base='| makeresults | eval _raw='+json.dumps(raw)+' | spath path=events{} output=event | mvexpand event | spath input=event | eval _time=observed_at'
def results(query):
    output=request('/servicesNS/admin/queue_times/search/jobs/export',{'search':query,'output_mode':'json'})
    rows=[]
    for line in output.splitlines():
        obj=json.loads(line)
        if obj.get('preview'): continue
        for message in obj.get('messages',[]):
            if message.get('type') in ('ERROR','FATAL'): raise AssertionError(message)
        if 'result' in obj: rows.append(obj['result'])
    return rows
rows=results(base+' | `queue_times_outage_segments` | table ride_id bounded duration_minutes')
completed=sorted(float(r['duration_minutes']) for r in rows if r['bounded']=='1')
assert completed==[5.0,10.0], rows
assert not any(r['bounded']=='1' for r in rows if r['ride_id']=='3'),rows
rows=results(base+' | `queue_times_observed_day` | stats max(complete_day) as eligible min(first_open) as opening max(last_open) as closing')
assert rows[0]['eligible']=='1', rows
assert float(rows[0]['opening'])==start and float(rows[0]['closing'])==start+180*60,rows
rows=results(base+' | where _time>='+str(start)+' | `queue_times_observed_day` | stats max(complete_day) as eligible')
assert rows[0]['eligible']=='0', rows
print('RELIABILITY OK: repeated outages, gap exclusion, inferred hours, partial-day exclusion')
