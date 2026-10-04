"""Original, script-assisted editable staff overhead components. Blender 4.3.2.
Every asset uses local ceiling mounting datum Z0; components hang below it.
Run: blender --background --threads 2 --python source/build_staff_overhead.py
"""
import bpy, bmesh, math, json, hashlib, importlib.util
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1]
CAT=BASE.parents[1]
PITCH=1.2
RADIUS=.6
MOUNT_HEIGHT=3.3
GAP=.002
RECORDS=[]
spec=importlib.util.spec_from_file_location('staff_materials',CAT/'standards/staff_materials.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
MATS=mod.materials()
# These keys are explicit semantic staff-only roles, supplied by the shared helper.
ROLES={'paint':'staff_white_paint','metal':'staff_zinc','dark':'staff_rubber','lens':'staff_opal','label':'staff_label','red':'staff_cable_red','blue':'staff_cable_blue'}

def reset():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for mesh in list(bpy.data.meshes):
        if mesh.users==0:bpy.data.meshes.remove(mesh)
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1

def scale(role):return tuple(MATS[ROLES[role]].get('meters_per_tile_uv',(.4,.4)))

def mesh_obj(name,verts,faces,role,bevel=0):
    me=bpy.data.meshes.new(name+'_editable_mesh');me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
    me.materials.append(MATS[ROLES[role]]);ob['material_role']=ROLES[role]
    ob['provenance']='Original script-assisted staff component; no original game geometry'
    layer=me.uv_layers.new(name='metric_material_uv');s=scale(role)
    for face in me.polygons:
        axis=max(range(3),key=lambda k:abs(face.normal[k]));axes=[k for k in range(3) if k!=axis]
        for li in face.loop_indices:
            p=me.vertices[me.loops[li].vertex_index].co;layer.data[li].uv=(p[axes[0]]/s[0],p[axes[1]]/s[1])
    if bevel:
        m=ob.modifiers.new('Editable formed-edge easing','BEVEL');m.width=bevel;m.segments=1;m.limit_method='ANGLE';m.angle_limit=math.radians(40)
        m=ob.modifiers.new('Editable weighted surface normals','WEIGHTED_NORMAL');m.keep_sharp=True;m.weight=30
    return ob

def box(name,center,dims,role='metal',bevel=.001,rotation=0):
    x,y,z=center;dx,dy,dz=[a/2 for a in dims];verts=[]
    c,s=math.cos(rotation),math.sin(rotation)
    for xx,yy,zz in [(-dx,-dy,-dz),(dx,-dy,-dz),(dx,dy,-dz),(-dx,dy,-dz),(-dx,-dy,dz),(dx,-dy,dz),(dx,dy,dz),(-dx,dy,dz)]:
        verts.append((x+xx*c-yy*s,y+xx*s+yy*c,z+zz))
    return mesh_obj(name,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel)

def station(kind,s):
    if kind=='straight':return (s,0,1,0,s)
    t=s/RADIUS;return(RADIUS*math.sin(t),RADIUS*(1-math.cos(t)),math.cos(t),math.sin(t),s)

def stations(kind,a=None,b=None,step=None):
    total=PITCH if kind=='straight' else RADIUS*math.pi/2
    a=.001 if a is None else a;b=total-.001 if b is None else b
    n=1 if kind=='straight' else max(1,math.ceil(abs(b-a)/(step or (RADIUS*math.pi/36))))
    rows=[station(kind,a+(b-a)*i/n) for i in range(n+1)]
    if a==.001:rows[0]=(.001,0,1,0,.001)
    if b==total-.001 and kind=='turn':rows[-1]=(RADIUS,RADIUS-.001,0,1,b)
    return rows

def sweep(name,rows,profile,role='metal',bevel=.0006):
    n=len(profile);verts=[];faces=[]
    for x,y,tx,ty,s in rows:verts.extend((x-ty*d,y+tx*d,z) for d,z in profile)
    for k in range(len(rows)-1):faces.extend((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for j in range(n))
    faces.extend([tuple(reversed(range(n))),tuple((len(rows)-1)*n+j for j in range(n))])
    ob=mesh_obj(name,verts,faces,role,bevel);me=ob.data;uv=me.uv_layers.active;scl=scale(role)
    per=[0]
    for a,b in zip(profile,profile[1:]):per.append(per[-1]+math.dist(a,b))
    perimeter=per[-1]+math.dist(profile[-1],profile[0])
    for face in me.polygons:
        cap=face.index>=len(faces)-2;edge=face.index%n
        for li in face.loop_indices:
            k,j=divmod(me.loops[li].vertex_index,n);d,z=profile[j]
            uv.data[li].uv=(d/scl[0],z/scl[1]) if cap else ((perimeter if edge==n-1 and j==0 else per[j])/scl[0],rows[k][4]/scl[1])
    ob['formed_section_dz_m']=json.dumps(profile)
    return ob

def tube(name,rows,d,z,r,role='metal',segments=10):
    return sweep(name,rows,[(d+r*math.cos(2*math.pi*i/segments),z+r*math.sin(2*math.pi*i/segments)) for i in range(segments)],role,0)

def cylinder_between(name,a,b,r,role='metal',segments=8):
    a,b=Vector(a),Vector(b);axis=(b-a).normalized();seed=Vector((1,0,0)) if abs(axis.x)<.9 else Vector((0,1,0));u=axis.cross(seed).normalized();v=axis.cross(u)
    verts=[p+r*(u*math.cos(t)+v*math.sin(t)) for p in(a,b) for t in[2*math.pi*i/segments for i in range(segments)]]
    faces=[(i,(i+1)%segments,segments+(i+1)%segments,segments+i) for i in range(segments)]+[tuple(reversed(range(segments))),tuple(segments+i for i in range(segments))]
    return mesh_obj(name,verts,faces,role,0)

def support(kind,s,index,objects,anchors):
    x,y,tx,ty,_=station(kind,s);ang=math.atan2(ty,tx)
    objects.append(box(f'support_{index}_formed_crossbeam',(x,y,-.412),(.055,.73,.028),'metal',.001,ang))
    # Ceiling plates, short hex nuts and rods form one visible load path each side.
    for sign in(-1,1):
        px,py=x-ty*sign*.327,y+tx*sign*.327
        objects.append(box(f'support_{index}_{sign:+d}_ceiling_anchor_plate',(px,py,-.006),(.105,.075,.012),'metal',.001,ang))
        objects.append(cylinder_between(f'support_{index}_{sign:+d}_suspension_rod',(px,py,-.442),(px,py,-.011),.006,'metal',8))
        objects.append(cylinder_between(f'support_{index}_{sign:+d}_beam_retaining_nut',(px,py,-.438),(px,py,-.426),.012,'metal',6))
        objects.append(cylinder_between(f'support_{index}_{sign:+d}_anchor_nut',(px,py,-.027),(px,py,-.012),.012,'metal',6))
        anchors.append({'name':f'support_{index}_{sign:+d}','position_m':[px,py,0],'normal':[0,0,1],'plate_size_m':[.105,.075,.012],'status':'geometric ceiling anchor proposal; substrate/load ratings unverified'})

def collar_sections():
    # Exit collars surround the formed side rails and bridge the 2 mm seam.
    return [[(-.303,-.405),(-.268,-.405),(-.268,-.399),(-.297,-.399),(-.297,-.264),(-.273,-.264),(-.273,-.258),(-.303,-.258)],
            [(.303,-.405),(.268,-.405),(.268,-.399),(.297,-.399),(.297,-.264),(.273,-.264),(.273,-.258),(.303,-.258)]]

def service(kind):
    objects=[];anchors=[];rows=stations(kind);total=PITCH if kind=='straight' else RADIUS*math.pi/2
    rail=[(-.294,-.398),(-.264,-.398),(-.264,-.391),(-.286,-.391),(-.286,-.276),(-.266,-.276),(-.266,-.268),(-.294,-.268)]
    for side,p in [('left',rail),('right',[(-d,z) for d,z in rail])]:objects.append(sweep('formed_'+side+'_return_lip_rail',rows,p,'metal'))
    rung_ss=[.09,.34,.60,.86,1.11] if kind=='straight' else [total*t for t in(.06,.27,.5,.73,.94)]
    for i,s in enumerate(rung_ss):
        x,y,tx,ty,_=station(kind,s);angle=math.atan2(ty,tx)
        objects.append(box(f'ladder_rung_{i+1:02d}_folded_pan',(x,y,-.402),(.054,.571,.028),'metal',.001,angle))
        # Padded band with two side feet visibly holds orderly services to the rung.
        for d in(.03,.158):
            objects.append(box(f'service_{i+1:02d}_saddle_{d:+.3f}',(x-ty*d,y+tx*d,-.387),(.041,.061,.012),'dark',.001,angle))
    services=[('large_conduit',.16,-.348,.033,'metal'),('small_conduit',.032,-.359,.022,'metal'),('cable_A',-.08,-.374,.014,'blue'),('cable_B',-.119,-.372,.016,'dark'),('cable_C',-.165,-.370,.018,'red')]
    for name,d,z,r,role in services:
        objects.append(tube(name+'_continuous_ordered_run',rows,d,z,r,role,12 if role=='metal' else 8))
        if role=='metal':
            # Slip sleeve at exit; sleeves clear the neighbouring module's pipe.
            sleeve=[(d+(r+.006)*math.cos(2*math.pi*i/12),z+(r+.006)*math.sin(2*math.pi*i/12)) for i in range(12)]
            # A hollow ring preserves the real service cap, yet avoids a sleeve end disk.
            for s0,s1 in[(total-.040,total+.035)]:
                objects.append(ring_sweep(name+'_exit_union_sleeve',exit_rows(kind,s0,s1),d,z,r+.003,r+.008,'metal'))
        else:
            objects.append(tube(name+'_end_identification_band',stations(kind,total-.11,total-.08),d,z,r+.0018,'label',8))
    for i,p in enumerate(collar_sections()):objects.append(sweep(f'exit_splice_collar_{i+1}',exit_rows(kind,total-.042,total+.035),p,'paint',.0004))
    for s in [total-.025,total+.023]:
        x,y,tx,ty,_=exit_rows(kind,s,s)[0]
        for side in [-1,1]:
            objects.append(cylinder_between(f'exit_splice_fastener_{s:.3f}_{side:+d}',(x-ty*side*.307,y+tx*side*.307,-.321),(x-ty*side*.278,y+tx*side*.278,-.321),.006,'metal',6))
    for i,s in enumerate([.24,.96] if kind=='straight' else[total*.25,total*.75]):support(kind,s,i+1,objects,anchors)
    # On the straight, six cable tie bridges have a deliberate underside and feet.
    for i,s in enumerate([.22,.96] if kind=='straight' else[total*.23,total*.77]):
        x,y,tx,ty,_=station(kind,s);ang=math.atan2(ty,tx)
        objects.append(box(f'cable_retainer_{i+1}_bridge',(x-ty*(-.128),y+tx*(-.128),-.348),(.014,.136,.005),'label',.0005,ang))
        for d in(-.196,-.061):objects.append(box(f'cable_retainer_{i+1}_foot_{d}',(x-ty*d,y+tx*d,-.370),(.014,.008,.044),'label',.0005,ang))
    return objects,anchors

def exit_rows(kind,a,b):
    total=PITCH if kind=='straight' else RADIUS*math.pi/2
    if kind=='straight':return[(a,0,1,0,a),(b,0,1,0,b)]
    return[(RADIUS,RADIUS+a-total,0,1,a),(RADIUS,RADIUS+b-total,0,1,b)]

def ring_sweep(name,rows,d,z,ri,ro,role):
    n=12;profile=[]
    # Radial walls and annular end caps: generated as rings, with actual planar UVs.
    verts=[]
    for x,y,tx,ty,s in rows:
        for r in(ro,ri):verts.extend((x-ty*(d+r*math.cos(2*math.pi*i/n)),y+tx*(d+r*math.cos(2*math.pi*i/n)),z+r*math.sin(2*math.pi*i/n)) for i in range(n))
    faces=[]
    for i in range(n):
        j=(i+1)%n;faces.extend([(i,j,2*n+j,2*n+i),(n+j,n+i,3*n+i,3*n+j),(j,i,n+i,n+j),(2*n+i,2*n+j,3*n+j,3*n+i)])
    return mesh_obj(name,verts,faces,role,0)

def fixture():
    objects=[];anchors=[]
    # 1.12 m formed body: stepped return lips, shallow reflector and two end closures.
    profile=[(-.159,-.424),(.159,-.424),(.173,-.454),(.173,-.527),(.150,-.537),(.142,-.526),(.158,-.518),(.158,-.456),(.149,-.440),(-.149,-.440),(-.158,-.456),(-.158,-.518),(-.142,-.526),(-.150,-.537),(-.173,-.527),(-.173,-.454)]
    objects.append(sweep('formed_enamel_channel_with_return_lips',[(.04,0,1,0,.04),(1.16,0,1,0,1.16)],profile,'paint',.001))
    reflector=[(-.141,-.474),(-.107,-.502),(0,-.485),(.107,-.502),(.141,-.474),(.137,-.469),(.104,-.494),(0,-.478),(-.104,-.494),(-.137,-.469)]
    objects.append(sweep('twin_bay_folded_reflector',[(.07,0,1,0,.07),(1.13,0,1,0,1.13)],reflector,'metal',.0005))
    # Opaque opal geometry only; zero emission, no runtime lights.
    lens=[(-.127,-.510),(.127,-.510),(.139,-.527),(.127,-.552),(.110,-.561),(-.110,-.561),(-.127,-.552),(-.139,-.527)]
    objects.append(sweep('continuous_opal_prismatic_lens',[(.086,0,1,0,.086),(1.114,0,1,0,1.114)],lens,'lens',.001))
    for i,x in enumerate((.064,1.136)):
        objects.append(box(f'closed_formed_end_cap_{i+1}',(x,0,-.493),(.042,.32,.117),'paint',.002))
        objects.append(box(f'end_cap_gasket_{i+1}',(x+(.022 if i==0 else-.022),0,-.494),(.007,.292,.100),'dark',.001))
        objects.append(box(f'captive_lens_clip_{i+1}',(x+(.033 if i==0 else-.033),0,-.556),(.019,.046,.013),'metal',.001))
    # Two rigid stem mounts connect to the ceiling datum, with plates and locks.
    for i,x in enumerate((.24,.96)):
        objects.append(box(f'fixture_mount_{i+1}_ceiling_plate',(x,0,-.006),(.105,.090,.012),'metal',.001))
        objects.append(box(f'fixture_mount_{i+1}_folded_drop',(x,0,-.215),(.038,.030,.412),'metal',.001))
        objects.append(box(f'fixture_mount_{i+1}_housing_saddle',(x,0,-.432),(.065,.128,.024),'metal',.001))
        objects.append(cylinder_between(f'fixture_mount_{i+1}_locking_pin',(x,-.043,-.404),(x,.043,-.404),.008,'metal',8))
        anchors.append({'name':f'fixture_ceiling_anchor_{i+1}','position_m':[x,0,0],'normal':[0,0,1],'status':'geometric anchor proposal only'})
    # Guard has two longitudinal rails and three arched standoffs, clear of lens.
    for y in(-.119,.119):objects.append(cylinder_between(f'lens_guard_longitudinal_{y}',(.065,y,-.603),(1.135,y,-.603),.0045,'metal',8))
    for i,x in enumerate((.095,.6,1.105)):
        pp=[(x,-.158,-.518),(x,-.158,-.572),(x,-.119,-.603),(x,.119,-.603),(x,.158,-.572),(x,.158,-.518)]
        for j,(a,b) in enumerate(zip(pp,pp[1:])):objects.append(cylinder_between(f'guard_hoop_{i+1}_segment_{j+1}',a,b,.0045,'metal',8))
    # Cable entry is a closed gland; it is not an electrical connection simulation.
    objects.append(cylinder_between('sealed_top_cable_entry_gland',(.6,.076,-.433),(.6,.076,-.401),.016,'dark',10))
    objects.append(box('small_service_identification_tab',(.62,-.174,-.475),(.12,.002,.024),'label',.0004))
    return objects,anchors

def measure(objects):
    dg=bpy.context.evaluated_depsgraph_get();pts=[];triangles=0
    for ob in objects:
        ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();triangles+=len(me.loop_triangles);pts.extend(ob.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
    lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)]
    return {'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]},triangles

def export(objects,path,ident):
    dg=bpy.context.evaluated_depsgraph_get();groups={}
    for src in objects:
        me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));active=me.uv_layers.active
        for layer in list(me.uv_layers):
            if layer!=active:me.uv_layers.remove(layer)
        active.name='metric_material_uv';active.active_render=True
        me.calc_loop_triangles();fix=set();s=tuple(MATS[src['material_role']].get('meters_per_tile_uv',(.4,.4)))
        for tr in me.loop_triangles:
            a,b,c=[active.data[i].uv for i in tr.loops]
            if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<2e-12:fix.add(tr.polygon_index)
        for pi in fix:
            p=me.polygons[pi];axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
            for li in p.loop_indices:
                co=me.vertices[me.loops[li].vertex_index].co;active.data[li].uv=(co[axes[0]]/s[0],co[axes[1]]/s[1])
        ob=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=src.matrix_world.copy();groups.setdefault(src['material_role'],[]).append(ob)
    runtime=[]
    for role,parts in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for ob in parts:ob.select_set(True)
        bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();ob=parts[0];ob.name=ident+'__'+role;ob['material_role']=role;ob['semantic_parts']=json.dumps([s.name for s in objects if s['material_role']==role]);runtime.append(ob)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in runtime:ob.select_set(True)
    bpy.context.view_layer.objects.active=runtime[0]
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
    for ob in runtime:bpy.data.objects.remove(ob,do_unlink=True)

