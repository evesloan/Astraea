"""Save one portable linked500 application. No repeated mesh export or Game writes."""
from pathlib import Path
import bpy,json,hashlib,runpy
S=Path(__file__).resolve().parents[1];M=S/'assemblies/GODOT_BATCH_INSTANCE_MAP.json';data=json.loads(M.read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
before={p:sha(p)for p in (S/'outputs/production_r011').glob('*/assembly.blend')}
# A native source export of exactly the books that the actual assemblies contain.
rows=[]
for key,prototype in data['prototypes'].items():
 source=S/prototype['source_blend'];bpy.ops.wm.open_mainfile(filepath=str(source));dest=source.parent/'detail_props.glb';assert not dest.exists()
 bpy.ops.object.select_all(action='DESELECT');names=[]
 for ob in bpy.context.scene.objects:
  if ob.type=='MESH'and ob.name.startswith(('SUI_DeskBook_','SUI_TableBook_')):ob.select_set(True);names.append(ob.name)
 assert 5<=len(names)<=7
 bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
 prototype['detail_props_glb']=str(dest.relative_to(S));prototype['detail_props_glb_sha256']=sha(dest)
 rows.append({'source_recipe_key':key,'source_sha256':before[source],'parts':names,'export_sha256':sha(dest),'source_unchanged':sha(source)==before[source]})
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
collections={};sections={}
for key,prototype in data['prototypes'].items():
 source=S/prototype['source_blend']
 with bpy.data.libraries.load(str(source),link=True)as(src,dst):dst.objects=list(src.objects)
 col=bpy.data.collections.new('SharedRecipe_'+key)
 for ob in dst.objects:
  if ob is not None and ob.type in ['MESH','EMPTY','CURVE']:col.objects.link(ob)
 collections[key]=col
for r in data['instances']:
 key=r['section_id']
 if key not in sections:
  col=bpy.data.collections.new(key);scene.collection.children.link(col);sections[key]=col
 ob=bpy.data.objects.new(r['rebuild_identity'],None);ob.instance_type='COLLECTION';ob.instance_collection=collections[r['source_recipe_key']]
 x,y,z=r['source_origin_world_xyz'];ob.location=(x,-z,y);ob.rotation_euler.z=r['source_yaw_godot'];sections[key].objects.link(ob)
 ob['census_source_index']=r['census_source_index'];ob['source_recipe_key']=r['source_recipe_key'];ob['view_target_id']=r['view_target_id'];ob['outlook_status']=r['outlook_construction_status'];ob['runtime_adoption_ready']=False
 r['source_detail_props_layer']=data['prototypes'][r['source_recipe_key']]['detail_props_glb']
scene['source_scope']='498source projections in18sections,2already-installed rooms protected separately. All500current identities/1300rests remain. Per-unit receiving/outlook validation required.'
scene['current_application_sha256']=sha(S/'RESIDENTIAL_500_CURRENT_APPLICATION.json')
output=S/'assemblies/Astraea_500_domestic_current_portable.blend';assert not output.exists()
for lib in bpy.data.libraries:lib.filepath=bpy.path.relpath(lib.filepath,start=str(output.parent))
bpy.ops.wm.save_as_mainfile(filepath=str(output))
assert len(sections)==18 and sum(len(c.objects)for c in sections.values())==498
for source,digest in before.items():assert sha(source)==digest
# Reopen actual saved assembly; verify link locations and exact instantiated counts.
bpy.ops.wm.open_mainfile(filepath=str(output));libs=[]
for lib in bpy.data.libraries:
 assert lib.filepath.startswith('//');resolved=Path(bpy.path.abspath(lib.filepath));assert resolved.is_file();libs.append({'relative':lib.filepath,'sha256':sha(resolved)})
actual={o.name:o for o in bpy.context.scene.objects if o.instance_type=='COLLECTION'};assert len(actual)==498
for row in data['instances']:
 o=actual[row['rebuild_identity']];x,y,z=row['source_origin_world_xyz'];assert max(abs(a-b)for a,b in zip(o.location,(x,-z,y)))<2e-5;assert abs(o.rotation_euler.z-row['source_yaw_godot'])<1e-6
M.write_text(json.dumps(data,indent=2)+'\n')
for section in sections:
 file=S/'assemblies'/(section+'.json');d=json.loads(file.read_text());d['instances']=[r for r in data['instances']if r['section_id']==section];file.write_text(json.dumps(d,indent=2)+'\n')
report={'status':'PASS_SAVED_PORTABLE_498_INSTANCE_18_SECTION_SOURCE','new_instances':498,'protected_installed':2,'recipes':18,'sections':{key:sum(r['section_id']==key for r in data['instances'])for key in sections},'portable_assembly_sha256':sha(output),'portable_assembly_bytes':output.stat().st_size,'actual_relative_libraries':libs,'detail_layers':rows,'all18sources_unchanged':True,'runtime_adoption':False,'game_or_catalogue_writes':False,'no_duplicate_mass_mesh_export':True}
(S/'qa/PORTABLE_SOURCE_ASSEMBLY.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(actual))
