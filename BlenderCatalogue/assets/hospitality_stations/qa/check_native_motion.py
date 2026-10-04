"""Native actual GLB node frames plus physical collision-proposal sweep checks."""
import json,math,hashlib
import numpy as np
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
ns={'__file__':str(BASE/'qa/validate_glb.py')};exec((BASE/'qa/validate_glb.py').read_text().split('records=[validate')[0],ns)
read,accessor,matrix=ns['read'],ns['accessor'],ns['matrix'];collisions=json.loads((BASE/'collision_proposals.json').read_text())
C=np.array([[1,0,0],[0,0,1],[0,-1,0]])
def overlap(a,b):return bool(np.all(np.minimum(a[1],b[1])-np.maximum(a[0],b[0])>1e-5))
rows=[]
for ident,group,distance in [('AST-HSP-003','DRIP_TRAY',.32),('AST-HSP-004','RECEIVING_CADDY',.80)]:
 doc,blob=read(BASE/'exports'/f'{ident}.glb');markers=[];part_pts=[];node_info={}
 def walk(i,parent,active=False):
  node=doc['nodes'][i];w=parent@matrix(node);active=active or node.get('name')==group;node_info[node.get('name')]=w
  ex=node.get('extras',{})
  if 'position_blender_source_m'in ex:
   p=np.array(ex['position_blender_source_m']);correct=C@p;error=float(np.linalg.norm(w[:3,3]-correct));wrong=float(np.linalg.norm(w[:3,3]-p));markers.append({'name':node['name'],'actual_gltf_world_m':w[:3,3].tolist(),'expected_gltf_world_m':correct.tolist(),'error_m':error,'passes':error<2e-6,'wrong_axis_unconverted_error_m':wrong,'kind':ex.get('kind')})
  if active and'mesh'in node:
   for prim in doc['meshes'][node['mesh']]['primitives']:
    v=accessor(doc,blob,prim['attributes']['POSITION']);world=(w@np.column_stack([v,np.ones(len(v))]).T).T[:,:3];part_pts.extend(world@C)
  for child in node.get('children',[]):walk(child,w,active)
 for i in doc['scenes'][doc.get('scene',0)]['nodes']:walk(i,np.eye(4))
 root=next(n for n in doc['nodes']if n.get('name')==group);ex=root['extras'];ds=np.array(ex['translation_axis_blender_source']);dg=np.array(ex['translation_axis_gltf_yup']);p=node_info[group][:3,3];tip=p+dg*distance;expected=p+C@ds*distance;wrongtip=p+ds*distance
 points=np.array(part_pts);lo,hi=points.min(0),points.max(0);static=[r for r in collisions[ident]['boxes']if r['group']=='static'];hits=[]
 for t in np.linspace(0,distance,81):
  bb=(lo+ds*t,hi+ds*t)
  for b in static:
   if overlap(bb,(np.array(b['min_source_m']),np.array(b['max_source_m']))):hits.append({'travel_m':float(t),'collider':b['name']})
 bad_direction=np.array([0,0,-1])if ident.endswith('003')else np.array([1,0,0]);bad_hits=[]
 for t in np.linspace(0,distance,81):
  for b in static:
   if overlap((lo+bad_direction*t,hi+bad_direction*t),(np.array(b['min_source_m']),np.array(b['max_source_m']))):bad_hits.append(b['name'])
 blocklo,blockhi=(np.array([-.27,-.42,.05]),np.array([.27,-.40,.085]))if ident.endswith('003')else(np.array([-.47,.5,.86]),np.array([.47,.53,.96]))
 blocked=any(overlap((lo+ds*t,hi+ds*t),(blocklo,blockhi))for t in np.linspace(0,distance,81))
 # Common tray pose enters return at safe height, descending onto the surface after insertion.
 tray=None
 if ident.endswith('004'):
  obstacles=collisions[ident]['boxes'];tray_hits=[]
  for y in np.linspace(-.7,.015,72):
   a=np.array([-.225,y-.16,1.01]);b=np.array([.225,y+.16,1.07])
   for ob in obstacles:
    if overlap((a,b),(np.array(ob['min_source_m']),np.array(ob['max_source_m']))):tray_hits.append(ob['name'])
  cap=(np.array([-.47,-.4,.98]),np.array([.47,-.36,1.12]));blocked_tray=any(overlap((np.array([-.225,y-.16,1.01]),np.array([.225,y+.16,1.07])),cap)for y in np.linspace(-.7,.015,72))
  tray={'size_m':[.45,.32,.06],'entry_bottom_source_z_m':1.01,'hits':tray_hits,'temporary_front_cap_rejected':blocked_tray,'passes':not tray_hits and blocked_tray}
 rows.append({'catalogue_id':ident,'glb_sha256':hashlib.sha256((BASE/'exports'/f'{ident}.glb').read_bytes()).hexdigest(),'actual_marker_checks':markers,'motion_node':group,'actual_moving_group_bounds_source':{'min':lo.tolist(),'max':hi.tolist()},'direction_source':ds.tolist(),'direction_gltf':dg.tolist(),'translation_tip_error_m':float(np.linalg.norm(tip-expected)),'wrong_axis_control_tip_error_m':float(np.linalg.norm(wrongtip-expected)),'proposed_collider_sweep_hits':hits,'wrong_direction_control_blockers':sorted(set(bad_hits)),'temporary_route_blocker_rejected':blocked,'tray_entry':tray,'passes':all(m['passes']for m in markers)and np.linalg.norm(tip-expected)<1e-7 and np.linalg.norm(wrongtip-expected)>.1 and not hits and bool(bad_hits)and blocked and(tray is None or tray['passes'])})
report={'scope':'Actual GLB hierarchy positions/directions checked. Sweeps use actual moving mesh bounds against explicit proposed static colliders; contact tolerance10 micrometres. This is exchange/component proof, not engine animation.','assets':rows,'all_passed':all(r['passes']for r in rows)};(BASE/'qa/native_motion_and_clearance_checks.json').write_text(json.dumps(report,indent=2)+'\n');print([(r['catalogue_id'],r['passes'],r['proposed_collider_sweep_hits'][:2])for r in rows])
