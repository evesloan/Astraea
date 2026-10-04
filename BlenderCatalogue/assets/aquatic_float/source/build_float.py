"""AST-AQU-006 Cove leisure float: original script-assisted editable mesh design.
Blender 4.3.2: blender -b -t 2 --python source/build_float.py
Z0 is the proposed design waterline at the XY centre, never a buoyancy result.
"""
import bpy,bmesh,math,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1];ID='AST-AQU-006'
spec=importlib.util.spec_from_file_location('aquatic_materials',CAT/'standards/aquatic_materials.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
MATS=m.materials();PARTS=[];JOINS=[]
ROLES={'orange':'aquatic_orange_float','pearl':'aquatic_pearl_float','teal':'aquatic_teal_sling','grip':'aquatic_dark_grip'}
A=.505;B=.605;N=96;Q=20

def ring_frame(t):
    # Oval normal follows ellipse geometry, not a scaled default torus.
    nx=math.sin(t)/A;ny=-math.cos(t)/B;nn=math.hypot(nx,ny);nx/=nn;ny/=nn
    rear=((1-math.cos(t))/2)**5
    horizontal=.200+.015*rear;vertical=.184+.118*rear;z=.022+.216*rear
    return Vector((A*math.sin(t),-B*math.cos(t),z)),Vector((nx,ny,0)),horizontal,vertical

def ring_point(t,p,offset=0):
    c,n,h,v=ring_frame(t)
    return c+n*((h+offset)*math.cos(p))+Vector((0,0,(v+offset)*math.sin(p)))

def mesh(name,verts,faces,role,smooth=True):
    me=bpy.data.meshes.new(name+'_editable');me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(MATS[ROLES[role]]);ob['material_role']=ROLES[role];ob['original_design']='Script-assisted original aquatic component; no original game geometry'
    uv=me.uv_layers.new(name='metric_material_uv');scale=MATS[ROLES[role]]['meters_per_tile_uv']
    for p in me.polygons:
        p.use_smooth=smooth;axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
        for li in p.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]]/scale[0],co[axes[1]]/scale[1])
    PARTS.append(ob);return ob

def set_sweep_uv(ob,rows,cols,us,vs):
    # Per-corner UV seam unwrap; closed wrap carries the complete metric distance.
    uv=ob.data.uv_layers.active;s=MATS[ob['material_role']]['meters_per_tile_uv']
    for p in ob.data.polygons:
        r=p.index//cols;j=p.index%cols
        for li in p.loop_indices:
            a,b=divmod(ob.data.loops[li].vertex_index,cols);u=us[-1] if r==rows-1 and a==0 else us[a];v=vs[-1] if j==cols-1 and b==0 else vs[b]
            uv.data[li].uv=(u/s[0],v/s[1])

def hull():
    verts=[ring_point(2*math.pi*i/N,2*math.pi*j/Q) for i in range(N) for j in range(Q)]
    faces=[(i*Q+j,((i+1)%N)*Q+j,((i+1)%N)*Q+(j+1)%Q,i*Q+(j+1)%Q) for i in range(N) for j in range(Q)]
    ob=mesh('continuous_oval_hull_with_raised_back_cradle',verts,faces,'orange')
    ob['shape_intent']='Variable elliptical coaming: lower front boarding/leg rim, full side supports, taller rear lower-back/head cradle; continuous closed mesh'
    us=[0]
    for i in range(N):us.append(us[-1]+(ring_frame(2*math.pi*((i+1)%N)/N)[0]-ring_frame(2*math.pi*i/N)[0]).length)
    vs=[0]
    for j in range(Q):vs.append(vs[-1]+(ring_point(0,2*math.pi*(j+1)/Q)-ring_point(0,2*math.pi*j/Q)).length)
    set_sweep_uv(ob,N,Q,us,vs)
    return ob

def shell_patch(name,t0,t1,p0,p1,nt=10,np=12):
    # Closed flexible applique, 4 mm inset into skin + 4 mm raised relief.
    verts=[]
    for off in(-.004,.004):
        for i in range(nt+1):
            for j in range(np+1):verts.append(ring_point(t0+(t1-t0)*i/nt,p0+(p1-p0)*j/np,off))
    k=(nt+1)*(np+1);faces=[]
    for layer in range(2):
        for i in range(nt):
            for j in range(np):
                a=layer*k+i*(np+1)+j;faces.append((a,a+1,a+np+2,a+np+1))
    boundary=[i*(np+1) for i in range(nt+1)]+[nt*(np+1)+j for j in range(1,np+1)]+[i*(np+1)+np for i in range(nt-1,-1,-1)]+[j for j in range(np-1,0,-1)]
    faces.extend((a,b,b+k,a+k) for a,b in zip(boundary,boundary[1:]+boundary[:1]))
    ob=mesh(name,verts,faces,'pearl');JOINS.append({'parts':[ob.name,'continuous_oval_hull_with_raised_back_cradle'],'method':'conforming closed flexible skin applique','radial_skin_inset_m':.004,'raised_relief_m':.004});return ob

