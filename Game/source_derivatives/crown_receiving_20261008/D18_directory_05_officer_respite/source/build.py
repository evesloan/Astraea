"""Officer respite: screened window conversation pockets around a quiet level walk."""
import sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import kit as k
from kit import *
p=Path(__file__).resolve().parents[1];init(__file__,'D18_directory_05')
# Offset arrival screens the quiet window edge from corridor movement.
prism('ArrivalPrivacyBlade',[(-16.4,-7.5),(-15.8,-7.5),(-15.4,-6),(-15.4,-2),(-16.3,-.5),(-17.0,-.5),(-16.1,-2.3),(-16.1,-5.8)],0,3.22,'blue','shared_floor','arrival',.065)
profile('ArrivalPrivacyReturn',[(-21.4,4.5),(-21.4,4.30),(-17,3.22),(-15.4,3.22),(-15.4,4.5)],-5.9,-2.2,'white','ArrivalPrivacyBlade','arrival',.035)
# Three open acoustic alcoves face the retained port panes. They shape genuine quiet rooms.
for num,cz in enumerate([-15.2,-3.3,8.0]):
 name='Conversation'+str(num)
 walls=arcwall(name+'Wall',-30,cz,4.6,.34,-math.pi/2,math.pi/2,0,2.60,'blue','shared_floor','quiet_conversation',24)
 # Weighted top/end conditions are directly seated on their own wall segments.
 for j in range(24):
  a=-math.pi/2+math.pi*j/24;b=-math.pi/2+math.pi*(j+1)/24
  poly=[(-30+r*math.cos(t),cz+r*math.sin(t)) for r,t in [(4.40,a),(4.84,a),(4.84,b),(4.40,b)]]
  prism(name+'Cap'+str(j),poly,2.60,.16,'wood',name+'Wall_'+str(j),'quiet_conversation',.01)
 # Useful paired seat edges and table, rather than all chairs facing an arbitrary focal prop.
 seat(name+'SeatFore',-30.6,cz-2.2,2.50,'quiet_conversation',math.pi,'oat')
 seat(name+'SeatAft',-30.6,cz+2.2,2.50,'quiet_conversation',0,'cloth')
 top=table(name+'Coffee',-31.4,cz,1.7,2.4,'quiet_conversation',.55,'wood',True)
 cup(name+'Cup',-31.4,cz+.35,.64,top,'quiet_conversation')
 # Local floor-supported side console, real compartment and mounted reading lamp.
 cabinet(name+'Side',-27.6,cz,1.0,1.6,'quiet_conversation',.95)
 box(name+'LampStem',(-27.6,1.21,cz),(.08,.52,.08),'brass',name+'Side_carcass','quiet_conversation',.015)
 light(name+'Read',-27.6,cz,1.50,.6,.45,name+'LampStem','quiet_conversation',55)
# Refreshment corner is fitted, maintained and bounded, not a new commercial bar.
cabinet('RefreshmentJoinery',-18.6,-20,2.0,5.2,'refreshment',.90)
box('RefreshmentWorktop',(-18.6,.96,-20),(2.12,.12,5.35),'ivory','RefreshmentJoinery_carcass','refreshment',.05)
box('RefreshmentBack',(-19.6,1.22,-20),(.14,1.15,5.1),'blue','RefreshmentWorktop','refreshment',.03)
box('RefreshmentShelf',(-19.15,1.80,-20),(1.0,.09,5.1),'wood','RefreshmentBack','refreshment',.025)
for j,z in enumerate([-21.1,-20.5,-19.9]):cup('StoredMug'+str(j),-18.9,z,1.85,'RefreshmentShelf','refreshment')
disc('KettleFoot',-18.4,-18.5,1.02,.23,.03,'rubber','RefreshmentWorktop','refreshment')
disc('KettleBody',-18.4,-18.5,1.05,.20,.32,'zinc','KettleFoot','refreshment')
disc('KettleLid',-18.4,-18.5,1.37,.20,.03,'blue','KettleBody','refreshment')
rod('KettleSpout',(-18.6,1.25,-18.5),(-18.88,1.39,-18.5),.05,'zinc','KettleBody','refreshment')
box('KettleHandle',(-18.10,1.28,-18.5),(.18,.28,.08),'rubber','KettleBody','refreshment',.035)
light('RefreshmentTask',-19.10,-20,1.76,.70,1.7,'RefreshmentShelf','refreshment',100)
# Care/return cupboard and a discreet locker/rest side behind the arrival.
care('RespiteCare',-12.9,8.3,'care')
cabinet('PersonalHooks',-12.9,-13.5,1.0,3.8,'staff_edge',2.30)
for j,z in enumerate([-14.5,-13.5,-12.5]):rod('CoatHook'+str(j),(-12.42,1.55,z),(-12.25,1.65,z),.03,'zinc','PersonalHooks_carcass','staff_edge')
seat('ArrivalPause',-12.5,1.1,3.3,'arrival',-math.pi/2,'cloth')
box('RespitePlaque',(-15.37,1.67,-5.2),(.06,.43,.82),'rubber','ArrivalPrivacyBlade','arrival',.015)
text('RespiteName','Officer respite',(-15.334,1.62,-5.2),.12,'RespitePlaque','arrival','east')
allocation=json.loads((p/'allocation.json').read_text())
save({**allocation,'architecture':'An offset screened threshold opens onto three port-view acoustic conversation pockets. Integrated benches, shaded table courts and a practical refreshment/care edge occupy the existing level floor. No new hull opening or guest-office clone.','programme_capacity':'No new capacity or roster; furniture candidates only.','paths':{
'entry_walk': [[-10,-4],[-12.9,-4],[-12.9,-9.2],[-22.8,-9.2]],
'fore_conversation':[[-22.8,-9.2],[-33.2,-9.2],[-33.2,-15.2]],
'middle_conversation':[[-22.8,-9.2],[-33.2,-9.2],[-33.2,-3.3]],
'aft_conversation':[[-22.8,-9.2],[-23.5,-9.2],[-23.5,2.1],[-33.2,2.1],[-33.2,8]],
'refreshment':[[-12.9,-9.2],[-16.2,-9.2],[-16.2,-20]],
'care':[[-12.9,-4],[-10.95,-4],[-10.95,5.8],[-10.95,8.3]]
},'views':[
['arrival',[-11.2,1.65,-4],[-17,1.65,-4]],
['window_walk',[-22.8,1.65,-9.2],[-32.8,1.65,-14]],
['conversation',[-33.2,1.65,-9.2],[-29.5,1.65,-15.2]],
['quiet_aft',[-33.2,1.65,2.1],[-29.5,1.65,8]],
['refreshment',[-14.8,1.65,-15.5],[-18.5,1.65,-20]],
['care',[-10.95,1.65,4.5],[-12.9,1.65,8.3]]
]})

