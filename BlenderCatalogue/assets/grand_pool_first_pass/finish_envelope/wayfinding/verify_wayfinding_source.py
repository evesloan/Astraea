"""Independent source reopen QA. No save, render, export, subprocess or runtime edit.

Parent-owned invocation only after the build/job gate is clear:
 blender -b -t 2 --python verify_wayfinding_source.py -- --source SOURCE.blend \
   --contract wayfinding_contract.json --report NEW_REPORT.json

72 degrees is treated explicitly as VERTICAL field of view at 360 pixels high.
Projection is geometric source evidence, never rendered-pixel legibility acceptance.
"""
import argparse,hashlib,itertools,json,math,struct,sys,traceback
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(a,b):return [x+y for x,y in zip(a,b)]
def sub(a,b):return [x-y for x,y in zip(a,b)]
def mul(a,k):return [x*k for x in a]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def norm(a):return math.sqrt(dot(a,a))
def unit(a):return mul(a,1/norm(a))
def bounds(vs):return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
def overlap(a,b):return all(min(a[1][i],b[1][i])>max(a[0][i],b[0][i]) for i in range(3))
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def exact_key(v):return tuple(struct.pack('<f',x) for x in v)
def ulp32(x):return 2**(math.floor(math.log2(abs(x)))-23) if x else 2**-149

def world_xyz(ob,v):
    # Use the saved ob.matrix_world, with Python-double multiplication. This avoids
    # introducing a NEW float32 world bake into QA of locally authored glyphs.
    m=ob.matrix_world;p=[sum(float(m[i][k])*float(v[k]) for k in range(3))+float(m[i][3]) for i in range(3)]
    return [p[0],p[2],-p[1]]
def local_uvd(s,p):
    q=sub(p,s['origin_xyz']);return [dot(q,s[k]) for k in ['right_xyz','up_xyz','normal_xyz']]
def bounds_close(a,b,tol):return all(abs(a[j][i]-b[j][i])<=tol for j in range(2) for i in range(3))
def within(a,b,tol):return all(a[0][i]>=b[0][i]-tol and a[1][i]<=b[1][i]+tol for i in range(3))

def topology(me):
    """Connectivity uses exact saved float32 positions. No distance-based welding."""
    keys={};ids=[]
    for v in me.vertices:
        key=exact_key(v.co)
        if key not in keys:keys[key]=len(keys)
        ids.append(keys[key])
    parent=list(range(len(keys)));edge_counts={};directed_edges={};triangles=[];areas=[];degenerate=[]
    def find(a):
        while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
        return a
    def union(a,b):parent[find(a)]=find(b)
    used=set()
    for ti,t in enumerate(me.loop_triangles):
        ii=[ids[i] for i in t.vertices];triangles.append(tuple(t.vertices));used.update(ii)
        vv=[list(me.vertices[i].co) for i in t.vertices];area=norm(cross(sub(vv[1],vv[0]),sub(vv[2],vv[0])))/2;areas.append(area)
        if len(set(ii))<3 or area<=1e-12:degenerate.append(ti)
        for a,b in zip(ii,ii[1:]+ii[:1]):
            union(a,b);key=tuple(sorted((a,b)));edge_counts[key]=edge_counts.get(key,0)+1;directed_edges[(a,b)]=directed_edges.get((a,b),0)+1
    shells={}
    for ti,t in enumerate(triangles):shells.setdefault(find(ids[t[0]]),[]).append(ti)
    return {'exact_coordinate_shells':list(shells.values()),'shell_count':len(shells),'degenerate_triangles':degenerate,
            'minimum_triangle_area_m2':min(areas) if areas else 0,'triangle_count':len(triangles),
            'boundary_edges':sum(n==1 for n in edge_counts.values()),'nonmanifold_edges':sum(n>2 for n in edge_counts.values()),
            'winding_mismatches':sum(directed_edges.get((a,b),0)!=directed_edges.get((b,a),0) for a,b in edge_counts),'unused_exact_vertices':len(keys)-len(used),'exact_unique_vertices':len(keys),'triangles':triangles}