def tube(name,centers,r,role='pearl',sides=8,closed=False):
    verts=[]
    for i,c in enumerate(centers):
        tangent=(centers[(i+1)%len(centers)]-centers[(i-1)%len(centers)] if closed else centers[min(i+1,len(centers)-1)]-centers[max(i-1,0)]).normalized()
        seed=Vector((0,0,1)) if abs(tangent.z)<.95 else Vector((1,0,0));u=tangent.cross(seed).normalized();v=tangent.cross(u)
        verts.extend(c+r*(u*math.cos(2*math.pi*j/sides)+v*math.sin(2*math.pi*j/sides)) for j in range(sides))
    faces=[];rows=len(centers)
    for i in range(rows if closed else rows-1):
        faces.extend((i*sides+j,((i+1)%rows)*sides+j,((i+1)%rows)*sides+(j+1)%sides,i*sides+(j+1)%sides) for j in range(sides))
    if not closed:faces.extend([tuple(reversed(range(sides))),tuple((rows-1)*sides+j for j in range(sides))])
    return mesh(name,verts,faces,role)

def ellipsoid(name,center,scale,role,segments=16,rings=8):
    verts=[Vector(center)+Vector((0,0,-scale[2]))]
    for j in range(1,rings):
        phi=-math.pi/2+math.pi*j/rings
        for i in range(segments):
            t=2*math.pi*i/segments;verts.append(Vector(center)+Vector((scale[0]*math.cos(phi)*math.cos(t),scale[1]*math.cos(phi)*math.sin(t),scale[2]*math.sin(phi))))
    top=len(verts);verts.append(Vector(center)+Vector((0,0,scale[2])));faces=[]
    for i in range(segments):faces.append((0,1+(i+1)%segments,1+i))
    for j in range(rings-2):
        for i in range(segments):a=1+j*segments+i;b=1+j*segments+(i+1)%segments;faces.append((a,b,b+segments,a+segments))
    for i in range(segments):faces.append((top,1+(rings-2)*segments+i,1+(rings-2)*segments+(i+1)%segments))
    return mesh(name,verts,faces,role)

def seat():
    n=64;radial=7;rs=[.055+(1-.055)*i/radial for i in range(radial+1)];center=Vector((0,-.06,-.064));edge=[]
    for j in range(n):
        c,normal,h,v=ring_frame(2*math.pi*j/n);edge.append(c-normal*(h-.025)+Vector((0,0,.004)))
    verts=[]
    for bottom in(0,1):
        for r in rs:
            for e in edge:
                p=center+(e-center)*r;p.z=center.z+(e.z-center.z)*r*r-bottom*.012;verts.append(p)
    k=(radial+1)*n;faces=[]
    for layer in range(2):
        for i in range(radial):
            for j in range(n):a=layer*k+i*n+j;b=layer*k+i*n+(j+1)%n;faces.append((a,b,b+n,a+n))
    for i in(0,radial):
        faces.extend((i*n+j,i*n+(j+1)%n,k+i*n+(j+1)%n,k+i*n+j) for j in range(n))
    ob=mesh('recessed_tensioned_seat_membrane_with_drain_aperture',verts,faces,'teal');ob['nominal_thickness_m']=.012
    # The flexible welt follows the membrane perimeter, inset in body for continuous contact.
    welt_centers=[]
    for j,e in enumerate(edge):
        c,normal,h,v=ring_frame(2*math.pi*j/64)
        welt_centers.append(e-normal*.025)
    welt=tube('continuous_flexible_seat_attachment_welt',welt_centers,.014,'pearl',8,True)
    drain=[Vector((center.x+(e.x-center.x)*rs[0],center.y+(e.y-center.y)*rs[0],center.z+(e.z-center.z)*rs[0]**2+.001)) for e in edge]
    tube('soft_bound_central_drain_aperture',drain,.0035,'grip',6,True)
    JOINS.append({'parts':[ob.name,welt.name,'continuous_oval_hull_with_raised_back_cradle'],'method':'membrane perimeter and flexible binding inset into coaming','nominal_radial_overlap_m':.025,'continuous_attachment_samples':n,'claim':'Geometric joining proposal; no fabric tension/load test'})
    return edge

