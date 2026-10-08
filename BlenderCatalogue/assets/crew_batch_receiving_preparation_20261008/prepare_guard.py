from pathlib import Path
import json,hashlib,shutil,re
R=Path(__file__).resolve().parent;G=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x/Game');C=R/'compiler_candidate';ctx=json.loads((C/'data/architecture/packages/crew_batch/BUILD_CONTEXT.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def copy(src,rel):
 q=C/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,q)
for rel in ['scripts/crew_batch_receiving.gd','data/architecture/crew_batch/runtime_manifest.json']:copy(R/'runtime_candidate'/rel,rel)
for item in json.loads((R/'INTAKE.json').read_text()):
 key=item['programme'];copy(R/'runtime_candidate'/key/(key+'_runtime_names001.glb'),'assets/models/'+key+'_runtime_names001.glb');copy(R/'runtime_candidate'/key/'NODE_NAME_MAP.json','data/architecture/crew_batch/'+key+'_NODE_NAME_MAP.json')
for name in ['AST-CIR-005_aft_uniforms_d03.glb']:copy(R/'uniforms_aperture_candidate'/name,'assets/models/'+name)
for name in ['RUNTIME_PROOF.json','SOURCE_PROOF.json','ADOPTION_CONTRACT.json','inverse_original_header.bin','verify_candidate.py']:copy(R/'uniforms_aperture_candidate'/name,'data/architecture/crew_batch/aperture/'+name)
# Exact original aft contract is retained and its minimal source edits are reversible.
aft='data/architecture/AFT_PUBLIC_CORE.json';b=(G/aft).read_bytes();ret='data/architecture/packages/crew_batch/retained_286/'+aft;copy(G/aft,ret);ctx['predecessors'][aft]={'sha256':hashlib.sha256(b).hexdigest(),'retained_path':ret};aft_text=b.decode();aft_edits=[]
for before,after in [('"enclosure_file": "AST-CIR-005_spine_core.glb"','"enclosure_file": "AST-CIR-005_aft_uniforms_d03.glb"'),('Sidewalls remain closed until supported branches are authored.','D03 starboard Uniforms aperture is source-authored; all other sidewalls remain closed until supported branches are authored.'),('"lateral_portal_decks": []','"lateral_portal_decks": ["D03"]'),('"lateral_portal_side": null','"lateral_portal_side": "starboard"')]:
 assert aft_text.count(before)==1; aft_text=aft_text.replace(before,after);aft_edits.insert(0,dict(before=before,after=after,count=1))
(C/aft).write_text(aft_text)
gpath='tests/medical_triage_successor_guard.gd';spath='scripts/ship.gd';s=(C/ctx['predecessors'][gpath]['retained_path']).read_text();edits=[]
def edit(before,after,count=1):
 global s
 assert s.count(before)==count,(before[:90],s.count(before));s=s.replace(before,after);edits.insert(0,dict(before=before,after=after,count=count))
