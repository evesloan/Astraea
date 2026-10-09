"""Navigation: an archive narthex, chart nave, two outward work courts and window watch edge."""
import sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import kit as k
from kit import *
p=Path(__file__).resolve().parents[1];init(__file__,'D18_directory_02')
# Thick stepped archive blade, not a scatter of freestanding furniture.
# Two asymmetric wings frame a broad central arrival to the window and chart nave.
prism('ForeArchiveBlade',[(16,-69),(17.4,-69),(20.1,-58.0),(18.7,-57.6),(16,-64)],0,3.70,'blue','shared_floor','fore_archive',.06)
prism('AftArchiveBlade',[(18.7,-46.3),(20.0,-46),(17.6,-31),(16.2,-31),(16.2,-39)],0,3.70,'blue','shared_floor','aft_archive',.06)
# Floor-standing deep portal; hollow central opening retains the real entry sightline.
box('ArrivalLeftJamb',(18.0,2.25,-56.5),(1.10,4.5,1.25),'blue','shared_floor','arrival',.06)
box('ArrivalRightJamb',(18.0,2.25,-47.5),(1.10,4.5,1.25),'blue','shared_floor','arrival',.06)
verts=[]
outline=[(-55.88,2.95),(-55.15,3.65),(-52,4.02),(-48.85,3.65),(-48.12,2.95),(-48.12,4.5),(-55.88,4.5)]
for x in [17.45,18.55]:verts += [(x,y,z) for z,y in outline]
n=len(outline);faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
mesh('ArrivalVault',verts,faces,'white','ArrivalLeftJamb','arrival',.04)
# Archive pockets fit behind blades; access turns from the entry court.
for i,(x,z,w) in enumerate([(13.6,-66.6,4.0),(14.0,-61.8,4.5),(13.2,-40.7,3.4),(13.2,-33.0,3.4)]):
 shelf('ChartArchive'+str(i),x,z,w,.72,'archive',2.85)
# Weighted ceiling returns rise into the retained roof, carrying archive wing character.
profile('ForeArchiveCoffer',[(16.0,3.70),(19.4,3.70),(23.0,4.38),(23.0,4.5),(16.0,4.5)],-68.4,-58.3,'white','ForeArchiveBlade','fore_archive',.035)
profile('AftArchiveCoffer',[(16.2,3.70),(19.4,3.70),(23.0,4.38),(23.0,4.5),(16.2,4.5)],-45.8,-31.3,'white','AftArchiveBlade','aft_archive',.035)
# Two low chart islands: their silhouettes lead to the glass, not a terminal wall.
top=table('ChartNave',25.2,-52,3.2,11.4,'comparison',.82,'white',True)
chart('MainRouteChart',25.2,-52,2.30,8.0,top,'comparison',.925)
# An offset comparison bench allows people to face each other across reachable charts.
wing=table('ComparisonWing',30.0,-51.2,2.6,7.5,'comparison',.82,'white',True)
chart('ComparisonInset',30.0,-51.2,1.75,5.5,wing,'comparison',.925)
for j,z in enumerate([-53.6,-50.8,-48.2]):
    box('ReferenceTray'+str(j),(25.3,1.01,z),(.90,.18,.58),'blue',top,'comparison',.028)
    box('RouteFolio'+str(j),(25.3,1.115,z),(.75,.035,.46),'ivory','ReferenceTray'+str(j),'comparison',.009)
# Instrument drawers and physical roll rests around the central chart.
for i,z in enumerate([-55.4,-48.6]):
 box('ChartDrawers'+str(i),(25.2,.48,z),(2.65,.50,1.1),'blue','ChartDrawerRail'+str(i),'comparison',.05)
 # drawer housing reaches the supporting central trunk? fitted from pedestal with visible rail.
 box('ChartDrawerRail'+str(i),(25.2,.52,(z+52)/2-52),(1.0,.16,abs(z+52)+.15),'zinc','ChartNave_pedestal','comparison',.02)
for i,z in enumerate([-55,-51.8,-48.5]):
 rod('ChartRoll'+str(i),(26.1,.94,z),(26.7,.94,z),.065,'ivory',top,'comparison')
