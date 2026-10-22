from pathlib import Path
import json,hashlib,math,shutil
from shapely.geometry import Polygon,Point,LineString,box
from shapely.ops import unary_union
R=Path('/workspace/Astraea-recovered-e6274e77-20261021');G=R/'Game';P=G/'night_garden_lower_bank_20261022';d=json.loads((P/'PACKAGE.json').read_text());index=json.loads((P/'evidence/INDEX.json').read_text())['rooms'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=0
for f,h in d['pins'].items():assert sha(R/f)==h;checks+=1
streets=json.loads((G/'data/architecture/CENTRAL_RESIDENTIAL_STREETS.json').read_text());compiler=[]
for file in ['structural_meshes.json','received_structural_meshes.json']:
 for r in json.loads((G/'data/generated'/file).read_text())['regions']:
  if r.get('floor_y') in [84,88.5]:compiler.append((file,r,Polygon(r['rings'][0],r['rings'][1:])))
rows=[];ids=set();rests=set()
for room in d['rooms']:
 a=room['allocation'];rid=a['proposed_runtime_id'];assert rid not in ids;ids.add(rid);assert not rests.intersection(a['proposed_rest_slot_ids']);rests.update(a['proposed_rest_slot_ids']);assert {c['rest_slot_id']for c in room['components']if 'rest_slot_id'in c}==set(a['proposed_rest_slot_ids']);checks+=3
 rec=index[room['model_file']];assert rec['room_id']==rid
 for kind in ['shell','detail','full']:
  file=rec[kind+'_path'];h=rec[kind+'_sha256']if kind!='full'else rec['sha256'];assert sha(G/file.removeprefix('res://'))==h;checks+=1
 assert rec['bounds_min'][0]>=a['allocation_x'][0]-.3 and rec['bounds_max'][0]<=a['allocation_x'][1]+.3;assert rec['bounds_min'][2]>=a['allocation_z'][0]-.3 and rec['bounds_max'][2]<=a['allocation_z'][1]+.3;checks+=2
 floor=a['floor_y'];z=sum(a['allocation_z'])/2;outer=a['allocation_x'][0]>84;front=a['allocation_x'][0]if outer else a['allocation_x'][1];poly=box(a['allocation_x'][0],a['allocation_z'][0],a['allocation_x'][1],a['allocation_z'][1]);owners=[]
 for file,r,p in compiler:
  if abs(r['floor_y']-floor)<.001 and p.intersection(poly).area>.001:owners.append({'file':file,'id':r['id'],'overlap_m2':p.intersection(poly).area})
 floorrows=[r for r in streets['regions']if r['floor_y']==floor];public=unary_union([Polygon(r['rings'][0],r['rings'][1:])for r in floorrows]);public_found=public.covers(Point(84,z)) or any(abs(r['floor_y']-floor)<.001 and poly2.covers(Point(84,z)) for file,r,poly2 in compiler);checks+=1
 cuts=[]
 for g in streets['exposed_edge_guards']:
  if abs(g['a'][1]-floor)>.001:continue
  line=LineString([(g['a'][0],g['a'][2]),(g['b'][0],g['b'][2])])
  if line.intersects(box(front-.05,z-.85,front+.05,z+.85)):cuts.append(g)
 rows.append({'source_envelope_index':a['source_envelope_index'],'room_id':rid,'deck':a['deck'],'allocation_x':a['allocation_x'],'allocation_z':a['allocation_z'],'public_street_point':[84,floor,z],'public_floor_in_surveyed_sources':public_found,'existing_guard_predecessors':cuts,'compiler_floor_owners_under_allocation':owners,'receiving_state':'HELD: exact physical support and missing-only threshold/guard successor unverified','view_state':'HELD: current inner-court or outer hull/enclosure visibility must be proven; no hull cut authorized'})
assert len(ids)==17 and len(rests)==19
out={'status':'PASS candidate source/integrity; RECEIVING HELD','checks':checks,'rooms':17,'reserved_rests':19,'original_native_sources_retained':True,'canonical_full_resources':True,'shared_shell_detail_wrappers':34,'new_capacity':0,'main_integrated':False,'geometry_connection_accepted':False,'free_bytes':shutil.disk_usage(R).free};(P/'evidence/SOURCE_INTEGRITY.json').write_text(json.dumps(out,indent=2)+'\n')
survey={'scope':'Exact current compiler floor definitions and central public street/guard source only; absence here is not proof that no other retained model supplies support','current_street_sha256':sha(G/'data/architecture/CENTRAL_RESIDENTIAL_STREETS.json'),'compiler_sha256':{f:sha(G/'data/generated'/f)for f in ['structural_meshes.json','received_structural_meshes.json']},'rooms':rows,'new_geometry_or_guard_changes':False,'remaining_action':'Resolve actual current non-compiler structural/hull/support owners, legal outlook context and positive connections before authoring receiving successors or registering these rooms in main.'};(P/'evidence/RECEIVING_SURVEY.json').write_text(json.dumps(survey,indent=2)+'\n');print(out);print('public approaches located',sum(r['public_floor_in_surveyed_sources']for r in rows));print('guarded thresholds',sum(bool(r['existing_guard_predecessors'])for r in rows),'compiler-supported allocations',sum(bool(r['compiler_floor_owners_under_allocation'])for r in rows))
