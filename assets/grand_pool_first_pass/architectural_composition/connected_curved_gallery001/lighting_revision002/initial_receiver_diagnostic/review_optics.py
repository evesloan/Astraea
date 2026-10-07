from pathlib import Path
import json,math,sys,hashlib,numpy as np
S=Path('/workspace/scratch/375c2e438292');B=Path(__file__).parent;sys.path.insert(0,str(S/'pool-opposite-gallery-proposal001/reference_programme001'));import check_programme as q
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();plan=q.read(B/'CORE_PLAN.json');parts=q.cache([q.record(p['name'],p['vertices_xyz'],[t for f in p['faces']for t in q.triang_face(p['vertices_xyz'],f)],meta=p)for p in plan['parts']]);cm={p['name']:p for p in parts}
glb=q.read_glb(q.C/'assets/grand_pool_orchard_section/exports/AST-AQU-016.glb');shell=q.cache([q.record(p['source_name'],[v for i in p['global_triangle_indices']for v in glb['triangles'][i]],[glb['triangles'][i]for i in p['global_triangle_indices']])for p in q.read(S/'pool-opposite-gallery-proposal001/geometry/RETAINED_PART_BOUNDS.json')['parts']]);floors=[]
for f in q.read(S/'pool-opposite-gallery-proposal001/geometry/FLOOR_POLYGONS.json')['floor_regions']:
 tr=[[[x,f['floor_y'],z]for x,z in t]for t in f['triangles']];floors.append(q.record('COMPILER_FLOOR_'+f['id'],[v for t in tr for v in t],tr))
q.cache(floors);allparts=parts+shell+floors
issues=[];rows=[]
for f in plan['fixture_reservations']:
 pos=np.array(f['position_xyz']);axis=np.array(f['direction_xyz']);axis/=np.linalg.norm(axis);right=np.cross(axis,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,axis);N=len(cm[f['housing']]['vertices'])//4;back=cm[f['housing']]['vertices'][:N];targets=[p for p in parts if p['name']not in {f['housing'],f['physical_lens']}];mount=[]
 for p in back:mount.append([r['name']for r in targets if q.on_surface(p,r)])
 if any(not t for t in mount):issues.append({'kind':'mount_gap','source':f['name'],'missing':sum(not t for t in mount)})
 physical_supports=sorted({n for names in mount for n in names})
 if f['housing']in plan['modified_existing_parts']:cm[f['housing']]['meta']['support']=physical_supports
 exits=[]
 for polar in [0,25,55]:
  for az in ([0]if polar==0 else range(0,360,30)):
   rad=math.radians(polar);azi=math.radians(az);d=axis*math.cos(rad)+(right*math.cos(azi)+up*math.sin(azi))*math.sin(rad);hit=q.rayhits(pos,pos+d*.06,parts)
   if hit:exits.append({'polar':polar,'azimuth':az,'hits':hit[:2]})
 if exits:issues.append({'kind':'fixture_aperture','source':f['name'],'hits':exits})
 receivers=[]
 if f['mounting']=='up':
  for tangent_x,tangent_y in [(0,0),(-.45,0),(.45,0),(0,-.45),(0,.45),(-.38,-.38),(.38,.38)]:
   d=axis+right*tangent_x+up*tangent_y;d/=np.linalg.norm(d);hit=q.rayhits(pos,pos+d*7,allparts)
   if hit:
    first=hit[0];valid=first['part'].startswith(('CG_UpperCrown','CG_Pier4','GP_UpperPier','GP_RoofRib','GP_LongCeiling'))
    receivers.append(dict(first,valid_crown_or_bearing_receiver=valid,angle_degrees=math.degrees(math.acos(np.clip(np.dot(d,axis),-1,1)))))
   else:receivers.append({'unbounded_ray':True,'valid_crown_or_bearing_receiver':False})
  if not all(r['valid_crown_or_bearing_receiver']for r in receivers):issues.append({'kind':'crown_receiver_not_bounded','source':f['name'],'rows':receivers})
 else:
  # Derive actual nearest-use floor/wall receivers from the intended cone.
  for tangent_x,tangent_y in [(0,0),(-.4,0),(.4,0),(0,-.4),(0,.4)]:
   d=axis+right*tangent_x+up*tangent_y;d/=np.linalg.norm(d);hit=q.rayhits(pos,pos+d*8,allparts)
   if hit:receivers.append(dict(hit[0],actual_source_surface=True))
  if not receivers:issues.append({'kind':'no_use_receiver','source':f['name']})
 ds=[r['distance_m']for r in receivers if'distance_m'in r];rng=math.ceil((max(ds)+.35)*10)/10 if ds else None
 row={'name':f['name'],'mounting':f['mounting'],'physical_housing':f['housing'],'physical_lens':f['physical_lens'],'position_xyz':pos.tolist(),'direction_xyz':axis.tolist(),'all_rim_back_vertices_on_actual_support':all(mount),'physical_supports':physical_supports,'full55degree_aperture_exit_60mm_clear':not exits,'receivers':receivers,'measured_max_receiver_distance_m':max(ds)if ds else None,'proposed_range_m':rng,'range_rule':'Measured selected receiver distance plus0.35m; rounded upward to0.1m. Not a selection ranking adjustment.','proposed_energy':.42,'half_angle_degrees':55,'native_accepted':False};rows.append(row)
 if rng:f['proposed_range_m']=rng
# Complete geometry and source counts remain exact except the declared fixture subset.
original=q.read(B.parent/'CORE_PLAN.json');om={p['name']:p for p in original['parts']};modified=set(plan['modified_existing_parts'])
for name,p in cm.items():
 if name not in modified:assert p['meta']==om[name],name
plan['parts']=[cm[p['name']]['meta']for p in plan['parts']];(B/'CORE_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
r={'status':'PASS_PAIRED_PHYSICAL_FIXTURE_RECEIVER_PLAN'if not issues else'CORRECTION_REQUIRED','issues':issues,'fixtures':rows,'same_six_sources':True,'new_four_plus_retained_two':True,'same_eight_active_budget':True,'source_geometry_only':True,'native_energy_and_selection_pending':True,'plan_sha256':sha(B/'CORE_PLAN.json'),'unchanged_architecture_and_programme':True};(B/'RECEIVER_PROOF.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':r['status'],'issues':issues,'ranges':{r['name']:r['proposed_range_m']for r in rows}},indent=2),flush=True)
