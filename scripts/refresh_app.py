"""Apply product presentation to generated dashboards; run through build_app.py."""
from pathlib import Path
import xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[1]; V=R/'queue_times/default/data/ui/views'
def sub(p,t,text=None,**attrs):
 e=E.SubElement(p,t,attrs);e.text=text;return e
def htmlrow(r,markup,index=None):
 row=E.Element('row');p=sub(row,'panel');h=sub(p,'html');h.append(E.fromstring(markup))
 if index is None:r.append(row)
 else:r.insert(index,row)
 return row
def save(r,name):
 E.indent(r);E.ElementTree(r).write(V/(name+'.xml'),encoding='unicode')
def hero(kicker,title,copy):
 kicker=kicker.replace('&','&amp;');title=title.replace('&','&amp;');copy=copy.replace('&','&amp;')
 return '<div class="pp-hero"><p class="pp-eyebrow">'+kicker+'</p><h1>'+title+'</h1><p class="pp-lede">'+copy+'</p><div class="pp-tags"><span>OBSERVE</span><span>COMPARE</span><span>PLAN</span></div></div>'
def footer(r):
 htmlrow(r,'<div class="pp-footer"><a href="https://queue-times.com/" target="_blank" rel="noopener noreferrer">Powered by Queue-Times.com</a><span>Posted waits. Observed patterns. Your decisions.</span><a href="research_guide">How to read the data →</a></div>')
def panel(row,title,query,kind='table',earliest='-7d'):
 v=sub(sub(row,'panel'),kind);sub(v,'title',title);s=sub(v,'search');sub(s,'query',query);sub(s,'earliest',earliest);sub(s,'latest','now')
 if kind=='table':sub(v,'option','8',name='count')
 return v
# Build a worldwide planner from the shared, tested Disney calculations.
r=E.parse(V/'disney_world.xml').getroot()
r.find('label').text='Park Planner';r.find('description').text='Pick a park. Find your opening advantage. Keep a backup.'
for q in r.findall('.//query'):q.text=q.text.replace(' park_id IN (5,6,7,8)','')
i=r.find(".//input[@token='park']")
for child in list(i):
 if child.tag in ('choice','default'):i.remove(child)
sub(i,'default','6');sub(i,'fieldForLabel','park_name');sub(i,'fieldForValue','park_id');s=sub(i,'search');sub(s,'query','`queue_times_index` sourcetype=queue_times:ride | stats latest(park_name) as park_name by park_id | sort park_name');sub(s,'earliest','-7d');sub(s,'latest','now')
save(r,'park_planner')
labels={'live_operations':('Live Explorer','What is happening in the parks right now?'),'wait_trends':('Wait Research','Compare observed wait patterns across time.'),'ride_reliability':('Ride Reliability','Know the patterns. Prepare a backup.'),'collection_health':('Data Health','Freshness, errors and collection performance.'),'disney_world':('Disney World','Four parks. One better-informed trip.'),'park_planner':('Park Planner','Your best day starts with a better first ride.')}
for name,(title,copy) in labels.items():
 r=E.parse(V/(name+'.xml')).getroot();r.set('stylesheet','planner.css');r.find('label').text=title;r.find('description').text=copy
 # Replace long introduction with a deliberate, shorter entry point.
 for row in list(r.findall('row')):
  if row.find('./panel/html') is not None:r.remove(row)
 firstrow=next((n for n,c in enumerate(r) if c.tag=='row'),len(r))
 htmlrow(r,hero('PARK ATLAS / '+title.upper(),title,copy),firstrow)
 if name in ('disney_world','park_planner'):
  fs=r.find('fieldset');fs.set('submitButton','true');fs.set('autoRun','true')
  for inp in fs.findall('input'):inp.set('searchWhenChanged','false')
  # Default to one park to keep research fast and comparisons meaningful.
  if name=='disney_world':r.find(".//input[@token='park']/default").text='7'
  htmlrow(r,'<div class="pp-note"><strong>Build your opening strategy</strong><p>Choose a park and weekday, then Apply. Start with the readiness check. Rank rides by the wait you might avoid, compare their early availability, and choose a backup. All hours are local to the park.</p><p>Three-day recommendations are the default. “1 day” is exploratory. Observed hours can include early entry; confirm your access and official hours.</p></div>',firstrow+1)
  # Human-readable column names without changing the calculations.
  names={'First30_median':'First 30m · median','First30_P95':'First 30m · P95','Next30_median':'Next 30m · median','Later_median':'Later · median','Potential_wait_avoided':'Potential minutes avoided','Cost_of_delaying_30m':'Cost of delaying 30m','Early_open_pct':'Early open %','Early_days':'Early days','Later_days':'Later days','park_name':'Park','ride_name':'Ride','Eligible_days':'Complete days','Observed_days':'Observed days','Required_days':'Required days','Minutes_after_open':'Minutes after opening','Unavailable_pct':'Unavailable %','park_local_hour':'Local hour','wait_time':'Wait · minutes','Observation_age_min':'Observation age · min','Source_age_min':'Source age · min'}
  for table in r.findall('.//table'):
   q=table.find('./search/query')
   renames=' '.join(k+' AS "'+v+'"' for k,v in names.items() if k in q.text)
   if renames:q.text+=' | rename '+renames
   sub(table,'option','8',name='count')
   sub(table,'option','none',name='drilldown')
  htmlrow(r,'<div class="pp-note pp-note-warm"><strong>A timing advantage is not an itinerary.</strong><p>Walking time, height requirements, reservations, paid-access inventory and official schedules are not included. P95 describes longer posted waits in the sample—not a promise. Use the live board before committing to a queue.</p></div>')
 for chart in r.findall('.//chart'):
  for opt in list(chart.findall("option[@name='charting.seriesColors']")):chart.remove(opt)
  sub(chart,'option','[0x4DE0C5,0xFFBD69,0x8C9EFF,0xEF8CAF]',name='charting.seriesColors')
 footer(r);save(r,name)
