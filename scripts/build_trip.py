"""Two-park planning brief with local-only persistence and transparent assumptions."""
from pathlib import Path
import xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[1]
def sub(p,t,text=None,**a):
 e=E.SubElement(p,t,a);e.text=text;return e
r=E.Element('form',version='1.1',theme='dark',stylesheet='planner.css',script='trip.js');sub(r,'label','My Trip');sub(r,'description','A personal shortlist, two parks, and a flexible plan you can save and print.')
init=sub(r,'init')
for token in ['visit_date','form.visit_date']:sub(init,'eval','strftime(relative_time(now(),"+30d@d"),"%Y-%m-%d")',token=token)
f=sub(r,'fieldset',submitButton='true',autoRun='false')
def inp(token,label,default,type='text',choices=None):
 i=sub(f,'input',type=type,token=token,searchWhenChanged='false');sub(i,'label',label)
 if default is not None:sub(i,'default',default)
 for value,name in choices or []:sub(i,'choice',name,value=value)
 return i
inp('trip_name','Trip name','My park day');inp('visit_date','Visit date · YYYY-MM-DD',None)
for token,label,default in [('morning','First park','7'),('afternoon','Second park','5')]:
 i=inp(token,label,default,'dropdown');sub(i,'fieldForLabel','park_name');sub(i,'fieldForValue','park_id');s=sub(i,'search');sub(s,'query','`queue_times_index` sourcetype=queue_times:ride | stats latest(park_name) as park_name by park_id | sort park_name');sub(s,'earliest','-7d');sub(s,'latest','now')
inp('entry','Entry eligibility','general','dropdown',[('general','General admission'),('early','Eligible for early entry')])
inp('entry_time','Your confirmed entry time · HH:MM','09:00')
inp('leave_time','Leave first park · HH:MM','13:00')
inp('transfer','Transfer allowance · minutes','90','dropdown',[(str(n),str(n)) for n in [30,60,90,120]])
inp('days','Minimum matched weekdays','3','dropdown',[('3','3 days · standard'),('1','1 day · exploratory'),('7','7 days · stronger history')])
inp('party_notes','Party needs / heights / mobility / exclusions','Confirm ride eligibility and walking tolerance')
inp('commitments','Meals / shows / reservation times','No fixed commitments entered')
inp('backup','Backup ride / alternate plan','Choose a backup after reviewing availability')
for token,label,park in [('morning_rides','Morning shortlist', 'morning'),('afternoon_rides','Afternoon shortlist','afternoon')]:
 i=inp(token,label,'*','multiselect',[('*','All rides · explore first')]);sub(i,'delimiter',',');sub(i,'fieldForLabel','ride_name');sub(i,'fieldForValue','ride_id')
 s=sub(i,'search');sub(s,'query','`queue_times_index` sourcetype=queue_times:ride park_id=$'+park+'|s$ | stats latest(ride_name) as ride_name by ride_id | sort ride_name');sub(s,'earliest','-7d');sub(s,'latest','now')
 # Safe multiselect choices originate only from numeric ride IDs in the catalog.
 # Reset stale selection when its park changes.
 p=next(x for x in f.findall('input') if x.get('token')==park);c=sub(p,'change');sub(c,'set','*',token='form.'+token)
row=sub(r,'row');h=sub(sub(row,'panel'),'html');h.append(E.fromstring('''<div class="pp-hero"><p class="pp-eyebrow">PARK ATLAS / MY TRIP</p><h1>A day worth looking forward to.</h1><p class="pp-lede">Choose your parks and rides. Confirm your entry time, make room for the transfer, and keep an alternate ready.</p><div class="pp-trip-actions"><button type="button" id="trip-save">Save on this browser</button><button type="button" id="trip-load">Load saved trip</button><button type="button" id="trip-export">Download trip JSON</button><button type="button" id="trip-print">Print / save PDF</button></div><p id="trip-status" role="status" aria-live="polite">Local-only saving requires JavaScript. Apply your selections to run the research.</p></div>'''))
row=sub(r,'row');h=sub(sub(row,'panel'),'html');h.append(E.fromstring('''<div class="pp-note"><strong>Your planning assumptions</strong><p>Enter the official entry time you can actually use. Eligibility is recorded, not verified. The first-park window starts at your entered time; it is not shifted automatically for early entry. Date filters match historical weekdays, not future weather or holiday demand.</p><p>Transfer timing assumes both parks share a timezone. Priorities are a shortlist, not a walking route or a guaranteed ride sequence. Party notes and commitments are reminders, not automatically enforced constraints. Refresh research after loading or changing a saved trip.</p></div>'''))
# Validated numeric/string tokens only; generated list is independently constrained to numeric ride IDs.
base='`queue_times_index` sourcetype=queue_times:ride | eval visit_day=strptime($visit_date|s$,"%Y-%m-%d"), selected_weekday=strftime(visit_day,"%w"), observed_weekday=strftime(strptime(park_local_date,"%Y-%m-%d"),"%w") | where observed_weekday=selected_weekday | `queue_times_observed_day` | where complete_day=1 | eval local_minute=tonumber(park_local_hour)*60+tonumber(substr(park_local_time,15,2)), entry_minute=tonumber(substr($entry_time|s$,1,2))*60+tonumber(substr($entry_time|s$,4,2)), leave_minute=tonumber(substr($leave_time|s$,1,2))*60+tonumber(substr($leave_time|s$,4,2)), arrival_minute=leave_minute+tonumber($transfer|s$) | where match($entry_time|s$,"^([01][0-9]|2[0-3]):[0-5][0-9]$") AND match($leave_time|s$,"^([01][0-9]|2[0-3]):[0-5][0-9]$") AND leave_minute>entry_minute AND arrival_minute<1440'
def table(title,q):
 row=sub(r,'row');v=sub(sub(row,'panel'),'table');sub(v,'title',title);s=sub(v,'search');sub(s,'query',q+' | appendpipe [stats count | where count=0 | eval Status="No qualifying evidence. Check times, date, shortlist and minimum days; use exploratory mode for sparse history." | fields Status]');sub(s,'earliest','-30d');sub(s,'latest','now');sub(v,'option','8',name='count');sub(v,'option','none',name='drilldown')
