"""Generate the observed-hours and reliability dashboard and shared SPL macros."""
from pathlib import Path
import xml.etree.ElementTree as E
root=Path(__file__).resolve().parents[1]
macros={
'queue_times_observed_day': '''eval open=if(is_open="true",1,0) | where isnotnull(park_local_date) | sort 0 park_id _time | streamstats current=f last(_time) as previous_poll last(park_local_date) as previous_poll_date by park_id | eval poll_gap=if(_time>previous_poll AND park_local_date=previous_poll_date,_time-previous_poll,null()) | eventstats median(poll_gap) as inferred_cadence max(poll_gap) as largest_gap_seconds dc(_time) as observed_polls by park_id park_local_date | eval expected_cadence=coalesce(poll_interval_seconds,inferred_cadence,300), gap_limit=expected_cadence*2+60 | eventstats min(open) as ride_min_open max(open) as ride_max_open by park_id ride_id park_local_date | eval hours_anchor=if(open=1 AND ride_min_open=0 AND ride_max_open=1,1,0) | eventstats min(eval(if(hours_anchor=1,_time,null()))) as first_open max(eval(if(hours_anchor=1,_time,null()))) as last_open min(_time) as first_sample max(_time) as last_sample by park_id park_local_date | eval coverage_pct=round(min(100,100*observed_polls/(floor((last_sample-first_sample)/expected_cadence)+1)),1) | eval complete_day=if(coverage_pct>=90 AND coalesce(largest_gap_seconds,0)<=gap_limit AND park_day_end<now() AND first_sample<=first_open-240 AND last_sample>=last_open+240 AND last_open-first_open>=7200,1,0)''',
'queue_times_outage_segments': '''`queue_times_observed_day` | where _time>=first_open AND _time<=last_open | sort 0 park_id ride_id _time | dedup park_id ride_id _time | streamstats current=f last(open) as prev_open last(_time) as prev_time last(park_local_date) as prev_date by park_id ride_id | eval new_segment=if(isnull(prev_open) OR open!=prev_open OR _time-prev_time>gap_limit OR park_local_date!=prev_date,1,0) | streamstats sum(new_segment) as segment by park_id ride_id | stats min(_time) as start max(_time) as finish max(gap_limit) as episode_gap_limit first(open) as state first(prev_open) as prior_state first(prev_time) as prior_time first(prev_date) as prior_date first(park_local_date) as local_date first(park_local_hour) as start_hour first(park_local_time) as local_start count as samples by park_id park_name ride_id ride_name segment | sort 0 park_id ride_id - start | streamstats current=f last(start) as next_start last(state) as next_state last(local_date) as next_date by park_id ride_id | where state=0 | eval bounded=if(prior_state=1 AND start-prior_time<=episode_gap_limit AND prior_date=local_date AND next_state=1 AND next_start-finish<=episode_gap_limit AND next_date=local_date,1,0), observed_minutes=round((finish-start)/60,1), duration_minutes=if(bounded=1,round((next_start-start)/60,1),null()), transition_uncertainty_minutes=if(bounded=1,round(((start-prior_time)+(next_start-finish))/60,1),null()), episode_status=if(bounded=1,"Completed","Incomplete / gap / boundary")'''
}
p=root/'queue_times/default/macros.conf'
s='[queue_times_index]\ndefinition = index=queue_times\niseval = 0\n'
for name,query in macros.items(): s+='\n['+name+']\ndefinition = '+query+'\niseval = 0\n'
p.write_text(s)
def sub(p,t,text=None,**attrs):
 e=E.SubElement(p,t,attrs);e.text=text;return e
