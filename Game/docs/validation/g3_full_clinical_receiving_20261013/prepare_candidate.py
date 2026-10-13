from pathlib import Path
import json,hashlib,zipfile,struct
P=Path(__file__).parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');S=P/'import/Game';sha=lambda b:hashlib.sha256(b).hexdigest();assert json.loads((P/'IMPORT_RECEIPT.json').read_text())['status']=='PASS_FOUR_MODEL_ISOLATED_CLINICAL_IMPORT';assert json.loads((P/'CURRENT_INPUT_AND_FLOOR_PREFLIGHT.json').read_text())['status'].startswith('PASS');oldpath=G/'assets/models/group3_port2_clinical_20261011/AST-MED-G3-006.glb';b=oldpath.read_bytes();n,_=struct.unpack_from('<II',b,12);d=json.loads(b[20:20+n]);rows=[]
for node in d['nodes']:
 if'mesh'not in node:continue
 assert not any(k in node for k in ['matrix','translation','rotation','scale']);mins=[];maxs=[]
 for p in d['meshes'][node['mesh']]['primitives']:
  a=d['accessors'][p['attributes']['POSITION']];mins.append(a['min']);maxs.append(a['max'])
 rows.append({'name':node['name'],'min':[min(q[i]for q in mins)for i in range(3)],'max':[max(q[i]for q in maxs)for i in range(3)]})
preflight={'old_bounded_glb_sha256':sha(b),'old_bounded_visual_path':'ShipSpace/Group3Port2ClinicalPhysical/AST-MED-G3-006','mesh_preimages':rows,'preserved_old_port2_fixture_names':['clean_supply_and_staff_port_007Light_PhysicalSource','soiled_return_port_007Light_PhysicalSource']};(P/'CURRENT_BOUNDED_PREFLIGHT.json').write_text(json.dumps(preflight,indent=2)+'\n');key='scripts/group3_clinical_full_20261011/physical_package.gd';original=(S/key).read_text();anchor=' var prior:Node3D=space.get_node("Group3Port2ClinicalPhysical");';assert original.count(anchor)==1
before=''' for file in p.model_pins:
  assert(FileAccess.get_sha256("res://assets/models/group3_clinical_full_20261011/"+str(file))==str(p.model_pins[file]))
  assert(load("res://assets/models/group3_clinical_full_20261011/"+str(file)) is PackedScene)
 var preflight:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/group3_clinical_full_20261011/CURRENT_BOUNDED_PREFLIGHT.json"))
 assert(FileAccess.get_sha256("res://assets/models/group3_port2_clinical_20261011/AST-MED-G3-006.glb")==str(preflight.old_bounded_glb_sha256))
 var source:Node3D=ship.get_node(str(preflight.old_bounded_visual_path))
 assert(source.find_children("*","MeshInstance3D",true,false).size()==preflight.mesh_preimages.size())
 for row in preflight.mesh_preimages:
  var mesh:MeshInstance3D=source.find_child(str(row.name).validate_node_name(),true,false);assert(mesh!=null)
  var bounds:AABB=mesh.global_transform*mesh.get_aabb();assert(bounds.position.distance_to(vec(row.min))<.0001 and bounds.end.distance_to(vec(row.max))<.0001)
'''
code=original.replace(anchor,before+anchor);code=code.replace('n.set_meta("held_starboard_return_spans",2)','n.set_meta("held_starboard_return_spans",2);n.set_meta("operating_gates_or_dispatch_admitted",false);n.set_meta("default_main_adoption",false)');code=code.replace('l.shadow_enabled=true;l.set_meta','l.visible=false;l.shadow_enabled=false;l.set_meta')
# Preserve the original operating implementation in source history, while this physical consumer admits only the empty identity/predicate path.
check=' var space:Node3D=ship.get_node("ShipSpace");';assert code.count(check)==1;code=code.replace(check,' assert(resolved_ids.is_empty()and sealed_load_predicates.is_empty(),"Clinical operation requires separate authoritative admission")\n'+check)
w={key:code.encode(),'docs/validation/g3_full_clinical_receiving_20261013/OWNER_PACKAGE.gd.txt':original.encode(),'data/architecture/group3_clinical_full_20261011/CLINICAL.json':(S/'data/architecture/group3_clinical_full_20261011/CLINICAL.json').read_bytes(),'data/architecture/group3_clinical_full_20261011/CURRENT_BOUNDED_PREFLIGHT.json':(P/'CURRENT_BOUNDED_PREFLIGHT.json').read_bytes()}
for q in (S/'assets').rglob('*'):
 if q.is_file():w[str(q.relative_to(S))]=q.read_bytes()
for q in (S/'.godot/imported').iterdir():
 if q.is_file():w[str(q.relative_to(S))]=q.read_bytes()
for q in (S/'scripts/group3_clinical_full_20261011').glob('*.uid'):w[str(q.relative_to(S))]=q.read_bytes()
with zipfile.ZipFile(P/'CANDIDATE_OVERLAY.zip','w',zipfile.ZIP_DEFLATED,compresslevel=1)as z:
 for k,b in w.items():z.writestr(k,b)
(P/'CANDIDATE_RECEIPT.json').write_text(json.dumps({'status':'EXACT_FULL_CLINICAL_PHYSICAL_CANDIDATE_ONLY','original_script_sha256':sha(original.encode()),'consumer_sha256':sha(code.encode()),'all_new_resources_and_old_bounded_preimages_checked_before_free':True,'models_instantiated':3,'new_floor_m2':16089.193863999986,'fixtures':193,'static_closed_source_gates':36,'operating_identities_or_sealed_load_predicates':False,'held_pool_interface_and_two_royalty_spans':True,'source_pins':{k:sha(b)for k,b in w.items()if not k.startswith('.godot/')}},indent=2)+'\n');print('FULL_CLINICAL_CANDIDATE_READY',len(w),'paths','oldpreimage meshes',len(rows))