def manifest(kind,ident,title,objects,anchors,bounds,tri):
    total=PITCH if kind=='straight' else RADIUS*math.pi/2
    joins=[]
    if kind!='fixture':
        joins=[{'id':'entry','origin_m':[0,0,0],'outward_tangent':[-1,0,0],'seam_plane':'X0','body_inset_m':.001,'receiver':'No entry collar; receives preceding exit collar'},
               {'id':'exit','origin_m':[PITCH,0,0] if kind=='straight' else[RADIUS,RADIUS,0],'outward_tangent':[1,0,0] if kind=='straight' else[0,1,0],'seam_plane':'X1.2' if kind=='straight' else'Y0.6','body_inset_m':.001,'exit_splice_extension_m':.035}]
    lowest=bounds['min_m'][2]
    return {'catalogue_id':ident,'title':title,'unique_design':True,'kind':kind,'units':'metres','source':'source/'+ident+'.blend','export':'exports/'+ident+'.glb','generator':'source/build_staff_overhead.py','script_assisted_original_design':True,
      'coordinates':'Blender Z up. Ceiling mounting datum at local Z0, hangs negative Z. Straight travel +X; turn exits +Y; fixture long axis +X. GLB standard Y-up conversion.',
      'pivot':{'position_m':[0,0,0],'datum':'Ceiling support plane at entry centreline, or fixture pitch start'},'bounds_blender_z_up':bounds,'evaluated_triangles':tri,'editable_semantic_parts':len(objects),'semantic_parts':[ob.name for ob in objects],
      'material_roles':sorted(set(ob['material_role'] for ob in objects)),'runtime_static_consolidation':'One mesh per semantic material role; active UV names normalized before join; real planar end caps; no runtime light objects',
      'nominal_straight_pitch_m':1.2,'turn_centerline_radius_m':RADIUS if kind=='turn' else None,'joins':joins,'ceiling_support_anchors':anchors,
      'lowest_geometry_z_m':lowest,'lowest_geometry_semantics':'guard rails/hoops' if kind=='fixture' else'suspension rod ends',
      'inspection_clearance_example':{'ceiling_datum_world_z_m':MOUNT_HEIGHT,'world_lowest_geometry_z_m':MOUNT_HEIGHT+lowest,'minimum_requested_clearance_m':2.65,'minimum_mounting_datum_for_2_65m_m':2.65-lowest,'installation_limit':'The fixture needs a mounting datum at least 3.2575 m for 2.65 m clearance; the 3.30 m example does not certify lower corridors or real ship routes.','meets_example':MOUNT_HEIGHT+lowest>=2.65,'limitation':'Component inspection placement only. No claim of actual ship route headroom, structural safety or installation'},
      'fixture_anchor_data_only':{'housing_centre_m':[.6,0,-.493],'lens_down_direction':[0,0,-1],'electrical_function':'None; opaque unlit lens material, no light nodes, cable entry is geometric only'} if kind=='fixture' else None,
      'hanger_length_editability':'Named rod/drop meshes and support dimensions are editable in source/generator. No single validated hanger-length parameter or tested shorter installation is provided.',
      'support_proposal':'Two paired ceiling rod supports with plates, crossbeams and retaining nuts' if kind!='fixture' else'Two rigid ceiling drops, plated anchors, housing saddles and locking pins',
      'collision_proposal_file':'collision_proposals.json','reference_manifest':'../../batches/batch03/reference_manifest.json','dependencies':['../../standards/staff_materials.py','../../materials/staff/'],
      'limitations':['Not installed in original ship','No electrical or photometric function','No engine/route/structural/load rating verification','No new game systems or room allocation']}

