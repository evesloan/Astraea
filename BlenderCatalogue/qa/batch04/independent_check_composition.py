"""Independent NumPy triangle intersection of actual GLB bytes and recorded QA placements."""
from pathlib import Path
import sys,json,hashlib,math,numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'qa'))
from inspect_glb_independent import GLB
OUT=ROOT/'qa/batch04';e=json.loads((OUT/'arrangement/evidence.json').read_text());groups={'plants':[],'soil':[],'timber':[]};bounds=[];root_vertices=[]
for inst in e['source_exports']:
 g=GLB(ROOT/inst['file']);d=g.doc;allv=[]
 assert hashlib.sha256(g.data).hexdigest()==inst['sha256'],'QA placement export hash changed'
 def visit(i,parent):
  n=d['nodes'][i];m=parent@g.matrix(n)
  if 'mesh' in n:
   for p in d['meshes'][n['mesh']]['primitives']:
    v=g.accessor(p['attributes']['POSITION']);v=np.c_[v,np.ones(len(v))]@m.T;xyz=v[:,[0,2,1]];xyz[:,1]*=-1
    a=inst['rotation_z_rad'];rot=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
    xyz=xyz@rot.T+inst['position_z_up_m'];allv.append(xyz);ids=g.accessor(p['indices']).ravel().reshape(-1,3);tris=xyz[ids];role=d['materials'][p['material']]['name']
    if 'botanical_planter' not in inst['file']:groups['plants'].append(tris)
    if 'botanical_soil' in role:groups['soil'].append(tris)
    if 'warm_walnut' in role:groups['timber'].append(tris)
  for child in n.get('children',[]):visit(child,m)
 for n in d['scenes'][d.get('scene',0)]['nodes']:visit(n,np.eye(4))
 allv=np.concatenate(allv)
 if 'botanical_planter' not in inst['file']:
  for p in allv[np.abs(allv[:,2]-.39)<1e-6]:root_vertices.append({'file':inst['file'],'point_m':p.tolist()})
 lo=allv.min(axis=0);hi=allv.max(axis=0);over=np.minimum(hi,e['proposed_clear_approach_m']['max'])-np.maximum(lo,e['proposed_clear_approach_m']['min']);bounds.append({'file':inst['file'],'min_xyz':lo.tolist(),'max_xyz':hi.tolist(),'approach_separated':bool((over<=0).any())})
groups={k:np.concatenate(v) for k,v in groups.items()}
def ray(tris,origin,direction,limit):
 origin=np.array(origin);direction=np.array(direction,dtype=float);direction/=np.linalg.norm(direction);v0=tris[:,0];ed1=tris[:,1]-v0;ed2=tris[:,2]-v0;p=np.cross(direction,ed2);det=np.einsum('ij,ij->i',ed1,p);valid=np.abs(det)>1e-12;inv=np.zeros_like(det);inv[valid]=1/det[valid];tv=origin-v0;u=np.einsum('ij,ij->i',tv,p)*inv;q=np.cross(tv,ed1);v=q@direction*inv;t=np.einsum('ij,ij->i',ed2,q)*inv;valid&=(u>=-1e-9)&(v>=-1e-9)&(u+v<=1+1e-9)&(t>=0)&(t<=limit)
 if not valid.any():return None
 dist=float(t[valid].min());return {'distance_m':dist,'point_m':(origin+direction*dist).tolist()}
contacts=[]
for c in e['plant_soil_contacts']:
 p=c['root'];hit=ray(groups['soil'],[p[0],p[1],p[2]+.02],[0,0,-1],.05);contacts.append({'plant':c['plant'],'hit':hit,'error_m':abs(hit['point_m'][2]-p[2]) if hit else None})
root_vertex_checks=[]
for r in root_vertices:
 p=r['point_m'];hit=ray(groups['soil'],[p[0],p[1],p[2]+.015],[0,0,-1],.03);root_vertex_checks.append({**r,'soil_hit':hit,'error_m':abs(hit['point_m'][2]-p[2]) if hit else None})
eye=e['proposed_seated_eye_m'];rays=[]
for r in e['outward_view_rays']:
 a,b=map(math.radians,[r['azimuth_deg'],r['elevation_deg']]);hit=ray(groups['plants'],eye,[math.sin(a)*math.cos(b),-math.cos(a)*math.cos(b),math.sin(b)],8);rays.append({**r,'independent_blocked':hit is not None,'hit':hit})
control=ray(groups['plants'],eye,np.array(e['known_occluded_plant_control'])-eye,8)
seat=ray(groups['timber'],[eye[0],eye[1],.51],[0,0,-1],.12)
result={'scope':'Independent actual exported-triangle geometry at recorded arrangement placements. Sampled outlook and unoccupied approach only; no room, actor, collision or game acceptance.','actual_root_base_vertex_checks':root_vertex_checks,'all_root_base_vertices_supported':all(r['error_m'] is not None and r['error_m']<1e-6 for r in root_vertex_checks),'root_contacts':contacts,'proposed_seated_eye_m':eye,'seat_surface_hit':seat,'sampled_outward_rays':rays,'known_plant_hit_control':control,'actual_asset_bounds_and_approach':bounds,'all_source_hashes_match_arrangement':True,'all_root_contacts_within_1um':all(c['error_m'] is not None and c['error_m']<1e-6 for c in contacts),'all_sampled_outward_rays_clear':not any(r['independent_blocked'] for r in rays),'control_hits_plant':control is not None,'all_approach_bounds_separated':all(x['approach_separated'] for x in bounds)}
(OUT/'independent_composition_geometry.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k.startswith('all_') or k in ['control_hits_plant','seat_surface_hit']})