def handles():
    anchors=[];contacts=[]
    for sign,side in[(-1,'left'),(1,'right')]:
        centers=[]
        for i in range(21):
            f=i/20;y=-.30+.42*f;t=math.acos(-y/B);t=t if sign>0 else 2*math.pi-t
            p=ring_point(t,math.pi/2);p.z+=-.014+.158*math.sin(math.pi*f)**.75;centers.append(p)
        grip=tube(side+'_arched_continuous_grip',centers,.023,'grip',10)
        for j,p in enumerate([centers[0],centers[-1]]):
            saddle=ellipsoid(side+f'_grip_foot_{j+1}_welded_flexible_saddle',p+Vector((0,0,-.002)),(.078,.070,.024),'pearl')
            JOINS.append({'parts':[grip.name,saddle.name],'method':'closed grip end embedded in reinforced saddle','endpoint_center_m':list(p),'grip_radius_m':.023,'saddle_center_offset_z_m':-.002,'expected_endpoint_inside_saddle':True})
            JOINS.append({'parts':[saddle.name,'continuous_oval_hull_with_raised_back_cradle'],'method':'saddle lower half embedded in coaming','saddle_center_m':list(p+Vector((0,0,-.002))),'saddle_bottom_below_coaming_crown_m':.040})
            anchors.append({'side':side,'foot':j+1,'position_m':list(p),'saddle_dimensions_m':[.156,.140,.048]})
        contacts.append({'side':side,'center_m':list(centers[10]),'tangent':[0,1,0],'grip_diameter_m':.046,'unobstructed_palm_span_approx_m':.22,'claim':'Grip contact proposal; no species reach or gripping animation test'})
    return anchors,contacts

def measure():
    pts=[];tri=0
    for o in PARTS:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles);pts.extend(o.matrix_world@v.co for v in o.data.vertices)
    lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)]
    return {'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]},tri

def export(path):
    groups={};dg=bpy.context.evaluated_depsgraph_get()
    for src in PARTS:
        me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));active=me.uv_layers.active
        for layer in list(me.uv_layers):
            if layer!=active:me.uv_layers.remove(layer)
        active.name='metric_material_uv';active.active_render=True
        # Repair only truly collapsed tiny corner UVs by triangle-safe dominant-axis per face projection.
        me.calc_loop_triangles();fix=set();sc=MATS[src['material_role']]['meters_per_tile_uv']
        for tr in me.loop_triangles:
            a,b,c=[active.data[i].uv for i in tr.loops]
            if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<2e-12:fix.add(tr.polygon_index)
        for pi in fix:
            p=me.polygons[pi];axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
            for li in p.loop_indices:
                co=me.vertices[me.loops[li].vertex_index].co;active.data[li].uv=(co[axes[0]]/sc[0],co[axes[1]]/sc[1])
        o=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(o);groups.setdefault(src['material_role'],[]).append(o)
    out=[]
    for role,parts in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in parts:o.select_set(True)
        bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=parts[0];o.name=ID+'__'+role;o['material_role']=role;o['semantic_parts']=json.dumps([p.name for p in PARTS if p['material_role']==role]);out.append(o)
    bpy.ops.object.select_all(action='DESELECT')
    for o in out:o.select_set(True)
    bpy.context.view_layer.objects.active=out[0];bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
    for o in out:bpy.data.objects.remove(o,do_unlink=True)

