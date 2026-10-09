"""Solar enclosure chart: static SunCorp study assembly and two consultation courts."""
import sys,json,math,bpy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import kit as k
from kit import *
p=Path(__file__).resolve().parents[1];init(__file__,'D18_directory_04')
# An inboard technical spine forms enclosed archives behind the consultation walk.
prism('NorthRecordBlade',[(16.7,-22.0),(18.1,-22.0),(19.0,-9),(17.6,-8.6),(16.7,-15)],0,3.55,'blue','shared_floor','records',.06)
prism('SouthServiceBlade',[(17.6,11.2),(19.0,11.7),(18.1,25.8),(16.7,25.8),(16.7,19)],0,3.55,'blue','shared_floor','service',.06)
shelf('ProjectArchive',12.7,-21.3,4.2,.86,'records',2.9)
cabinet('PlanDrawers',13.1,-13.3,2.0,4.2,'records',1.4)
box('ArchivePlotLedge',(13.1,1.46,-13.3),(2.12,.12,4.3),'white','PlanDrawers_carcass','records',.04)
chart('StoredEnclosurePlan',13.1,-13.3,1.55,2.7,'ArchivePlotLedge','records',1.535)
# Curved split consultation edges provide distinct north/south rooms and level routes.
for side,z in [('Fore',-14.4),('Aft',17.8)]:
 top=table(side+'Consult',25.8,z,8.4,3.5,'consultation',.78,'white',True)
 chart(side+'Study',25.8,z,5.2,2.2,top,'consultation',.875)
 for j,x in enumerate([23.1,25.8,28.5]):swivel(side+'ConsultSeat'+str(j),x,z+2.75,'consultation')
 # Behind the seats: a low fitted crescent, resting/access edge stays at floor level.
 pieces=arcwall(side+'Crescent',25.8,z+1.2,5.5,.32,.12,math.pi-.12,0,1.25,'blue','shared_floor','consultation',18)
 # First ten joined cabinet compartments on the outside give real useful depth.
 for j,x in enumerate([21.7,29.9]):cabinet(side+'Returns'+str(j),x,z+4.8,.70,1.5,'consultation',1.1)
# The central solar project model rests on a faceted fitted consultation plinth, no hologram.
top=table('SolarStudy',25,1,9.4,9.4,'solar_focus',.80,'ivory',True)
disc('ModelMast',25,1,.89,.18,.46,'zinc',top,'solar_focus')
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=.85,location=k.xyz((25,2.15,1)))
finish(bpy.context.object,'StudyStar','ivory','ModelMast','solar_focus','static_nonoperating_project_model',0)
# Four anchored supports carry a partial enclosure study cage. Geometry is illustrative fiction.
for j,angle in enumerate([0,math.pi/2,math.pi,3*math.pi/2]):
 x,z=25+2.4*math.cos(angle),1+2.4*math.sin(angle)
 rod('ModelStanchion'+str(j),(x,.89,z),(x,2.15,z),.065,'zinc',top,'solar_focus')
previous='ModelStanchion0'
for j in range(32):
 a=j*math.tau/32;b=(j+1)*math.tau/32
 rod('ModelEquator'+str(j),(25+2.4*math.cos(a),2.15,1+2.4*math.sin(a)),(25+2.4*math.cos(b),2.15,1+2.4*math.sin(b)),.035,'brass',previous,'solar_focus')
 previous='ModelEquator'+str(j)
for wing in range(3):
 yaw=wing*math.pi/3;previous='ModelEquator'+str(round(yaw/math.tau*32)%32)
 for j in range(18):
  t0=math.pi*j/18;t1=math.pi*(j+1)/18
  def pt(t):return (25+2.4*math.cos(t)*math.cos(yaw),2.15+1.45*math.sin(t),1+2.4*math.cos(t)*math.sin(yaw))
  rod('ModelMeridian'+str(wing)+'_'+str(j),pt(t0),pt(t1),.030,'zinc',previous,'solar_focus');previous='ModelMeridian'+str(wing)+'_'+str(j)
