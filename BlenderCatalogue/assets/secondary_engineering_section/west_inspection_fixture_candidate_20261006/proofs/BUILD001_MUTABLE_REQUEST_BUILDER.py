"""Unexecuted source-only builder. Requires a later parent-allocated Blender slot.
Adds one supported fixture representation; never changes any retained input.
"""
from pathlib import Path
import json,hashlib,math
import bpy,bmesh
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
assert str(R)=='/workspace/scratch/375c2e438292/engineering-west-fixture-candidate-20261006'
PINS=json.loads((R/'INPUT_PINS.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in PINS.items():assert sha(Path(p))==h,p
SOURCE=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/secondary_engineering_section/source/AST-ENG-008.blend')
blend=R/'source/AST-ENG-008_west_inspection_fixture.blend';glb=R/'exports/AST-ENG-008_west_inspection_fixture.glb'
assert not blend.exists() and not glb.exists(),'Preserve every surviving output; use a reviewed new iteration, never overwrite'
(R/'exports').mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
names=['plant_inspection_n_mount','plant_inspection_n_housing','plant_inspection_n_opal','plant_inspection_n_ceiling_stem']
with bpy.data.libraries.load(str(SOURCE),link=False) as (src,dst):
 assert all(n in src.objects for n in names)
 dst.objects=names
objects={o.name:o for o in dst.objects};assert set(objects)==set(names)
def cv(p):return Vector((p[0],-p[2],p[1]))
def mesh_pin(me):
 value={'v':[list(v.co) for v in me.vertices],'polygons':[list(p.vertices) for p in me.polygons],'uv':{layer.name:[list(v.uv) for v in layer.data] for layer in me.uv_layers},'materials':[m.name for m in me.materials]}
 return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
old=cv((31,10.225,-437));new=cv((25.55,9.5,-432));T=Matrix.Translation(new)@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Translation(-old)
parts=[];preservation=[]
for name in names[:3]:
 ob=objects[name];before=mesh_pin(ob.data);assert ob.type=='MESH' and ob.parent is None
 bpy.context.collection.objects.link(ob);ob.matrix_world=T@ob.matrix_world;ob.name='WEST_'+name.removeprefix('plant_inspection_n_')
 ob['catalogue_id']='AST-ENG-008';ob['representation']='west_front_fixture_candidate';ob['collision_contract']='static_surface';ob['source_parent_object']=name
 assert mesh_pin(ob.data)==before
 preservation.append({'original_object':name,'new_object':ob.name,'local_mesh_topology_uv_material_pin_unchanged':before})
 parts.append(ob)
# The new, explicitly extended stem uses the retained stem material and fresh
# metre-scaled UVs, not a stretched old texture or a floating light source.
donor=objects[names[3]];assert len(donor.data.materials)==1;material=donor.data.materials[0];tile=material.get('meters_per_tile_uv');assert tile is not None and len(tile)==2
bpy.data.objects.remove(donor,do_unlink=True)
x,y,z,X,Y,Z=(25.515,9.735,-432.035,25.585,10.48,-431.965)
vertices=[(x,y,z),(X,y,z),(X,y,Z),(x,y,Z),(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)]
faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
me=bpy.data.meshes.new('WEST_CapStem');me.from_pydata([cv(v) for v in vertices],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(material)
layer=me.uv_layers.new(name='MetreScaled')
for face in me.polygons:
 n=face.normal;u=Vector((1,0,0)) if abs(n.x)<.7 else Vector((0,1,0));u=(u-n*u.dot(n)).normalized();v=n.cross(u)
 for li in face.loop_indices:
  point=me.vertices[me.loops[li].vertex_index].co;layer.data[li].uv=(point.dot(u)/float(tile[0]),point.dot(v)/float(tile[1]))
stem=bpy.data.objects.new('WEST_CapStem',me);bpy.context.collection.objects.link(stem);stem['catalogue_id']='AST-ENG-008';stem['representation']='west_front_fixture_candidate';stem['collision_contract']='static_surface';stem['support_owner']='retained containment_cap undersideY10.48';parts.append(stem)
marker=bpy.data.objects.new('DATUM_plant_west_front',None);bpy.context.collection.objects.link(marker);marker.location=new;marker.empty_display_type='PLAIN_AXES';marker['fixture_source']=True;marker['emitter_offset_y_m']=-.08;marker['trial_aim_xyz']=[26.22,8.05,-432];marker['trial_range_m']=4.0;marker['trial_half_cone_degrees']=32.0;marker['energy_approved']=False
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene['scope']='Additional source fixture candidate only; original9fixtures unchanged; source selection, energy and full visual acceptance unapproved'
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows=[]
for ob in parts:
 evaluated=ob.evaluated_get(dg);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();points=[ob.matrix_world@v.co for v in mesh.vertices];godot=[(v.x,v.z,-v.y) for v in points];bounds=[min(v[i] for v in godot) for i in range(3)]+[max(v[i] for v in godot) for i in range(3)]
 rows.append({'name':ob.name,'bounds_xyz':bounds,'triangles':len(mesh.loop_triangles),'material_names':[m.name for m in ob.data.materials]});evaluated.to_mesh_clear()
assert len(rows)==4
bounds={row['name']:row['bounds_xyz'] for row in rows}
assert abs(bounds['WEST_CapStem'][4]-10.48)<1e-5
assert abs(bounds['WEST_CapStem'][1]-bounds['WEST_mount'][4])<1e-5
for a,b in [('WEST_mount','WEST_housing'),('WEST_housing','WEST_opal')]:assert abs(bounds[a][1]-bounds[b][4])<1e-5
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for ob in parts+[marker]:ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_apply=True,export_cameras=False,export_lights=False)
for p,h in PINS.items():assert sha(Path(p))==h,p
receipt={'stage':'Source build only; independent reload/export/rays/runtime/render still required','source_sha256':sha(blend),'export_sha256':sha(glb),'parts':rows,'marker_xyz':[25.55,9.5,-432],'emitter_xyz':[25.55,9.42,-432],'local_donor_geometry_uv_material_preservation':preservation,'retained_input_hashes_unchanged':True,'existing_fixtures_replaced':0,'new_authored_fixture_sources':1,'exported_lights':0,'central_disc_scope':'49prior planned rays sample central0.65m-radius disc only to0.59m, not entire1.73m-profile endcap','limits':['Source fixture selection under8/32 budget unverified','Energy unapproved','No complete endcap/department first-pass acceptance','No live runtime/source registry adoption']}
(R/'qa/SOURCE_BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n');print('WEST_FIXTURE_SOURCE_BUILD_ONLY',len(rows),sum(r['triangles'] for r in rows))
