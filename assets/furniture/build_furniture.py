"""Astraea DAY family, new independent script-assisted Blender authoring.
Run: blender -b -t 4 --python build_furniture.py
Editable source; no original game files or reference pixels are used.
"""
from pathlib import Path
import sys, math, json, hashlib
import bpy, bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent.parent
sys.path.insert(0, str(BASE / 'standards'))
from materials import materials

M={}; COMPONENTS=[]

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    global M,COMPONENTS
    M=materials();COMPONENTS=[]

def uv_metric(obj,grain='x'):
    """Project actual local metres; walnut texture V follows the part's grain axis."""
    mesh=obj.data
    if mesh.uv_layers:uv=mesh.uv_layers.active
    else:uv=mesh.uv_layers.new(name='UV_Metric_Metres')
    for poly in mesh.polygons:
        axis=max(range(3),key=lambda i:abs(poly.normal[i]))
        # V follows timber length; tile scales come from the shared material contract.
        axes=[a for a in range(3) if a!=axis]
        preferred={'x':0,'y':1,'z':2}[grain]
        if preferred in axes:axes.remove(preferred);axes.append(preferred)
        material=obj.data.materials[poly.material_index] if obj.data.materials else None
        scale=material.get('meters_per_tile_uv',[1,1]) if material else [1,1]
        for li in poly.loop_indices:
            p=mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv=(p[axes[0]]/scale[0],p[axes[1]]/scale[1])

def mesh_obj(name,verts,faces,role,bevel=0,grain='x',smooth=False):
    me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update()
    # Recalculate winding consistently before assigning UVs.
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
    ob.data.materials.append(M[role]);ob['semantic_role']=role;ob['grain_axis']=grain
    uv_metric(ob,grain)
    if bevel:
        mod=ob.modifiers.new('Editable soft join edges','BEVEL');mod.width=bevel;mod.segments=1
        mod.affect='EDGES'
        mod=ob.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL');mod.keep_sharp=True
    for p in me.polygons:p.use_smooth=smooth
    COMPONENTS.append(ob);return ob

def extrusion(name,profile,lo,hi,role,axis='x',bevel=0,grain='z'):
    # Profile coordinates are YZ for x extrusion, XY for z extrusion.
    if axis=='x':verts=[(x,a,b) for x in (lo,hi) for a,b in profile]
    else:verts=[(a,b,z) for z in (lo,hi) for a,b in profile]
    n=len(profile);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh_obj(name,verts,faces,role,bevel,grain)

def rounded_outline(w,d,r,n=5):
    points=[]
    for cx,cy,start in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
        for j in range(n):
            a=math.radians(start+j*90/(n-1));points.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    return points

def pill_slab(name,w,d,z0,z1,role,center=(0,0),r=.06,grain='x',bevel=.005):
    p=[(x+center[0],y+center[1]) for x,y in rounded_outline(w,d,r,n=4)]
    return extrusion(name,p,z0,z1,role,axis='z',bevel=bevel,grain=grain)

def beam(name,a,b,width,depth,role,bevel=.005):
    mid=(Vector(a)+Vector(b))/2;delta=Vector(b)-Vector(a)
    bpy.ops.mesh.primitive_cube_add(size=1,location=mid)
    ob=bpy.context.object;ob.name=name;ob.dimensions=(width,depth,delta.length)
    ob.rotation_euler=delta.to_track_quat('Z','Y').to_euler()
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(M[role]);uv_metric(ob,'z');ob['semantic_role']=role;ob['grain_axis']='z'
    mod=ob.modifiers.new('Editable join easing','BEVEL');mod.width=bevel;mod.segments=1
    mod=ob.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL');mod.keep_sharp=True
    COMPONENTS.append(ob);return ob

