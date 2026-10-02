"""Independent final relative native-component geometry, usable soil and outlook screen."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch13';PLAN=OUT/'assembly/plan.json'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import Hull,nearest_distances,segment_triangles,clip_polygon,inside_mesh
sys.path.insert(0,str(ROOT/'qa/batch12'));from independent_void_geometry import triangle_box_mask
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();plan=json.loads(PLAN.read_text());geometry={};models={};mat={};trans={};items={x['key']:x for x in plan['items']};bindings=[]
for item in plan['items']:
 gp=ROOT/item['path'];g=Native(gp);a=np.deg2rad(item['source_z_rotation_deg']);R=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]]);o=np.array(item['source_origin_m']);geometry[item['key']]=(g.tris@C)@R.T+o;models[item['key']]=g;mat[item['key']]=g.materials;trans[item['key']]=(R,o);bindings.append({'key':item['key'],'export_path':item['path'],'export_sha256':sha(gp),**({'source_path':item['source_path'],'source_sha256':sha(ROOT/item['source_path'])}if item.get('source_path')else{}),**({'manifest_path':item['manifest_path'],'manifest_sha256':sha(ROOT/item['manifest_path'])}if item.get('manifest_path')else{})})
alltri=np.concatenate(list(geometry.values()));allnames=np.concatenate([np.array([key]*len(t))for key,t in geometry.items()]);boxes=[];rays=[]
for box in plan['empty_spaces']:
 lo=np.array(box['min_source_m'])+.0002;hi=np.array(box['max_source_m'])-.0002;mask=triangle_box_mask(alltri,lo,hi);inside=[]
 for key in ['straight','start_closure','transition']:
  if inside_mesh([(lo+hi)/2],geometry[key])[0]:inside.append(key)
 boxes.append({'id':box['id'],'source_box_m':[box['min_source_m'],box['max_source_m']],'surface_inset_m':.0002,'intruding_triangles':int(mask.sum()),'intruding_components':sorted(set(str(x)for x in allnames[mask])),'midpoint_inside_hard_components':inside,'pass':not mask.any()and not inside})
 for axis in range(3):
  other=[x for x in range(3)if x!=axis]
  for u,v in itertools.product([.1,.3,.5,.7,.9],repeat=2):
   a=lo.copy();b=hi.copy()
   for i,f in zip(other,[u,v]):a[i]=b[i]=lo[i]+(hi[i]-lo[i])*f
   hits=segment_triangles(a,b,alltri);rays.append({'id':box['id'],'segment_source_m':[a.tolist(),b.tolist()],'expected_clear':True,'hits':len(hits),'pass':not hits})
for ray in plan['seated_outlook_proposal']['rays']:
 hits=segment_triangles(ray['eye_source_m'],ray['target_source_m'],alltri);rays.append({'id':'seated_outlook','segment_source_m':[ray['eye_source_m'],ray['target_source_m']],'expected_clear':True,'hits':len(hits),'pass':not hits})
for name,a,b in [('blocked_seat',[.9,-.25,.44],[.9,-.25,.50]),('blocked_terminal',[1.66,.5,.6],[1.81,.5,.6]),('blocked_riser',[.54,.5,.6],[.70,.5,.6]),('blocked_tree_stem',[-1.75,.5,.48],[-1.45,.5,.48])]:
 hits=segment_triangles(a,b,alltri);rays.append({'id':name,'segment_source_m':[a,b],'expected_clear':False,'hits':len(hits),'pass':bool(hits)})
roots=[]
for key in ['canopy','trailing','flowering']:
 item=items[key];m=json.loads((ROOT/item['manifest_path']).read_text());R,o=trans[key];poly=np.array(m['planting_and_placement']['root_reservation_polygon_source_xy']);world=(np.column_stack([poly,np.zeros(len(poly))])@R.T+o)[:,:2];host=item['host_key'];hm=json.loads((ROOT/items[host]['manifest_path']).read_text());hR,ho=trans[host]
 if host=='straight':opening=hm['planting_opening'];lo=np.array(opening['min_xy_m'])+ho[:2];hi=np.array(opening['max_xy_m'])+ho[:2];top=opening['soil_top_z_m']+ho[2];depth=opening['soil_depth_m']
 else:cell=next(x for x in hm['soil_cells']if x['id']=='upper');pol=np.array(cell['soil_polygon_source_xy_m']);lo=pol.min(0)+ho[:2];hi=pol.max(0)+ho[:2];top=cell['soil_top_z_m']+ho[2];depth=cell['depth_m']
 mr=[]
 for marker in m['physical_and_proposal_markers']:
  if not marker['kind'].startswith('physical_soil'):continue
  ng=models[key];index=next(i for i,n in enumerate(ng.g.doc['nodes'])if n.get('name')==marker['name']);p=(ng.world[index][:3,3]@C)@R.T+o;soil=geometry[host][np.array(['botanical_soil'in x for x in mat[host]])];distance=float(nearest_distances([p],soil)[0]);mr.append({'name':marker['name'],'actual_native_contact_world_source_m':p.tolist(),'distance_to_actual_host_soil_surface_m':distance,'pass':distance<.0002})
 d=m['planting_and_placement']['suggested_spatial_soil_depth_m'];fit=bool((world>=lo-1e-7).all()and(world<=hi+1e-7).all());roots.append({'asset':m['catalogue_id'],'host':host,'reservation_world_polygon_xy_m':world.tolist(),'usable_host_bounds_xy_m':[lo.tolist(),hi.tolist()],'host_soil_depth_m':depth,'proposed_reserved_depth_m':d,'root_reservation_inside_usable_soil_polygon':fit,'root_datum_z_error_m':float(abs(o[2]-top)),'actual_native_root_contacts':mr,'pass':fit and d<=depth and abs(o[2]-top)<1e-7 and all(x['pass']for x in mr),'limit':'Spatial reservation only. Below-soil roots are unmodelled; no plant viability or growth claim.'})
# Exact triangle clipping over the actual upper rear coping plan footprint.
lo=np.array([.68,.854]);hi=np.array([1.68,1.037]);pts=[]
for t in geometry['trailing']:
 poly=t.copy()
 for plane in [np.array([1,0,0,-hi[0]]),np.array([-1,0,0,lo[0]]),np.array([0,1,0,-hi[1]]),np.array([0,-1,0,lo[1]])]:
  if len(poly)<3:break
  poly=clip_polygon(poly,plane)
 if len(poly)>=3:pts.extend(poly)
pts=np.array(pts);coping=geometry['transition'][np.array(['ivory_enamel'in x for x in mat['transition']])];copingtop=float(coping[:,:,2].max());gap=float(pts[:,2].min()-copingtop);trail=geometry['trailing'].reshape(-1,3);crossing={'actual_mesh_clipped_over_coping_xy_m':[lo.tolist(),hi.tolist()],'clipped_vertices':len(pts),'actual_lowest_trailing_z_in_band_m':float(pts[:,2].min()),'actual_coping_top_z_m':copingtop,'minimum_vertical_clearance_m':gap,'negative_control_downward_translation_m':.25,'negative_control_fails_height_clearance':gap-.25<0,'complete_trailing_bounds_world_m':[trail.min(0).tolist(),trail.max(0).tolist()],'pass':gap>.005 and gap-.25<0}
whole=Hull(alltri.reshape(-1,3));negative=sum(x['expected_clear']and whole.segment(*x['segment_source_m'])is not None for x in rays)
res={'passed':all(x['pass']for x in boxes+rays+roots)and crossing['pass']and negative>0,'plan_path':str(PLAN.relative_to(ROOT)),'plan_sha256':sha(PLAN),'bindings':bindings,'whole_empty_box_checks':boxes,'finite_clear_and_blocked_rays':rays,'root_reservation_and_soil_contacts':roots,'actual_coping_crossing':crossing,'whole_arrangement_hull_wrongly_blocks_clear_probes':negative,'executed_script_sha256':sha(Path(__file__)),'limits':['Relative partial edge only. No ship coordinates, host floor/room/void or courtyard reconstruction.','Box geometry is screened at0.2mm inset; sightlines are finite rays from explicitly proposed eyes, not a continuous visual field or actor fit.','Coping minimum clearance comes from clipping actual native triangles over the full coping footprint, not from markers or whole-object bounds.','The ordinary-height images need separate pixel inspection; geometry alone cannot establish visual quality.']}
(OUT/'independent_assembly_geometry_review.json').write_text(json.dumps(res,indent=2)+'\n');print('ASSEMBLY',res['passed'],'boxes',len(boxes),'ray failures',[r['id']for r in rays if not r['pass']],'roots',[x['pass']for x in roots],'coping gap',gap,'whole hull negatives',negative,flush=True)