def main():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    hull()
    # Broad asymmetrical resort accent hierarchy follows the formed skin, not box attachments.
    shell_patch('rear_pearl_headrest_crescent',math.pi-.66,math.pi+.66,.36,2.70,20,10)
    shell_patch('front_pearl_boarding_band',-.235,.235,-.18,2.88,8,12)
    shell_patch('left_pearl_quarter_band',4.91,5.15,-.25,2.62,4,12)
    shell_patch('right_pearl_quarter_band',1.13,1.37,-.25,2.62,4,12)
    # Equatorial welded seam: closed tiny bead follows the hull side as a readable construction line.
    tube('perimeter_flexible_weld_seam',[ring_point(2*math.pi*i/96,-.12,-.001) for i in range(96)],.005,'orange',6,True)
    edge=seat();anchors,contacts=handles()
    # Soft valve boss is closed; no inflation, pressure or interaction implementation.
    valve_center=ring_point(math.pi,0,-.005)
    valve=ellipsoid('rear_recessed_soft_valve_boss',valve_center,(.042,.018,.033),'grip',12,6)
    JOINS.append({'parts':[valve.name,'continuous_oval_hull_with_raised_back_cradle'],'method':'soft valve boss intersects rear skin by 5 mm radial inset','geometric_only':True})
    seat_contacts=[]
    for x in(-.12,.12):
        hit,loc,normal,face=bpy.data.objects['recessed_tensioned_seat_membrane_with_drain_aperture'].ray_cast(Vector((x,-.06,1)),Vector((0,0,-1)))
        assert hit
        seat_contacts.append({'position_m':list(loc),'normal':list(normal),'status':'Measured surface location; actor contact remains a proposal'})
    nominal_head=ring_point(math.pi,2.20,.004);head_normal=Vector((0,math.cos(2.20)/.219,math.sin(2.20)/.306)).normalized()
    head_hit,head_point,head_norm,head_face=bpy.data.objects['rear_pearl_headrest_crescent'].ray_cast(nominal_head+head_normal*.10,-head_normal)
    assert head_hit
    bounds,tri=measure();scene['catalogue_id']=ID;scene['datum']='Design centre at proposed waterline Z0; this does not calculate flotation';scene['authoring']='Original script-assisted intentional editable design'
    bpy.ops.object.select_all(action='DESELECT')
    for o in PARTS:o.select_set(True)
    bpy.context.view_layer.objects.active=PARTS[0]
    source=BASE/'source'/f'{ID}.blend';glb=BASE/'exports'/f'{ID}.glb';bpy.ops.wm.save_as_mainfile(filepath=str(source));export(glb)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    manifest={'catalogue_id':ID,'title':'Cove leisure seating float','unique_design':True,'script_assisted_original_design':True,'units':'metres','source':str(source.relative_to(BASE)),'export':str(glb.relative_to(BASE)),'generator':'source/build_float.py','coordinates':'Blender metres Z-up, front -Y, rear back/head cradle +Y; standard GLB Y-up conversion','pivot':{'position_m':[0,0,0],'datum':'XY design centre on proposed calm-waterline Z0; no mass, flotation, load or buoyancy result'},'bounds_blender_z_up':bounds,'evaluated_triangles':tri,'editable_semantic_parts':len(PARTS),'semantic_parts':[o.name for o in PARTS],'material_roles':sorted(set(o['material_role'] for o in PARTS)),'material_finish_intent':{'orange_pearl':'Soft flexible float skin finish; pearl is not hard ivory enamel','teal':'Textured flexible seat sling','grip':'Dark opaque grip and soft bound drainage/valve finish'},'runtime_static_consolidation':'One evaluated mesh per material role; normalized active metric_material_uv layer; no game controller or water materials','design_proposals':{'external_nominal_width_depth_m':[1.41,1.64],'clear_well_nominal_width_depth_m':[.61,.795],'seat_center_datum_m':[0,-.06,-.064],'seat_center_datum_note':'Central drain is open; this datum is not a contact point','seat_contact_proposals':seat_contacts,'seat_well_status':'Recessed shaped membrane with actual small central drain aperture; no solid convex fill proposed above it','waterline_local_z_m':0,'front_rim_crown_z_m':.206,'rear_cradle_crown_z_m':.540,'headrest_contact_m':list(head_point),'grips':contacts,'handle_saddle_anchors':anchors,'approach_direction':[0,-1,0],'intended_occupancy':'One seated body-scale occupant proposal; species fit, mass and use remain unverified'},'support_and_join_records':JOINS,'collision_proposal_file':'collision_proposals.json','reference_manifest':'../../batches/batch05/reference_manifest.json','dependencies':['../../standards/aquatic_materials.py','../../materials/aquatic/manifest.json'],'limitations':['No physical flotation, balance, inflation, rescue or safety rating','No species fit, actor contact or animation result','No water shader, buoyancy system, controller or game integration','Component QA only; original project recovery remains pending'],'source_sha256':sha(source),'glb_sha256':sha(glb),'generator_sha256':sha(Path(__file__))}
    (BASE/f'{ID}.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(BASE/'manifest.json').write_text(json.dumps({'batch':'batch05','asset_count':1,'assets':[manifest]},indent=2)+'\n')
    # Data-only conservative split collision proposals with no convex shape across the well.
    coll={'catalogue_id':ID,'status':'Proposal only; not instantiated in a game engine','coordinate_frame':'Blender Z-up metres, same design waterline datum as visual','body_proposal':{'type':'segmented convex coaming wedges','segments':24,'construction':'For each 15 degree hull sector, create a convex hull from that sector only; do not merge sectors across the seating well','preserve_void':'Keep open XY well above the recessed membrane; no global convex hull'},'seat_proposal':{'type':'thin concave/small-convex-patch surface','construction':'Use underside/top membrane triangles or narrow local strips, excluding central drain; never an AABB that fills from membrane to rim height','top_center_z_m':-.064,'thickness_m':.012},'grip_proposal':{'type':'capsule chains along the two grip paths','radius_m':.023,'preserve_void':'Keep openings under arches; no grip AABB or one convex body filling finger space'},'excluded':'Tiny seams, flexible appliques and valve can be omitted from broadphase collision; proposed contact records retained separately','limitations':'Collision choice depends on recovered engine dynamic-body support. No solver, buoyancy or physical handling check.'}
    (BASE/'collision_proposals.json').write_text(json.dumps(coll,indent=2)+'\n');print('BUILT',ID,'parts',len(PARTS),'triangles',tri,'bounds',bounds)
if __name__=='__main__':main()
