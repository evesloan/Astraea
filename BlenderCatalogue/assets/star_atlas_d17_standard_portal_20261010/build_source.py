from pathlib import Path
import bpy, json, hashlib, sys
from mathutils import Vector

W = Path(__file__).resolve().parent
R = W.parents[2]
P = json.loads((W / 'PLAN.json').read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
B = lambda p: (p[0], -p[2], p[1])
for p, h in P['source_pins'].items():
    assert sha(R / p) == h, p
bpy.ops.wm.read_factory_settings(use_empty=True)
old = R / 'BlenderCatalogue/assets/star_atlas_upper_commons_20261009/source/StarAtlasUpperCommons.blend'
with bpy.data.libraries.load(str(old), link=False) as (a, b):
    assert 'SA_D17_SouthWall_0' in a.objects
    b.objects = ['SA_D17_SouthWall_0']
original = b.objects[0]
bpy.context.collection.objects.link(original)
expected = sorted(tuple(B(v)) for v in P['preimage_wall']['verts'])
actual = sorted(tuple(v.co) for v in original.data.vertices)
assert len(actual) == len(expected)
assert max(abs(a-b) for v,q in zip(actual, expected) for a,b in zip(v,q)) < .00003
material = original.data.materials[0]
bpy.data.objects.remove(original, do_unlink=True)

faces = [[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
parts = []
def cube(name, lo, hi):
    x,y,z = lo; X,Y,Z = hi
    vs = [(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)]
    me = bpy.data.meshes.new(name)
    me.from_pydata([B(v) for v in vs], [], faces)
    me.update(); me.materials.append(material)
    uv = me.uv_layers.new(name='MetreScaled')
    for f in me.polygons:
        n = f.normal
        u = Vector((1,0,0)) if abs(n.z) > .7 else Vector((-n.y,n.x,0)).normalized()
        v = n.cross(u)
        for li in f.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (co.dot(u),co.dot(v))
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    ob['runtime_collision'] = True
    ob['retained_preimage'] = 'SA_D17_SouthWall_0'
    ob['adoption_status'] = 'held_until_supported_onward_route'
    ob['source_plan_sha256'] = sha(W/'PLAN.json')
    parts.append({'name':name,'min':lo,'max':hi})
    return ob
wall = [
    cube('D17_StandardPortal_WestRetainedWall',[-97,102,13.78],[-65.79,106.26,14]),
    cube('D17_StandardPortal_EastRetainedWall',[-64.21,102,13.78],[-63,106.26,14]),
    cube('D17_StandardPortal_RetainedHeader',[-65.79,104.50,13.78],[-64.21,106.26,14]),
]
# Reuse the exact registered editable door. Native review contains the complete
# fitting; production replacement-wall export excludes the separate controller.
door_path = R/'BlenderCatalogue/assets/guest_entry_door/source/AST-DOR-002.blend'
with bpy.data.libraries.load(str(door_path),link=False) as (a,b):
    b.objects = a.objects
doors = [o for o in b.objects if o]
before = {o.name: [tuple(v.co) for v in o.data.vertices] for o in doors if o.type == 'MESH'}
for o in doors:
    bpy.context.collection.objects.link(o)
roots = [o for o in doors if o.parent not in doors]
for o in roots:
    o.location += Vector(B(P['door_origin']))
for o in doors:
    o['retained_door_source_sha256'] = sha(door_path)
    o['adoption_status'] = 'source_only'
bpy.context.view_layer.update()
door_points = [o.matrix_world @ v.co for o in doors if o.type == 'MESH' for v in o.data.vertices]
gpoints = [(v.x,v.z,-v.y) for v in door_points]
bounds = {'min':[min(v[i] for v in gpoints) for i in range(3)],'max':[max(v[i] for v in gpoints) for i in range(3)]}
assert abs(bounds['min'][0]+66.74)<.00003 and abs(bounds['max'][0]+63.26)<.00003, bounds
assert bounds['max'][2] > 14, 'Do not hide the missing onward support dependency'
for name,vs in before.items():
    assert [tuple(v.co)for v in bpy.data.objects[name].data.vertices] == vs
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.file.pack_all()
native = W/'StarAtlasD17StandardPortal.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
def export():
    bpy.ops.object.select_all(action='DESELECT')
    for o in wall: o.select_set(True)
    bpy.context.view_layer.objects.active=wall[0]
    bpy.ops.export_scene.gltf(filepath=str(W/P['receiving_model']),export_format='GLB',use_selection=True,export_extras=True,export_yup=True)
export(); export_hash=sha(W/P['receiving_model'])
bpy.ops.wm.open_mainfile(filepath=str(native))
wall=[bpy.data.objects[p['name']]for p in parts]
export(); assert sha(W/P['receiving_model'])==export_hash
for name,vs in before.items(): assert [tuple(v.co)for v in bpy.data.objects[name].data.vertices] == vs
sys.path.insert(0,str(R/'Game/tools'))
from validate_production_glb import validate_and_copy
validate_and_copy(W/P['receiving_model'],R/'Game/assets/models'/P['receiving_model'])
old_volume=34*4.26*.22
cut_volume=1.58*2.50*.22
volume=sum((p['max'][0]-p['min'][0])*(p['max'][1]-p['min'][1])*(p['max'][2]-p['min'][2])for p in parts)
assert abs(volume+cut_volume-old_volume)<1e-8
for p,h in P['source_pins'].items(): assert sha(R/p)==h,p
rec={'status':'PASS','scope':'Editable source-only standard receiving doorway, not adopted','native_sha256':sha(native),'export_sha256':export_hash,'replacement_parts':parts,'removed_wall_volume_m3':cut_volume,'retained_wall_volume_m3':volume,'preimage_vertex_count':len(actual),'door_source_meshes_exact':len(before),'door_world_bounds':bounds,'source_pins_unchanged':True,'fresh_native_repeat_export_identical':True,'new_floor_area_m2':0,'actual_main_wall_changed':False,'adoption_status':'HOLD_MISSING_ONWARD_FLOOR_SUPPORT','limits':P['adoption_gates']}
(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps({k:rec[k]for k in ['status','replacement_parts','door_source_meshes_exact','door_world_bounds','actual_main_wall_changed']}))
