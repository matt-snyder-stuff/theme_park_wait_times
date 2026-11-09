"""Generate the Walt Disney World trip planning dashboard."""
from pathlib import Path
import xml.etree.ElementTree as E
root=Path(__file__).resolve().parents[1]
def sub(p,t,text=None,**attrs):
 e=E.SubElement(p,t,attrs);e.text=text;return e
r=E.Element('form',version='1.1',theme='dark');sub(r,'label','Disney World Planner');sub(r,'description','Plan your December 2026 visit • Magic Kingdom / EPCOT / Hollywood Studios / Animal Kingdom • All hours are Orlando local time')
f=sub(r,'fieldset',submitButton='false')
def dropdown(token,label,choices,default):
 i=sub(f,'input',type='dropdown',token=token,searchWhenChanged='true');sub(i,'label',label)
 for value,name in choices:sub(i,'choice',name,value=value)
 sub(i,'default',default);return i
p=dropdown('park','Park',[('*','All Disney World parks'),('6','Magic Kingdom'),('5','EPCOT'),('7','Hollywood Studios'),('8','Animal Kingdom')],'*')
sub(p,'change')
# Clear a previously selected ride when changing parks.
c=p.find('change');sub(c,'set','*',token='form.ride');sub(c,'set','*',token='ride')
base='`queue_times_index` sourcetype=queue_times:ride park_id IN (5,6,7,8) park_id=$park|s$'
i=dropdown('ride','Ride',[('*','All rides')],'*');sub(i,'fieldForLabel','label');sub(i,'fieldForValue','ride_id');s=sub(i,'search');sub(s,'query',base+' | stats latest(ride_name) as ride_name latest(park_name) as park_name by ride_id | eval label=park_name." / ".ride_name | sort label');sub(s,'earliest','-30d');sub(s,'latest','now')
dropdown('weekday','Visit weekday',[('*','Any day')]+[(str(n),name) for n,name in enumerate(['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'])],'*')
dropdown('days','Minimum days per hourly recommendation',[('3','3 days'),('7','7 days'),('1','1 day (exploratory)')],'3')
i=sub(f,'input',type='time',token='window',searchWhenChanged='true');sub(i,'label','Learning window');d=sub(i,'default');sub(d,'earliest','-30d');sub(d,'latest','now')
h=sub(sub(sub(r,'row'),'panel'),'html');sub(h,'h2','Opening strategy: ride early, save passes for later');sub(h,'p','Select your morning park and visit weekday. Start with Opening priorities: rides whose first-30-minute median wait is lower than their later-day median. Potential wait avoided is that historical difference; Cost of delaying 30m shows how quickly the opportunity fades. Check Early open % and the live board before committing. Then choose a must-do ride for detail. Compare the best observed hour with its typical wait, and use P95 to see the longer-wait scenario. Hourly recommendations require at least 12 open snapshots and your selected minimum number of distinct days per hour. Observed day boundaries use attractions that have both open and closed snapshots that day; always-open shows do not define opening time. Opening priorities require completed observed days, at least 6 early and 12 later open samples, and the selected minimum days in each period. These are ride timing priorities, not a timed route or a guarantee of pass savings.')
sub(h,'p','History began in November 2026; this is observed guidance for your December trip, not a December forecast. Holiday demand, special events and operating hours can differ. This tool does not include walking time, reservations, Lightning Lane availability or eligibility for early entry. Blank recommendations mean more history is needed. Live queues ignore the weekday and history filters.')
sub(h,'a','Powered by Queue-Times.com',href='https://queue-times.com/',target='_blank',rel='noopener noreferrer')
history=base+' | where isnotnull(park_local_date) | eval weekday=strftime(strptime(park_local_date,"%Y-%m-%d"),"%w") | search weekday=$weekday|s$'
ride=' | search ride_id=$ride|s$'
open_samples=history+' | `queue_times_observed_day`'+ride+' | where open=1 AND _time>=first_open AND _time<=last_open'
hourly=open_samples+' | stats median(wait_time) as Median perc95(wait_time) as P95 avg(wait_time) as Average count as Samples dc(park_local_date) as Days by park_id park_name ride_id ride_name park_local_hour | where Days>=tonumber($days|s$) AND Samples>=12 | eval Average=round(Average,1)'
def panel(row,title,q,kind='table',chart=None,live=False):
 v=sub(sub(row,'panel'),kind);sub(v,'title',title);s=sub(v,'search');sub(s,'query',q + (' | appendpipe [ stats count | where count=0 | eval Status=\"No qualifying observations for these filters yet. Check Opening data readiness, widen the learning window, or select 1 day for exploratory results.\" | fields Status ]' if kind=='table' else ''));sub(s,'earliest','-30m' if live else '$window.earliest$');sub(s,'latest','now' if live else '$window.latest$');sub(s,'refresh','300s')
 if chart:sub(v,'option',chart,name='charting.chart')
 return v