# Two-stage aggregation gives each day equal weight instead of overweighting dense days.
q=base.replace(' | eval visit_day',' park_id=$morning|s$ | eval visit_day',1)+' | eval shortlist=split($morning_rides|s$,",") | where mvfind(shortlist,"^[*]$")>=0 OR mvfind(shortlist,"^".tostring(ride_id)."$")>=0 | eval early_wait=if(open=1 AND local_minute>=entry_minute AND local_minute<entry_minute+30,wait_time,null()),later_wait=if(open=1 AND local_minute>=entry_minute+30 AND local_minute<leave_minute,wait_time,null()),early_open=if(local_minute>=entry_minute AND local_minute<entry_minute+30,100*open,null()) | stats median(early_wait) as early median(later_wait) as later avg(early_open) as availability count(early_wait) as early_samples by park_name ride_name park_local_date | where isnotnull(early) AND isnotnull(later) AND early_samples>=2 | eval advantage=later-early | stats median(early) as Early_minutes median(later) as Later_minutes median(advantage) as Potential_minutes_avoided min(advantage) as Smallest_daily_advantage max(advantage) as Largest_daily_advantage avg(availability) as Early_open_pct count as Days by park_name ride_name | where Days>=tonumber($days|s$) | eval Early_open_pct=round(Early_open_pct,1) | sort 0 - Potential_minutes_avoided Early_minutes | table park_name ride_name Early_minutes Later_minutes Potential_minutes_avoided Smallest_daily_advantage Largest_daily_advantage Early_open_pct Days'
table('First park · choose your first ride and a backup',q)
q=base.replace(' | eval visit_day',' park_id=$afternoon|s$ | eval visit_day',1)+' | eval shortlist=split($afternoon_rides|s$,",") | where mvfind(shortlist,"^[*]$")>=0 OR mvfind(shortlist,"^".tostring(ride_id)."$")>=0 | where open=1 AND local_minute>=arrival_minute AND _time<=last_open | stats median(wait_time) as daily_median count as Samples by park_name ride_name park_local_hour park_local_date | stats median(daily_median) as Median_minutes min(daily_median) as Lowest_day max(daily_median) as Highest_day count as Days sum(Samples) as Samples by park_name ride_name park_local_hour | where Days>=tonumber($days|s$) | sort 0 park_name ride_name Median_minutes park_local_hour | dedup park_name ride_name | table park_name ride_name park_local_hour Median_minutes Lowest_day Highest_day Days Samples'
table('Second park · best observed hour after your transfer',q)
row=sub(r,'row');h=sub(sub(row,'panel'),'html');h.append(E.fromstring('''<div class="pp-section" id="trip-brief"><h2>Your saved brief</h2><p id="trip-summary">Save your selections to create a readable brief here. Download the JSON as a portable backup; browser storage does not sync between devices.</p></div>'''))
row=sub(r,'row');h=sub(sub(row,'panel'),'html');h.append(E.fromstring('<div class="pp-footer"><a href="https://queue-times.com/">Powered by Queue-Times.com</a><a href="research_guide">Understand the evidence →</a></div>'))
E.indent(r);E.ElementTree(r).write(R/'queue_times/default/data/ui/views/trip_builder.xml',encoding='unicode')
p=R/'queue_times/default/data/ui/nav/default.xml';t=E.parse(p);nav=t.getroot();nav.insert(1,E.Element('view',name='trip_builder'));E.indent(nav);t.write(p,encoding='unicode')