def pipe(name,points,role,r=.0035,cyclic=True,parent=None):
    # Editable low-poly welt geometry; its UV length is measured in metres.
    verts=[];faces=[];lengths=[0.0];total=0.0;n=len(points)
    for i,p in enumerate(points):
        prev=Vector(points[(i-1)%n] if cyclic or i>0 else points[i])
        nxt=Vector(points[(i+1)%n] if cyclic or i<n-1 else points[i])
        tangent=(nxt-prev).normalized();side=Vector((-tangent.y,tangent.x,0)).normalized()
        up=tangent.cross(side).normalized()
        for j in range(4):
            a=2*math.pi*j/4;verts.append(tuple(Vector(p)+r*(math.cos(a)*side+math.sin(a)*up)))
        if i:
            total+=(Vector(p)-Vector(points[i-1])).length;lengths.append(total)
    for i in range(n if cyclic else n-1):
        for j in range(4):faces.append((i*4+j,i*4+(j+1)%4,((i+1)%n)*4+(j+1)%4,((i+1)%n)*4+j))
    if not cyclic:faces += [(3,2,1,0),tuple((n-1)*4+j for j in range(4))]
    ob=mesh_obj(name,verts,faces,role,smooth=True)
    uv=ob.data.uv_layers.active;scale=M[role].get('meters_per_tile_uv',[1,1]);circ=2*math.pi*r
    for poly in ob.data.polygons:
        # End caps retain mesh_obj's planar metric projection rather than constant path V.
        if not cyclic and poly.index >= (n-1)*4:continue
        for li in poly.loop_indices:
            vi=ob.data.loops[li].vertex_index;uv.data[li].uv=((vi%4)/4*circ/scale[0],lengths[vi//4]/scale[1])
    ob['editable_path_points_local_m']=json.dumps(points);ob['construction']='Measured four-sided welt tube, editable mesh and generator path'
    if parent:ob.parent=parent
    return ob

def cushion(name,w,d,t,loc,role,angle=0):
    # Unequal ring sizes sculpt a tapered underside, broad shoulder and true crown.
    layers=[(-.50,.82),(-.46,.92),(-.33,.985),(-.07,1.0),(.21,.99),(.39,.955),(.53,.80),(.61,.52),(.645,.20)]
    verts=[];n=20
    for z,s in layers:
        verts.extend((x,y,z*t) for x,y in rounded_outline(w*s,d*s,min(.085,w*.14,d*.2)*s,n=5))
    faces=[]
    for j in range(len(layers)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    verts += [(0,0,-.5*t),(0,0,.65*t)]
    for i in range(n):
        faces.append((len(verts)-2,(i+1)%n,i))
        faces.append((len(verts)-1,(len(layers)-1)*n+i,(len(layers)-1)*n+(i+1)%n))
    ob=mesh_obj(name,verts,faces,role,smooth=True)
    ob.location=loc;ob.rotation_euler.x=math.radians(angle)
    # Control surface is already intentionally shaped; subdivision retained and off by default.
    sub=ob.modifiers.new('Optional upholstery refinement','SUBSURF');sub.levels=0;sub.render_levels=0
    seampts=[(x,y,.375*t) for x,y in rounded_outline(w*.96,d*.96,min(.085,w*.14,d*.2)*.96)]
    seam=pipe(name+'_welt_seam',seampts,role,r=.0036,parent=ob)
    # Three restrained inset vertical pull seams on the broad back faces.
    ob['crown_height_m']=.65*t;ob['construction']='Tapered crown rings, separate perimeter welt'
    return ob

def seating(kind):
    bench=kind=='bench';outer=2.4 if bench else .94;xside=outer/2-.0665
    role='clay_weave' if bench else 'teal_weave';stem='DAY_BENCH' if bench else 'DAY_CHAIR'
    # Side cheek flows from low front arm to high reclined rear shoulder.
    profile=[(-.428,.225),(-.447,.38),(-.433,.543),(-.39,.625),(-.32,.665),(-.22,.67),
      (.025,.64),(.12,.69),(.24,.865),(.333,.969),(.421,.961),(.468,.894),(.475,.319),
      (.438,.227),(.33,.202),(.28,.267),(-.282,.267),(-.332,.20)]
    for sign,label in [(-1,'L'),(1,'R')]:
        xc=sign*xside
        ob=extrusion(stem+'_'+label+'_swept_walnut_cheek',profile,xc-.043,xc+.043,'warm_walnut',bevel=.009,grain='z')
        ob['relationship']='Upper rail / backrest cheek, joined to front and rear trestle posts'
        # Inner liner: lighter ceramic-like resin insert, recessed inside timber perimeter.
        inner=[(-.366,.323),(-.375,.49),(-.338,.582),(-.235,.61),(.019,.585),(.159,.691),(.29,.883),(.358,.905),(.398,.855),(.395,.336)]
        xface=xc-sign*.045
        extrusion(stem+'_'+label+'_recessed_ivory_liner',inner,min(xface,xface-sign*.016),max(xface,xface-sign*.016),'ivory_enamel',bevel=.006,grain='z')
        pill_slab(stem+'_'+label+'_rubber_floor_shoe',.133,.742,0,.018,'dark_rubber',(xc,.012),r=.035,grain='y',bevel=.003)
        pill_slab(stem+'_'+label+'_timber_runner',.119,.716,.016,.07,'warm_walnut',(xc,.012),r=.039,grain='y',bevel=.005)
        for yy,lab in [(-.282,'front'),(.312,'rear')]:
            beam(stem+'_'+label+'_'+lab+'_splayed_post',(xc,yy,.064),(xc,yy+(.019 if yy<0 else -.019),.295),.084,.095,'warm_walnut',.006)
        # Thin metal pin crosses the real post-to-cheek join, not a luminous outline.
        for yy,lab in [(-.284,'front'),(.312,'rear')]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.009,depth=.004,location=(xc+sign*.046,yy,.285),rotation=(0,math.pi/2,0))
            pin=bpy.context.object;pin.name=stem+'_'+label+'_'+lab+'_inset_join_pin';pin.data.materials.append(M['champagne_metal']);uv_metric(pin);pin['semantic_role']='champagne_metal';COMPONENTS.append(pin)
        cushion(stem+'_'+label+'_arm_pad',.106,.405,.052,(xc,-.14,.676), 'oatmeal_weave')
    for yy,label in [(-.298,'front'),(.303,'rear')]:
        beam(stem+'_'+label+'_continuous_cross_rail',(-xside,yy,.296),(xside,yy,.296),.080,.063,'warm_walnut')
    pill_slab(stem+'_inset_seat_deck',outer-.195,.701,.305,.344,'warm_walnut',(0,-.042),r=.075,bevel=.005)
    # Solid low back shell visibly overlaps the rear cross rail and both cheeks.
    back=beam(stem+'_reclined_back_cross_shell',(-xside,.399,.656),(xside,.399,.656),.101,.413,'warm_walnut',.01)
    back.rotation_euler=(0,0,0)
    # Replace beam's radial orientation with intentional upright slab dimensions.
    back.dimensions=(outer-.075,.069,.588);back.location=(0,.399,.63);back.rotation_euler.x=math.radians(-10)
    bpy.context.view_layer.objects.active=back;back.select_set(True);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);back.select_set(False)
    uv_metric(back,'x')
    seats=[(-.548,'L'),(.548,'R')] if bench else [(0,'single')]
    w=1.070 if bench else .718
    for xx,label in seats:
        seat=cushion(stem+'_'+label+'_crowned_seat',w,.696,.123,(xx,-.077,.39505),role)
        seat['contact_crown_world_z_m']=.475
        backp=cushion(stem+'_'+label+'_reclined_back_cushion',w-.006,.508,.143,(xx,.326,.744),role,78)
        # Subtle back-centre dart in actual fabric geometry.
        for sx in (-.23,.23) if bench else (-.17,.17):
            p=[(sx,-.163,.0805),(sx,-.07,.0880),(sx,.06,.0880),(sx,.153,.0805)]
            pipe(stem+'_'+label+'_back_pull_'+str(sx),p,role,r=.0022,cyclic=False,parent=backp)
    return {'catalogue_id':'AST-FUR-001' if bench else 'AST-FUR-002','name':'Astraea Day Window Bench' if bench else 'Astraea Day Reading Chair',
      'intended_use':'Two-person view-facing daytime seating' if bench else 'Companion reading and conversation chair',
      'seat_contact_proposal':{'crown_z_m':.475,'seat_centres_m':[[-.548,-.11,.475],[.548,-.11,.475]] if bench else [[0,-.11,.475]],'front_edge_y_m':-.425,'usable_depth_m':.56},
      'approach_proposal':{'front_direction':[0,-1,0],'clear_floor_rectangle_m':[[-outer/2,-1.16],[outer/2,-.47]],'status':'Proposal only; actor rig and original game fit untested'},
      'collision_proposal':{'method':'Compound simple boxes for runners, posts, seat deck, back, side cheeks; omit decorative seams and pins; do not hull the complete chair','status':'Not generated or engine-tested'},
      'contact_joins':[{'members':['floor_shoe','timber_runner'],'overlap_m':.002},{'members':['splayed_post','cross_rail','swept_walnut_cheek'],'intent':'Continuous physical load path with fitted join overlap'}, {'members':['crowned_seat','inset_seat_deck'],'overlap_m':.01045}, {'members':['reclined_back_cross_shell','swept_walnut_cheek'],'intent':'Back shell ends overlap cheeks'}]}

def table():
    stem='DAY_TABLE'
    # Long-radius oval/squircle profile has no box silhouette.
    def oval(w,d,power=2.55,n=32):
        out=[]
        for i in range(n):
            a=2*math.pi*i/n;c=math.cos(a);s=math.sin(a)
            out.append((w/2*math.copysign(abs(c)**(2/power),c),d/2*math.copysign(abs(s)**(2/power),s)))
        return out
    extrusion(stem+'_oval_walnut_edge_apron',oval(.98,.62),.596,.647,'warm_walnut',axis='z',bevel=.008,grain='x')
    extrusion(stem+'_inset_stone_worktop',oval(.953,.593),.638,.665,'warm_stone',axis='z',bevel=.004,grain='x')
    ring=oval(.966,.606)
    pipe(stem+'_recessed_champagne_edge_inlay',[(x,y,.643) for x,y in ring],'champagne_metal',r=.0025)
    # Trestles flare toward both floor and top, leaving central knee/foot voids.
    p=[(-.225,.038),(-.22,.095),(-.125,.28),(-.086,.40),(-.191,.586),(-.182,.61),
       (.182,.61),(.191,.586),(.086,.40),(.125,.28),(.22,.095),(.225,.038)]
    for xc,lab in [(-.275,'L'),(.275,'R')]:
        extrusion(stem+'_'+lab+'_waisted_trestle',p,xc-.036,xc+.036,'warm_walnut',bevel=.007,grain='z')
        for yy,side in [(-.181,'front'),(.181,'rear')]:
            pill_slab(stem+'_'+lab+'_'+side+'_rubber_foot',.093,.103,0,.046,'dark_rubber',(xc,yy),r=.022,bevel=.003)
        beam(stem+'_'+lab+'_top_bearing_rail',(xc,-.213,.599),(xc,.213,.599),.08,.047,'warm_walnut')
    beam(stem+'_low_cross_stretcher',(-.311,0,.19),(.311,0,.19),.075,.076,'warm_walnut',.006)
    # Central narrow shelf makes join visible and gives a place for a book.
    pill_slab(stem+'_small_lower_book_shelf',.555,.252,.222,.245,'warm_walnut',r=.04,bevel=.004)
    for xx in [-.313,.313]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.012,depth=.004,location=(xx,0,.19),rotation=(0,math.pi/2,0))
        ob=bpy.context.object;ob.name=stem+('_L' if xx<0 else '_R')+'_stretcher_join_pin';ob.data.materials.append(M['champagne_metal']);uv_metric(ob);ob['semantic_role']='champagne_metal';COMPONENTS.append(ob)
    return {'catalogue_id':'AST-FUR-003','name':'Astraea Day Table','intended_use':'Forward-of-knees day-use surface for two drinks or a book; no tucked-in dining claim',
      'contact_proposal':{'worktop_z_m':.665,'usable_top_m':[.953,.593],'shelf_z_m':.245},
      'approach_proposal':{'directions':[[0,-1,0],[0,1,0]],'underside_apron_z_m':.596,'placement_note':'Place forward of knees, not over the seated knee envelope; broad-body fit not established','status':'Proposal only; ergonomic and original-engine validation pending'},
      'collision_proposal':{'method':'Top shallow convex capsule approximation; separate trestle and stretcher boxes; retain space between supports','status':'Not generated or engine-tested'},
      'contact_joins':[{'members':['rubber_foot','waisted_trestle'],'overlap_m':.008},{'members':['waisted_trestle','top_bearing_rail','oval_walnut_edge_apron'],'intent':'Continuous support overlap'},{'members':['low_cross_stretcher','waisted_trestle'],'intent':'Through-tenon overlap'},{'members':['small_lower_book_shelf','waisted_trestle'],'intent':'Shelf ends housed in trestles'}]}

