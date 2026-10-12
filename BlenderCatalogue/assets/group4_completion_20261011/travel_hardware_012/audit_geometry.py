from pathlib import Path
import sys,json,hashlib
import numpy as np
W=Path(__file__).resolve().parent;R=next(p for p in W.parents if (p/'Game').is_dir());sys.path.insert(0,str(W.parent));from glb_geometry import triangles
I=json.loads((W/'HARDWARE_INTERFACE.json').read_text());P=json.loads((W/'TRAVEL_SOURCE_PLAN.json').read_text());checks=0;errors=[];exports=[]
def check(v,s):
 global checks
 checks+=1
 if not v:errors.append(s)
for item in I['exports']:
 path=W/item['file'];check(hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'],path.name+' export pin')
 parts=list(triangles(path));check(len(parts)==item['mesh_count'],path.name+' all authored members')
 for name,t,extras in parts:
  check(np.isfinite(t).all(),name+' finite');check(np.all(np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)>1e-9),name+' nondegenerate')
  if 'Carriage' in name:check(t[:,:,1].min()>-.30 and t[:,:,1].max()<-.21,name+' correct parent inverse')
  if 'EndBuffer_WebFoot' in name:check(t[:,:,1].min()<55.60 and t[:,:,1].max()>55.68,name+' actual guideway web receiving')
  if 'end_buffers' in path.name:check(t[:,:,0].max()<=-4.49 and t[:,:,1].min()>55.55,name+' outside original lower pedestrian axis/headroom')
 exports.append({'file':path.name,'meshes':len(parts),'triangles':sum(len(t) for n,t,e in parts),'sha256':item['sha256']})
for pose in P['pose_knots']:
 check(all(np.isfinite(pose)), 'finite actual source pose')
 check(max(abs(pose[4]),abs(pose[7]))<.20,'source bounded traverse')
check(P['retained_kingpin_chord_m']==3 and P['retained_wheel_gauge_m']==1.72,'original chord/gauge')
check(abs(P['central_exact_pose'][1])<1e-8 and abs(P['central_exact_pose'][2]+72)<1e-8 and P['central_exact_pose'][3]==0,'original central dock exact')
for file,expected in P['source_pins'].items():check(hashlib.sha256((R/file).read_bytes()).hexdigest()==expected,file+' original unchanged')
result={'status':'PASS' if not errors else 'HOLD','checks':checks,'errors':errors,'exports':exports,'actual_source_route_m':P['source_route_total_m'],'pose_knots':len(P['pose_knots']),'maximum_cross_slide_m':P['maximum_cross_slide_m'],'original_source_gauge_chord_and_dock_preserved':True,'original_wheels_exported_or_duplicated':False,'capacity_or_impact_accepted':False};(W/'GEOMETRY_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print('TRAVEL_GEOMETRY_AUDIT',result);assert not errors
