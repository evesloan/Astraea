"""Preserve r001, replace its rejected global cap with narrow head closure."""
from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'source/natives/G7_Completion_r001.blend'))
rows=json.load(open(P/'qa/SOURCE_GEOMETRY.json'));plan=json.load(open(P/'docs/PLAN.json'))
removed=[r for r in rows if r['cell'].startswith('Roof_')]
for row in removed:bpy.data.objects.remove(bpy.data.objects[row['name']],do_unlink=True)
rows=[r for r in rows if not r['cell'].startswith('Roof_')]
for i,poly in enumerate(plan['roof_triangles']):
    name='G7C3_PerimeterHeadRoof_'+str(i);cz=sum(q[1]for q in poly)/3;cell='Roof_'+str(int((cz+510)//120)).zfill(2);n=3
    world=[(x,y,z)for y in [106.5,106.78]for x,z in poly]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
    me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y)for x,y,z in world],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(bpy.data.materials['G7C3_roof']);uv=me.uv_layers.new(name='MetreScaled')
    for face in me.polygons:
        normal=face.normal;u=Vector((0,1,0))if abs(normal.x)>.8 else Vector((1,0,0));w=normal.cross(u)
        for k in face.loop_indices:q=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(q.dot(u),q.dot(w))
    ob['contact_category']='solid_roof';ob['group7_cell']=cell;ob['immutable_originals_preserved']=True;me.calc_loop_triangles()
    rows.append({'name':name,'vertices_world_xyz':world,'faces':[list(f)for f in faces],'role':'roof','category':'solid_roof','cell':cell,'triangles':len(me.loop_triangles)})
native=P/'source/natives/G7_Completion_r002.blend';assert not native.exists();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
(P/'qa/SOURCE_GEOMETRY_R002.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
(P/'qa/ROOF_REVISION.json').write_text(json.dumps({'status':'R001_GLOBAL_CAP_HELD_R002_PERIMETER_HEAD_CLOSURE','r001_native_sha256':hashlib.sha256((P/'source/natives/G7_Completion_r001.blend').read_bytes()).hexdigest(),'r001_preserved_unchanged':True,'removed_candidate_roof_triangular_prisms':len(removed),'selected_perimeter_roof_area_m2':plan['roof_area_m2'],'no_global_blanket_roof':'R002 closes only the 2 m exterior head band, outside all source-owned roofs and crown/route voids. Internal enclosure seams remain integration holds.','other_source_parts_unchanged':len(rows)-len(plan['roof_triangles'])},indent=2)+'\n')
print('GROUP7_R002_NARROW_ROOF',len(rows),'parts',round(plan['roof_area_m2'],3),'m2')
