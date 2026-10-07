from pathlib import Path
import sys,json,gzip,math,numpy as np
S=Path('/workspace/scratch/375c2e438292');B=Path(__file__).parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(S/'pool-opposite-gallery-proposal001/reference_programme001'));import check_programme as q
actual=q.read(B/'source_build001/qa/BUILD_EVALUATED_CORE.json');parts=q.cache([q.record(p['name'],p['vertices_xyz'],[[p['vertices_xyz'][i]for i in t]for t in p['evaluated_triangles']])for p in actual['parts']])
old=q.read_glb(q.C/'assets/grand_pool_orchard_section/exports/AST-AQU-016.glb');shell=q.cache([q.record(p['source_name'],[v for i in p['global_triangle_indices']for v in old['triangles'][i]],[old['triangles'][i]for i in p['global_triangle_indices']])for p in q.read(S/'pool-opposite-gallery-proposal001/geometry/RETAINED_PART_BOUNDS.json')['parts']]);allparts=parts+shell
for path in [S/'pool-connected-gallery-curved001/source_build001/qa/BUILD_EVALUATED_NEW_PROGRAMME.json.gz',B/'source_build001/qa/BUILD_EVALUATED_STOCK.json.gz']:
 with gzip.open(path,'rt')as f:rows=json.load(f)
 allparts+=q.cache([q.record(p['name'],p['vertices_xyz'],[[p['vertices_xyz'][i]for i in t]for t in p['evaluated_triangles']])for p in rows])
for floor in q.read(S/'pool-opposite-gallery-proposal001/geometry/FLOOR_POLYGONS.json')['floor_regions']:
 ts=[[[x,floor['floor_y'],z]for x,z in t]for t in floor['triangles']];allparts+=q.cache([q.record('COMPILER_FLOOR_'+floor['id'],[v for t in ts for v in t],ts)])
initial=q.read(B/'FIXTURE_FIT_REVIEW.json');issues=[];records=[]
for spec in actual['fixture_reservations']:
 # A parentless Blender Empty stores the assigned source translation as float32.
 # Geometry is the independently reopened evaluated source; export snapshot will
 # also serialize the actual marker node, with these same declared coordinates.
 a=np.asarray(spec['position_xyz'],dtype=np.float32).astype(float);axis=q.unit(spec['direction_xyz']);oldrow=next(r for r in initial['fixtures']if r['name']==spec['name']);hits=[]
 for r in oldrow['receivers']:
  target=np.array(r['point_xyz']);direction=target-a;direction/=np.linalg.norm(direction);found=q.rayhits(a,target+direction*.05,allparts)
  if not found:issues.append({'kind':'missing_actual_receiver','fixture':spec['name'],'target':target.tolist()});continue
  row=found[0];row['source_fixture']=spec['name'];row['within_authored_cone_range']=row['distance_m']<spec['proposed_range_m'] and np.dot(direction,axis)>math.cos(math.radians(55));row['permanent_receiver']=not row['part'].startswith(('FIN_Orbit','FIN_Stellar','FIN_Ceramic','FIN_Catalogue','FIN_Guest','FIN_Case','CG_EAST_'))
  if not row['within_authored_cone_range']:issues.append({'kind':'outside_real_source_range_cone','row':row})
  hits.append(row)
 stable=[r for r in hits if r['permanent_receiver']]
 if not stable:issues.append({'kind':'no_permanent_receiver','fixture':spec['name']})
 selected=stable[0]if stable else None
 records.append({'name':spec['name'],'position_xyz':a.tolist(),'source_position_representation':'Parentless marker translation assigned through float32 mathutils.Vector; actual exported-node equivalence remains required','direction_xyz':list(axis),'range_m':spec['proposed_range_m'],'energy':spec['proposed_energy'],'all_actual_candidate_parts_in_trace':True,'actual_first_receivers':hits,'selected_permanent_receiver':selected,'visibility_sample_xyz':q.add(selected['point_xyz'],q.mul(q.unit(q.sub(a,selected['point_xyz'])),.06))if selected else None})
report={'status':'PASS_COMPLETE_SOURCE_RECEIVER_CORRESPONDENCE'if not issues else'CORRECTION_REQUIRED','source_sha256':q.read(B/'source_build001/qa/BUILD_RECEIPT.json')['sha256'],'included_current_core_parts':len(parts),'included_retained_and_new_programme':True,'included_retained_shell_and_floors':True,'issues':issues,'fixtures':records,'native_selection_and_visual_finish_accepted':False};(B/'ACTUAL_RECEIVERS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'issues':issues,'receivers':{r['name']:r['selected_permanent_receiver']['part']if r['selected_permanent_receiver']else None for r in records}},indent=2),flush=True)
