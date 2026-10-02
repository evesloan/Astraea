"""Independent actual-native component arrangement and swept reserve check, not a deck plan."""
from pathlib import Path
import sys,json,hashlib,itertools,numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch14';sys.path.insert(0,str(OUT));from independent_collision_adapters import expand,Hull
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch12'));from independent_void_geometry import triangle_box_mask,hull_box_overlap
from independent_collision_geometry import inside_mesh,segment_triangles
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
pp=ROOT/'qa/batch14/assembly/plan.json';plan=json.loads(pp.read_text());rows=[];bindings=[];states={};sweeps=[]
for state in ['closed','all_removed']:
 tris=[];names=[];hulls=[];bounds=[]
 for item in plan['items']:
  ident=item['catalogue_id'];mp=ROOT/item['manifest_path'];m=json.loads(mp.read_text());gp=ROOT/(plan['withdrawn_export']if state=='all_removed'and ident=='AST-AQU-008'else item['path']);g=Native(gp);t=g.tris@C;off=np.asarray(item['source_origin_m']);theta=np.radians(item['source_z_rotation_deg']);rot=np.array([[np.cos(theta),-np.sin(theta),0],[np.sin(theta),np.cos(theta),0],[0,0,1]])
  if state=='all_removed'and ident in ['AST-AQU-009','AST-AQU-010']:
   ni={n.get('name'):i for i,n in enumerate(g.g.doc['nodes'])}
   for rem in m['independent_removable_roots']:
    rix=ni[rem['name']]
    def desc(i):
     while i in g.parents:
      i=g.parents[i]
      if i==rix:return True
     return False
    nn=[g.g.doc['nodes'][i].get('name')for i in g.world if desc(i)and'mesh'in g.g.doc['nodes'][i]];t[np.isin(g.nodes,nn)]+=np.asarray(rem['removal_vector_source_m'])
  t=t@rot.T+off;tris.extend(t);names.extend([ident]*len(t));bounds.append({'catalogue_id':ident,'min_m':t.min((0,1)).tolist(),'max_m':t.max((0,1)).tolist()})
  cp=mp.parent/(ident+'.collision_proposal.json'if ident in ['AST-AQU-007','AST-AQU-008']else'collision_proposals.json');c=json.loads(cp.read_text());c=c if ident in ['AST-AQU-007','AST-AQU-008']else c[ident]
  for rec in c['shapes']:
   delta=np.zeros(3)
   if state=='all_removed':
    if ident=='AST-AQU-008'and rec.get('motion_group')=='container':delta=np.array([0,.92,0])
    if ident in ['AST-AQU-009','AST-AQU-010']:
     for rem in m['removal_proposals']:
      if set(rec['covered_parts'])<=set(rem['parts']):delta=np.asarray(rem['translation_source_m'])
   for h in expand(rec):hulls.append(Hull((h.points+delta)@rot.T+off,{**h.record,'catalogue_id':ident}))
  if state=='closed':bindings.append({'catalogue_id':ident,'files':{k:bind(p)for k,p in [('source',ROOT/item['source_path']),('export',gp),('manifest',mp),('collision',cp)]}})
 tris=np.asarray(tris);names=np.asarray(names);boxes=[]
 for box in plan['proposed_empty_regions']:
  lo=np.asarray(box['min_source_m']);hi=np.asarray(box['max_source_m']);mask=triangle_box_mask(tris,lo+.0002,hi-.0002);overlaps=[h.record['catalogue_id']+':'+h.record['name']for h in hulls if hull_box_overlap(h,lo+.0002,hi-.0002)['overlaps']];boxes.append({'name':box['id'],'source_box_m':[lo.tolist(),hi.tolist()],'actual_native_intruding_triangle_count':int(mask.sum()),'actual_native_intruding_assets':sorted(set(names[mask])),'collision_overlaps':overlaps,'pass':not mask.any()and not overlaps})
 pairs=[]
 for a,b in itertools.combinations(bounds,2):
  alo,ahi=np.array(a['min_m']),np.array(a['max_m']);blo,bhi=np.array(b['min_m']),np.array(b['max_m']);gap=np.maximum(np.maximum(alo-bhi,blo-ahi),0);pairs.append({'assets':[a['catalogue_id'],b['catalogue_id']],'separating_axis_gaps_m':gap.tolist(),'aabb_disjoint':bool((gap>.0002).any())})
 controls=[]
 for item in plan['items']:
  ident=item['catalogue_id'];off=np.asarray(item['source_origin_m']);p=off+np.array([.451,-.005,-.01]if ident=='AST-AQU-008'else[0,0,-.01]);q=off+np.array([.451,-.005,.15]if ident=='AST-AQU-008'else[0,0,.15]);t=tris[names==ident];hit=bool(segment_triangles(p,q,t));controls.append({'asset':ident,'probe_source_m':[p.tolist(),q.tolist()],'hit':hit})
 states[state]={'actual_native_bounds':bounds,'complete_region_checks':boxes,'pair_separation_checks':pairs,'floor_solid_positive_controls':controls,'passed':all(x['pass']for x in boxes)and all(x['aabb_disjoint']for x in pairs)and all(x['hit']for x in controls)}
for item in plan['items']:
 ident=item['catalogue_id'];a=next(x for x in states['closed']['actual_native_bounds']if x['catalogue_id']==ident);b=next(x for x in states['all_removed']['actual_native_bounds']if x['catalogue_id']==ident);lo=np.minimum(a['min_m'],b['min_m']);hi=np.maximum(a['max_m'],b['max_m']);checks=[]
 for box in plan['proposed_empty_regions']:
  separated=bool(((hi<=np.asarray(box['min_source_m']))|(lo>=np.asarray(box['max_source_m']))).any());checks.append({'region':box['id'],'entire_linear_sweep_aabb_disjoint':separated})
 sweeps.append({'asset':ident,'complete_linear_sweep_bounds_m':[lo.tolist(),hi.tolist()],'checks':checks,'pass':all(x['entire_linear_sweep_aabb_disjoint']for x in checks)})
r={'passed':all(x['passed']for x in states.values())and all(x['pass']for x in sweeps),'bindings':bindings,'withdrawn_export':bind(ROOT/plan['withdrawn_export']),'plan':bind(pp),'states':states,'whole_linear_sweep_region_separation':sweeps,'scope':'Relative dry and wet component examples only. Two-metre front strip and rear stance are deliberately empty QA reserves. Exact D08 room placement, adjacency, through-route, wet/dry boundary, species/body/cart fit and physical operation remain unknown.','method':'Actual native triangle hierarchy transformed into the explicit relative source placement. Full inset-box triangle SAT plus convex-proposal feasibility at closed and all-removed poses. Monotone translation sweep is enclosed by full endpoint bounds and shown disjoint from both complete reserve boxes. Pairwise conservative bounds establish component separation; no room fit is inferred.','executed_script_sha256':sha(Path(__file__))}
(OUT/'independent_assembly_geometry_review.json').write_text(json.dumps(r,indent=2)+'\n');print('ASSEMBLY',r['passed'],[(k,v['passed'])for k,v in states.items()],flush=True)
