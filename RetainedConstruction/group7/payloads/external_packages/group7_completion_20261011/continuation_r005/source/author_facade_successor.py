"""Restore proven-clear omitted fields in a retained-source body successor."""
import bpy,bmesh,json,hashlib,re
from pathlib import Path
import numpy as np
from mathutils import Vector
P=Path(__file__).resolve().parents[1];C=P.parent;R=C.parents[1]
plan=json.loads((P/'docs/FACADE_RESOLUTION.json').read_text());base=C/'source/natives/G7_Completion_r003.blend';native=P/'source/natives'/plan.get('native_filename','G7_BodyEnclosure_r005.blend')
assert not native.exists(),'Never overwrite a retained native revision'
base_sha=hashlib.sha256(base.read_bytes()).hexdigest();assert base_sha=='21ea0a9cda7942bacf81e288ab89e12b979ffef1933d192eb200d0f0c438b327'
for name,want in plan['source_pins'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==want
bpy.ops.wm.open_mainfile(filepath=str(base));base_plan=json.loads((C/'docs/PLAN.json').read_text());panels={q['id']:q for q in base_plan['panels']}
def signature(ob):
    h=hashlib.sha256();h.update(np.array(ob.matrix_world).tobytes());h.update(ob.type.encode())
    if ob.type=='MESH':
        h.update(np.array([q.co[:]for q in ob.data.vertices],dtype='<f4').tobytes());h.update(json.dumps([list(f.vertices)for f in ob.data.polygons]).encode())
        for uv in ob.data.uv_layers:h.update(np.array([q.uv[:]for q in uv.data],dtype='<f4').tobytes())
        h.update(json.dumps([m.name if m else None for m in ob.data.materials]).encode())
    return h.hexdigest()
original={ob.name:signature(ob)for ob in bpy.context.scene.objects};added=[];cells=set()
for row in plan['accepted_clear_fields']:
    name=row['name'];assert name not in bpy.data.objects;v=row['candidate_vertices'];match=re.match(r'(G7C3_Body_(-?1)_\d{2}_\d{3})_',name);assert match
    panel=panels[match[1]];cell='Body_'+match[2]+'_'+str(int((panel['z'][0]+510)//120)).zfill(2)
    frame='_Receiver_'in name or '_RoofHead_'in name;role='metal'if frame or '_Pier_'in name else'glass'if '_Glass_'in name else'shell';category='solid_frame'if frame else'solid_skin'
    faces=[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]
    me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y)for x,y,z in v],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume()>1e-9;bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(bpy.data.materials['G7C3_'+role]);uv=me.uv_layers.new(name='MetreScaled')
    for face in me.polygons:
        n=face.normal;u=Vector((0,1,0))if abs(n.x)>.8 else Vector((1,0,0));w=n.cross(u)
        for k in face.loop_indices:q=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(q.dot(u),q.dot(w))
    ob['group7_cell']=cell;ob['contact_category']=category;ob['source_clearance_revision']='R005_ACTUAL_COMPONENTS_AND_PROTECTED_VOLUME_GUARDS';ob['original_source_edited']=False
    added.append({'name':name,'cell':cell,'role':role,'category':category,'vertices_world_xyz':v,'faces':[list(f)for f in faces]});cells.add(cell)
for name,want in original.items():assert signature(bpy.data.objects[name])==want,name
assert hashlib.sha256(base.read_bytes()).hexdigest()==base_sha
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
report={'status':'SOURCE_AUTHORED_ORIGINAL_OBJECTS_EXACT','native':native.relative_to(P).as_posix(),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'retained_base_native':base.relative_to(R).as_posix(),'retained_base_native_sha256':base_sha,'original_object_signatures':original,'original_objects_preserved':len(original),'added_parts':added,'export_cells':sorted(cells),'protected_held_fields':len(plan['remaining_held_fields']),'capacity_delta':0,'new_room_ids':0,'source_originals_overwritten':False,'whole_group_accepted':False}
(P/'docs/AUTHORED_BODY_SUCCESSOR.json').write_text(json.dumps(report,separators=(',',':'))+'\n');print('G7_R005_BODY_SOURCE',len(added),'restored fields',len(cells),'body cells',len(original),'original objects exact',report['native_sha256'])
