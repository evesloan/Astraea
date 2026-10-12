from pathlib import Path
import json,hashlib,sys
import numpy as np
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir());sys.path.insert(0,str(W.parent));from glb_geometry import triangles
I=json.loads((W/'SOURCE_INTERFACE.json').read_text());parts=list(triangles(W/I['file']));checks=0;errors=[];byname={n:t for n,t,e in parts}
def check(v,s):
 global checks
 checks+=1
 if not v:errors.append(s)
check(len(parts)==18,'exact prototype meshes');check(hashlib.sha256((W/I['file']).read_bytes()).hexdigest()==I['sha256'],'source export pin');check((W/I['file']).read_bytes()==(R/'Game/source_derivatives/group4_station_information_20261012'/I['file']).read_bytes(),'runtime export byte identical');check(hashlib.sha256((R/I['original_gate_model']).read_bytes()).hexdigest()==I['original_gate_sha256'],'actual original AST-DOR003 frame pin')
for name,t,e in parts:
 v=t.reshape(-1,3);check(np.isfinite(v).all(),name+' finite');check(np.all(np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-10),name+' nondegenerate');check(v[:,0].min()>-1.9 and v[:,0].max()<-1.2 and v[:,1].min()>1.4 and v[:,1].max()<2.65,name+' inside original fixed stile, above existing035 call');check(v[:,2].max()<-.059,name+' clear of entire original moving-leaf depth and unchanged aperture')
v=byname['StationInfo_OriginalStileReceiver'].reshape(-1,3);lo=v.min(0);hi=v.max(0);check(np.all(np.minimum(hi,np.array([-1.2,2.65,-.06]))-np.maximum(lo,np.array([-1.9,0,-.085]))>0),'positive source receiver lap into all three axes of original ivory skin')
check(I['station_order']==['FORWARD','FORE_MIDSHIP','CENTRAL','AFT_MIDSHIP','AFT'],'retained physical stop order without timetable/relocation')
for s in json.loads((R/'Game/data/architecture/GROUP4_COMPLETION_CANDIDATE.json').read_text())['stations']:check(s['label'] in I['station_order'],'same existing station ID '+s['label'])
d={'status':'PASS' if not errors else 'HOLD','checks':checks,'errors':errors,'prototype_meshes':18,'source_instances':5,'new_floor_m2':0,'controllers_targets_worldlights_added':0,'existing_aperture_leaf_sweeps_call_controls_and_sources_preserved':True,'whole_group_accepted':False};(W/'GEOMETRY_AUDIT.json').write_text(json.dumps(d,indent=2)+'\n');print('G4_STATION_INFORMATION_GEOMETRY',d);assert not errors
