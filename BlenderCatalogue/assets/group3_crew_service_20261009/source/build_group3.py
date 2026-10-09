"""Editable source and compact native export; never changes shared manifests."""
from pathlib import Path
import bpy, bmesh, json, hashlib, sys
from mathutils import Vector

HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[2]
CAT=ROOT/'BlenderCatalogue'
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
spec_path=HERE/'source'/(args[0] if args else 'CREW_BANK_HOME.json')
spec=json.loads(spec_path.read_text()); asset=spec['catalogue_id']
catalogue=json.loads((CAT/'catalogue_manifest.json').read_text())
assert not any(r['catalogue_id']==asset and r.get('family')!='group3_crew_service_20261009' for r in catalogue['assets'])
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version=0
defs=json.loads((CAT/'materials/staff/manifest.json').read_text())['materials']; mats={}
def mat(role):
    if role in mats:return mats[role]
    row=defs[role];m=bpy.data.materials.new(role);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=row['roughness'];bs.inputs['Metallic'].default_value=row['metallic']
    bs.inputs['Base Color'].default_value=tuple(v/255 for v in row['colour_srgb_8bit'])+(1,)
    tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.interpolation='Closest'
    tex.image=bpy.data.images.load(str(CAT/'materials/staff'/row['file']),check_existing=True);tex.image.pack()
    m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    m.diffuse_color=tuple(v/255 for v in row['colour_srgb_8bit'])+(1,);mats[role]=m;return m
def gv(x,y,z):return(x,-z,y)
for p in spec['parts']:
    if 'aabb' in p:
        x0,x1,y0,y1,z0,z1=p['aabb']
        verts=[gv(x,y,z) for y in [y0,y1] for z in [z0,z1] for x in [x0,x1]]
        faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    else:
        verts=[];faces=[];lo,hi=p['y']
        for tri in p['triangles']:
            k=len(verts);verts.extend([gv(x,lo,z)for x,z in tri]+[gv(x,hi,z)for x,z in tri]);faces.extend([(k+2,k+1,k),(k+3,k+4,k+5)])
        for ring in [p['boundary']]+p['holes']:
            for a,b in zip(ring,ring[1:]+ring[:1]):
                k=len(verts);verts.extend([gv(a[0],lo,a[1]),gv(b[0],lo,b[1]),gv(b[0],hi,b[1]),gv(a[0],hi,a[1])]);faces.append((k,k+1,k+2,k+3))
    me=bpy.data.meshes.new(p['name']);me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(p['name'],me);bpy.context.collection.objects.link(o)
    o['role']=p['role'];o['category']=p.get('category','architecture');o['source_asset']=asset;o['construction_wip']=True
    o['batch_cell']=p.get('batch_cell','room')
    me.materials.append(mat(p['role']))
    uv=me.uv_layers.new(name='MetricUV')
    tile=defs[p['role']]['meters_per_tile_uv']
    for poly in me.polygons:
        axes=[i for i in range(3) if i!=max(range(3),key=lambda a:abs(poly.normal[a]))]
        for li in poly.loop_indices:
            v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]/tile[0],v[axes[1]]/tile[1])
for f in spec.get('fixtures',[]):
    o=bpy.data.objects.new(f['name'],None);o.location=gv(*f['position']);o['receiving_fixture']=True;bpy.context.collection.objects.link(o)
for d in spec.get('door_proposals',[]):
    o=bpy.data.objects.new('DoorDatum_'+d['role'],None);o.location=gv(*d['position']);o['yaw_godot']=d['yaw'];o['existing_controller']='residential_suite.gd';bpy.context.collection.objects.link(o)
bpy.context.scene['source_asset']=asset;bpy.context.scene['zero_registered_people']=True;bpy.context.scene['zero_exported_room_floor']=True
native=HERE/'source'/f'{asset}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
# Export mesh batching preserves category and material; editable semantic source remains above.
groups={}
for o in list(bpy.context.scene.objects):
    if o.type=='MESH':groups.setdefault((o['category'],o['role'],o['batch_cell']),[]).append(o)
for (category,role,cell),objects in groups.items():
    # Avoid thousands of scene operators and their repeated dependency-graph work.
    if len(objects)==1:
        objects[0].name=category+'_'+role+'_'+cell
        continue
    vertices=[];polygons=[];uvcoords=[]
    for o in objects:
        me=o.data;base=len(vertices);vertices.extend(tuple(o.matrix_world@v.co)for v in me.vertices)
        for p in me.polygons:
            polygons.append(tuple(base+i for i in p.vertices))
            uvcoords.extend(tuple(me.uv_layers.active.data[li].uv)for li in p.loop_indices)
    name=category+'_'+role+'_'+cell
    me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],polygons);me.update();me.materials.append(mat(role))
    layer=me.uv_layers.new(name='MetricUV')
    for i,value in enumerate(uvcoords):layer.data[i].uv=value
    o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
    o['source_asset']=asset;o['role']=role;o['category']=category;o['batch_cell']=cell;o['construction_wip']=True
    for old in objects:
        old_mesh=old.data;bpy.data.objects.remove(old,do_unlink=True)
        if old_mesh.users==0:bpy.data.meshes.remove(old_mesh)
export=HERE/'exports'/f'{asset}.glb'
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_extras=True,export_yup=True,export_cameras=False,export_lights=False)
receipt={'status':'source_export_completed','asset':asset,'source_spec':str(spec_path.relative_to(HERE)),'source_parts':len(spec['parts']),'runtime_meshes':len(groups),'editable_blend_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'runtime_glb_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'source_spec_sha256':hashlib.sha256(spec_path.read_bytes()).hexdigest(),'no_game_edits':True,'no_capacity_registration':True,'runtime_acceptance':False}
(HERE/'qa'/f'{asset}_BUILD.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
