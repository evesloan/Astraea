"""Blender4.3.2 isolated native authoring; no changes to retained source assets."""
from pathlib import Path
import bpy
import json
import hashlib
from mathutils import Vector

P=Path(__file__).resolve().parent
D=P.parent
plan=json.loads((D/'MEMBERS.json').read_text())
assert bpy.app.version[:3]==(4,3,2)
assert not plan['production_adoption']
catalogue=(P.parents[2]/'catalogue_manifest.json').read_text()
houses=sorted({row['house'] for row in plan['regions']})
for house in houses:
    assert ('APPROVED_RECEIVER_'+house+'_r003') not in catalogue
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
material=bpy.data.materials.new('Receiver_dark_zinc');material.use_nodes=True
shader=material.node_tree.nodes.get('Principled BSDF')
shader.inputs['Base Color'].default_value=(.18,.20,.21,1)
shader.inputs['Roughness'].default_value=.76
objects={house:[] for house in houses}
def prism(name, start,end, u0,u1,v0,v1,house,role):
    a,b=Vector(start),Vector(end);direction=b-a
    if direction.length<1e-6:return
    direction.normalize()
    cross=Vector((0,1,0)) if abs(direction.y)<.9 else Vector((1,0,0))
    u=direction.cross(cross).normalized();v=u.cross(direction).normalized()
    corners=[a+u*u0+v*v0,a+u*u1+v*v0,a+u*u1+v*v1,a+u*u0+v*v1,
             b+u*u0+v*v0,b+u*u1+v*v0,b+u*u1+v*v1,b+u*u0+v*v1]
    coords=[(p.x,-p.z,p.y) for p in corners]
    # Rotation from world XYZ to Blender X,-Z,Y preserves orientation.
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(coords,[],[tuple(reversed(face)) for face in faces]);mesh.update()
    center=sum((vertex.co for vertex in mesh.vertices),Vector())/len(mesh.vertices)
    assert all(poly.normal.dot(poly.center-center)>0 for poly in mesh.polygons),name
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material);obj['receiver_role']=role
    objects[house].append(obj)

for row in plan['regions']:
    profile=row['profile'];width=profile['width'];depth=profile['depth']
    flange=profile['flange_thickness'];web=profile['web_thickness']
    for member in row['members']:
        name=row['region_id']+'_'+member['name'];house=row['house'];role=member['role']
        if role=='same_unit_post':
            prism(name,member['a'],member['b'],-.12,.12,-.12,.12,house,role)
        else:
            for suffix,u0,u1,v0,v1 in [('lower_flange',-width/2,width/2,-depth/2,-depth/2+flange),
                                      ('web',-web/2,web/2,-depth/2+flange,depth/2-flange),
                                      ('upper_flange',-width/2,width/2,depth/2-flange,depth/2)]:
                prism(name+'_'+suffix,member['a'],member['b'],u0,u1,v0,v1,house,role)
# Bounded new collars contain each exact primary surface witness positively.
# This is an architectural connection, without fastener or capacity certification.
for row in plan['regions']:
    for index,anchor in enumerate(row['source_surface_anchors']):
        if 'source_model' not in anchor:continue
        point=Vector((anchor['surface_point_xz'][0],row['floor_y']-.52,anchor['surface_point_xz'][1]))
        direction=point-Vector(anchor['slab_attachment_xyz'])
        if direction.length<1e-6:direction=Vector((1,0,0))
        direction.normalize()
        prism(row['region_id']+'_primary_collar_'+str(index),point-direction*.08,point+direction*.08,
              -.21,.21,-.29,.29,row['house'],'positive_primary_surface_collar')

native=D/'source';native.mkdir(exist_ok=True)
export=D/'exports';export.mkdir(parents=True,exist_ok=True)
bpy.data.texts.new('MEMBERS.json').write(json.dumps(plan,indent=2))
manifest=[]
def export_house(house, destination):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects[house]:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[house][0]
    bpy.ops.export_scene.gltf(filepath=str(destination),export_format='GLB',export_yup=True,
                               use_selection=True,export_extras=True)
for house in houses:
    file='APPROVED_RECEIVER_'+house+'_r003.glb';path=export/file
    export_house(house,path)
    b=path.read_bytes();manifest.append({'house':house,'file':file,'bytes':len(b),
                                        'sha256':hashlib.sha256(b).hexdigest(),'meshes':len(objects[house])})
native_file=native/'APPROVED_SIX_HOUSE_RECEIVERS_r003.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(native_file))
object_names={house:[obj.name for obj in original] for house,original in objects.items()}
bpy.ops.wm.open_mainfile(filepath=str(native_file))
objects={house:[bpy.data.objects[name] for name in names] for house,names in object_names.items()}
fresh=D/'fresh_native_reexport';fresh.mkdir(exist_ok=True)
for row in manifest:
    q=fresh/row['file'];export_house(row['house'],q)
    assert hashlib.sha256(q.read_bytes()).hexdigest()==row['sha256'],row['file']
receipt={'status':'PASS_NATIVE_SAVE_FRESH_REEXPORT_EXACT_BYTES_NOT_INSTALLED',
         'blender_version':bpy.app.version_string,'native_file':str(native_file),
         'native_sha256':hashlib.sha256(native_file.read_bytes()).hexdigest(),
         'models':manifest,'source_regions':87,'same_unit_upper_posts':10,
         'production_adoption':False,'contact_clearance_or_capacity_accepted':False}
(D/'NATIVE_EXPORT_VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_NATIVE_RECEIVER_EXPORT six_models=',len(manifest),'meshes=',sum(r['meshes'] for r in manifest))