# Outward work courts, low enough to keep the sloping panes wholly visible.
for i,z in enumerate([-64.0,-39.1]):
 topi=table('OutwardChart'+str(i),30.5,z,5.6,4.6,'outward_work',.82,'white',True)
 chart('OutwardPlot'+str(i),31.1,z,2.8,2.75,topi,'outward_work',.925)
 terminal('RouteTerminal'+str(i),29.1,z-.7,topi,'outward_work',.91,-math.pi/2)
 swivel('Navigator'+str(i),26.8,z-.6,'outward_work',math.pi/2)
 # Deep hull-side reference ledge remains 1.45m inside original sill.
 box('WindowLedge'+str(i),(33.2,.44,z+3.2),(1.5,.88,3.8),'blue','shared_floor','window_watch',.06)
 box('WindowLedgeCap'+str(i),(33.2,.93,z+3.2),(1.6,.10,3.9),'white','WindowLedge'+str(i),'window_watch',.035)
 for j in range(3):
  box('WindowRecord'+str(i)+'_'+str(j),(33.35,1.19,z+2.3+j*.65),(.68,.40,.40),'rubber','WindowLedgeCap'+str(i),'window_watch',.04)
# Watch/rest terminus oriented to actual view, plus level cart/broad-body pauses.
seat('ForeWatch',30.7,-70.3,3.4,'window_watch',math.pi/2)
seat('AftWatch',31.0,-32.0,3.2,'window_watch',math.pi/2)
ct=table('WatchSideTable',29.1,-30.3,1.1,1.3,'window_watch',.55,'wood',True)
cup('WatchCup',29.1,-30.3,.64,ct,'window_watch')
seat('HandoverBench',12.9,-46.0,3.4,'arrival',math.pi/2)
box('HandoverPinback',(11.9,.99,-47.4),(.25,1.98,2.1),'blue','shared_floor','arrival',.055)
box('HandoverFace',(12.05,1.44,-47.4),(.045,.80,1.6),'rubber','HandoverPinback','arrival',.025)
care('ChartCare',11.4,-35.2,'care')
# Locally supported mounted illumination; retained Crown fixture rows provide the ceiling rhythm.
light('ArchiveTask',14.2,-61.8,2.74,1.9,.4,'ChartArchive1_back','archive',130)
# Text remains subordinate. Entry sign is mounted in the new arch's side jamb.
box('NavigationPlaque',(18.575,1.65,-56.5),(.06,.46,.88),'rubber','ArrivalLeftJamb','arrival',.015)
text('NavigationName','Navigation',(18.611,1.60,-56.5),.13,'NavigationPlaque','arrival','east')
allocation=json.loads((p/'allocation.json').read_text())
contract={**allocation,'architecture':'Deep archive narthex framing a level chart nave; two outward work courts and low window-watch edges. No new slab, hull aperture or operating simulation.','programme_capacity':'No new capacity/roster declared; candidate furniture only.','support_notes':'Archive blades and vault jambs stand on retained floor. Crown roof and glazing are context only.','paths':{'arrival_chart':[[10,-52],[14,-52],[20.7,-52],[20.7,-57.5],[25.2,-59.1]],'fore_work':[[20.7,-52],[20.7,-60],[24,-60],[24,-64],[25.8,-64]],'aft_work':[[20.7,-52],[20.7,-44.1],[24.0,-44.1],[24,-39.1],[25.8,-39.1]],'window_watch':[[24,-44.1],[24,-33.8],[28.8,-33.8],[28.8,-32],[29.4,-32]],'care':[[14,-52],[14,-44],[15.5,-44],[15.5,-35.2],[13.4,-35.2]]},'views':[
 ['arrival',[11.3,1.65,-52],[28,1.65,-52]],
 ['chart_nave',[20.7,1.65,-58.8],[27.0,1.65,-48.8]],
 ['fore_work',[24.0,1.65,-59.0],[31.1,1.65,-65.0]],
 ['aft_watch',[24.0,1.65,-44.1],[32.8,1.65,-34]],
 ['archive_care',[15.5,1.65,-36.2],[11.9,1.65,-35.2]]
 ]}
save(contract)

