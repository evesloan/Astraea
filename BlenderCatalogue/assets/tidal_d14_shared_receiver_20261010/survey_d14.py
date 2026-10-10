from pathlib import Path
import json,hashlib,sys,struct,numpy as np
sys.path.insert(0,'/workspace/shared/astraea_python_deps')
from shapely.geometry import Polygon,box,shape
from shapely.ops import unary_union
R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');G=R/'Game';W=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reader=R/'BlenderCatalogue/assets/group4_tram_connections_20261009/boarding_north_005/glb_source_reader.py'
s=reader.read_text();u={'R':R,'PIN':[],'np':np};exec('import math, struct, json\n'+s[s.index('def read(p):'):s.index('def contacts(')],u)
a=json.load(open(R/'BlenderCatalogue/assets/group3_crew_service_20261009/source/TIDAL_STAFF_INTERFACE.json'));d=json.load(open(G/'data/architecture/TIDAL_LIFT_RECEIVING_CANDIDATE.json'));allgeo={};pins={};sources=[];floor_names=set()
def add(file,tag,at=(0,0,0),yaw=0):
 pins['Game/assets/models/'+file]=sha(G/'assets/models'/file);sources.append({'file':file,'tag':tag,'origin':at,'yaw':yaw})
 raw=(G/'assets/models'/file).read_bytes();ln=struct.unpack_from('<I',raw,12)[0];gltf=json.loads(raw[20:20+ln])
 for node in gltf['nodes']:
  n=node.get('name','');cat=node.get('extras',{}).get('category','')
  if cat=='floor'or 'floor'in n.lower():floor_names.add(tag+'/'+n)
 for n,t in u['triangles'](file,at,yaw):allgeo[tag+'/'+n]=t
add(d['model_file'],'house')
# Mirror all six installed frontage replacement steps in adoption order, without mutating the source.
for cfg in ['TIDAL_SPECIALTY_102.json','TIDAL_SPECIALTY_D13_BATCH.json','TIDAL_AQUATIC_SINGLES.json','TIDAL_AQUATIC_DOUBLE.json','TIDAL_LOW_NEST_SINGLES.json','TIDAL_QUIET_DOUBLES.json']:
 q=json.load(open(G/'data/architecture'/cfg));pins['Game/data/architecture/'+cfg]=sha(G/'data/architecture'/cfg)
 if q.get('frontage_model'):
  file=q['frontage_model'];ts=dict(u['triangles'](file));pins['Game/assets/models/'+file]=sha(G/'assets/models'/file)
  for p in q.get('frontage',{}).get('changed_batches',[]):allgeo['house/'+p['batch']]=ts[p['batch']]
# D14 final street successor, not its replaced predecessor.
aq=json.load(open(G/'data/architecture/TIDAL_AQUATIC_DOUBLE.json'));add(aq['street_model'],'D14_final_south_street')
u14=json.load(open(G/'data/architecture/TIDAL_UNIT_CANDIDATES.json'));proto={x['key']:x for x in u14['prototypes']}
for q in u14['units']:
 if abs(q['floor_y']-88.5)<1e-6 and min(q['allocation_z'])<-478:
  add(proto[q['source_recipe_key']]['model_file'],q['address'],q['source_origin_world_xyz'],q['source_yaw_godot'])
for cfg in ['TIDAL_AQUATIC_SINGLES.json','TIDAL_AQUATIC_DOUBLE.json']:
 for q in json.load(open(G/'data/architecture'/cfg))['units']:
  add(q['model_file'],q['allocation']['proposed_runtime_id'])
# Exact imported floors plus all compiled/received at the D14 datum.
ownerpoly={}
for n,t in allgeo.items():
 if n not in floor_names:continue
 top=t[np.all(abs(t[:,:,1]-88.5)<2e-4,axis=1)];polys=[Polygon(x[:,[0,2]]) for x in top if Polygon(x[:,[0,2]]).area>1e-8]
 if polys:ownerpoly[n]=unary_union(polys)
for fname in ['structural_meshes.json','received_structural_meshes.json']:
 path=G/'data/generated'/fname;pins['Game/data/generated/'+fname]=sha(path)
 for q in json.load(open(path))['regions']:
  if abs(q['floor_y']-88.5)<1e-6:ownerpoly[fname+'/'+q['id']]=unary_union([Polygon(t) for t in q['triangles']])
old=unary_union(list(ownerpoly.values()))
fp=next(x for x in a['floor_proposals']if x['deck']=='D14');request=unary_union([Polygon(q['boundary'],q['holes'])for q in fp['polygons']]);collars=[]
for role,z in [('clean_linen_supply',-493),('sealed_soiled_waste',-487)]:
 c=box(-63.34,z-1.8,-62.8,z+1.8);collars.append({'role':role,'bounds_xz':list(c.bounds),'actual_floor_overlap_m2':c.intersection(old).area,'approach_overlap_m2':c.intersection(request).area,'missing_support_area_m2':c.difference(old.union(request)).area,'floor_owners':[{'owner':n,'area_m2':p.intersection(c).area}for n,p in ownerpoly.items()if p.intersection(c).area>1e-8]})
# Local screen: exact source triangle AABB candidates only. This identifies concrete solids; final placement checks clip candidates exactly.
bounds=[-68,-16,88.26,91.85,-504,-480];local=[]
for n,t in allgeo.items():
 lo=t.min(axis=1);hi=t.max(axis=1);keep=np.all((hi>=np.array([bounds[0],bounds[2],bounds[4]]))&(lo<=np.array([bounds[1],bounds[3],bounds[5]])),axis=1)
 if keep.any():local.append({'mesh':n,'bounds_xyz':[t[keep].min(axis=(0,1)).tolist(),t[keep].max(axis=(0,1)).tolist()],'candidate_triangles':int(keep.sum())})
for path in [reader,R/'BlenderCatalogue/assets/group3_crew_service_20261009/source/TIDAL_STAFF_INTERFACE.json',G/'data/architecture/TIDAL_LIFT_RECEIVING_CANDIDATE.json',G/'data/architecture/TIDAL_UNIT_CANDIDATES.json',G/'scripts/tidal_garden_adoption.gd',G/'scripts/tidal_aquatic_double.gd']:
 pins[str(path.relative_to(R))]=sha(path)
result={'schema':'astraea.tidal.d14_exact_receiver_survey.v1','status':'source_survey_only','floor_y':88.5,'sources':sources,'collars':collars,'approach_requested_area_m2':request.area,'approach_existing_floor_overlap_m2':request.intersection(old).area,'approach_missing_only_area_m2':request.difference(old).area,'local_triangle_candidate_bounds':bounds,'local_source_mesh_candidates':local,'nearby_floor_owners':[{'owner':n,'bounds_xz':list(p.bounds),'local_area_m2':p.intersection(box(-68,-504,-16,-480)).area}for n,p in ownerpoly.items()if p.intersects(box(-68,-504,-16,-480))],'source_pins':pins,'no_geometry_changed':True,'no_runtime_changed':True,'no_lift_extension':True}
(W/'D14_ACTUAL_SOURCE_SURVEY.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k]for k in ['collars','approach_existing_floor_overlap_m2','nearby_floor_owners','local_source_mesh_candidates']},indent=2))
