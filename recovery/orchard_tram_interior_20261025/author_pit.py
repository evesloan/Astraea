"""Exact named floor successor; leave the compiled original immutable."""
from pathlib import Path
import json,hashlib,copy,importlib.util,sys
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2];D=R/'Game/orchard_tram_interior_20261025/integration'
spec=importlib.util.spec_from_file_location('screen',R/'recovery/tram_section_successor_20261023/screen_section.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
source=R/'Game/data/generated/structural_meshes.json';compiled=json.loads(source.read_text())
before=next(r for r in compiled['regions'] if r['id']=='D09_thread_shell_floor')
rect=[10.8,15.2,-231.96,-227.94]
def area(poly):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1])))/2
def subtract(triangle):
 inside=triangle;outside=[]
 for axis,value,above in [(0,rect[0],True),(0,rect[1],False),(1,rect[2],True),(1,rect[3],False)]:
  if not inside:break
  piece=s.clip(inside,axis,value,not above)
  if len(piece)>2 and area(piece)>1e-10:outside.extend([[piece[0],piece[i],piece[i+1]] for i in range(1,len(piece)-1) if area([piece[0],piece[i],piece[i+1]])>1e-10])
  inside=s.clip(inside,axis,value,above)
 removed=area(inside) if len(inside)>2 else 0
 return (outside,removed) if removed>1e-10 else ([triangle],0)
after=copy.deepcopy(before);triangles=[];removed=0;untouched=0
for t in before['triangles']:
 pieces,a=subtract(t);triangles.extend(pieces);removed+=a;untouched+=int(a==0)
assert abs(removed-17.688)<1e-8
assert abs(sum(map(area,before['triangles']))-sum(map(area,triangles))-removed)<1e-8
after['triangles']=triangles;after['structural_area_m2']-=removed
# Original outer orientation is preserved; inner wall faces point into the pit.
outer=before['rings'][0];signed=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(outer,outer[1:]+outer[:1]))
hole=[[rect[0],rect[2]],[rect[1],rect[2]],[rect[1],rect[3]],[rect[0],rect[3]]]
if signed>0:hole.reverse()
after['rings'].append(hole)
for chunk in after.get('render_chunks',[]):chunk['triangles']=[p for t in chunk['triangles'] for p in subtract(t)[0]]
after['status']='Exact Orchard boarding lift receiving successor; installed acceptance required'
station=next(r for r in json.loads((R/'Game/data/architecture/GROUP4_COMPLETION_CANDIDATE.json').read_text())['stations'] if r['label']=='FORE_MIDSHIP')
station=copy.deepcopy(station);station.update(lift_root=[13,0,-231.8],boarding_edge_x=14.9,physical_docking_z=-236.1,track_x=17.3,lower_lift_recess_xz=rect,retained_lower_floor_owners=['D09_thread_shell_floor'])
station['bridge_reach_m']=17.3-(2.2-1.0925925925925928)-14.9
# Close the old empty lift recess, without filling any other retained opening.
old=[[-13.4,-225.2],[-9,-225.2],[-9,-221.2],[-13.4,-221.2]]
infill={'id':'D09_retired_foremid_lift_pit_infill','deck':'D09','floor_y':52.5,'thickness':.24,'material_role':'guest_floor','structural_area_m2':17.6,'rings':[old],'triangles':[[old[0],old[1],old[2]],[old[0],old[2],old[3]]],'status':'Existing station pit closure; no added room or capacity'}
proof={'selected':False,'compiled_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'before':before,'after':after,'removed_m2':removed,'unchanged_triangles':untouched,'before_triangles':len(before['triangles']),'after_triangles':len(triangles),'old_pit_infill':infill,'station':station,'remaining':['Actual source floor replacement identity/triangle check','Lift cabin/gate/stair/guest/service circulation','Original old pit footprint and infill installed verification','Structural receiver capacity','Boarding and installed-world acceptance']}
D.mkdir(exist_ok=True);out=D/'PIT_AND_BINDING.json';assert not out.exists();out.write_bytes((json.dumps(proof,indent=2)+'\n').encode());print(json.dumps({k:proof[k] for k in ['removed_m2','unchanged_triangles','before_triangles','after_triangles']}))