# Consultation card pockets are mounted into the central installation.
for j,z in enumerate([-2.4,4.4]):
 box('StudyCard'+str(j),(25,.94,z),(1.9,.075,.95),'blue',top,'solar_focus',.035)
# A single circular ceiling aperture within retained roof shapes the focus.
# Hanging members meet roof underside; connected ring segments carry their mounted lights.
for j,t in enumerate([0,math.pi/2,math.pi,3*math.pi/2]):
 x,z=25+5.35*math.cos(t),1+5.35*math.sin(t)
 rod('CoveHang'+str(j),(x,4.5,z),(x,4.00,z),.052,'zinc','shared_ceiling','solar_focus')
previous='CoveHang0'
for j in range(40):
 a=j*math.tau/40;b=(j+1)*math.tau/40
 poly=[(25+r*math.cos(t),1+r*math.sin(t)) for r,t in [(5.15,a),(5.55,a),(5.55,b),(5.15,b)]]
 prism('FocusCove'+str(j),poly,3.88,.20,'white',previous,'solar_focus',.01);previous='FocusCove'+str(j)
for j,t in enumerate([0,math.pi/2,math.pi,3*math.pi/2]):
 x,z=25+5.35*math.cos(t),1+5.35*math.sin(t)
 light('FocusTask'+str(j),x,z,3.90,.38,.42,'FocusCove'+str(j*10),'solar_focus',300)
# Real service/rest corners occupy the opaque rear portion instead of inventing more glazing.
care('SolarCare',11.6,22,'care')
seat('QuietProjectRest',13.2,15.6,4.0,'rest',math.pi/2)
rt=table('RestCupTable',14.3,12.8,1.1,1.2,'rest',.55,'wood',True)
cup('ProjectCup',14.3,12.8,.64,rt,'rest')
shelf('RevisionHandover',13.0,25.5,4.8,.65,'handover',2.6)
box('ProjectEntryPier',(14.4,2.25,-4.4),(1.0,4.5,1.1),'blue','shared_floor','arrival',.05)
profile('ProjectEntryBrow',[(13.9,3.75),(17.7,4.12),(18.1,4.5),(13.9,4.5)],-4.95,-3.85,'white','ProjectEntryPier','arrival',.035)
box('SolarPlaque',(14.93,1.66,-4.4),(.055,.43,.80),'rubber','ProjectEntryPier','arrival',.012)
text('SolarName','Solar project',(14.966,1.61,-4.4),.13,'SolarPlaque','arrival','east')
allocation=json.loads((p/'allocation.json').read_text())
save({**allocation,'architecture':'A grounded SunCorp solar-enclosure study cage anchors a circular cove and split consultation courts; inboard records/service spine and opaque rear rest/care. Static architectural fiction, no operating simulation.','programme_capacity':'No new capacity/roster declared; furniture candidates only.','paths':{
'arrival_focus':[[10,0],[15,0],[19.6,0],[19.6,-5.5],[25,-5.5]],
'fore_consult':[[19.6,0],[19.6,-8],[19.6,-13.4],[21.0,-13.4]],
'aft_consult':[[19.6,0],[19.6,10.2],[21,10.2],[21,14.8],[22,14.8]],
'care':[[15,0],[15,11],[15.7,11],[15.7,22],[13.7,22]],
'records':[[15,0],[15,-9],[15.6,-9],[15.6,-23.2],[13.2,-23.2]]
},'views':[
['arrival',[11.5,1.65,0],[25,1.65,1]],
['solar_focus',[19.5,1.65,-5.5],[26,1.65,2]],
['fore_consult',[20.5,1.65,-8],[28,1.65,-15]],
['aft_consult',[20.5,1.65,10.3],[28,1.65,18]],
['rest_care',[15.5,1.65,10.4],[12.0,1.65,23]],
['records',[13.2,1.65,-23.2],[13.2,1.65,-20.7]]
]})