def convex_contact(a,b):
    """Strict SAT for the authored convex bodies (boxes and octagonal fasteners).
    A positive overlap is required; no tolerance is used to bridge a geometric gap.
    """
    if not overlap(a['bounds'],b['bounds']):return False
    axes=a['normals']+b['normals']
    axes += [cross(x,y) for x in a['edges'] for y in b['edges']]
    for axis in axes:
        if norm(axis)<1e-12:continue
        aa=[dot(v,axis) for v in a['world']];bb=[dot(v,axis) for v in b['world']]
        if min(max(aa),max(bb))<=max(min(aa),min(bb)):return False
    return True

def project_segment(eye,target,centre,height,up):
    forward=unit(sub(target,eye));right=unit(cross(forward,[0,1,0]));camera_up=cross(right,forward)
    focal=360/(2*math.tan(math.radians(72)/2))
    def project(p):
        q=sub(p,eye);depth=dot(q,forward)
        if depth<=0:raise ValueError('Projected cap is behind declared approach camera')
        return [focal*dot(q,right)/depth,focal*dot(q,camera_up)/depth]
    a,b=project(add(centre,mul(up,-height/2))),project(add(centre,mul(up,height/2)))
    return {'cap_height_px_geometric':abs(b[1]-a[1]),'cap_segment_length_px_geometric':norm(sub(a,b)),
            'vertical_fov_degrees':72,'image_height_px':360,'aim_xyz':target,'eye_xyz':eye,
            'scope':'Pinhole geometry only. No rendered pixels, effects, occlusion or readability acceptance.'}