row=sub(r,'row')
panel(row,'Distinct days collected',history+ride+' | stats dc(park_local_date) as Days','single')
panel(row,'Open ride samples available',open_samples+' | stats count as Samples','single')
panel(row,'Rides with enough history for recommendations',hourly+' | stats dc(ride_id) as Rides','single')
row=sub(r,'row')
panel(row,'Opening data readiness · completed days required',history+' | `queue_times_observed_day` | stats dc(park_local_date) as Observed_days dc(eval(if(complete_day=1,park_local_date,null()))) as Eligible_days min(coverage_pct) as Lowest_coverage_pct max(largest_gap_seconds) as Largest_gap_seconds by park_name | eval Required_days=tonumber($days|s$), Status=if(Eligible_days<Required_days,"Collecting history: choose 1 day for exploratory results or wait for more complete days","Day coverage ready; individual rides still need enough open samples") | table park_name Observed_days Eligible_days Required_days Lowest_coverage_pct Largest_gap_seconds Status')
row=sub(r,'row')
panel(row,'Opening priorities · save passes for later',history+' | `queue_times_observed_day`'+ride+' | where complete_day=1 AND _time<=last_open | eval period=case(_time>=first_open AND _time<first_open+1800,"First30",_time>=first_open+1800 AND _time<first_open+3600,"Next30",_time>=first_open+3600,"Later") | where isnotnull(period) | stats median(eval(if(period="First30" AND open=1,wait_time,null()))) as First30_median perc95(eval(if(period="First30" AND open=1,wait_time,null()))) as First30_P95 median(eval(if(period="Next30" AND open=1,wait_time,null()))) as Next30_median median(eval(if(period="Later" AND open=1,wait_time,null()))) as Later_median avg(eval(if(period="First30",100*open,null()))) as Early_open_pct count(eval(period="First30" AND open=1)) as Early_samples count(eval(period="Later" AND open=1)) as Later_samples dc(eval(if(period="First30" AND open=1,park_local_date,null()))) as Early_days dc(eval(if(period="Later" AND open=1,park_local_date,null()))) as Later_days by park_name ride_name | where Early_days>=tonumber($days|s$) AND Later_days>=tonumber($days|s$) AND Early_samples>=6 AND Later_samples>=12 | eval Potential_wait_avoided=round(Later_median-First30_median,1), Cost_of_delaying_30m=round(Next30_median-First30_median,1),Early_open_pct=round(Early_open_pct,1) | where Potential_wait_avoided>0 | sort 0 - Potential_wait_avoided - Cost_of_delaying_30m First30_median | table park_name ride_name First30_median First30_P95 Next30_median Later_median Potential_wait_avoided Cost_of_delaying_30m Early_open_pct Early_days Later_days')
row=sub(r,'row')
panel(row,'First hour in 15-minute steps · choose your first and second ride',history+' | `queue_times_observed_day`'+ride+' | where complete_day=1 AND open=1 AND _time>=first_open AND _time<first_open+3600 | eval Minutes_after_open=floor((_time-first_open)/900)*15 | stats median(wait_time) as Median perc95(wait_time) as P95 count as Samples dc(park_local_date) as Days by park_name ride_name Minutes_after_open | where Days>=tonumber($days|s$) | sort 0 park_name ride_name Minutes_after_open')
row=sub(r,'row')
panel(row,'Best observed hour for each ride · lowest median',hourly+' | eventstats max(Median) as busiest_hour_median by park_id ride_id | sort 0 park_id ride_id Median P95 - Days park_local_hour | dedup park_id ride_id | eval Compared_to_busiest_hour=busiest_hour_median-Median, Hour=park_local_hour.":00" | sort 0 - Compared_to_busiest_hour | table park_name ride_name Hour Median P95 Compared_to_busiest_hour Samples Days')
row=sub(r,'row')
panel(row,'Hourly ride wait matrix · median minutes',hourly+' | eval Ride=park_name." / ".ride_name | chart max(Median) over Ride by park_local_hour limit=0')
panel(row,'Hourly wait curve · select one ride for detail',open_samples+' | chart median(wait_time) over park_local_hour by park_name limit=4','chart','line')
row=sub(r,'row')
panel(row,'Opening vs closing hour · completed observed days',history+' | `queue_times_observed_day`'+ride+' | where complete_day=1 AND open=1 | eval Visit_window=case(_time<first_open+3600,"Opening hour",_time>last_open-3600,"Closing hour") | where isnotnull(Visit_window) | stats median(wait_time) as Median perc95(wait_time) as P95 count as Samples dc(park_local_date) as Days by park_name ride_name Visit_window | sort 0 park_name ride_name Visit_window')
panel(row,'Unavailable frequency by local hour',history+' | `queue_times_observed_day`'+ride+' | where _time>=first_open AND _time<=last_open | eval unavailable=if(open=0,100,0) | stats avg(unavailable) as Unavailable_pct count as Samples dc(park_local_date) as Days by park_name ride_name park_local_hour | eval Unavailable_pct=round(Unavailable_pct,1) | sort 0 - Unavailable_pct - Samples')
row=sub(r,'row')
panel(row,'Live ride board · lowest queues first',base+ride+' | sort 0 - _time | dedup park_id ride_id | eval Status=if(is_open="true","OPEN","UNAVAILABLE"), Observation_age_min=round((now()-_time)/60,1), Source_age_min=round((now()-strptime(last_updated,"%Y-%m-%dT%H:%M:%S.%3NZ"))/60,1) | sort 0 Status wait_time | table park_name ride_name Status wait_time Observation_age_min Source_age_min',live=True)
E.indent(r);E.ElementTree(r).write(root/'queue_times/default/data/ui/views/disney_world.xml',encoding='unicode')
p=root/'queue_times/default/data/ui/nav/default.xml';nav=E.parse(p);n=nav.getroot()
if not any(v.get('name')=='disney_world' for v in n):n.insert(1,E.Element('view',name='disney_world'))
E.indent(n);nav.write(p,encoding='unicode')
