"""Author the exact reviewed member schedule as editable source, no Game writes."""
from pathlib import Path
import bpy, bmesh, json, hashlib, argparse, sys
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT.parent
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
p=argparse.ArgumentParser();p.add_argument('--schedule',required=True);p.add_argument('--revision',required=True)
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
schedule=Path(args.schedule);data=json.loads(schedule.read_text())
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert data['status']=='PASS_CONSERVATIVE_SOURCE_FIT_PROPOSAL'
assert all(sha(path)==digest for path,digest in data['source_pins'].items())
OUT=ROOT/'outputs'/args.revision;assert not OUT.exists();OUT.mkdir()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
materials={};mat_records=json.loads((CAT/'materials/material_manifest.json').read_text())['materials'];material_pins={}
def material(role):
    if role in materials:return materials[role]
    record=mat_records[role];m=bpy.data.materials.new('RECEIVING_'+role);m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Roughness'].default_value=record.get('roughness',.8);n.inputs['Metallic'].default_value=record.get('metallic',0)
    image_path=CAT/'materials'/(role+'.png');material_pins[str(image_path)]=sha(image_path)
    image=bpy.data.images.load(str(image_path),check_existing=True);image.pack();tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Closest';tex.extension='REPEAT';m.node_tree.links.new(tex.outputs['Color'],n.inputs['Base Color'])
    materials[role]=m;return m
records=[]
for member in data['members']:
    vertices=[(x,-z,y)for x,y,z in member['vertices_world_xyz']]
    mesh=bpy.data.meshes.new(member['name']);mesh.from_pydata(vertices,[],member['faces']);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    obj=bpy.data.objects.new(member['name'],mesh);scene.collection.objects.link(obj);mesh.materials.append(material(member['material_role']))
    obj['source_member_id']=member['name'];obj['receiving_category']=member['category'];obj['status']='proposed source geometry; not installed or load-certified'
    obj['schedule_sha256']=sha(schedule);obj['intended_contact_owners']=member['intended_contact_owners'];obj['source_purpose']=member['purpose'];obj['frame']='Blender(X,-worldZ,worldY);GLB is actual Godot world XYZ'
    uv=mesh.uv_layers.new(name='MetreScaled');scale=mat_records[member['material_role']].get('meters_per_tile_uv',[1,1])
    for face in mesh.polygons:
        normal=face.normal;u=(Vector((1,0,0))-normal*normal.x).normalized() if abs(normal.z)>.7 else Vector((-normal.y,normal.x,0)).normalized();v=normal.cross(u)
        for index in face.loop_indices:
            q=mesh.vertices[mesh.loops[index].vertex_index].co;uv.data[index].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
    mesh.calc_loop_triangles();assert len(mesh.loop_triangles)==12
    world=[(v.co.x,v.co.z,-v.co.y)for v in mesh.vertices]
    lo=[min(v[i]for v in world)for i in range(3)];hi=[max(v[i]for v in world)for i in range(3)]
    delta=max(abs(a-b)for a,b in zip(lo+hi,member['bounds_world_min_xyz']+member['bounds_world_max_xyz']));assert delta<.00003
    records.append({'source_member_id':member['name'],'source_node_name':obj.name,'category':member['category'],'material_role':member['material_role'],'world_bounds':[lo,hi],'bounds_error_m':delta,'triangles':12,'intended_contact_owners':member['intended_contact_owners']})
scene['status']='Source-only connected receiving-frame successor; source-fit proposal, no load certification or native acceptance'
scene['world_coordinate_contract']='Blender(X,-worldZ,worldY), GLB actual ship world XYZ'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'receiving_frame.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'receiving_frame.glb'),export_format='GLB',export_yup=True,export_extras=True)
receipt={'status':'PASS_AUTHORED_MEMBER_SCHEDULE_FIDELITY','source_schedule_path':str(schedule),'source_schedule_sha256':sha(schedule),'source_pins':data['source_pins'],'material_pins':material_pins,'source_sha256':sha(OUT/'receiving_frame.blend'),'glb_sha256':sha(OUT/'receiving_frame.glb'),'members':records,'member_count':len(records),'triangles':sum(r['triangles']for r in records),'limits':['Geometric contacts and lower-volume exclusions are the separate proposal checks, not structural capacity certification','Finite current shell heights do not prove unresolved specialty or luxury fit','Native imported geometry, contacts and player/cart routes remain untested']}
(OUT/'SOURCE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert all(sha(path)==digest for path,digest in data['source_pins'].items())
assert all(sha(path)==digest for path,digest in material_pins.items())
print('RECEIVING_FRAME_SOURCE_READY',len(records),'members',receipt['triangles'],'triangles',flush=True)