def collisions(kind):
    if kind=='fixture':return {'type':'separate_box_proposals','boxes':[{'semantic_part':'housing_and_guard','min_m':[.04,-.177,-.61],'max_m':[1.16,.177,-.424]},{'semantic_part':'mount_left','min_m':[.1875,-.045,-.424],'max_m':[.2925,.045,0]},{'semantic_part':'mount_right','min_m':[.9075,-.045,-.424],'max_m':[1.0125,.045,0]}],'note':'Keep clearance below guard; proposal is not active physics'}
    out=[];rows=stations(kind,0,PITCH if kind=='straight' else RADIUS*math.pi/2,step=RADIUS*math.pi/12)
    for a,b in zip(rows,rows[1:]):
        points=[]
        for x,y,tx,ty,s in(a,b):points.extend([[x-ty*d,y+tx*d,z] for d,z in[(-.305,-.416),(.305,-.416),(.305,-.255),(-.305,-.255)]])
        out.append({'semantic_part':'tray_service_envelope_segment','type':'convex_hull_points','points_m':points})
    return {'type':'segmented_overhead_envelopes','hulls':out,'separate_supports':'Use each source support crossbeam/rod bound if required; never extend one convex collider down into circulation','note':'Static proposal only; expected walk/cart space remains below measured lowest geometry'}

