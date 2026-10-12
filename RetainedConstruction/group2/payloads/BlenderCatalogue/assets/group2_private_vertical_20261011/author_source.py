"""Five editable private cabin/gate kits and held pit receiver source meshes."""
import bpy, bmesh, hashlib, json, math, pathlib, argparse, sys
from mathutils import Matrix, Vector
ROOT = pathlib.Path(__file__).resolve().parents[3]
P = pathlib.Path(__file__).resolve().parent
data = json.loads((ROOT / 'Game/data/group2_private_vertical/INTERFACES.json').read_text())
parser=argparse.ArgumentParser();parser.add_argument('--revision',default='r002')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--'in sys.argv else [])
for rel, expected in data['dependency_pins'].items():
    assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == expected
bpy.ops.wm.read_factory_settings(use_empty=True)
material = bpy.data.materials.new('PrivatePit_warm_stone_source')
material.diffuse_color = (.53, .49, .43, 1)
material.use_nodes = True
material.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.53,.49,.43,1)
material.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .86
pit_objects = []
components = []
def append_source(rel, label, origin, yaw):
    path = ROOT / rel
    with bpy.data.libraries.load(str(path), link=False) as (available, requested):
        requested.objects = available.objects
    loaded = [o for o in requested.objects if o]
    for obj in loaded:
        bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.update()
    transform = Matrix.Translation(Vector((origin[0], -origin[2], origin[1]))) @ Matrix.Rotation(yaw, 4, 'Z')
    before = {o: o.matrix_world.copy() for o in loaded}
    assert abs(transform.to_3x3().determinant()-1) < 1e-5  # Blender Matrix uses float32.
    for obj in loaded:
        if obj.parent not in loaded:
            obj.matrix_world = transform @ before[obj]
        obj.name = label + '_' + obj.name
        obj['retained_source_sha256'] = data['dependency_pins'][rel]
    components.append({'label':label,'source':rel,'source_sha256':data['dependency_pins'][rel],
                       'origin_world':origin,'proper_yaw':yaw,'objects':len(loaded),'rigid_transform_only':True})

for row in data['suites']:
    key = str(row['source_index']); assert key != '790'
    origin = row['origin_world']; yaw = row['cabin_yaw']
    append_source('BlenderCatalogue/assets/commons_lift_cabin/source/AST-CIR-003.blend',
                  'G2V_'+key+'_Cabin', origin, yaw)
    # Landing mounting successor clears the actual shaft front; cabin gate remains12cm inward.
    into = Vector((-math.sin(yaw), 0, -math.cos(yaw)))
    for stop in row['stops_y']:
        offset=row['landing_gate_outward_mount_m']
        gate_origin = [origin[0]-offset*into.x, stop, origin[2]-offset*into.z]
        append_source('BlenderCatalogue/assets/telescoping_gate/source/AST-DOR-003.blend',
                      'G2V_'+key+'_Landing_'+str(stop), gate_origin, yaw+math.pi)
    append_source('BlenderCatalogue/assets/telescoping_gate/source/AST-DOR-003.blend',
                  'G2V_'+key+'_CabinGate', [origin[0]+.12*into.x,102,origin[2]+.12*into.z],yaw+math.pi)
    outline = row['pit_outline_xz']; top=row['pit_receiver_top_y']; bottom=top-row['pit_receiver_thickness']
    vertices = [(p[0],-p[1],h) for h in [bottom,top] for p in outline]
    n=len(outline);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
    mesh=bpy.data.meshes.new('G2V_'+key+'_PitReceiver');mesh.from_pydata(vertices,[],faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0
    bm.to_mesh(mesh);bm.free()
    obj=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(obj);mesh.materials.append(material)
    obj['source_index']=row['source_index'];obj['status']='HELD lower-neighbour/support interface; no live slab cut'
    pit_objects.append((key,obj))
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.file.pack_all()
native=P/'source'/('PRIVATE_VERTICAL_KITS_'+args.revision+'.blend');assert not native.exists()
bpy.ops.wm.save_as_mainfile(filepath=str(native))
exports=[]
for key,obj in pit_objects:
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    export=ROOT/'Game/assets/group2_private_vertical'/('PIT_'+key+'_r001.glb');export.parent.mkdir(parents=True,exist_ok=True)
    if export.exists():
        previous=json.loads((P/'evidence/SOURCE_NATIVE_r001.json').read_text())
        assert hashlib.sha256(export.read_bytes()).hexdigest()==next(r['sha256']for r in previous['pit_receivers']if r['source_index']==int(key))
    else:
        bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
    exports.append({'source_index':int(key),'path':str(export.relative_to(ROOT)),
                    'sha256':hashlib.sha256(export.read_bytes()).hexdigest()})
for rel,expected in data['dependency_pins'].items():
    assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==expected
receipt={'pass':True,'five_private_suites':[r['source_index']for r in data['suites']],
         'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'components':components,
         'pit_receivers':exports,'closed_manifold_positive_pit_volumes':True,
         'retained_originals_unchanged':True,'new_catalogue_ids':0,'790_excluded':True,
         'installed_or_engineering_acceptance':False}
(P/'evidence'/('SOURCE_NATIVE_'+args.revision+'.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS five rigid original cabin kits,15 original gates, five held closed pit receivers')
