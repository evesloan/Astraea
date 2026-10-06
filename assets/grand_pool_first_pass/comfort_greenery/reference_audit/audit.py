"""Read-only retained geometry audit; writes this scratch directory only."""
import sys,json,hashlib,importlib.util,math
from pathlib import Path
import numpy as np
sys.dont_write_bytecode=True
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
GAME=Path('/workspace/shared/astraea-godot-production-20261003')
OUT=Path(__file__).parent
spec=importlib.util.spec_from_file_location('geom',CAT/'assets/grand_pool_first_pass/finish_envelope/stock/geometry.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((CAT/'assets/grand_pool_first_pass/source/placement_contract.json').read_text())
s=json.loads((CAT/'assets/grand_pool_orchard_section/source/connected_contract.json').read_text())
m=json.loads((CAT/'catalogue_manifest.json').read_text());ids={a['catalogue_id']:a for a in m['assets']}
want=['AST-FUR-001','AST-AQU-001','AST-AQU-016','AST-BOT-001','AST-BOT-002','AST-BOT-003','AST-BOT-007','AST-BOT-008','AST-BOT-009','AST-BOT-011','AST-BOT-012','AST-LIB-010','AST-RES-001','AST-ENG-003','AST-LND-001']
geo={};inv={}
for aid in want:
 a=ids[aid];geo[aid]=g.read_glb(CAT/a['export']);inv[aid]={k:a[k] for k in ['catalogue_id','name','family','source','export']};inv[aid].update(actual_gltf_bounds=g.bounds(geo[aid]['vertices']),source_sha256=sha(CAT/a['source']),export_sha256=sha(CAT/a['export']),source_pin_matches=sha(CAT/a['source'])==a['source_sha256'],export_pin_matches=sha(CAT/a['export'])==a['export_sha256'])
(OUT/'SOURCE_INVENTORY.json').write_text(json.dumps(inv,indent=2)+'\n')
# All source GLB triangles, including fixtures, plus world-transformed retained furnishing mesh triangles.
tri=[];names=[]
for mm in geo['AST-AQU-016']['meshes']:
 tri.extend(mm['triangles']);names.extend([mm['name']]*len(mm['triangles']))
for p in c['placements']:
 aid=Path(p['retained_export']).stem.split('_')[0]
 q=geo.get(aid)
 if not q:q=g.read_glb(CAT/p['retained_export'])
 for mm in q['meshes']:
  t=[tuple(g.transform(v,p['position_xyz'],p['yaw_radians']) for v in t) for t in mm['triangles']];tri.extend(t);names.extend([p['name']+'/'+mm['name']]*len(t))
T=np.array(tri);N=np.array(names);v0=T[:,0];e1=T[:,1]-v0;e2=T[:,2]-v0
# Moller-Trumbore against actual retained source triangles. Eye poses are explicitly human-scale audit proposals.
def hits(o,d,maxdist=100):
 o=np.array(o);d=np.array(d);d=d/np.linalg.norm(d);h=np.cross(d,e2);det=(e1*h).sum(1);good=abs(det)>1e-9;iv=np.divide(1.,det,out=np.zeros_like(det),where=good);s0=o-v0;u=iv*(s0*h).sum(1);q=np.cross(s0,e1);v=iv*(d*q).sum(1);t=iv*(e2*q).sum(1);valid=good&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(t>.015)&(t<maxdist)
 ix=np.where(valid)[0];ix=ix[np.argsort(t[ix])];out=[];seen=set()
 for i in ix:
  if N[i] in seen:continue
  seen.add(N[i]);out.append({'mesh':str(N[i]),'distance_m':float(t[i]),'point_xyz':(o+d*t[i]).tolist()})
 return out[:8]
seats=[]
for p in c['placements']:
 if p['asset'] not in ['bench','lounger']:continue
 # Bench root front +Z, seat centre x +-0.548,z .11. Human upright eye floor+1.18 is proposed, not ergonomic acceptance.
 # Reclining high back local -Z; front/feet +Z; use elevated eye near head -0.70, y1.10.
 poses=[[-.548,1.18,.11],[.548,1.18,.11]] if p['asset']=='bench' else [[0,1.10,-.70]]
 forward=g.rotate((0,0,1),p['yaw_radians']);eyes=[g.transform(q,p['position_xyz'],p['yaw_radians']) for q in poses]
 rays=[]
 for ei,eye in enumerate(eyes):
  for yaw in [0,-20,20]:
   d=g.rotate(forward,math.radians(yaw));rays.append({'eye_index':ei,'eye_xyz':eye,'yaw_offset_degrees':yaw,'direction_xyz':d,'hits':hits(eye,d)})
 seats.append({'name':p['name'],'position_xyz':p['position_xyz'],'asset':p['asset'],'yaw_radians':p['yaw_radians'],'forward_xyz':forward,'local_eye_proposals':poses,'rays':rays})
(OUT/'SEAT_SIGHTLINES.json').write_text(json.dumps({'status':'source_triangle_audit_not_occupied_runtime_acceptance','seats':seats},indent=2)+'\n')
for seat in seats:
 print(seat['name'],seat['forward_xyz']);
 for ray in seat['rays']:
  if ray['yaw_offset_degrees']==0:print(' ',ray['eye_xyz'],ray['hits'][:3])
for aid in ['AST-BOT-001','AST-BOT-002','AST-BOT-003','AST-BOT-007','AST-BOT-008','AST-BOT-009','AST-BOT-011','AST-LIB-010','AST-RES-001']:
 print(aid,inv[aid]['actual_gltf_bounds'])
# Geometry metadata small enough to inspect without running authoring tools.
for aid in ['AST-FUR-001','AST-AQU-001','AST-LIB-010','AST-RES-001']:
 (OUT/(aid+'_MESH_BOUNDS.json')).write_text(json.dumps({'meshes':[{'name':x['name'],'bounds':x['bounds']}for x in geo[aid]['meshes']],'markers':geo[aid]['markers']},indent=2)+'\n')
# Bounded media fitting candidates; no geometry is authored.
media=[
 {'name':'market_rest_0_screen','for_seat':'market_rest_0','support':'GP_OrangeReveal_0_-444.6','axis':'z','face':-446.28,'bounds':[[-52.05,54.03,-446.30],[-50.35,55.03,-446.10]],'image_rect':[-51.97,-50.43,54.11,54.95]},
 {'name':'market_rest_1_screen','for_seat':'market_rest_1','support':'GP_UpperPier_1','axis':'z','face':-434.42,'bounds':[[-51.48,53.68,-434.44],[-49.92,54.58,-434.26]],'image_rect':[-51.40,-50.0,53.76,54.50]},
 {'name':'market_rest_2_screen','for_seat':'market_rest_2','support':'GP_UpperPier_2','axis':'z','face':-417.42,'bounds':[[-51.48,53.68,-417.44],[-49.92,54.58,-417.26]],'image_rect':[-51.40,-50.0,53.76,54.50]},
 {'name':'wet_end_rest_floor_display','for_seat':'wet_end_rest','support':'D08_grand_pool_wet','axis':'x','face':-41.35,'bounds':[[-41.35,46.2,-403.6],[-40.88,48.6,-401.4]],'image_rect':[-403.48,-401.52,47.12,48.38]}]
finish=json.loads((CAT/'assets/grand_pool_first_pass/finish_envelope/source/finish_contract.json').read_text())
parts=[{'name':p['name'],'bounds':g.bounds(p['world_vertices'])}for p in s['source_parts']if not p.get('export_excluded')]
parts +=[{'name':p['name'],'bounds':[p['bounds_min_xyz'],p['bounds_max_xyz']]}for p in finish['parts']]
parts +=[{'name':p['name'],'bounds':[p['envelope_min_xyz'],p['envelope_max_xyz']]}for p in c['placements']]
stock=json.loads((CAT/'assets/grand_pool_first_pass/finish_envelope/stock/stock_placement_contract.json').read_text())
parts +=[{'name':p['name'],'bounds':[p['envelope_min_xyz'],p['envelope_max_xyz']]}for p in stock['placements']]
# Include retained48 future stock and convex-face triangulation of staged finish in media fitting rays.
for p in stock['placements']:
 q=g.read_glb(CAT/p['retained_export'])
 for mm in q['meshes']:
  t=[tuple(g.transform(v,p['position_xyz'],p['yaw_radians']) for v in t)for t in mm['triangles']];tri.extend(t);names.extend(['planned48/'+p['name']+'/'+mm['name']]*len(t))
# Non-convex finish faces are not fan-triangulated. A clear segment versus their full
# conservative envelopes is sufficient for absence; an overlap stays a fitting gate.
def box_segment(a,b,box):
 lo,hi=0.,1.
 for k in range(3):
  d=b[k]-a[k]
  if abs(d)<1e-10:
   if a[k]<box[0][k] or a[k]>box[1][k]:return False
  else:
   x=(box[0][k]-a[k])/d;y=(box[1][k]-a[k])/d
   lo=max(lo,min(x,y));hi=min(hi,max(x,y))
   if lo>hi:return False
 return hi>.0001 and lo<.9999
T=np.array(tri);N=np.array(names);v0=T[:,0];e1=T[:,1]-v0;e2=T[:,2]-v0
for a in media:
 b=a['bounds'];a['strict_aabb_overlap_names_excluding_support']=[p['name']for p in parts if p['name']!=a['support'] and g.overlap(b,p['bounds'])];a['protected_route_overlaps']=[]
 for n,y,r in c['protected_route_rects']:
  if g.overlap(b,[[r[0],y+.001,r[2]],[r[1],y+3.2,r[3]]]):a['protected_route_overlaps'].append(n)
 lo,hi,ylo,yhi=a['image_rect'];sample=[((lo+hi)/2,(ylo+yhi)/2),(lo,ylo),(lo,yhi),(hi,ylo),(hi,yhi)];targets=[(x,y,a['face'])if a['axis']=='z' else(a['face'],y,x)for x,y in sample]
 p=next(p for p in c['placements']if p['name']==a['for_seat']);checks=[]
 for lateral in [-.548,.548]:
  for ey in [1.00,1.18,1.40]:
   eye=g.transform((lateral,ey,.11),p['position_xyz'],p['yaw_radians'])
   for target in targets:
    d=np.array(target)-eye;ob=hits(eye,d,np.linalg.norm(d)-.003)
    checks.append({'eye_xyz':eye,'target_xyz':target,'occlusions':ob,'staged_finish_envelope_hits':[fp['name']for fp in finish['parts']if box_segment(eye,target,[fp['bounds_min_xyz'],fp['bounds_max_xyz']])],'distance_m':float(np.linalg.norm(d))})
 a['sampled_current_triangle_sightlines']=checks;a['occluded_ray_count']=sum(bool(q['occlusions'])or bool(q['staged_finish_envelope_hits'])for q in checks)
 if a['support'].startswith('D08'):
  f=next(x for x in s['floor_regions']if x['id']==a['support']);bad=[];count=0
  for x in np.linspace(b[0][0],b[1][0],12):
   for z in np.linspace(b[0][2],b[1][2],46):
    count+=1
    def inside(pt,t):
     aa,bb,cc=np.array(t);v0=cc-aa;v1=bb-aa;v2=np.array(pt)-aa;den=v0[0]*v1[1]-v1[0]*v0[1]
     if abs(den)<1e-10:return False
     u=(v2[0]*v1[1]-v1[0]*v2[1])/den;v=(v0[0]*v2[1]-v2[0]*v0[1])/den
     return u>=-1e-8 and v>=-1e-8 and u+v<=1+1e-8
    if not any(inside((x,z),t)for t in f['triangles']):bad.append((x,z))
  a['floor_screen']={'sample_count':count,'unsupported_count':len(bad),'bad_samples':bad[:10]}
 print('MEDIA',a['name'],'AABB',a['strict_aabb_overlap_names_excluding_support'],'routes',a['protected_route_overlaps'],'occluded',a['occluded_ray_count'],'floor',a.get('floor_screen'))
(OUT/'MEDIA_FITTING_CANDIDATES.json').write_text(json.dumps({'status':'conservative_read_only_candidates_not_source_or_runtime_acceptance','candidates':media},indent=2)+'\n')
# Two optional major wet-bed envelopes behind the lounger line. These are not included in retained48 stock.
wet_beds=[]
for z in [-445.8,-410.0]:
 b=[[-51.10,46.2,z-.60],[-49.15,48.25,z+.60]]
 a={'name':'optional_wet_backdrop_'+str(abs(z)),'bounds':b,'support':'D08_grand_pool_wet','housing_height_proposed_m':.52,'root_plane_proposed_y':46.72,'foliage_top_proposed_y':48.25,'strict_aabb_overlap_names':[p['name']for p in parts if g.overlap(b,p['bounds'])]}
 a['protected_route_overlaps']=[]
 for n,y,r in c['protected_route_rects']:
  if g.overlap(b,[[r[0],y+.001,r[2]],[r[1],y+3.2,r[3]]]):a['protected_route_overlaps'].append(n)
 print('OPTIONAL BED',a['name'],a['strict_aabb_overlap_names'],a['protected_route_overlaps']);wet_beds.append(a)
(OUT/'OPTIONAL_WET_BED_CANDIDATES.json').write_text(json.dumps({'status':'uncommitted_optional_scope_needs_complete_floor_support_and_source_design','candidates':wet_beds},indent=2)+'\n')
planting=[]
for p in s['source_parts']:
 if not p['name'].startswith('GP_PlantSoil'):continue
 b=g.bounds(p['world_vertices']);z=(b[0][2]+b[1][2])/2
 low=[[-50.55,53.2,z-.44],[-48.35,53.62,z+.44]]
 is_screen_bed=abs(z+446.7)<.01
 high=[[-49.60 if is_screen_bed else -50.55,53.62,z-.40],[-48.35,55.20,z+.40]]
 layers=[{'name':'dense_low_basal','bounds':low},{'name':'shifted_outer_mid_and_crown'if is_screen_bed else 'layered_mid_and_crown','bounds':high}]
 a={'support':p['name'],'soil_bounds':b,'top_root_plane_y':53.2,'is_market_rest_0_view_bed':is_screen_bed,'layers':layers,'screen_sightline_checks':[]}
 for layer in layers:
  layer['nonbotanical_source_and_finish_overlap_names']=[q['name']for q in parts if q['name']!=p['name'] and not q['name'].startswith(('market_understory','market_rosette','wet_pot_rosette'))and g.overlap(layer['bounds'],q['bounds'])]
  layer['media_body_overlap_names']=[q['name']for q in media if g.overlap(layer['bounds'],q['bounds'])]
 for screen in media:
  for ray in screen['sampled_current_triangle_sightlines']:
   blocking=[layer['name']for layer in layers if box_segment(ray['eye_xyz'],ray['target_xyz'],layer['bounds'])]
   if blocking:a['screen_sightline_checks'].append({'screen':screen['name'],'eye_xyz':ray['eye_xyz'],'target_xyz':ray['target_xyz'],'blocked_by':blocking})
 print('PLANT',p['name'],'layer overlaps',[(x['name'],x['nonbotanical_source_and_finish_overlap_names'],x['media_body_overlap_names'])for x in layers],'view blockers',len(a['screen_sightline_checks']));planting.append(a)
(OUT/'PLANTING_ENVELOPE_CANDIDATES.json').write_text(json.dumps({'status':'bounded_foliage_reservations_pass_read_only_screening_not_authored_plants','candidates':planting,'screen_probes_per_candidate':120,'intent':'Opaque connected broad foliage within these conservative bounds; roots inside actual chamfered soil polygons; preserve installed rooted plants and all approaches.'},indent=2)+'\n')
# Additive compact whorls attach to retained rosette crown; not enlarged planters.
wet_companions=[]
for p in c['placements']:
 if not p['name'].startswith('wet_pot_rosette_'):continue
 x,y,z=p['position_xyz'];b=[[x-.29,y,z-.28],[x+.29,y+.48,z+.28]]
 allowed={p['name'],p['support']}
 a={'name':p['name']+'_fullness_whorl','parent_design_id':'AST-BOT-003','family':'botanical_understory','position_xyz':p['position_xyz'],'bounds':b,'attachment':'Retained rosette_basal_crown around original root plane +0.025..0.045 m, original root and pot remain','support':p['support'],'strict_unrelated_overlap_names':[q['name']for q in parts if q['name']not in allowed and g.overlap(b,q['bounds'])],'protected_route_overlaps':[],'media_view_blockers':[]}
 for n,fy,r in c['protected_route_rects']:
  if g.overlap(b,[[r[0],fy+.001,r[2]],[r[1],fy+3.2,r[3]]]):a['protected_route_overlaps'].append(n)
 for screen in media:
  for ray in screen['sampled_current_triangle_sightlines']:
   if box_segment(ray['eye_xyz'],ray['target_xyz'],b):a['media_view_blockers'].append(screen['name'])
 wet_companions.append(a);print('WET COMPANION',a['name'],a['strict_unrelated_overlap_names'],a['protected_route_overlaps'],a['media_view_blockers'])
OUT.joinpath('WET_POT_FULLNESS_CANDIDATES.json').write_text(json.dumps({'status':'additive_envelopes_screen_clear_final_crown_attachments_pending','candidates':wet_companions},indent=2)+'\n')
