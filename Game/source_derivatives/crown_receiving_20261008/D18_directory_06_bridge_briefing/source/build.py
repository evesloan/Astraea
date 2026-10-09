"""Bridge briefing: a directed shared chamber, group arrival and screened breakout court."""
import sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import kit as k
from kit import *
p=Path(__file__).resolve().parents[1];init(__file__,'D18_directory_06')
# Fitted focal joinery and its full-height structural/acoustic cheeks establish the room axis.
box('BriefingFocusCarcass',(-27,1.875,20.2),(13.4,3.75,.72),'blue','shared_floor','briefing_focus',.07)
for side,x in [('Port',-34.2),('Inboard',-19.8)]:
 prism('Focus'+side+'Cheek',chamfer(x-.50,x+.50,19.5,22.3,.18),0,4.5,'white','shared_floor','briefing_focus',.04)
box('BriefingBoard',(-27,2.2,20.586),(7.6,1.75,.045),'rubber','BriefingFocusCarcass','briefing_focus',.035)
# Physical paper/plot boards; these are meeting materials, not live ship instrumentation.
for j,x in enumerate([-29.2,-27,-24.8]):
 box('BoardPlot'+str(j),(x,2.2,20.618),(1.82,1.25,.026),'white','BriefingBoard','briefing_focus',.015)
 for row,y in enumerate([1.85,2.12,2.39]):
  box('BoardRule'+str(j)+'_'+str(row),(x,y,20.637),(1.52,.018,.012),'zinc','BoardPlot'+str(j),'briefing_focus',.002)
box('BriefingCredenza',(-27,.47,21.45),(10.8,.94,1.4),'blue','shared_floor','briefing_focus',.06)
box('BriefingCredenzaCap',(-27,1.0,21.45),(10.95,.12,1.48),'white','BriefingCredenza','briefing_focus',.04)
# One forward-folded ceiling mass meets the preserved roof and directs the chamber axis.
profile('DirectedCoffer',[(-33.2,4.5),(-33.2,4.12),(-30.0,3.65),(-23.6,3.65),(-18.8,4.12),(-18.8,4.5)],23.4,38.2,'white','shared_ceiling','briefing',.04)
for j,(x,z) in enumerate([(-29,26),(-24.5,26),(-29,35.7),(-24.5,35.7)]):light('BriefingCofferTask'+str(j),x,z,3.62,1.10,.40,'DirectedCoffer','briefing',550)
# Table length supports group handover without a second bridge/control wall.
top=table('SharedBriefing',-27,32.5,3.25,10.8,'briefing',.78,'white',True)
chart('BriefingTablePlot',-27,32.5,2.2,7.8,top,'briefing',.875)
for side,x,angle in [('Port',-30.5,math.pi/2),('Inboard',-23.5,-math.pi/2)]:
 for j,z in enumerate([29.0,31.3,33.6,35.9]):swivel(side+'BriefingSeat'+str(j),x,z,'briefing',angle)
# Arrival has somewhere to gather, stow materials and turn a cart before joining the table.
arcwall('ArrivalAcousticBlade',-18.5,46.0,5.0,.42,-.30,1.43,0,2.60,'blue','shared_floor','group_arrival',22)
seat('GroupPause',-14.6,35.2,4.2,'group_arrival',-math.pi/2)
shelf('HandoverRecords',-14.5,46.7,3.8,.70,'handover',2.9)
cabinet('GroupMaterials',-13.8,29,1.5,5.5,'group_arrival',2.2)
# The screened aft court supports quiet post-briefing discussion and a resting perimeter.
walls=arcwall('BreakoutWall',-28.5,51,5.4,.35,math.pi/2,3*math.pi/2,0,2.70,'blue','shared_floor','breakout',24)
for j in range(24):
 a=math.pi/2+math.pi*j/24;b=math.pi/2+math.pi*(j+1)/24
 poly=[(-28.5+r*math.cos(t),51+r*math.sin(t)) for r,t in [(5.19,a),(5.61,a),(5.61,b),(5.19,b)]]
 prism('BreakoutCrest'+str(j),poly,2.70,.16,'white','BreakoutWall_'+str(j),'breakout',.01)
bt=table('BreakoutTable',-28.5,51,4.8,2.7,'breakout',.78,'white',True)
for j,x in enumerate([-29.9,-27.1]):
 swivel('BreakoutFore'+str(j),x,48.3,'breakout',math.pi)
 swivel('BreakoutAft'+str(j),x,53.7,'breakout',0)
seat('BriefingQuietRest',-33.1,57.8,3.4,'rest',math.pi/2)
rt=table('QuietSideTable',-31.3,56.8,1.1,1.2,'rest',.55,'wood',True)
cup('BriefingCup',-31.3,56.8,.64,rt,'rest')
care('BriefingCare',-13.1,55,'care')
box('BriefingPlaque',(-19.27,1.72,21.4),(.06,.44,.84),'rubber','FocusInboardCheek','arrival',.016)
text('BriefingName','Briefing',(-19.234,1.67,21.4),.14,'BriefingPlaque','arrival','east')
allocation=json.loads((p/'allocation.json').read_text())
save({**allocation,'architecture':'A directed briefing chamber under one folded coffer, with shared reachable table, fitted focal paper-board wall, group arrival/materials edge and a separately screened breakout/rest court. Deliberately enclosed; no windows or second bridge simulation.','programme_capacity':'No new capacity/roster declared; group furniture candidates only.','paths':{
'entry_table':[[-10,40],[-15,40],[-20.8,40],[-20.8,32.5],[-22,32.5]],
'focal_approach':[[-20.8,32.5],[-20.8,24],[-27,24]],
'breakout':[[-20.8,40],[-22,43.4],[-22,51],[-24.8,51]],
'quiet_rest':[[-22,51],[-22,58.8],[-31.8,58.8]],
'care':[[-10,40],[-11.1,40],[-11.1,55]]
},'views':[
['arrival',[-11.3,1.65,40],[-26,1.65,30]],
['briefing',[-20.8,1.65,38.7],[-27,1.65,22]],
['focal_table',[-32.0,1.65,37.5],[-27,1.65,20.6]],
['breakout',[-22,1.65,43.4],[-29,1.65,51]],
['rest_care',[-11.1,1.65,51.5],[-13.1,1.65,55]],
['quiet_rest',[-29,1.65,58.8],[-33.1,1.65,57.8]]
]})

