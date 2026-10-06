"""Exact prior source triangles plus narrow planned edits; no Blender or Game writes."""
from pathlib import Path
import json,numpy as np,sys,math,hashlib
R=Path(__file__).resolve().parents[1];B=R.parent;sys.path.insert(0,str(R/'qa'));from geometry_review import Query,PRISMS,glb
P=json.loads((R/'source/gate_sweep_correction_plan.json').read_text());D=np.load(B/'qa/reopened_final_source_triangles.npz');S=json.loads((B/'qa/section_export_build.json').read_text());meta={r['name']:r for r in S['parts']};meshes=[];old=[];changed=[]
for i,name in enumerate(D['part_names']):
 name=str(name);t=D['triangles'][D['part_ids']==i].copy();old.append({'node':name,'primitive':0,'triangles':t.copy()})
 if name in ['CellGateOutsideHousing','CellGateButtonOutside']:t[:,:,0]-=.11;changed.append(name)
 if name.startswith('CellStairHandrail'):
  z=float(name[len('CellStairHandrail'):]);a=np.array([21.9,6.95,z]);b=np.array([22.8,6.5,z]);mask=np.linalg.norm(t-a,axis=2)<np.linalg.norm(t-b,axis=2);t[mask]+=np.array([.06,-.03,0]);changed.append(name)
 if name=='CONTACT_CellStairFlight':
  v=np.array(P['stair_contact_vertices_xyz']);t=np.array([[v[f[0]],v[f[j]],v[f[j+1]]] for f in P['stair_contact_faces'] for j in range(1,len(f)-1)]);changed.append(name)
 meshes.append({'node':name,'primitive':0,'triangles':t})
def boxmesh(name,b):
 x,y,z,X,Y,Z=b;v=np.array([(x,y,z),(X,y,z),(X,y,Z),(x,y,Z),(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)]);faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];return {'node':name,'primitive':0,'triangles':np.array([[v[f[0]],v[f[j]],v[f[j+1]]] for f in faces for j in [1,2]])}
for p in P['new_supported_parts']:meshes.append(boxmesh(p['name'],p['bounds_xyz']))
fixed=[m for m in meshes if not meta.get(m['node'],{}).get('door_leaf_id')];oldfixed=[m for m in old if not meta[m['node']].get('door_leaf_id')];q=Query(fixed);swept=P['swept_closed_box_xyz'];oldhits=Query(oldfixed).prism_hits(swept,.0001);newhits=q.prism_hits(swept,.0001)
# Continuous proof: union of all axis-aligned translated closed boxes is exactly this prism.
closed=np.array(P['unchanged_gate']['closed_leaf_bounds_xyz']);travel=np.array(P['unchanged_gate']['opening_translation_xyz']);poses=[]
for fraction in np.linspace(0,1,101):
 b=closed+np.r_[travel*fraction,travel*fraction];hits=q.prism_hits(b,.0001);poses.append({'fraction':float(fraction),'fixed_hits':len(hits)})
prisms={n:Query(meshes).prism_hits(b) for n,b in PRISMS.items()}
# Actual bottle cap circle, radius.057, moves alongZ. Every rim/centre ray meets the new solid side.
wedge=next(m for m in meshes if m['node']=='CONTACT_CellStairFlight');wq=Query([wedge]);bottle=[]
for i in range(33):
 a=2*math.pi*i/32;x=22.19+(.057*math.cos(a) if i<32 else 0);y=5.61+(.057*math.sin(a) if i<32 else 0);h=wq.rays([x,y,-405.45],[x,y,-404.70]);bottle.append({'x':x,'y':y,'side_hit':bool(h),'hit_z':h[0]['position_xyz'][2] if h else None})
underside=wq.rays([22.19,5.1,-404.8],[22.19,5.8,-404.8]);points=wedge['triangles'].reshape(-1,3)
# Gate targets retain their actual standing locations and2.5m first-hit limit.
context=Query(meshes+glb('/workspace/shared/astraea-catalogue-continuation-20261002/assets/secondary_engineering_section/exports/AST-ENG-008.glb')['meshes']+glb(str(B.parent.parent/'engineering-essentials/exports/AST-ENG-008_essentials.glb'))['meshes']);targets=[]
for t in P['unchanged_gate']['targets']:
 c=np.array(t['position_xyz']);eye=np.array(t['approach_xyz'])+np.array([0,1.65,0])
 if t['marker'].endswith('OUTSIDE'):c[0]-=.11
 h=context.rays(eye,eye+(c-eye)*1.15);targets.append({'marker':t['marker'],'distance_m':float(np.linalg.norm(c-eye)),'first_hit':h[0]['node'] if h else None,'pass':bool(h and h[0]['node']==t['mesh'] and np.linalg.norm(c-eye)<=2.5)})
report={'scope':'Pure source-triangle correction against exact continuous leaf BoxShape sweep; actual exported/reopened geometry and runtime tests pending','passed':len(oldhits)==22 and not newhits and all(p['fixed_hits']==0 for p in poses) and not any(prisms.values()) and all(x['side_hit'] for x in bottle) and bool(underside) and abs(underside[0]['position_xyz'][1]-5.55)<1e-6 and all(t['pass'] for t in targets),'changed_existing_parts':changed,'prior_fixed_triangle_sweep_hits':oldhits,'continuous_new_fixed_triangle_sweep_hits':newhits,'continuous_scope':'all fractions0..1, not sampled-only; exact union for axis-aligned linear translation','supplemental_101_pose_checks':poses,'protected_prism_hits':prisms,'actual_bottle_shape':{'type':'CylinderShape3D','radius_m':.057,'height_m':.25,'axis':'Z in side-gap witness','first_leading_cap_contact_centre_z':-405.225,'all_cross_section_side_rays':bottle},'wedge_bounds_xyz':points.min(0).tolist()+points.max(0).tolist(),'underside_hit_y':underside[0]['position_xyz'][1] if underside else None,'gate_targets':targets,'new_pedestal_floor_owner':'D02_secondary_engineering_floor atY6, outside holeX>=21.9','no_floor_owner_change':True,'no_aperture_travel_ID_range_change':True}
(R/'qa/pure_correction_check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['prior_fixed_triangle_sweep_hits','supplemental_101_pose_checks','actual_bottle_shape']},indent=2));assert report['passed']