def evaluated_stats(objects):
    dg=bpy.context.evaluated_depsgraph_get();verts=[];tri=0;parts=[]
    for ob in objects:
        if ob.type not in {'MESH','CURVE'}:continue
        eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles()
        worldverts=[tuple(ob.matrix_world@v.co) for v in me.vertices]
        verts.extend(worldverts);tri+=len(me.loop_triangles)
        plo=[min(p[i] for p in worldverts) for i in range(3)];phi=[max(p[i] for p in worldverts) for i in range(3)]
        parts.append({'name':ob.name,'type':ob.type,'triangles':len(me.loop_triangles),'bounds_min_m':plo,'bounds_max_m':phi,'materials':[m.name for m in ob.data.materials],'modifiers':[m.name for m in ob.modifiers]})
        eo.to_mesh_clear()
    lo=[min(p[i] for p in verts) for i in range(3)];hi=[max(p[i] for p in verts) for i in range(3)]
    return {'bounds_min_m':lo,'bounds_max_m':hi,'dimensions_m':[hi[i]-lo[i] for i in range(3)],'triangles_evaluated':tri,'parts':parts}

def finish(info,slug):
    for ob in COMPONENTS:
        ob['catalogue_id']=info['catalogue_id'];ob['provenance']='New independent script-assisted original geometry, 2026-10-02'
    root=bpy.data.objects.new(info['catalogue_id']+'_floor_origin',None);bpy.context.collection.objects.link(root)
    root['catalogue_id']=info['catalogue_id'];root['pivot']='Floor origin (0,0,0), +X width, +Z up, front -Y'
    for ob in COMPONENTS:
        if ob.parent is None:ob.parent=root
    bpy.context.view_layer.update();info.update(evaluated_stats(COMPONENTS))
    info.update({'blender_version':bpy.app.version_string,'units':'metres','pivot_m':[0,0,0],'front_axis':'-Y','authoring':'Script-assisted intentional ring, extrusion and join design; editable semantic parts and modifiers retained',
      'provenance':'New independent 2026-10-02 continuation. Not recovery or reconstruction of lost game. Reference images used only for warm residential palette, material restraint and use; no reference pixels copied.',
      'materials':sorted(set(m.name for ob in COMPONENTS for m in ob.data.materials)),'qa_scope':'Blender component QA only; original Godot integration, actor contact, physics and target-PC performance are untested',
      'export':{'format':'GLB','Y_up':True,'apply_modifiers':True,'UVs':True,'normals':True,'materials':'EXPORT','textures':'Embedded ordinary Principled base-color roles'},
      'source_generator':'build_furniture.py','asset_files':[slug+'.blend',slug+'.glb']})
    info['source_generator_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    info['shared_material_source_sha256']=hashlib.sha256((BASE/'standards'/'materials.py').read_bytes()).hexdigest()
    info['shared_material_manifest_sha256']=hashlib.sha256((BASE/'materials'/'material_manifest.json').read_bytes()).hexdigest()
    info['reference_provenance']=[{'file':str(p.relative_to(BASE)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'use':'Shape, material and spatial-use guidance only; no sampled or copied image pixels'} for p in sorted((BASE/'references').glob('*/*.png'))]
    collision=[]
    keywords=['rubber_floor_shoe','rubber_foot','splayed_post','seat_deck','back_cross_shell','swept_walnut_cheek','crowned_seat','edge_apron','inset_stone_worktop','waisted_trestle','low_cross_stretcher']
    for p in info['parts']:
        if not any(k in p['name'] for k in keywords) or '_welt_seam' in p['name']:continue
        lo=p['bounds_min_m'];hi=p['bounds_max_m']
        collision.append({'source_part':p['name'],'type':'box_proposal','centre_m':[(a+b)/2 for a,b in zip(lo,hi)],'size_m':[b-a for a,b in zip(lo,hi)],'note':'Conservative per-part AABB proposal. Sculpted shell/back/top shapes should be checked and refined for final actor and engine.'})
    (ROOT/(slug+'.collision_proposal.json')).write_text(json.dumps({'catalogue_id':info['catalogue_id'],'status':'Data proposal only. No physics shapes are exported or validated in any engine. Never use a whole-seat convex hull.','axis':'Blender metres, Z up, front -Y','parts':collision,'approach':info['approach_proposal']},indent=2))
    # Keep source clean: no QA cameras/lights/floors or human proxy in asset source.
    bpy.ops.file.pack_all()
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/(slug+'.blend')))
    # Export-only evaluated consolidation. Source objects/modifiers remain editable in .blend.
    bpy.ops.object.select_all(action='DESELECT');dg=bpy.context.evaluated_depsgraph_get();copies=[]
    for source in COMPONENTS:
        eo=source.evaluated_get(dg)
        me=bpy.data.meshes.new_from_object(eo,preserve_all_data_layers=True,depsgraph=dg)
        # Blender object.join matches UV layers by name; normalize BEFORE joining.
        if not me.uv_layers.active:
            raise RuntimeError('Missing metric UV map on evaluated source '+source.name)
        active_uv=me.uv_layers.active
        for layer in list(me.uv_layers):
            if layer != active_uv:me.uv_layers.remove(layer)
        active_uv.name='UV_Metric_Metres';active_uv.active_render=True
        ob=bpy.data.objects.new('EXPORT_'+source.name,me);bpy.context.collection.objects.link(ob)
        ob.matrix_world=source.matrix_world.copy();ob.select_set(True);copies.append(ob)
    bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();combined=bpy.context.object
    combined.name=info['catalogue_id']+'_static_visual';bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    combined['catalogue_id']=info['catalogue_id'];combined['source_part_count']=len(COMPONENTS)
    combined['provenance']='Evaluated export-only consolidation; editable semantic parts in paired blend source'
    combined.parent=root;root.select_set(True)
    info['export']['static_visual_meshes']=1
    info['export']['material_primitives']=len(combined.data.materials)
    info['export']['source_semantic_part_count']=len(COMPONENTS)
    info['export']['consolidation']='Disconnected evaluated visual parts joined by shared material role, no auto-collision or object deletion in saved source'
    bpy.ops.export_scene.gltf(filepath=str(ROOT/(slug+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_materials='EXPORT',export_extras=True)
    for suffix in ['blend','glb']:
        info[ suffix+'_sha256']=hashlib.sha256((ROOT/(slug+'.'+suffix)).read_bytes()).hexdigest()
    (ROOT/(slug+'.manifest.json')).write_text(json.dumps(info,indent=2))
    return info

if __name__=='__main__':
    summary=[]
    for kind,slug in [('bench','AST-FUR-001_day_window_bench'),('chair','AST-FUR-002_day_reading_chair'),('table','AST-FUR-003_day_table')]:
        reset();info=table() if kind=='table' else seating(kind);summary.append(finish(info,slug))
    (ROOT/'family_summary.json').write_text(json.dumps([{k:v for k,v in d.items() if k!='parts'} for d in summary],indent=2))
    print('FURNITURE_FAMILY_COMPLETE',[(d['catalogue_id'],d['dimensions_m'],d['triangles_evaluated']) for d in summary])