r=E.Element('form',version='1.1',theme='dark')
sub(r,'label','Hours & Ride Reliability')
sub(r,'description','Observed park hours • Local park time • Five-minute samples • Unavailable does not necessarily mean a mechanical fault')
f=sub(r,'fieldset',submitButton='false')
i=sub(f,'input',type='dropdown',token='park',searchWhenChanged='true');sub(i,'label','Park');sub(i,'choice','All parks',value='*');sub(i,'default','*');sub(i,'fieldForLabel','park_name');sub(i,'fieldForValue','park_id')
s=sub(i,'search');sub(s,'query','`queue_times_index` sourcetype=queue_times:ride | stats latest(park_name) as park_name by park_id');sub(s,'earliest','-30d');sub(s,'latest','now')
i=sub(f,'input',type='time',token='window',searchWhenChanged='true');sub(i,'label','History');d=sub(i,'default');sub(d,'earliest','-7d@d');sub(d,'latest','now')
h=sub(sub(sub(r,'row'),'panel'),'html')
sub(h,'h2','Opening hour / Closing hour / Ride reliability')
sub(h,'p','Hours are inferred from the first and last open observations of attractions that also report closed on each local calendar day. Opening/closing comparisons require a finished day, observations before and after those boundaries, and at least two hours between them. Today and partial days remain provisional. History starts with collection; older events without local-time fields are excluded.')
sub(h,'p','Outages are observed unavailable episodes inside inferred park hours. Completed durations require open observations on both sides, on the same local date, with no sample gap over two expected polling intervals plus one minute. Overnight closures and incomplete episodes are excluded from typical-duration statistics. Five-minute sampling limits precision; schedules crossing midnight are split at midnight.')
sub(h,'a','Powered by Queue-Times.com',href='https://queue-times.com/',target='_blank',rel='noopener noreferrer')
base='`queue_times_index` sourcetype=queue_times:ride park_id=$park|s$'
windows=base+' | `queue_times_observed_day` | where complete_day=1 AND open=1 | eval window=case(_time<first_open+3600,"Opening hour",_time>last_open-3600,"Closing hour") | where isnotnull(window)'
outages=base+' | `queue_times_outage_segments`'
def panel(row,title,q,kind='table',chart=None):
 v=sub(sub(row,'panel'),kind);sub(v,'title',title);s=sub(v,'search');sub(s,'query',q);sub(s,'earliest','$window.earliest$');sub(s,'latest','$window.latest$');sub(s,'refresh','300s')
 if chart:sub(v,'option',chart,name='charting.chart')
 return v
row=sub(r,'row')
panel(row,'Opening vs closing · average wait (minutes)',windows+' | chart avg(wait_time) over park_name by window','chart','column')
panel(row,'Completed outages · median duration (minutes)',outages+' | where bounded=1 | stats median(duration_minutes) as Minutes','single')
row=sub(r,'row')
panel(row,'Opening / closing wait history',windows+' | stats avg(wait_time) as Average perc95(wait_time) as P95 count as Samples by park_name park_local_date window | eval Average=round(Average,1),P95=round(P95,1) | sort 0 - park_local_date park_name window')
panel(row,'Best rides near opening and closing',windows+' | stats avg(wait_time) as Average perc95(wait_time) as P95 count as Samples dc(park_local_date) as Days by park_name ride_name window | eval Average=round(Average,1),P95=round(P95,1) | sort 0 Average')
row=sub(r,'row')
panel(row,'Typical completed outage by ride',outages+' | where bounded=1 | stats count as Episodes median(duration_minutes) as Median perc95(duration_minutes) as P95 max(duration_minutes) as Longest by park_name ride_name | sort 0 - Median')
panel(row,'Unavailable likelihood by local hour · sampled frequency',base+' | `queue_times_observed_day` | where _time>=first_open AND _time<=last_open | eval unavailable=if(open=0,100,0) | chart avg(unavailable) over park_local_hour by park_name limit=10','chart','column')
row=sub(r,'row')
panel(row,'Most likely unavailable hour for each ride',base+' | `queue_times_observed_day` | where _time>=first_open AND _time<=last_open | eval unavailable=if(open=0,100,0) | stats avg(unavailable) as Unavailable_pct count as Samples dc(park_local_date) as Days by park_id park_name ride_id ride_name park_local_hour | eval Unavailable_pct=round(Unavailable_pct,1) | sort 0 park_id ride_id - Unavailable_pct - Samples park_local_hour | dedup park_id ride_id | table park_name ride_name park_local_hour Unavailable_pct Samples Days')
panel(row,'Completed outage starts by local hour',outages+' | where bounded=1 | chart count over start_hour by park_name limit=10','chart','column')
row=sub(r,'row')
panel(row,'Episode ledger · incomplete durations are not estimates',outages+' | sort 0 - start | table park_name ride_name local_start episode_status duration_minutes observed_minutes transition_uncertainty_minutes samples')
row=sub(r,'row')
panel(row,'Observed daily boundaries and eligibility',base+' | `queue_times_observed_day` | eval first_label=if(_time=first_open,park_local_time,null()),last_label=if(_time=last_open,park_local_time,null()) | stats values(first_label) as First_open values(last_label) as Last_open max(complete_day) as Eligible count as Samples by park_name park_local_date | eval Comparison=if(Eligible=1,"Eligible estimate","Provisional / incomplete / short day") | fields - Eligible | sort 0 - park_local_date')
E.indent(r);E.ElementTree(r).write(root/'queue_times/default/data/ui/views/ride_reliability.xml',encoding='unicode')
p=root/'queue_times/default/data/ui/nav/default.xml';nav=E.parse(p);n=nav.getroot()
if not any(v.get('name')=='ride_reliability' for v in n): n.insert(2,E.Element('view',name='ride_reliability'))
E.indent(n);nav.write(p,encoding='unicode')