def main():
    bpy.context.preferences.filepaths.save_version=0
    collision={};api={}
    for kind,ident,title in [('straight','AST-STF-004','Supported straight service run'),('turn','AST-STF-005','Compatible quarter-turn service junction'),('fixture','AST-STF-006','Guarded utility light housing')]:
        reset();objects,anchors=fixture() if kind=='fixture' else service(kind);bounds,tri=measure(objects)
        rec=manifest(kind,ident,title,objects,anchors,bounds,tri);bpy.context.scene['component_scope']='Independent staff component. No game/ship installation.';bpy.context.scene['catalogue_id']=ident;bpy.context.scene['mounting_datum']='Z0 at ceiling; lowest geometry '+str(bounds['min_m'][2])
        for im in bpy.data.images:
            if im.source=='FILE' and not im.packed_file:im.pack()
        bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'),compress=True)
        export(objects,BASE/'exports'/f'{ident}.glb',ident)
        rec['source_sha256']=hashlib.sha256((BASE/'source'/f'{ident}.blend').read_bytes()).hexdigest();rec['glb_sha256']=hashlib.sha256((BASE/'exports'/f'{ident}.glb').read_bytes()).hexdigest()
        (BASE/f'{ident}.manifest.json').write_text(json.dumps(rec,indent=2)+'\n');RECORDS.append(rec);collision[ident]=collisions(kind);api[ident]={'joins':rec['joins'],'ceiling_anchors':anchors,'lowest_geometry_z_m':rec['lowest_geometry_z_m']}
    (BASE/'manifest.json').write_text(json.dumps({'family':'Staff overhead service components','unique_design_count':3,'assets':RECORDS},indent=2)+'\n')
    (BASE/'collision_proposals.json').write_text(json.dumps(collision,indent=2)+'\n')
    (BASE/'mounting_api.json').write_text(json.dumps({'units':'metres; Blender Z up','assets':api,'inspection_assembly':[
      {'instance':'approach_run','id':'AST-STF-004','translation_m':[-1.2,0,MOUNT_HEIGHT],'rotation_z_degrees':0},
      {'instance':'quarter_turn','id':'AST-STF-005','translation_m':[0,0,MOUNT_HEIGHT],'rotation_z_degrees':0},
      {'instance':'exit_run','id':'AST-STF-004','translation_m':[.6,.6,MOUNT_HEIGHT],'rotation_z_degrees':90},
      {'instance':'adjacent_fixture','id':'AST-STF-006','translation_m':[-1.2,-.73,MOUNT_HEIGHT],'rotation_z_degrees':0}],
      'seam_policy':{'body_gap_m':.002,'exit_collar_extension_m':.035,'collar_overlap_is_intentional':True,'collar_joint':'Painted rail collar bridges seam on exterior of both side rails; hollow metal conduit sleeves enclose following conduit; cable ends have 2 mm seam gap. No structural/utility continuity claim.'},
      'clearance_example':{'mount_height_m':MOUNT_HEIGHT,'lowest_fixture_world_z_m':MOUNT_HEIGHT+RECORDS[2]['lowest_geometry_z_m'],'floor_z_m':0,'clear_body_cart_width_m':1.8,'width_scope':'Open inspection aid footprint; not real ship route'}} ,indent=2)+'\n')
    print('STAFF_OVERHEAD_COMPLETE',[(r['catalogue_id'],r['evaluated_triangles'],r['lowest_geometry_z_m']) for r in RECORDS])
if __name__=='__main__':main()
