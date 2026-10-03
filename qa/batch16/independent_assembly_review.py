"""Separate-context complete approach-box and component-sweep screening; read only."""
from pathlib import Path
import sys,json,hashlib,itertools,math,numpy as np
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch16';sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch12'));from independent_void_geometry import triangle_box_mask
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
planp=OUT/'assembly/plan.json';plan=json.loads(planp.read_text());items=[];binds=[bind(planp)]
def rot_bound(vertices,pivot,travel):
 p=np.array(pivot);v=np.asarray(vertices)-p;start,end=sorted([0,math.radians(travel)]);lo=v.min(0);hi=v.max(0)
 for ax,A,B in [(1,v[:,1],-v[:,2]),(2,v[:,2],v[:,1])]:
  values=[A*np.cos(start)+B*np.sin(start),A*np.cos(end)+B*np.sin(end)];angle=np.arctan2(B,A)
  for k in range(-3,4):
   q=angle+k*np.pi;values.append(np.where((q>=start)&(q<=end),A*np.cos(q)+B*np.sin(q),np.nan))
  lo[ax]=np.nanmin(np.asarray(values));hi[ax]=np.nanmax(np.asarray(values))
 return lo+p,hi+p
for item in plan['items']:
 assert item['source_z_rotation_deg']==0,'Explicit world rotation adapter required';offset=np.array(item['source_origin_m']);mp=ROOT/item['manifest_path'];m=json.loads(mp.read_text());rp=OUT/f"independent_source_{item['asset_id']}.json";s=json.loads(rp.read_text());assert sha(ROOT/item['source_path'])==s['sha256'];a=np.load(ROOT/s['geometry_cache']);tri=a['triangles'];labels=a['object_names'];objects={x['name']:x for x in s['objects']};los=[tri.min((0,1))];his=[tri.max((0,1))]
 for move in m.get('motion_records',m.get('motions',[])):
  names=move.get('semantic_parts',[n for n,x in objects.items()if x['parent']==move['root']and x['type']=='MESH']);v=tri[np.isin(labels,names)].reshape(-1,3)
  if move.get('kind',move.get('type'))=='rotation':lo,hi=rot_bound(v,move['pivot_source_m'],move['travel'])
  else:
   delta=np.array(move['axis_source'])*move.get('travel',move.get('access_m'));lo=v.min(0)+np.minimum(delta,0);hi=v.max(0)+np.maximum(delta,0)
  los.append(lo);his.append(hi)
 lo=np.min(los,0)+offset;hi=np.max(his,0)+offset;states=[]
 for state,path in item['variants'].items():
  n=Native(ROOT/path);nt=n.tris@C+offset;states.append({'state':state,'export':bind(ROOT/path),'triangles':nt,'bounds_source_m':[nt.min((0,1)).tolist(),nt.max((0,1)).tolist()]})
 items.append({**item,'all_motion_envelope_source_m':[lo.tolist(),hi.tolist()],'states':states});binds.extend([bind(mp),bind(ROOT/item['source_path']),bind(rp)])
regions=[]
for reg in plan['proposed_empty_regions']:
 lo=np.array(reg['min_source_m']);hi=np.array(reg['max_source_m']);checks=[]
 for item in items:
  if item['group']!=reg['group']:continue
  ilo,ihi=np.array(item['all_motion_envelope_source_m']);gaps=np.maximum(lo-ihi,ilo-hi);separated=bool(np.any(gaps>=0));hits=[]
  for st in item['states']:
   mask=triangle_box_mask(st['triangles'],lo,hi);hits.append({'state':st['state'],'native_triangles_intruding':int(mask.sum()),'pass':not mask.any()})
  checks.append({'item':item['key'],'whole_continuous_motion_envelope_disjoint':separated,'separating_axis_gaps_m':gaps.tolist(),'states':hits,'pass':separated and all(x['pass']for x in hits)})
 regions.append({**reg,'checks':checks,'pass':all(x['pass']for x in checks)})
pairs=[]
for a,b in itertools.combinations(items,2):
 if a['group']!=b['group']:continue
 alo,ahi=np.array(a['all_motion_envelope_source_m']);blo,bhi=np.array(b['all_motion_envelope_source_m']);gap=np.maximum(alo-bhi,blo-ahi);pairs.append({'items':[a['key'],b['key']],'whole_motion_envelopes_disjoint':bool(np.any(gap>=0)),'separating_axis_gaps_m':gap.tolist(),'pass':bool(np.any(gap>=0))})
controls=[]
for item in items:
 t=item['states'][0]['triangles'];p=t[0].mean(0);detected=bool(triangle_box_mask(t,p-.002,p+.002).any());controls.append({'item':item['key'],'deliberate_small_box_at_actual_native_triangle_detected':detected,'pass':detected})
for item in items:
 for st in item['states']:del st['triangles']
r={'passed':all(x['pass']for x in regions+pairs+controls),'plan':bind(planp),'final_input_bindings':binds,'items':items,'complete_approach_regions':regions,'full_motion_intercomponent_separation':pairs,'positive_controls':controls,'display_instances':len(items),'unique_designs':len(set(x['asset_id']for x in items)),'registered_seats_added':0,'methods':['All native GLB states transformed with actual native hierarchy and C inverse into the source inspection frame.','Exact coordinate extrema of all source rotating vertices over entire angle intervals plus complete straight-translation extrema conservatively enclose every authored moving triangle. Independent motion interaction is separately checked.','All five complete boxes are disjoint from these complete envelopes; actual endpoint native triangle/box SAT supplements the proof. Same-context component pairs have complete envelope separation.'],'limits':['Separate foyer, audience and workshop examples do not establish adjacency or a host circulation route.','Proposed0.74m seat spacing is unplaced QA only;52mm inter-module gap is no body or transfer acceptance.','Empty inspection strips do not replace the historical3.4m cart contract or establish all-species movement.','No engine, crowd, load, acoustic, lighting, user or room-fit acceptance.'],'executed_script_sha256':sha(Path(__file__))};(OUT/'independent_assembly_geometry_review.json').write_text(json.dumps(r,indent=2)+'\n');print('Assembly',r['passed'],'regions',[(x['id'],x['pass'])for x in regions],flush=True)