a=s.index('# LAUNDRY_EXACT_SECTION_BEGIN');part=s[a:];new=part
new=new.replace('FileAccess.get_sha256("res://"+str(path))','_crew_current_sha256("res://"+str(path))').replace('FileAccess.get_file_as_string("res://"+str(path))','_crew_current_text("res://"+str(path))')
for p in ['data/spatial_layout.json','data/generated/structural_meshes.json','docs/LAYOUT_COMPILE_CHECKS.json']:new=new.replace('FileAccess.get_file_as_string("res://'+p+'")','_crew_current_text("res://'+p+'")')
new=new.replace('else FileAccess.get_file_as_string(path)','else _crew_current_text(path)').replace('else FileAccess.get_sha256(path)','else _crew_current_sha256(path)').replace('assert(floors!=null and floors.get_child_count()==286)','assert(floors!=null and floors.get_child_count()==296)').replace('var children:=floors.get_children();var retained:Array=[]','var children:=_crew_floor_children(floors);var retained:Array=[]');edit(part,new)
edit('value==laundry_current_compiled)','value==laundry_current_compiled or value==crew_current_compiled)')
edit('\tif value==laundry_current_compiled: value=night_current_compiled','\tif value==crew_current_compiled: value=laundry_current_compiled\n\tif value==laundry_current_compiled: value=night_current_compiled')
edit('\t_laundry_validate_runtime(floors.get_parent().get_parent())','\t_crew_validate_runtime(floors.get_parent().get_parent())\n\t_laundry_validate_runtime(floors.get_parent().get_parent())')
block=(R/'predecessor_guard_block.gd').read_text().replace('LAUNDRY','CREW').replace('laundry','crew');block=re.sub('const CREW_PROOF_SHA="[a-f0-9]+"','const CREW_PROOF_SHA="<PROOF_SHA>"',block).replace('packages/crew/','packages/crew_batch/').replace('==286','==296').replace('==284','==286').replace('i<284','i<286')
start=block.index('static func _crew_validate_runtime');block=block[:start]+'''static func _crew_validate_model(wrapper:Node3D,file:String,expected_meshes:int)->void:
\tvar original:Node3D=(load("res://assets/models/"+file)as PackedScene).instantiate()
\tassert(wrapper.get_child_count()==1)
\tvar visual:Node3D=wrapper.get_child(0);assert(visual.transform==original.transform)
\tvar count:=0
\tfor mesh in original.find_children("*","MeshInstance3D",true,false):
\t\tvar actual:MeshInstance3D=visual.get_node(original.get_path_to(mesh))
\t\tassert(actual.transform==mesh.transform and actual.mesh==mesh.mesh and actual.material_override==null)
\t\tvar collision:CollisionShape3D=actual.get_node("StaticContact/SharedShape")
\t\tassert(collision.shape.get_faces()==mesh.mesh.create_trimesh_shape().get_faces());count+=1
\tassert(count==expected_meshes);original.free()
static func _crew_validate_runtime(ship:Node)->void:
\t_crew_ensure()
\tvar data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/crew_batch/runtime_manifest.json"))
\tvar root:Node3D=ship.get_node("ShipSpace/"+str(data.root_name))
\tassert(root.transform==Transform3D.IDENTITY and root.get_child_count()==5 and root.get_meta("operational_acceptance")==false)
\tvar counts:Dictionary={"D03_directory_05":555,"D03_directory_06":576,"D03_directory_07":403,"D03_directory_08":346,"D03_directory_10":817}
\tfor section in data.sections:
\t\tvar room:Node3D=root.get_node(str(section.root_name));assert(room.transform==Transform3D.IDENTITY and room.get_meta("programme_key")==str(section.programme))
\t\tvar wrapper:Node3D=room.get_node("Source");assert(wrapper.transform==Transform3D.IDENTITY)
\t\t_crew_validate_model(wrapper,str(section.model_file),int(counts[section.programme]))
\t\tassert(room.get_child_count()==1+section.mounted_receiving_lights.size())
\t\tvar index:=0
\t\tfor spec in section.mounted_receiving_lights:
\t\t\tvar light:OmniLight3D=room.get_node("MountedSourceFixture_%02d"%index);index+=1
\t\t\tassert(light.position.is_equal_approx(Vector3(spec.position[0],spec.position[1],spec.position[2])))
\t\t\tassert(is_equal_approx(light.light_energy,float(spec.energy))and is_equal_approx(light.omni_range,float(spec.range_m)))
\t\t\tassert(light.light_color.is_equal_approx(Color(spec.color[0],spec.color[1],spec.color[2])))
\t\t\tassert(light.get_meta("source_fixture")==str(spec.fixture_source_name))
\t\t\tvar fixture:MeshInstance3D=wrapper.find_child(str(spec.fixture_runtime_name),true,false)as MeshInstance3D;assert(fixture!=null)
\t\t\tvar center:Vector3=ship.get_node("ShipSpace").to_local(fixture.to_global(fixture.mesh.get_aabb().get_center()))
\t\t\tassert(center.is_equal_approx(Vector3(spec.fixture_center[0],spec.fixture_center[1],spec.fixture_center[2])))
\tvar aft:Node3D=ship.get_node("ShipSpace/Districts/AftPublicCore_WIP/PrimaryCoreEnclosure")
\t_crew_validate_model(aft,"AST-CIR-005_aft_uniforms_d03.glb",9)
# CREW_EXACT_SECTION_END
'''
s+=block
ship=(C/ctx['predecessors'][spath]['retained_path']).read_text();before='\tlighting_budget.configure(self,player)';after='\tload("res://scripts/crew_batch_receiving.gd").build(self)\n'+before;assert ship.count(before)==1;ship=ship.replace(before,after)
for path,text in [(gpath,s),(spath,ship)]:p=C/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
layout=json.loads((C/'data/spatial_layout.json').read_text());compiled=json.loads((C/'data/generated/structural_meshes.json').read_text());proof=dict(schema=1,predecessors=ctx['predecessors'],added_layout=layout['regions'][-10:],added_compiled=compiled['regions'][-10:],inverse_edits={gpath:edits,spath:[dict(before=before,after=after,count=1)],'tools/compile_layout.py':ctx['compiler_inverse_edits'],aft:aft_edits},block_normalized_sha256=hashlib.sha256(block.encode()).hexdigest(),current_sha256={})
paths=[spath,aft,'data/spatial_layout.json','data/generated/structural_meshes.json','docs/LAYOUT_COMPILE_CHECKS.json','tools/compile_layout.py','tools/crew_batch_incremental_preservation.py','data/architecture/packages/crew_batch/CREW_BATCH_COMPILER_PROOF.json','scripts/crew_batch_receiving.gd','assets/models/AST-CIR-005_aft_uniforms_d03.glb','assets/models/AST-CIR-005_spine_core.glb','scripts/primary_atrium_core.gd']
paths +=[str(f.relative_to(C))for f in (C/'data/architecture/crew_batch').rglob('*')if f.is_file()]
paths += ['assets/models/'+item['programme']+'_runtime_names001.glb'for item in json.loads((R/'INTAKE.json').read_text())]
for path in paths:
 if not(C/path).exists():copy(G/path,path)
proof['current_sha256']={f:sha(C/f)for f in paths};q=C/'data/architecture/packages/crew_batch/RUNTIME_PROOF.json';q.write_text(json.dumps(proof,indent=2)+'\n');s=s.replace('const CREW_PROOF_SHA="<PROOF_SHA>"','const CREW_PROOF_SHA="'+sha(q)+'"');(C/gpath).write_text(s)
for path,es in proof['inverse_edits'].items():
 text=(C/path).read_text()
 if path==gpath:text=text[:text.index('# CREW_EXACT_SECTION_BEGIN')]
 for e in es:assert text.count(e['after'])==e['count'],path;text=text.replace(e['after'],e['before'])
 assert text==(C/proof['predecessors'][path]['retained_path']).read_text(),path
print('Crew whole predecessor inverse source proofs pass in isolated staging; no live application')