def verify(args):
    import bpy
    from mathutils import Vector
    source=args.source.resolve();before=sha(source);d=json.loads(args.contract.read_text())
    checks=[];mesh_rows=[];glyph_rows=[];sign_rows=[];issues=[]
    def check(name,ok,**details):
        r={'check':name,'pass':bool(ok),**details};checks.append(r)
        if not ok:issues.append(r)
    report={'status':'source_reopen_qa_running','source_file':str(source),'source_sha256':before,'contract_sha256':sha(args.contract),
            'no_save_render_export_or_runtime_edits':True,'checks':checks,'meshes':mesh_rows,'glyphs':glyph_rows,'signs':sign_rows,'issues':issues}
    try:
        for pin in d['pins']:
            path=Path(d['source_defaults'][pin['root']])/pin['path'];check('preserved_input:'+pin['path'],path.is_file() and sha(path)==pin['sha256'])
        bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
        scene=bpy.context.scene;check('metric_scene',scene.unit_settings.system=='METRIC' and abs(scene.unit_settings.scale_length-1)<1e-8)
        root=bpy.data.objects.get('AST_RES_001_PoolWayfinding')
        check('root_identity',root is not None and root.get('catalogue_id')=='AST-RES-001' and root.get('source_family')=='residential_wayfinding_bay' and root.get('new_design_count')==0 and root.get('contract_sha256')==sha(args.contract))
        if root is None:raise ValueError('Missing source ownership root')
        check('root_transform',max(abs(float(root.matrix_world[i][j])-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-8)
        sign_objects=[ob for ob in scene.objects if ob.name.startswith('SIGN_') and ob.get('wayfinding_export')]
        check('exact_eleven_signs',len(sign_objects)==11 and {ob.name for ob in sign_objects}=={'SIGN_'+s['id'] for s in d['signs']})
        expected_names=set();actual_parts={ob.name:ob for ob in scene.objects if ob.type=='MESH' and ob.get('wayfinding_export')}
        records={}
        def read_mesh(ob,s):
            if ob.name in records:return records[ob.name]
            check(ob.name+':editable_mesh',ob.type=='MESH' and not ob.modifiers and ob.data.shape_keys is None)
            me=ob.data;me.calc_loop_triangles();top=topology(me);world=[world_xyz(ob,v.co) for v in me.vertices];b=bounds(world)
            normals=[];edges=[]
            for t in top['triangles']:
                a,bb,c=[world[i] for i in t];n=cross(sub(bb,a),sub(c,a))
                if norm(n)>1e-12:normals.append(unit(n))
            for edge in me.edges:
                e=sub(world[edge.vertices[1]],world[edge.vertices[0]])
                if norm(e)>1e-12:edges.append(unit(e))
            # Deduplicate axes without altering any actual coordinate or topology.
            normals=list({tuple(round(x,10) for x in n):n for n in normals}.values());edges=list({tuple(round(x,10) for x in e):e for e in edges}.values())
            rec={'object':ob,'world':world,'bounds':b,'topology':top,'normals':normals,'edges':edges};records[ob.name]=rec
            check(ob.name+':positive_nondegenerate_triangles',top['triangle_count']>0 and not top['degenerate_triangles'],minimum_area_m2=top['minimum_triangle_area_m2'],degenerate_count=len(top['degenerate_triangles']))
            check(ob.name+':closed_exact_edge_topology',top['boundary_edges']==0 and top['nonmanifold_edges']==0 and top['winding_mismatches']==0,boundary_edges=top['boundary_edges'],nonmanifold_edges=top['nonmanifold_edges'],winding_mismatches=top['winding_mismatches'])
            shell_volumes=[]
            for shell in top['exact_coordinate_shells']:
                ids={i for ti in shell for i in top['triangles'][ti]};anchor=[sum(float(me.vertices[i].co[k]) for i in ids)/len(ids) for k in range(3)];volume=0.0
                for ti in shell:
                    points=[sub(list(me.vertices[i].co),anchor) for i in top['triangles'][ti]]
                    volume+=dot(points[0],cross(points[1],points[2]))/6
                shell_volumes.append(volume)
            top['shell_signed_volumes_m3']=shell_volumes
            check(ob.name+':positive_per_shell_volume',bool(shell_volumes) and all(v>0 for v in shell_volumes),signed_volumes_m3=shell_volumes,calculation='Python-double signed volume about each shell local centroid; no world-coordinate cancellation')
            check(ob.name+':proper_rigid_world_basis',abs(float(ob.matrix_world.to_3x3().determinant())-1)<1e-6 and all(abs(float(v)-1)<1e-6 for v in ob.matrix_world.to_scale()))
            check(ob.name+':ownership',ob.get('catalogue_id')=='AST-RES-001' and ob.get('source_sign_id')==s['id'] and ob.parent is bpy.data.objects.get('SIGN_'+s['id']))
            role=ob.get('semantic_role');check(ob.name+':material_slot',len(me.materials)==1 and role in d['material_roles'] and me.materials[0].name==role)
            # UV coordinates may be translated with a locally authored object; test
            # per-face DIFFERENCES against metric geometry, not a hard-coded offset.
            uv_error=0.0;uv_ok=bool(me.uv_layers and me.uv_layers.active)
            if uv_ok and role in d['material_roles']:
                tile=d['material_roles'][role]['meters_per_tile_uv'];layer=me.uv_layers.active
                for face in me.polygons:
                    n=face.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized() if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u).normalized()
                    first=face.loop_indices[0];anchor=me.vertices[me.loops[first].vertex_index].co;auv=layer.data[first].uv
                    for li in face.loop_indices:
                        q=me.vertices[me.loops[li].vertex_index].co-anchor;actual=layer.data[li].uv-auv;want=[q.dot(u)/tile[0],q.dot(v)/tile[1]]
                        if not all(math.isfinite(float(x)) for x in layer.data[li].uv):uv_ok=False
                        uv_error=max(uv_error,max(abs(float(actual[i])-want[i]) for i in range(2)))
            check(ob.name+':metric_uv',uv_ok and uv_error<2e-5,max_metric_delta_error=uv_error)
            mesh_rows.append({'name':ob.name,'bounds_xyz':b,**{k:v for k,v in top.items() if k not in ['exact_coordinate_shells','triangles']}})
            return rec
        def reference_font(body,include_topology=False):
            cu=bpy.data.curves.new('QA_TEMP_Font','FONT');cu.body=body;cu.size=1;cu.align_x='LEFT';cu.extrude=.002;cu.resolution_u=6
            ob=bpy.data.objects.new('QA_TEMP_Font',cu);scene.collection.objects.link(ob)
            bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();eo=ob.evaluated_get(dg);me=eo.to_mesh()
            me.calc_loop_triangles();vs=[list(v.co) for v in me.vertices];reference_topology=topology(me) if include_topology else None;eo.to_mesh_clear();bpy.data.objects.remove(ob,do_unlink=True)
            if cu.users==0:bpy.data.curves.remove(cu)
            return (vs,reference_topology) if include_topology else vs
        h=bounds(reference_font('H'));unit_cap=h[1][1]-h[0][1]
        for s in d['signs']:
            sid=s['id'];parent=bpy.data.objects.get('SIGN_'+sid)
            if parent is None:check(sid+':parent_exists',False);continue
            check(sid+':parent_transform',parent.parent is root and max(abs(float(parent.matrix_world[i][j])-(1 if i==j else 0)) for i in range(4) for j in range(4))<1e-8)
            check(sid+':proper_text_viewing_basis',norm(sub(cross(s['right_xyz'],s['up_xyz']),s['normal_xyz']))<1e-9 and dot(sub(s['viewpoint_xyz'],s['origin_xyz']),s['normal_xyz'])>0)
            tolerance=2*max(ulp32(x) for x in s['origin_xyz'])
            bodies=[];mounted=set()
            for c in s['components']:
                name='PWF_'+sid+'_'+c['name'];expected_names.add(name);ob=actual_parts.get(name)
                if ob is None:check(name+':exists',False);continue
                rec=read_mesh(ob,s);bodies.append(rec)
                check(name+':actual_component_bounds',bounds_close(rec['bounds'],c['world_bounds_xyz'],tolerance),max_coordinate_rounding_allowance_m=tolerance)
                check(name+':one_exact_connected_closed_shell',rec['topology']['shell_count']==1 and rec['topology']['boundary_edges']==0 and rec['topology']['nonmanifold_edges']==0,exact_shells=rec['topology']['shell_count'],boundary_edges=rec['topology']['boundary_edges'],nonmanifold_edges=rec['topology']['nonmanifold_edges'])
                for patch in s['contact_patches']:
                    p=mul(add(*patch['bounds_xyz']),.5)
                    # Rooted part must strictly contain the contact-patch centre.
                    # No epsilon may turn a gap into a support connection.
                    if all(rec['bounds'][0][i]<p[i]<rec['bounds'][1][i] for i in range(3)):mounted.add(len(bodies)-1)
            changed=True
            while changed:
                prev=len(mounted)
                for i,a in enumerate(bodies):
                    if i not in mounted and any(convex_contact(a,bodies[j]) for j in mounted):mounted.add(i)
                changed=len(mounted)>prev
            check(sid+':actual_positive_overlap_mount_graph',len(mounted)==len(bodies),connected_parts=len(mounted),body_parts=len(bodies),gap_bridging_tolerance_m=0)
            backing=records.get('PWF_'+sid+'_MapBacking')
            for index,line in enumerate(s['text_lines']):
                name='PWF_'+sid+'_Glyphs_'+str(index);expected_names.add(name);ob=actual_parts.get(name)
                if ob is None:check(name+':exists',False);continue
                rec=read_mesh(ob,s);coords=[local_uvd(s,v) for v in rec['world']];gb=bounds(coords);raw,reference_topology=reference_font(line,True);rb=bounds(raw)
                sx=(gb[1][0]-gb[0][0])/(rb[1][0]-rb[0][0]);sy=(gb[1][1]-gb[0][1])/(rb[1][1]-rb[0][1]);cap=sy*unit_cap
                check(name+':actual_cap_and_uniform_scale',cap>=s['minimum_glyph_cap_height_m']-1e-6 and abs(sx-sy)<2e-5 and abs(cap-float(ob.get('actual_cap_height_m',-1)))<2e-5,actual_cap_m=cap,minimum_cap_m=s['minimum_glyph_cap_height_m'],scale_u=sx,scale_v=sy)
                check(name+':unchanged_lettering',ob.get('original_lettering')==line)
                # Compare the actual 2D glyph vertex pattern to the correct, unmirrored
                # font pattern after independent positive uniform scale/centering.
                cx,cy=(gb[0][0]+gb[1][0])/2,(gb[0][1]+gb[1][1])/2;rx,ry=(rb[0][0]+rb[1][0])/2,(rb[0][1]+rb[1][1])/2
                reference=list({(v[0],v[1]) for v in raw});observed=list({(v[0],v[1]) for v in coords})
                def shape_error(flip):
                    wanted=[((x-rx)*sy*flip+cx,(y-ry)*sy+cy) for x,y in reference]
                    observed_to_wanted=max(min(math.hypot(x-a,y-b) for a,b in wanted) for x,y in observed)
                    wanted_to_observed=max(min(math.hypot(x-a,y-b) for a,b in observed) for x,y in wanted)
                    return max(observed_to_wanted,wanted_to_observed)
                correct=shape_error(1);mirrored=shape_error(-1)
                check(name+':physical_glyph_pattern_not_mirrored',correct<max(tolerance,5e-6),correct_pattern_error_m=correct,mirrored_pattern_error_m=mirrored)
                fronts=[];backs=[];shell_contacts=[];shell_orientation=[]
                for shell in rec['topology']['exact_coordinate_shells']:
                    shell_ids={v for ti in shell for v in rec['topology']['triangles'][ti]};shell_vs=[coords[i] for i in shell_ids];sb=bounds(shell_vs)
                    shell_contacts.append(sb[0][2]<.124 and sb[1][2]>.124 and sb[0][0]>=-s['width_m']/2+s['frame_border_m']-tolerance and sb[1][0]<=s['width_m']/2-s['frame_border_m']+tolerance)
                    local_origin=[sum(float(ob.data.vertices[i].co[k]) for i in shell_ids)/len(shell_ids) for k in range(3)]
                    signed_volume=0.0;front_directions=[];back_directions=[]
                    for ti in shell:
                        indices=rec['topology']['triangles'][ti];local_points=[sub(list(ob.data.vertices[i].co),local_origin) for i in indices]
                        signed_volume+=dot(local_points[0],cross(local_points[1],local_points[2]))/6
                        world_points=[rec['world'][i] for i in indices];n=cross(sub(world_points[1],world_points[0]),sub(world_points[2],world_points[0]));length=norm(n)
                        if not length:continue
                        facing=dot(mul(n,1/length),s['normal_xyz']);depths=[coords[i][2] for i in indices]
                        if min(depths)>sb[1][2]-2e-6:front_directions.append(facing)
                        if max(depths)<sb[0][2]+2e-6:back_directions.append(facing)
                    shell_orientation.append({'signed_volume_m3':signed_volume,'has_outward_front':bool(front_directions) and min(front_directions)>.99,'has_inward_back':bool(back_directions) and max(back_directions)<-.99})
                for t in rec['topology']['triangles']:
                    pts=[rec['world'][i] for i in t];nn=cross(sub(pts[1],pts[0]),sub(pts[2],pts[0]));length=norm(nn)
                    if not length:continue
                    direction=dot(mul(nn,1/length),s['normal_xyz']);depths=[coords[i][2] for i in t]
                    if min(depths)>gb[1][2]-2e-6:fronts.append(direction)
                    if max(depths)<gb[0][2]+2e-6:backs.append(direction)
                expected_shells=reference_topology['shell_count']
                check(name+':reference_topology_measured',reference_topology['boundary_edges']==0 and reference_topology['nonmanifold_edges']==0 and reference_topology['winding_mismatches']==0,reference_shells=expected_shells,reference_boundary_edges=reference_topology['boundary_edges'],reference_nonmanifold_edges=reference_topology['nonmanifold_edges'],reference_winding_mismatches=reference_topology['winding_mismatches'])
                check(name+':each_saved_shell_outward',all(r['signed_volume_m3']>0 and r['has_outward_front'] and r['has_inward_back'] for r in shell_orientation),shells=shell_orientation)
                check(name+':exact_letter_shells_and_backing_contact',rec['topology']['shell_count']==expected_shells and all(shell_contacts),expected_shells=expected_shells,actual_shells=rec['topology']['shell_count'],all_shells_engage_backing=all(shell_contacts))
                check(name+':outward_front_inward_back_faces',bool(fronts) and bool(backs) and min(fronts)>.99 and max(backs)<-.99,front_face_count=len(fronts),back_face_count=len(backs))
                check(name+':glyph_reserved_bounds',within(rec['bounds'],s['glyph_envelope_world_xyz'],tolerance))
                centre=mul(add(*rec['bounds']),.5);target=add(s['origin_xyz'],mul(s['normal_xyz'],.129));projection=project_segment(s['viewpoint_xyz'],target,centre,cap,s['up_xyz'])
                glyph_rows.append({'sign':sid,'line':line,'actual_cap_height_m':cap,'minimum_cap_height_m':s['minimum_glyph_cap_height_m'],'correct_pattern_error_m':correct,**projection})
            if 'arrow' in s:
                name='PWF_'+sid+'_RouteArrow';expected_names.add(name);ob=actual_parts.get(name)
                if ob is None:check(name+':exists',False)
                else:
                    rec=read_mesh(ob,s);coords=[local_uvd(s,v) for v in rec['world']];direction=s['arrow']['unit_arrow_uv'];hi=s['glyph_envelope_local_uvd'][1];cx=hi[0]-.12
                    expected=[(cx+x*direction[0]-y*direction[1],x*direction[1]+y*direction[0]) for x,y in [(-.105,-.025),(.025,-.025),(.025,-.073),(.115,0),(.025,.073),(.025,.025),(-.105,.025)]]
                    err=max(min(math.hypot(v[0]-x,v[1]-y) for x,y in expected) for v in coords)
                    tangent=unit(sub(s['arrow']['route_to_xyz'],s['arrow']['route_from_xyz']));projected=[dot(tangent,s['right_xyz']),dot(tangent,s['up_xyz'])];projected=unit(projected)
                    check(name+':physical_direction_matches_route',err<max(tolerance,5e-6) and norm(sub(projected,direction))<1e-9 and rec['topology']['shell_count']==1,maximum_outline_error_m=err,actual_route_projected_uv=projected)
            actual=[v for name,rec in records.items() if name.startswith('PWF_'+sid+'_') for v in rec['world']]
            check(sid+':whole_sign_inside_contract',bool(actual) and within(bounds(actual),s['complete_envelope_xyz'],tolerance))
            sign_rows.append({'sign':sid,'actual_bounds_xyz':bounds(actual) if actual else None,'source_contract_bounds_xyz':s['complete_envelope_xyz'],'numerical_bound_comparison_allowance_m':tolerance,'physical_gap_bridging_tolerance_m':0})
        check('exact_component_and_glyph_inventory',set(actual_parts)==expected_names,unexpected=sorted(set(actual_parts)-expected_names),missing=sorted(expected_names-set(actual_parts)))
        for role,expected in d['material_roles'].items():
            mat=bpy.data.materials.get(role)
            if mat is None:check('material:'+role,False);continue
            tex=[n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'];bsdf=mat.node_tree.nodes.get('Principled BSDF')
            links=[{'from_node':link.from_node.name,'from_socket':link.from_socket.name,'to_node':link.to_node.name,'to_socket':link.to_socket.name} for link in mat.node_tree.links]
            # Blender RNA wrappers are not Python object identities. Compare the
            # underlying nodes, while checking both exact sockets and output flow.
            image_connected=len(tex)==1 and tex[0].image is not None and bsdf is not None and any(link.from_node.as_pointer()==tex[0].as_pointer() and link.to_node.as_pointer()==bsdf.as_pointer() and link.from_socket.name=='Color' and link.to_socket.name=='Base Color' for link in mat.node_tree.links)
            check(role+':complete_single_image_graph',image_connected,actual_links=links)
            outputs=[n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output]
            output_connected=bsdf is not None and len(outputs)==1 and any(link.from_node.as_pointer()==bsdf.as_pointer() and link.to_node.as_pointer()==outputs[0].as_pointer() and link.from_socket.name=='BSDF' and link.to_socket.name=='Surface' for link in mat.node_tree.links)
            check(role+':shader_connected_to_active_surface',output_connected,actual_links=links)
            if len(tex)!=1 or tex[0].image is None:continue
            image=tex[0].image;packed=image.packed_file
            check(role+':packed_retained_texture_exact',packed is not None and hashlib.sha256(bytes(packed.data)).hexdigest()==expected['sha256'])
            palette_ok=(tex[0].interpolation=='Closest' and list(image.size)==expected['texture_resolution'] and image.colorspace_settings.name=='sRGB' and len(mat.get('meters_per_tile_uv',[]))==2 and all(abs(float(a)-b)<1e-6 for a,b in zip(mat.get('meters_per_tile_uv',[]),expected['meters_per_tile_uv'])))
            roughness_ok=abs(float(bsdf.inputs['Roughness'].default_value)-expected['roughness'])<1e-6
            metallic_ok=abs(float(bsdf.inputs['Metallic'].default_value)-expected['metallic'])<1e-6
            check(role+':closest_metric_palette',palette_ok and roughness_ok and metallic_ok,roughness_matches=roughness_ok,metallic_matches=metallic_ok)
        check('no_scene_lights_or_cameras',[o for o in scene.objects if o.type in ['LIGHT','CAMERA']]==[])
        check('reference_receivers_excluded',all(ob.hide_render and ob.get('export_excluded') and not ob.get('wayfinding_export') for ob in scene.objects if ob.name.startswith('REFERENCE_')))
    except Exception as exc:
        check('verifier_completed',False,error=str(exc),traceback=traceback.format_exc())
    check('opened_source_bytes_unchanged',source.is_file() and sha(source)==before)
    report['pass']=not issues;report['status']='independent_source_reopen_pass_render_export_engine_pending' if not issues else 'fail_closed'
    report['rendered_pixel_acceptance']='NOT RUN. Geometric cap projections do not establish font rasterization, texture/effects contrast, approach occlusion or normal/effects-off readability.'
    report['export_gate']='CLOSED; this verifier never exports or grants export approval'
    report['minimum_projected_cap_px_geometric']=min((r['cap_height_px_geometric'] for r in glyph_rows),default=None)
    report['blender_version']=bpy.app.version_string
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=HERE/'source/grand_pool_wayfinding.blend');p.add_argument('--contract',type=Path,default=HERE/'wayfinding_contract.json');p.add_argument('--report',type=Path,default=HERE/'qa/wayfinding_independent_reopen.json')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if a.report.exists():raise SystemExit('Preserve existing QA report; choose a new --report path')
    if a.report.resolve()==a.source.resolve() or a.report.suffix.lower()!='.json':raise SystemExit('QA may write only a new JSON report')
    r=verify(a);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'pass':r['pass'],'report':str(a.report),'issues':r['issues'],'minimum_geometric_cap_px':r['minimum_projected_cap_px_geometric']},indent=2));raise SystemExit(0 if r['pass'] else 1)