# Home: editorial story followed by actionable entry points and actual data coverage.
r=E.Element('dashboard',version='1.1',theme='dark',stylesheet='planner.css');sub(r,'label','Start Here');sub(r,'description','Park Atlas · Plan less waiting. Make more memories.')
htmlrow(r,hero('PARK ATLAS / TRIP INTELLIGENCE','Less waiting.<br />More of the day you came for.','Turn live queues and collected history into a smarter opening move, a flexible afternoon, and a better backup plan.'))
htmlrow(r,'''<div class="pp-card-grid">
<a class="pp-card" href="park_planner"><span class="pp-number">01 / PLAN</span><h2>Find your opening advantage</h2><p>Choose a park. Compare the first 30 minutes with later waits. Decide what deserves your first stop.</p><strong>Build a morning →</strong></a>
<a class="pp-card" href="disney_world"><span class="pp-number">02 / EXPLORE</span><h2>Four parks. Your kind of day.</h2><p>A focused Disney World workspace for early rides, park hops and evenings worth staying for.</p><strong>Explore Disney World →</strong></a>
<a class="pp-card" href="ride_reliability"><span class="pp-number">03 / ADAPT</span><h2>Have a plan B you like</h2><p>Understand observed unavailable periods. Keep an alternate ride ready before the morning changes.</p><strong>Research reliability →</strong></a>
</div>''')
row=sub(r,'row')
for title,q in [('Parks reporting · 30m','dc(park_id) as Parks'),('Ride observations · 30m','count as Observations'),('Latest observation · minutes ago','max(_time) as seen | eval Minutes=round((now()-seen)/60,1) | fields Minutes')]:
 panel(row,title,'`queue_times_index` sourcetype=queue_times:ride | stats '+q,'single','-30m')
