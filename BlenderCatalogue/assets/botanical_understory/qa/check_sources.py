"""Reload editable sources and inspect actual meshes/contact/attachments without rendering."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BASE=Path(__file__).resolve().parents[1]
results=[]
for ident in ('AST-BOT-002','AST-BOT-003'):
    record=json.loads((BASE/f'{ident}.manifest.json').read_text());source=BASE/record['source']
    bpy.ops.wm.open_mainfile(filepath=str(source));objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];rows=[];trees={};points=[]
    for ob in objects:
        bm=bmesh.new();bm.from_mesh(ob.data);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free()
        ob.data.calc_loop_triangles();vertices=[ob.matrix_world@v.co for v in ob.data.vertices];points+=vertices
        trees[ob.name]=BVHTree.FromPolygons(vertices,[list(p.vertices) for p in ob.data.polygons])
        closed=ob['surface_kind']=='closed_support';uv=ob.data.uv_layers.active;areas=[]
        for tr in ob.data.loop_triangles:
            a,b,c=[uv.data[l].uv for l in tr.loops];areas.append(abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))*.5)
        rows.append({'name':ob.name,'kind':ob['surface_kind'],'triangles':len(ob.data.loop_triangles),'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'volume_m3':volume,'unit_scale':all(abs(x-1)<1e-7 for x in ob.scale),'minimum_uv_triangle_area':min(areas),'passed':(boundary==0 and nonmanifold==0 and volume>0 if closed else boundary>0) and min(areas)>1e-12})
    joints=[]
    for row in record['support_joints']:
        q=Vector(row['child_attachment_m']);near,normal,index,distance=trees[row['parent']].find_nearest(q)
        signed=(q-near).dot(normal);inside_or_on=signed<1e-5
        child=bpy.data.objects[row['child']]
        child_tree=trees[row['child']];cnear,cnormal,ci,cdistance=child_tree.find_nearest(q)
        # Exact start-tip for leaf; cap interior for closed support.
        child_captured=cdistance<=max(row['parent_radius_m'],.010)
        joints.append({'child':row['child'],'parent':row['parent'],'kind':row['joint_type'],'parent_surface_distance_m':distance,'signed_parent_surface_distance_m':signed,'child_surface_distance_m':cdistance,'attachment_inside_or_on_actual_parent_mesh':inside_or_on,'child_root_captured':child_captured,'passed':inside_or_on and child_captured})
    lo=[min(p[k] for p in points) for k in range(3)];hi=[max(p[k] for p in points) for k in range(3)]
    ymin,ymax=lo[1]+.51,hi[1]+.51
    result={'catalogue_id':ident,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_reloaded':True,'mesh_parts':rows,'part_count':len(rows),'triangles':sum(r['triangles'] for r in rows),'bounds_blender_z_up':{'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]},'soil_plane_contact':{'min_z_m':lo[2],'mesh_vertex_count_at_z0':sum(abs(p.z)<1e-7 for p in points),'no_vertices_below_soil':lo[2]>=-1e-7},'actual_mesh_attachment_tests':joints,'texture_dependencies':{'all_file_images_packed':all(im.packed_file for im in bpy.data.images if im.source=='FILE'),'used_materials':[m.name for m in bpy.data.materials if m.users]},'planter_placement_proposal':{'base_m':[1.2,.51,.39],'foliage_world_y_min_m':ymin,'foliage_world_y_max_m':ymax,'soil_opening_y_m':[.15,.88],'fully_within_soil_strip':ymin>=.15 and ymax<=.88,'frontmost_foliage_to_seat_back_m':ymin-(-.02),'seat_back_y_m':-.02,'top_world_z_m':hi[2]+.39,'scope':'Component bounds only, does not certify users/seat comfort or biological soil volume'},'all_passed':all(r['passed'] for r in rows) and all(r['passed'] for r in joints) and abs(lo[2])<1e-7 and ymin>=.15 and ymax<=.88}
    results.append(result)
(BASE/'qa/source_reload_checks.json').write_text(json.dumps({'inspector':'Independent source reload, BMesh topology, BVH closest-surface attachment and measured vertex bounds','results':results,'all_passed':all(r['all_passed'] for r in results)},indent=2)+'\n')
print('SOURCE_QA',[(r['catalogue_id'],r['all_passed'],r['triangles']) for r in results])
for r in results:
    for j in r['actual_mesh_attachment_tests']:
        if not j['passed']:print('FAILED_JOINT',r['catalogue_id'],j)
