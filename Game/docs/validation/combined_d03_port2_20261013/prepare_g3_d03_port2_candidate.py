from pathlib import Path
import json,hashlib,zipfile,struct
C=Path(__file__).parent;S=C/'g3_d03_port2_staging/Game';sha=lambda b:hashlib.sha256(b).hexdigest();p=json.loads((S/'data/architecture/group3_d03_port2_20261011/CONNECTION.json').read_text());assert json.loads((C/'G3_D03_PORT2_IMPORT_RECEIPT.json').read_text())['passed'];writes={};docs={}
for q in (S/'assets/models/group3_d03_port2_20261011').iterdir():
 if q.is_file():writes[str(q.relative_to(S))]=q.read_bytes()
for q in (S/'.godot/imported').iterdir():
 if q.is_file():writes[str(q.relative_to(S))]=q.read_bytes()
for file,h in p['model_pins'].items():
 b=writes['assets/models/group3_d03_port2_20261011/'+file];assert sha(b)==h;n,_=struct.unpack_from('<II',b,12);docs[file]=json.loads(b[20:20+n])
key='scripts/group3_d03_port2_20261011/physical_package.gd';original=(S/key).read_text();anchor=' var n:=Node3D.new();n.name="Group3D03Port2Connection";space.add_child(n);n.set_meta("registered_berths_added",0);n.set_meta("authoritative_identity_mapping",false);n.set_meta("owner_current_spine_patch_applied",apply_current_spine_patch)';assert original.count(anchor)==1
prefix=''' for file in p.model_pins:
  assert(FileAccess.get_sha256("res://assets/models/group3_d03_port2_20261011/"+file)==p.model_pins[file])
  assert(load("res://assets/models/group3_d03_port2_20261011/"+file) is PackedScene)
 if apply_current_spine_patch:
  assert(FileAccess.get_sha256("res://assets/models/AST-STF-009_pool_market_home_equipment.glb")==p.current_spine_sha256)
  var preflight:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_d03_port2_20261011/CURRENT_CELL_PREFLIGHT.json"))
  var current:Node3D=ship.get_node("ShipSpace/Districts/LowerStaffNetwork_WIP/LowerStaffEnclosure")
  for row in preflight.mesh_preimages:
   var mesh:MeshInstance3D=current.find_child(str(row.name),true,false);assert(mesh!=null)
   var bounds:AABB=mesh.global_transform*mesh.get_aabb();assert(bounds.position.distance_to(vec(row.min))<.0001 and bounds.end.distance_to(vec(row.max))<.0001)
'''
code=original.replace(anchor,prefix+anchor+';n.set_meta("operating_doors_admitted",false);n.set_meta("default_main_adoption",false)').replace('l.shadow_enabled=true;l.set_meta','l.visible=false;l.shadow_enabled=false;l.set_meta');writes[key]=code.encode();writes[key+'.uid']=(S/(key+'.uid')).read_bytes();writes['data/architecture/group3_d03_port2_20261011/CONNECTION.json']=(S/'data/architecture/group3_d03_port2_20261011/CONNECTION.json').read_bytes();writes['data/architecture/group3_d03_port2_20261011/CURRENT_CELL_PREFLIGHT.json']=(C/'G3_D03_PORT2_CURRENT_CELL_BOUNDS.json').read_bytes()
mappings=[]
for fixture in p['fixtures']:
 found=[]
 for file,d in docs.items():
  for node in d['nodes']:
   if 'opal'not in node.get('name','').lower()or'mesh'not in node:continue
   assert not any(k in node for k in ['matrix','translation','rotation','scale'])
   for prim in d['meshes'][node['mesh']]['primitives']:
    a=d['accessors'][prim['attributes']['POSITION']]
    if all(lo-.025<=v<=hi+.025 for lo,v,hi in zip(a['min'],fixture['position'],a['max'])):found.append({'model':file,'node':node['name']})
 assert len(found)==1,(fixture['name'],found);mappings.append({'fixture':fixture['name'],**found[0]})
with zipfile.ZipFile(C/'G3_D03_PORT2_CANDIDATE_OVERLAY.zip','w',zipfile.ZIP_DEFLATED,compresslevel=1)as z:
 for k,b in writes.items():z.writestr(k,b)
(C/'G3_D03_PORT2_LENS_MAPPING.json').write_text(json.dumps({'model_pins':p['model_pins'],'mappings':mappings},indent=2)+'\n');result={'status':'CANDIDATE_ONLY_EXACT_CURRENT_RECEIVING_PENDING','source_revision':'6f2d0da67429ea940edf7011348ec08a346f37db','models':4,'native_floor_m2':p['new_floor_m2'],'fixture_sources':4,'original_script_sha256':sha(original.encode()),'current_spine_sha256':p['current_spine_sha256'],'all_new_models_and_allfour_current_bounds_preflight_before_scene_mutation':True,'operating_identities_created':False,'source_sha256':{k:sha(b)for k,b in writes.items()if not k.startswith('.godot/')}};(C/'G3_D03_PORT2_CANDIDATE.json').write_text(json.dumps(result,indent=2)+'\n');print('candidate',len(writes),'paths',len(mappings),'exact lens bindings')