htmlrow(r,'''<div class="pp-section"><p class="pp-eyebrow">THE RESEARCH LOOP</p><h2>A great day has more than one good route.</h2><div class="pp-step-grid"><div><b>Start with evidence</b><p>Check completed days and sample counts before trusting a pattern.</p></div><div><b>Spend your first hour wisely</b><p>Favor rides with a meaningful early wait advantage and reliable opening observations.</p></div><div><b>Leave room to change</b><p>Check today’s queues. Save flexible rides for gaps. Keep your must-dos separate from your maybes.</p></div></div></div>''')
row=sub(r,'row');panel(row,'Your research footprint · click a park to plan','`queue_times_index` sourcetype=queue_times:ride | stats latest(park_name) as Park dc(park_local_date) as Days latest(park_timezone) as Timezone max(_time) as last_seen by park_id | eval Age_minutes=round((now()-last_seen)/60,1) | sort Park | table Park Days Timezone Age_minutes park_id')
t=row.find('.//table');d=sub(t,'drilldown');sub(d,'link','park_planner?form.park=$row.park_id|u$')
htmlrow(r,'''<div class="pp-note"><strong>New installation?</strong><p>Empty charts are normal until collection begins. Start with <a href="setup_guide">Setup &amp; Data Guide</a>, then return after your first poll. Historical recommendations improve as complete operating days accumulate.</p></div>''')
footer(r);save(r,'start_here')
# Two durable in-app guides, no dependence on a public repository URL.
for name,title,content in [
('research_guide','How to Read the Research','''<div class="pp-section"><div class="pp-step-grid"><div><h2>Opening advantage</h2><p>Later-day median minus the first-30-minute median. A larger positive difference is a reason to investigate a ride early—not guaranteed time saved.</p></div><div><h2>Evidence before confidence</h2><p>Recommendations normally require three distinct days. Opening comparisons also require six early and twelve later open snapshots. One-day mode is exploratory.</p></div><div><h2>Median and P95</h2><p>Median is the middle posted wait. P95 is a longer-wait scenario within the observed sample. Neither measures your actual time in line.</p></div></div><h2>What counts as a complete day?</h2><p>Hours are inferred from attractions observed both open and closed that day. We require observations before and after the inferred boundaries, a finished local day and at least two operating hours. Always-open shows cannot define the boundaries. Overnight operations are split at midnight.</p><h2>Unavailable does not mean broken</h2><p>Weather, scheduled closures and maintenance can all appear unavailable. Completed episodes require open observations on both sides. Gaps and incomplete episodes are not included in typical outage durations.</p><h2>Keep the human decisions</h2><p>Choose your must-dos, check ride eligibility, confirm official schedules and leave time for food and travel. This app has no reservation inventory, walking-time model or December crowd forecast. No historical samples are fabricated.</p></div>'''),
('setup_guide','Setup & Data Guide','''<div class="pp-section"><h2>1. Install and choose your parks</h2><p>Install the app on Splunk Enterprise with Python 3. Create a Queue-Times input in Settings → Data inputs. Enter park IDs or * for all parks. Select the queue_times index and a polling interval of at least 300 seconds.</p><h2>2. Keep collection running</h2><p>Run one collector on an always-on host with outbound HTTPS access to queue-times.com. A sleeping laptop cannot collect missed snapshots. The public API supplies current data; history begins when you enable collection.</p><h2>3. Watch your license budget</h2><p>Our worldwide five-minute deployment used about 690 MiB/day—above the 500 MB/day trial limit. The Docker example keeps Disney World at five minutes and other parks at fifteen. Measure your own usage under Settings → Licensing.</p><h2>4. Validate before planning</h2><p>Open <a href="collection_health">Data Health</a>, confirm recent successful polls, then check <a href="live_operations">Live Explorer</a>. Wait for completed days before treating patterns as useful planning evidence.</p><h2>Deployment boundaries</h2><p>The app is tested locally on Splunk Enterprise 9.4.13. It is not Splunkbase-certified or AppInspect-certified. Use persistent volumes, protect administrator credentials, and do not expose the local development ports publicly.</p></div>''')]:
 r=E.Element('dashboard',version='1.1',theme='dark',stylesheet='planner.css');sub(r,'label',title);htmlrow(r,hero('PARK ATLAS / FIELD GUIDE',title,'A better trip starts with knowing what the data can—and cannot—tell you.'));htmlrow(r,content);footer(r);save(r,name)
nav=E.Element('nav',search_view='search');sub(nav,'view',name='start_here',default='true');sub(nav,'view',name='park_planner');sub(nav,'view',name='disney_world');sub(nav,'view',name='live_operations')
c=sub(nav,'collection',label='Research');sub(c,'view',name='wait_trends');sub(c,'view',name='ride_reliability');sub(c,'view',name='research_guide')
c=sub(nav,'collection',label='Setup & Health');sub(c,'view',name='collection_health');sub(c,'view',name='setup_guide');sub(c,'view',name='search')
E.indent(nav);E.ElementTree(nav).write(R/'queue_times/default/data/ui/nav/default.xml',encoding='unicode')
