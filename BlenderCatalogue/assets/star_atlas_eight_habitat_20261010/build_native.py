from pathlib import Path
import bpy,json,math,hashlib,shutil,bmesh
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PHYSICAL_PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda v:(v[0],-v[2],v[1]);records=[]
current=json.load(open(W/'ALLOCATION_PROPOSAL.json'))
for room in P['rooms']:
 revised=next(r for r in current['rooms']if r['source_envelope_index']==room['source_envelope_index'])
 for key in ['proposed_design_species','design_species_assignment','design_choice_status','alien_body_compatibility_accepted']:
  if key in revised:room[key]=revised[key]
for ref in P['references']:
 if ref['key']=='AST-RST-LN-001':ref['proposed_design_species']='';ref['status']='Generic measured low-rest construction reference; canonical species and alien compatibility unassigned'
P['proposed_choices']=current['proposed_choices'];P['allocation_reconciliation']=current['allocation_reconciliation']
for k,h in P['source_pins'].items():assert sha(R/'Game/assets/models'/(k+'.glb'))==h
manifest=json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'))
for k in P['source_pins']:assert sum(a.get('catalogue_id')==k for a in manifest['assets'])==1
palette={'ivory_enamel':(.78,.73,.63,1),'warm_walnut':(.25,.12,.065,1),'teal_weave':(.09,.25,.23,1)}
def material(role):
 name='EightHabitat_'+role
 if name in bpy.data.materials:return bpy.data.materials[name]
 m=bpy.data.materials.new(name);m.diffuse_color=palette[role];m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=palette[role];bs.inputs['Roughness'].default_value=.75
 files=sorted((R/'Game/assets/models').glob('*_'+role+'.png'))
 if files:
  tx=m.node_tree.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(files[0]),check_existing=True);tx.image.pack();tx.interpolation='Closest';m.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
 return m
def mesh(q):
 me=bpy.data.meshes.new(q['name']);me.from_pydata([B(v)for v in q['verts']],[],q['faces']);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(material(q['material']));uv=me.uv_layers.new(name='MetreScaled')
 for f in me.polygons:
  n=f.normal;u=Vector((1,0,0))if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for li in f.loop_indices:co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co.dot(u),co.dot(v))
 ob=bpy.data.objects.new(q['name'],me);bpy.context.collection.objects.link(ob);ob['runtime_collision']=q['runtime_collision'];ob['physical_plan_sha256']=sha(W/'PHYSICAL_PLAN.json');ob['material_role']=q['material'];return ob
def export(label,objs=None):
 native=W/(label+'.blend');glb=W/(label+'.glb');bpy.ops.file.pack_all();bpy.context.preferences.filepaths.save_version=0
 if objs is not None:
  bpy.ops.object.select_all(action='DESELECT')
  for o in objs:o.select_set(True)
 bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
 bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_extras=True,use_selection=objs is not None);first=sha(glb);bpy.ops.wm.open_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_extras=True,use_selection=objs is not None);assert first==sha(glb);shutil.copy2(glb,R/'Game/assets/models'/glb.name);return {'native':native.name,'native_sha256':sha(native),'export':glb.name,'export_sha256':first,'fresh_native_repeat_identical':True}
bpy.ops.wm.read_factory_settings(use_empty=True);shells=[mesh(q)for q in P['parts']];records.append(export('StarAtlasEightHabitatFittings',shells))
for ref in P['references']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 for q in ref['parts']:mesh(q)
 record=export('StarAtlasBodyFit_'+ref['key']);ref['model_sha256']=record['export_sha256'];ref['native_sha256']=record['native_sha256'];records.append(record)
# Preserve complete editable per-room derivative assemblies; original exports are not replaced.
for room in P['rooms']:
 idx=room['source_envelope_index'];old=R/'BlenderCatalogue/assets'/('star_atlas_specialty_first_20261010'if idx<461 else'star_atlas_specialty_second_20261010')/f'StarAtlasSpecialty_{idx}.blend';oldsha=sha(old);bpy.ops.wm.open_mainfile(filepath=str(old))
 for name in room.get('remove_source_meshes',[]):
  assert name in bpy.data.objects;ob=bpy.data.objects[name];bpy.data.objects.remove(ob,do_unlink=True)
 for q in P['parts']:
  if q['name'].startswith(f'SA{idx}_'):mesh(q)
 rest=room['rest_source'];cy,sy=math.cos(rest['yaw']),math.sin(rest['yaw']);at=lambda v:[rest['position'][0]+v[0]*cy+v[2]*sy,rest['position'][1]+v[1],rest['position'][2]-v[0]*sy+v[2]*cy]
 for i,c in enumerate(room.get('wet_cells_local',[])):
  ob=mesh({'name':f'SA{idx}_WetQueryCell_{i:03d}','verts':[at(v)for v in c['vertices']],'faces':c['faces'],'material':'teal_weave','runtime_collision':False});ob.hide_render=True;ob.hide_set(True);ob['purpose']='Nonblocking volume detector source; never drawn water or solid contact'
 bpy.context.scene['habitat_body_status']='Proposed design species plus measured construction body reference; canonical actors/rigs/animations/operations not accepted';bpy.context.scene['original_native_sha256']=oldsha;bpy.context.scene['plan_sha256']=sha(W/'PHYSICAL_PLAN.json');bpy.ops.file.pack_all();native=W/f'StarAtlasHabitatAssembly_{idx}.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);assert sha(old)==oldsha;room['assembly_native']=native.name;room['assembly_native_sha256']=sha(native)
P['runtime_model_sha256']=records[0]['export_sha256'];P['native_exports']=records
# Runtime data excludes authoring triangle arrays/body parts; exact native source retains them.
runtime={k:v for k,v in P.items()if k not in ['parts','references']};runtime['references']=[{k:v for k,v in ref.items()if k not in ['parts','support_top_triangles']}for ref in P['references']];runtime['status']='physical_construction_pending_engine_witnesses';runtime['plan_sha256']=sha(W/'PHYSICAL_PLAN.json')
(W/'RUNTIME_HABITATS.json').write_text(json.dumps(runtime,indent=2)+'\n');(R/'Game/data/architecture/STAR_ATLAS_EIGHT_HABITATS.json').write_text(json.dumps(runtime,indent=2)+'\n');(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','blender_version':bpy.app.version_string,'exports':records,'assembly_native_count':8,'original_sources_unchanged':True,'no_new_catalogue_id':True,'body_status':'measured original construction rest references, no canonical species-body or animation acceptance'},indent=2)+'\n');print('HABITAT_NATIVE_PASS',len(records),flush=True)
