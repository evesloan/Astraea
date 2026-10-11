"""Preserve r002; replace enclosed court heads with real open diffuser bezels."""
from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
old=P/'source/natives/G7_Completion_r002.blend';old_sha=hashlib.sha256(old.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(old))
rows=json.load(open(P/'qa/SOURCE_GEOMETRY_R002.json'));plan=json.load(open(P/'docs/PLAN.json'))
remove={p['id']+suffix for p in plan['botanical_pockets']for suffix in ['_LampFoot','_LampPost','_LampHead']}
for name in remove:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
rows=[r for r in rows if r['name']not in remove]
def rect(name,lo,hi,cell):
    x0,y0,z0=lo;x1,y1,z1=hi
    world=[(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1),(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)]
    faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y)for x,y,z in world],[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(bpy.data.materials['G7C3_metal']);uv=me.uv_layers.new(name='MetreScaled')
    for face in me.polygons:
        normal=face.normal;u=Vector((0,1,0))if abs(normal.x)>.8 else Vector((1,0,0));w=normal.cross(u)
        for k in face.loop_indices:q=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(q.dot(u),q.dot(w))
    ob['contact_category']='solid_frame';ob['group7_cell']=cell;ob['immutable_originals_preserved']=True;me.calc_loop_triangles()
    rows.append({'name':name,'vertices_world_xyz':world,'faces':[list(f)for f in faces],'role':'metal','category':'solid_frame','cell':cell,'triangles':len(me.loop_triangles)})
for pocket in plan['botanical_pockets']:
    x,y,z=pocket['origin'];side=-1 if x<0 else 1;lx=x-side*.5;lz=z+2.3;name=pocket['id']
    # Rear stem and base attach to the back bezel; leave the diffuser centre free.
    rect(name+'_LampFoot',(lx-.07,y,lz+.05),(lx+.07,y+.1,lz+.19),name)
    rect(name+'_LampPost',(lx-.035,y+.1,lz+.085),(lx+.035,y+2.12,lz+.155),name)
    rect(name+'_LampHead',(lx-.15,y+2.10,lz-.15),(lx+.15,y+2.15,lz+.15),name)
    rect(name+'_BezelLeft',(lx-.15,y+1.95,lz-.15),(lx-.12,y+2.10,lz+.15),name)
    rect(name+'_BezelRight',(lx+.12,y+1.95,lz-.15),(lx+.15,y+2.10,lz+.15),name)
    rect(name+'_BezelFront',(lx-.12,y+1.95,lz-.15),(lx+.12,y+2.10,lz-.12),name)
    rect(name+'_BezelBack',(lx-.12,y+1.95,lz+.12),(lx+.12,y+2.10,lz+.15),name)
native=P/'source/natives/G7_Completion_r003.blend';assert not native.exists()
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
assert hashlib.sha256(old.read_bytes()).hexdigest()==old_sha
(P/'qa/SOURCE_GEOMETRY_R003.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
(P/'qa/LAMP_REVISION_R003.json').write_text(json.dumps({'status':'R002_COURT_LIGHT_SOURCE_HELD_R003_OPEN_BEZEL','r002_native_sha256':old_sha,'r002_preserved_unchanged':True,'court_fixtures':11,'retained_opal_diffusers_unchanged':True,'emitter_world_positions_unchanged':True,'post_relocated_rear_m':.12,'solid_top_and_four_bezel_bars_per_lamp':True,'authored_parts':len(rows),'geometry_scope':'Only court lamp foot/post/head geometry revised; all hull/roof/court furniture/plant originals and their bindings remain unchanged. Light exit/admission checks still required.'},indent=2)+'\n')
(P/'docs/SELECTED_NATIVE.json').write_text(json.dumps({'native':native.relative_to(P).as_posix(),'source_geometry':'qa/SOURCE_GEOMETRY_R003.json','export_dir':'exports_r003','export_prefix':'G7_Completion_R003_','previous_native_immutable':'source/natives/G7_Completion_r002.blend'},indent=2)+'\n')
print('GROUP7_R003_OPEN_LAMP_BEZELS',len(rows))
