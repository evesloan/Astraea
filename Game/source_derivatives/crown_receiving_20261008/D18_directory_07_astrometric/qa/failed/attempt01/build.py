"""Astrometric station: paired task hoods, a reference spine and a precision comparison bench."""
import sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent));import kit as k
from kit import *
p=Path(__file__).resolve().parents[1];init(__file__,'D18_directory_07')
# Two mirrored, grounded cantilever task cells make a compact precision workplace.
profile('ForeTaskHood',[(15.5,0),(16.4,0),(16.4,3.28),(22.5,3.60),(23.2,4.5),(15.5,4.5)],37.0,42.5,'blue','shared_floor','fore_task',.055)
profile('AftTaskHood',[(33.7,0),(32.8,0),(32.8,3.25),(26.8,3.60),(26.1,4.5),(33.7,4.5)],50.5,56.0,'blue','shared_floor','aft_task',.055)
# Visible rods mount level luminaires below sloping soffits.
for j,x in enumerate([18.5,21.5]):
 roof=3.28+(x-16.4)/6.1*.32
 rod('ForeTaskHang'+str(j),(x,3.30,39.6),(x,roof+.01,39.6),.035,'zinc','ForeTaskHood','fore_task')
light('ForePrecisionTask',20,39.6,3.27,3.25,.50,'ForeTaskHang0','fore_task',450)
for j,x in enumerate([28,31]):
 roof=3.25+(32.8-x)/6*.35
 rod('AftTaskHang'+str(j),(x,3.30,52),(x,roof+.01,52),.035,'zinc','AftTaskHood','aft_task')
light('AftPrecisionTask',29.5,52,3.27,3.25,.50,'AftTaskHang0','aft_task',450)
# Paired small-team benches compare records rather than duplicating the public Star Atlas.
nt=table('ForePrecisionBench',20.4,39.6,6.4,2.8,'fore_task',.85,'white')
st=table('AftPrecisionBench',29.3,52,6.4,2.8,'aft_task',.85,'white')
for j,x in enumerate([19.0,21.8]):
 terminal('ForeComparison'+str(j),x,39.6,nt,'fore_task',.94,math.pi)
 swivel('ForeOperator'+str(j),x,42.4,'fore_task')
for j,x in enumerate([27.9,30.7]):
 terminal('AftComparison'+str(j),x,52,st,'aft_task',.94,0)
 swivel('AftOperator'+str(j),x,49.2,'aft_task',math.pi)
# The central fitted reference spine is a shared physical landmark and working edge.
prism('ReferenceSpine',chamfer(24.75,26.05,41.8,50.2,.34),0,2.65,'blue','shared_floor','reference_spine',.055)
box('ReferenceSpineCrown',(25.4,2.73,46),(1.48,.16,8.55),'white','ReferenceSpine','reference_spine',.035)
for face,x,sign in [('Port',24.725,-1),('Starboard',26.075,1)]:
 for j,z in enumerate([43.2,46,48.8]):
  box(face+'ComparisonPocket'+str(j),(x,1.48,z),(.06,1.54,2.1),'rubber','ReferenceSpine','reference_spine',.025)
  box(face+'ReferenceSheet'+str(j),(x+sign*.045,1.52,z),(.025,1.13,1.64),'white',face+'ComparisonPocket'+str(j),'reference_spine',.012)
 light(face+'SpineLight',x+sign*.27,46,2.50,.80,5.8,'ReferenceSpine','reference_spine',200)
# Calibration/storage court: a bench with a mounted instrument, not an invented live observatory.
ct=table('CalibrationBench',21.9,54,4.7,2.0,'calibration',.85,'white')
disc('CalibrationInstrumentFoot',21.7,54,.94,.31,.05,'rubber',ct,'calibration')
rod('CalibrationStem',(21.7,.99,54),(21.7,1.33,54),.09,'zinc','CalibrationInstrumentFoot','calibration')
rod('StaticComparatorTube',(21.1,1.33,54),(22.3,1.33,54),.18,'blue','CalibrationStem','calibration',16)
disc('ComparatorDial',22.3,54,1.17,.075,.08,'zinc','StaticComparatorTube','calibration')
box('CalibrationPad',(22.8,.98,54),(.72,.075,1.15),'rubber',ct,'calibration',.025)
swivel('CalibrationOperator',21.9,51.5,'calibration',math.pi)
rod('CalibrationLampPost',(23.6,.94,54),(23.6,1.65,54),.040,'zinc',ct,'calibration')
light('CalibrationLamp',23.6,54,1.60,.7,.50,'CalibrationLampPost','calibration',80)
shelf('AstrometricRecords',25,58.1,6.3,.70,'records',2.9)
care('AstrometricCare',12.1,55,'care')
seat('QuietWatchBreak',13.0,35.5,3.0,'rest',math.pi/2)
rt=table('WatchBreakTable',13.5,33.2,1.1,1.0,'rest',.55,'wood',True)
cup('AstrometricCup',13.5,33.2,.64,rt,'rest')
box('AstrometricPlaque',(24.706,1.88,46),(.055,.43,1.08),'rubber','ReferenceSpine','arrival',.012)
text('AstrometricName','Astrometry',(24.671,1.82,46),.13,'AstrometricPlaque','arrival','west')
allocation=json.loads((p/'allocation.json').read_text())
save({**allocation,'architecture':'Two grounded sloping task hoods frame paired precision benches around a tall fitted record/comparison spine. An enclosed calibration/storage court and modest quiet/care edge complete the level workplace. No new window, telescope aperture, public planetarium or operating astrometric simulation.','programme_capacity':'No capacity/roster declared; candidate staff furniture only.','paths':{
'arrival_fore':[[10,46],[14,46],[20.4,46],[20.4,43.5]],
'aft_work':[[20.4,46],[23.5,46],[23.5,48],[29.3,48]],
'calibration':[[20.4,46],[18.7,46],[18.7,52.5],[20.4,52.5]],
'care':[[14,46],[14,55]],
'rest':[[14,46],[14.5,46],[14.5,35.5]]
},'views':[
['arrival',[11.3,1.65,46],[25.4,1.65,46]],
['fore_work',[20.4,1.65,44.5],[20.4,1.65,39.6]],
['aft_work',[23.5,1.65,48],[30.2,1.65,52]],
['calibration',[18.7,1.65,50.5],[23,1.65,55]],
['care',[14,1.65,50.7],[12.2,1.65,55]],
['rest',[14.5,1.65,41.4],[13.0,1.65,35.5]]
]})

