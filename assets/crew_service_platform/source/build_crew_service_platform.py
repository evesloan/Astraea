"""Editable AST-STF-010. Parent schedules Blender execution and export.
Consumes actual source boxes only; compiler preview floors are NEVER imported.
"""
from pathlib import Path
import json,sys,math
import bpy,bmesh
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-STF-010'
sys.path.insert(0,str(C/'standards'));import staff_materials
D=json.loads((R/'source/section_contract.json').read_text());parts=json.loads((R/'source/geometry_parts.json').read_text())
assert D['floor_exported'] is False
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats=staff_materials.materials()
for p in parts:
 x0,x1,y0,y1,z0,z1=p['world_aabb'];vs=[(x,-z,y) for y in [y0,y1] for x,z in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]]
 faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 me=bpy.data.meshes.new(p['name']);me.from_pydata(vs,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(p['name'],me);bpy.context.collection.objects.link(ob);me.materials.append(mats[p['role']]);ob['catalogue_id']=AID;ob['source_kind']=p['kind'];ob['collision_contract']='concave_static_surface';ob['floor_owner']='parent compiler; no source floor';ob['cell_x']=math.floor((x0+x1)/40);ob['cell_z']=math.floor((z0+z1)/40)
 uv=me.uv_layers.new(name='MetreScaled');scale=mats[p['role']]['meters_per_tile_uv']
 for f in me.polygons:
  n=f.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized() if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u)
  for li in f.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
# Door and interface datums are empties, never new gates/controllers or collision blockers.
for i,g in enumerate(D['gate_reservations']):
 ob=bpy.data.objects.new('CRW_RESERVED_GATE_%02d'%i,None);bpy.context.collection.objects.link(ob);x,z=g['xz'];ob.location=(x,-z,12);ob['owner']=g['owner'];ob['clear_width_m']=3.6;ob['clear_height_m']=2.65
# Explicit source-backed runtime-light datums, exported as nodes with downward direction.
for i,light in enumerate(D['light_markers']):
 x,y,z=light['xyz']
 housing=next(p for p in parts if p['name'].endswith('_Housing') and abs((p['world_aabb'][0]+p['world_aabb'][1])/2-x)<1e-7 and abs((p['world_aabb'][4]+p['world_aabb'][5])/2-z)<1e-7)
 stem=housing['name'].rsplit('_Housing',1)[0]
 ob=bpy.data.objects.new('CRW_TASK_LIGHT_DATUM_%03d'%i,None);bpy.context.collection.objects.link(ob);ob.location=(x,-z,y);ob.empty_display_type='SINGLE_ARROW';ob.empty_display_size=.2
 ob['catalogue_id']=AID;ob['datum_kind']='supported_staff_task_light';ob['world_direction_godot_xyz']=[0.0,-1.0,0.0];ob['source_housing']=housing['name'];ob['source_supports_json']=json.dumps([stem+'_Hanger0',stem+'_Hanger1']);ob['source_role_family']=light['catalogue_source'];ob['lowest_fixture_y']=light['lowest_y'];ob['controller_owner']='parent runtime light integration; not installed'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'source/AST-STF-010.blend'))
# Export is explicit opt-in after parent has reserved the serial engine slot.
if '--export' in sys.argv:
 (R/'exports').mkdir(exist_ok=True)
 bpy.ops.export_scene.gltf(filepath=str(R/'exports/AST-STF-010.glb'),export_format='GLB',export_extras=True,export_yup=True,export_cameras=False,export_lights=False)
print('Editable source saved; no compiler floors or dynamic hardware authored')
