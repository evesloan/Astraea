from pathlib import Path
import sys,json,hashlib
import numpy as np
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir());sys.path.insert(0,str(W.parent));from glb_geometry import triangles
I=json.loads((W/'SOURCE_INTERFACE.json').read_text());P=json.loads((R/'Game/data/architecture/GROUP4_OPERATING_CONTROLS_SOURCE_CANDIDATE.json').read_text());checks=0;errors=[];parts={}
def check(v,s):
 global checks
 checks+=1
 if not v:errors.append(s)
for item in I['exports']:
 p=W/item['file'];data=list(triangles(p));check(hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],p.name+' pin');check(len(data)==item['mesh_count'],p.name+' mesh count')
 check(p.read_bytes()==(R/'Game/source_derivatives/group4_controls_20261012'/p.name).read_bytes(),p.name+' runtime byte identical')
 for name,t,e in data:
  parts[name]=t;check(np.isfinite(t).all(),name+' finite');check(np.all(np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-10),name+' nondegenerate')
  if item['id']=='AST-TRM-G4-034':check(t[:,:,0].min()>=-1.08 and t[:,:,0].max()<=1.08 and t[:,:,2].min()>=-2.285 and t[:,:,2].max()<=2.285,name+' inside original car envelope')
  else:check(t[:,:,0].max()<-1.2 and t[:,:,2].max()<-.059,name+' outside retained aperture and entire negative leaf sweep')
def bounds(name):
 t=parts[name].reshape(-1,3);return t.min(0),t.max(0)
lo,hi=bounds('CarConsole_ReceivedSlopedHousing');check(lo[1]<1.17 and hi[1]>1.17,'positive original pedestal top receiving')
lo,hi=bounds('CarWorkLamp_RoofReceiver');check(hi[1]>2.57249999 and lo[1]<2.57249999,'positive original roof reveal receiving')
lo,hi=bounds('StationCall_StileReceiver');skinlo=np.array([-1.9,0,-.085]);skinhi=np.array([-1.2,2.65,-.06]);check(np.all(np.minimum(hi,skinhi)-np.maximum(lo,skinlo)>0),'positive original ivory stile skin receiving in all three axes')
for spec in P['car_buttons']+[P['station_call_button']]:
 axis=np.array(spec['axis_xyz']);verts=np.unique(parts[spec['source_mesh']].reshape(-1,3),axis=0);proj=verts@axis;face=verts[abs(proj-proj.max())<2e-6];points=np.array(spec['target_points_xyz']);center=np.array(spec['surface_center_xyz']);check(np.linalg.norm(center-face.mean(0))<1e-9,spec['id']+' exact original exported face centroid')
 check(len(points)==2*len(face),spec['id']+' exact source face target cardinality')
 for depth in [-.0003,.0003]:
  expected=face+axis*depth;actual=points[:len(face)]+center if depth<0 else points[len(face):]+center;check(np.max(np.abs(actual-expected))<1e-9,spec['id']+' exact face polygon extrusion')
lo,hi=bounds('CarWorkLamp_OpalLens');origin=np.array(P['car_light']['position_xyz']);check(abs(lo[1]-origin[1]-.005)<2e-7,'lamp emitter five mm below real lens with unobstructed downward origin')
check(hashlib.sha256((R/I['material_donor_native']).read_bytes()).hexdigest()==I['material_donor_sha256'],'immutable original donor pin')
result={'status':'PASS' if not errors else 'HOLD','checks':checks,'errors':errors,'closed_source_meshes':25,'exact_physical_face_targets':9,'station_instances':5,'new_floor_m2':0,'engineering_species_or_final_art_accepted':False};(W/'GEOMETRY_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print('G4_OPERATING_GEOMETRY',result);assert not errors
