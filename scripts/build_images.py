"""Generate original SVG editorial illustrations, explicitly not UI screenshots."""
from pathlib import Path
import xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[1]/'docs/images'
R.mkdir(exist_ok=True)
NS='http://www.w3.org/2000/svg'
def svg(title,desc):
 s=E.Element('svg',xmlns=NS,width='1280',height='720',viewBox='0 0 1280 720',role='img');E.SubElement(s,'title').text=title;E.SubElement(s,'desc').text=desc
 defs=E.SubElement(s,'defs');g=E.SubElement(defs,'linearGradient',id='night',x1='0',y1='0',x2='1',y2='1');E.SubElement(g,'stop',offset='0%',**{'stop-color':'#152e44'});E.SubElement(g,'stop',offset='100%',**{'stop-color':'#09111d'})
 E.SubElement(s,'rect',width='1280',height='720',rx='28',fill='url(#night)');return s
def shape(s,tag,**a):return E.SubElement(s,tag,{k.replace('_','-'):str(v) for k,v in a.items()})
def text(s,x,y,value,size=22,color='#e8f2ff',weight=400):
 e=shape(s,'text',x=x,y=y,fill=color,font_size=size,font_weight=weight,font_family='Arial, Helvetica, sans-serif');e.text=value
 return e
def line(s,x,y,value):text(s,x,y,value,18,'#acbfd2')
def card(s,x,y,w,h):shape(s,'rect',x=x,y=y,width=w,height=h,rx=18,fill='#162738',stroke='#35536b')
def save(s,name):E.indent(s);E.ElementTree(s).write(R/name,encoding='unicode')
s=svg('Park Atlas — less waiting, more of your day','Original editorial illustration of a theme-park research app. Not a product screenshot.')
text(s,64,78,'PARK ATLAS',23,'#57e1c5',700);text(s,64,174,'Less waiting.',66,weight=700);text(s,64,250,'More of your day.',66,weight=700)
line(s,67,305,'Theme park planning and research, powered by observations.');line(s,67,337,'Find an opening advantage. Keep a good backup. Go enjoy the park.')
for x,n,t,d in [(64,'01','PLAN','Choose your first ride'),(451,'02','COMPARE','Learn from complete days'),(838,'03','ADAPT','Keep an alternate ready')]:
 card(s,x,405,350,172);text(s,x+26,445,n+' / '+t,16,'#ffbd69',700);text(s,x+26,493,d,22,weight=700);shape(s,'path',d=f'M {x+27} 542 L {x+102} 542 L {x+144} 522 L {x+206} 532 L {x+306} 511',fill='none',stroke='#57e1c5',stroke_width=3)
text(s,65,652,'SPLUNK APP  /  LIVE QUEUES  /  LOCAL PARK TIME  /  TRANSPARENT EVIDENCE',15,'#a8bed1',700)
text(s,65,685,'Editorial illustration • not a dashboard screenshot',12,'#8097ac')
save(s,'park-atlas-hero.svg')
s=svg('A flexible two-park plan','Concept illustration with fictional ride examples; not a screenshot or actual recommendation.')
text(s,64,70,'MY TRIP / TWO PARKS / ONE FLEXIBLE DAY',18,'#57e1c5',700);text(s,64,136,'Give your morning a purpose.',46,weight=700)
for x,heading in [(64,'FIRST PARK'),(664,'SECOND PARK')]:card(s,x,185,552,390);text(s,x+28,227,heading,18,'#ffbd69',700)
text(s,92,278,'Opening priority',25,weight=700);line(s,92,316,'Summit Coaster · a fictional example');line(s,92,350,'Compare early waits, later waits and daily variation.')
text(s,92,410,'Backup you would actually enjoy',23,weight=700);line(s,92,448,'River Voyage · if the first ride is unavailable');line(s,92,502,'Confirm entry time and ride eligibility.');line(s,92,534,'Keep meals and must-dos in the brief.')
text(s,692,278,'Arrive with realistic expectations',25,weight=700);line(s,692,316,'Include travel time before choosing a window.');line(s,692,350,'Compare matched weekdays, not a single snapshot.')
text(s,692,410,'Keep the afternoon flexible',23,weight=700);line(s,692,448,'Use live conditions to choose the next queue.');line(s,692,502,'Save locally • Export JSON • Print a brief');line(s,692,534,'No booking or walking-route optimization implied.')
text(s,64,638,'A shortlist is useful. A false promise of perfect timing is not.',26,'#57e1c5',700)
text(s,64,685,'Concept illustration • fictional ride examples • not a dashboard screenshot',13,'#a8bed1')
save(s,'trip-planning-story.svg')
s=svg('Evidence before recommendations','Diagram of the data-quality pipeline: observations, coverage checks, daily comparisons, and planning decisions.')
text(s,64,75,'HOW PARK ATLAS THINKS',18,'#57e1c5',700);text(s,64,143,'Evidence before recommendations.',43,weight=700)
items=[('01','OBSERVE','Current API snapshots','Preserve source timestamps'),('02','CHECK','Cadence + daily coverage','Exclude incomplete days'),('03','COMPARE','Equal-weight daily medians','Expose variation and counts'),('04','DECIDE','Priority + backup','Confirm real-world access')]
for j,(n,heading,a,b) in enumerate(items):
 x=64+j*300;card(s,x,235,270,235);text(s,x+22,278,n,30,'#ffbd69',700);text(s,x+22,325,heading,19,'#57e1c5',700);text(s,x+22,375,a,17);text(s,x+22,407,b,15,'#acbfd2')
 if j<3:shape(s,'path',d=f'M {x+277} 346 L {x+293} 346 M {x+287} 340 L {x+293} 346 L {x+287} 352',stroke='#57e1c5',fill='none',stroke_width=2)
text(s,64,552,'Never invent missing history.',29,weight=700);line(s,64,595,'The app describes observations. It does not guarantee waits, availability or an optimized route.')
text(s,64,682,'Architecture illustration • no live data shown',13,'#a8bed1');save(s,'research-pipeline.svg')
print('Built three original, labeled SVG illustrations')
