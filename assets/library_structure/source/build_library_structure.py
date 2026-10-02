"""Three original, independent Astraea collection components, script-assisted design.

Run with Blender 4.3: blender -b --python source/build_library_structure.py
The existing materials-02 helper is read unchanged. No room/game content is used.
All dimensions below are metres. Architecture seam pivot is (0, 0, 0).
"""
import bpy, bmesh, math, json, hashlib, importlib.util
from pathlib import Path
from mathutils import Vector

BASE = Path(__file__).resolve().parents[1]
CAT = BASE.parents[1]
spec = importlib.util.spec_from_file_location('catalogue_materials', CAT/'standards/materials.py')
material_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(material_module)
MATS = material_module.materials()
TOPS = [.30, .68, 1.06, 1.44, 1.82, 2.20, 2.58]
RADIUS = 1.8
GAP = .002
COLLISIONS = {}
RECORDS = []

# Sections are (forward depth, height). Positive depth points toward the reader.
CROWN = [(-.09,3.40),(.34,3.40),(.62,3.366),(.84,3.292),(.995,3.178),
         (1.015,3.125),(.994,3.092),(.933,3.090),(.794,3.206),
         (.580,3.285),(.310,3.320),(-.09,3.320)]
SOFFIT = [(-.025,3.315),(.310,3.315),(.575,3.278),(.788,3.197),
          (.930,3.079),(.934,3.041),(.882,3.025),(.736,3.149),
          (.544,3.227),(.285,3.266),(-.025,3.266)]
PLINTH = [(-.08,0),(.370,0),(.432,.040),(.445,.095),(.422,.159),
          (.387,.212),(.387,.248),(-.08,.248)]
BACK = [(-.079,.235),(-.017,.235),(-.017,3.285),(-.079,3.285)]
# Shaped vertical frames carry shelf noses into the matching coved soffit.
FRAME = [(-.078,.010),(.385,.010),(.422,.090),(.376,.255),(.368,2.680),
         (.410,2.810),(.520,2.905),(.680,2.970),(.825,3.045),
         (.930,3.104),(.794,3.206),(.580,3.285),(.310,3.320),(-.078,3.320)]
TERMINAL = [(-.09,0),(.370,0),(.432,.040),(.445,.095),(.422,.159),
            (.387,.248),(.371,2.650),(.416,2.792),(.552,2.913),
            (.733,3.005),(.885,3.070),(.994,3.092),(1.015,3.125),
            (.995,3.178),(.840,3.292),(.620,3.366),(.340,3.4),(-.09,3.4)]

def wipe():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.context.scene.unit_settings.system='METRIC'
    bpy.context.scene.unit_settings.scale_length=1

def path(kind, a=0, b=None):
    if kind=='straight':
        return [(x,0,1,0,x) for x in (a if a else .001,b if b is not None else 2.399)]
    if kind=='curved':
        aa=a if a else .001/RADIUS
        bb=b if b is not None else math.pi/2-.001/RADIUS
        steps=max(1,math.ceil((bb-aa)/math.radians(5)))
        stations=[(RADIUS*math.sin(t),RADIUS*(1-math.cos(t)),math.cos(t),math.sin(t),RADIUS*t)
                for t in [aa+(bb-aa)*k/steps for k in range(steps+1)]]
        # End caps sit on exact tangent seam planes, so the broad canopy and
        # narrower boards share the same 2 mm mating gap across their depth.
        if abs(aa-.001/RADIUS)<1e-9:stations[0]=(.001,0,1,0,.001)
        if abs(bb-(math.pi/2-.001/RADIUS))<1e-9:stations[-1]=(RADIUS,RADIUS-.001,0,1,RADIUS*math.pi/2-.001)
        return stations
    return [(x,0,1,0,x) for x in (a if a else .001,b if b is not None else .259)]

def section_mesh(name, stations, profile, role, grain='longitudinal', bevel=.001):
    """Closed sweep with a separate metric cap unwrap, never collapsed cap UVs."""
    verts=[]
    for x,y,tx,ty,s in stations:
        verts.extend((x+ty*d,y-tx*d,z) for d,z in profile)
    n=len(profile); faces=[]
    for k in range(len(stations)-1):
        faces.extend((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j) for j in range(n))
    faces.extend([tuple(reversed(range(n))),tuple((len(stations)-1)*n+j for j in range(n))])
    me=bpy.data.meshes.new(name+'_profile_mesh'); me.from_pydata(verts,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob)
    me.materials.append(MATS[role]); ob['material_role']=role
    ob['provenance']='New script-assisted independent collection profile; no recovered assets'
    ob['profile_depth_height_m']=json.dumps(profile)
    ob['grain']='V follows '+('height' if grain=='vertical' else 'sweep length')
    scale=tuple(MATS[role]['meters_per_tile_uv']); layer=me.uv_layers.new(name='metric_material_uv')
    perimeter=[0]
    for p,q in zip(profile,profile[1:]):perimeter.append(perimeter[-1]+math.dist(p,q))
    total=perimeter[-1]+math.dist(profile[-1],profile[0])
    for face in me.polygons:
        cap=face.index>=len(faces)-2
        edge=face.index%n
        for li in face.loop_indices:
            vi=me.loops[li].vertex_index; k,j=divmod(vi,n); d,z=profile[j]; s=stations[k][4]
            if cap:uv=(d/scale[0],z/scale[1])
            elif grain=='vertical':
                # Full-height backing/frame surfaces use heightwise timber grain.
                uv=(s/scale[0],(z if abs(profile[(edge+1)%n][1]-profile[edge][1])>.015 else d)/scale[1])
            else:uv=((total if edge==n-1 and j==0 else perimeter[j])/scale[0],s/scale[1])
            layer.data[li].uv=uv
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(me); bm.free()
    if bevel:
        mod=ob.modifiers.new('Editable 1 mm eased join edges','BEVEL'); mod.width=bevel; mod.segments=1
        mod.limit_method='ANGLE'; mod.angle_limit=math.radians(44); mod.use_clamp_overlap=True
        mod=ob.modifiers.new('Editable weighted surface normals','WEIGHTED_NORMAL'); mod.keep_sharp=True; mod.weight=35
    return ob

def shelf_profile(top):
    return [(-.015,top),(.395,top),(.415,top-.011),(.420,top-.026),
            (.405,top-.044),(.370,top-.052),(-.015,top-.052)]

def add_collider(name,stations,profile):
    parts=[]
    # Individual convex wedges preserve the empty collection/approach volumes.
    for a,b in zip(stations,stations[1:]):
        points=[]
        for x,y,tx,ty,s in (a,b):points.extend([x+ty*d,y-tx*d,z] for d,z in profile)
        parts.append({'type':'convex_hull_points','points_m':points})
    return {'semantic_part':name,'hulls':parts}

def create(kind):
    pieces=[]; coll=[]; stations=path(kind)
    if kind!='terminal':
        for name,profile,role,grain in [('continuous_coved_canopy',CROWN,'ivory_enamel','longitudinal'),
                ('timber_shelter_soffit',SOFFIT,'warm_walnut','longitudinal'),
                ('floor_contact_sculpted_plinth',PLINTH,'ivory_enamel','longitudinal'),
                ('continuous_timber_back',BACK,'warm_walnut','vertical')]:
            pieces.append(section_mesh(name,stations,profile,role,grain)); coll.append(add_collider(name,stations,profile))
        for i,z in enumerate(TOPS):
            name=f'supported_shelf_{i+1:02d}_top_{z:.2f}'
            pieces.append(section_mesh(name,stations,shelf_profile(z),'warm_walnut'))
            coll.append(add_collider(name,stations,[(-.015,z-.052),(.410,z-.052),(.410,z),(-.015,z)]))
        frames=[0,.8,1.6,2.4] if kind=='straight' else [0,math.pi/6,math.pi/3,math.pi/2]
        for i,datum in enumerate(frames):
            half=.038 if kind=='straight' else .038/RADIUS
            high=2.4 if kind=='straight' else math.pi/2
            inset=.001 if kind=='straight' else .001/RADIUS
            pp=path(kind,max(inset,datum-half),min(high-inset,datum+half))
            name=f'shelf_to_canopy_load_frame_{i+1:02d}'
            pieces.append(section_mesh(name,pp,FRAME,'warm_walnut','vertical'))
            coll.append(add_collider(name,pp,FRAME))
            # A thin ivory face follows the carved support above the collection.
            accent=[(.369,.270),(.380,.270),(.380,2.680),(.425,2.805),(.530,2.896),
                    (.530,2.909),(.415,2.817),(.369,2.689)]
            pieces.append(section_mesh(f'ivory_frame_inlay_{i+1:02d}',pp,accent,'ivory_enamel',bevel=0))
    else:
        # The collection and its canopy truly close against one shaped terminal.
        # The .26 m extension belongs to this terminal, not another shelf bay.
        pieces.append(section_mesh('closed_terminal_ivory_carrier',stations,TERMINAL,'ivory_enamel','vertical'))
        coll.append(add_collider('closed_terminal_ivory_carrier',stations,TERMINAL))
        # Exposed outer timber field is recessed within the perimeter, with a
        # purposeful stepped crown and base rather than an unrelated flat box.
        field=[(.010,.150),(.280,.150),(.319,.260),(.303,2.608),(.341,2.761),
               (.458,2.911),(.641,3.063),(.783,3.133),(.623,3.242),(.325,3.294),(.010,3.294)]
        pieces.append(section_mesh('inset_outline_timber_terminal_field',path('terminal',.257,.266),field,'warm_walnut','vertical',bevel=.0008))
        # Fine stepped rails bring the collection levels to the end face.
        for i,z in enumerate(TOPS[1:]):
            p=[(.030,z-.012),(.299,z-.012),(.299,z+.012),(.030,z+.012)]
            pieces.append(section_mesh(f'outer_terminal_shelf_datum_{i+2:02d}',path('terminal',.265,.272),p,'champagne_metal',bevel=.0005))
    return pieces,coll

def measured(objects):
    dg=bpy.context.evaluated_depsgraph_get(); pts=[]; triangles=0
    for ob in objects:
        eo=ob.evaluated_get(dg); me=eo.to_mesh(); me.calc_loop_triangles(); triangles+=len(me.loop_triangles)
        pts.extend(ob.matrix_world@v.co for v in me.vertices); eo.to_mesh_clear()
    lo=[min(v[i] for v in pts) for i in range(3)]; hi=[max(v[i] for v in pts) for i in range(3)]
    return {'min_m':lo,'max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)]},triangles

def export(objects,file):
    dg=bpy.context.evaluated_depsgraph_get(); groups={}
    for source in objects:
        me=bpy.data.meshes.new_from_object(source.evaluated_get(dg))
        # Normalize BEFORE consolidation; preserve the active data first.
        active=me.uv_layers.active
        for other in list(me.uv_layers):
            if other!=active:me.uv_layers.remove(other)
        active.name='metric_material_uv'; active.active_render=True
        # Tiny interpolated bevel UVs and planar vertical end faces receive
        # a metric dominant-plane repair. Never substitute arbitrary 0..1 caps.
        me.calc_loop_triangles(); repair=set(); scale=tuple(MATS[source['material_role']]['meters_per_tile_uv'])
        for tr in me.loop_triangles:
            a,b,c=[active.data[i].uv for i in tr.loops]
            if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<2e-12:repair.add(tr.polygon_index)
        for index in repair:
            p=me.polygons[index]; axis=max(range(3),key=lambda k:abs(p.normal[k])); axes=[k for k in range(3) if k!=axis]
            for li in p.loop_indices:
                v=me.vertices[me.loops[li].vertex_index].co
                active.data[li].uv=(v[axes[0]]/scale[0],v[axes[1]]/scale[1])
        ob=bpy.data.objects.new('runtime_'+source.name,me); bpy.context.collection.objects.link(ob); ob.matrix_world=source.matrix_world.copy()
        groups.setdefault(source['material_role'],[]).append(ob)
    runtime=[]
    for role,parts in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for ob in parts:ob.select_set(True)
        bpy.context.view_layer.objects.active=parts[0]; bpy.ops.object.join()
        ob=parts[0]; ob.name='ASTRAEA_library_'+role; ob['material_role']=role
        ob['semantic_parts']=json.dumps([x.name for x in objects if x['material_role']==role]); runtime.append(ob)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in runtime:ob.select_set(True)
    bpy.context.view_layer.objects.active=runtime[0]
    bpy.ops.export_scene.gltf(filepath=str(file),export_format='GLB',use_selection=True,export_apply=True,
        export_yup=True,export_extras=True,export_materials='EXPORT',export_texcoords=True,export_normals=True,
        export_cameras=False,export_lights=False)
    for ob in runtime:bpy.data.objects.remove(ob,do_unlink=True)

def anchors(kind):
    rows=[]
    stations=path(kind)
    support_polygon=[]
    for d,order in [(.395,stations),(-.015,list(reversed(stations)))]:
        support_polygon.extend([x+ty*d,y-tx*d] for x,y,tx,ty,s in order)
    for level,z in enumerate(TOPS):
        for cell in range(3):
            angle=0 if kind=='straight' else math.radians(15+cell*30)
            x=.4+.8*cell if kind=='straight' else 2*math.sin(angle)
            y=-.2 if kind=='straight' else RADIUS-2*math.cos(angle)
            corners=[]
            for tx,fy in [(-.34,-.12),(.34,-.12),(.34,.12),(-.34,.12)]:
                # local y positive points toward the back of the stock envelope.
                corners.append([x+math.cos(angle)*tx-math.sin(angle)*fy,y+math.sin(angle)*tx+math.cos(angle)*fy,z])
            record={'id':f'{kind}_s{level+1:02d}_c{cell+1:02d}','position_m':[x,y,z],'rotation_z_degrees':math.degrees(angle),
                'forward_unit':[math.sin(angle),-math.cos(angle),0],'tangent_unit':[math.cos(angle),math.sin(angle),0],
                'stock_local_min_m':[-.34,-.12,0],'stock_local_max_m':[.34,.12,.29],
                'footprint_corners_m':corners,'shelf_top_z_m':z,'clear_height_m':.328 if level<6 else .67,
                'support_polygon_xy_m':support_polygon,
                'access':'Staff access planning required' if z>=1.82 else 'Guest reach proposal; rig/access pending'}
            if kind=='curved':
                radial=[math.hypot(p[0],p[1]-RADIUS) for p in corners]
                record['support_check']={'board_top_inner_radius_m':1.785,'board_top_outer_radius_m':2.195,
                  'maximum_facet_angle_degrees':5,'conservative_outer_chord_radius_m':2.195*math.cos(math.radians(2.5)),
                  'corner_radius_range_m':[min(radial),max(radial)],
                  'outer_chord_margin_m':2.195*math.cos(math.radians(2.5))-max(radial),
                  'inner_radius_margin_m':min(radial)-1.785,'supported':min(radial)>=1.785 and max(radial)<=2.195*math.cos(math.radians(2.5))}
            else:record['support_check']={'shelf_top_y_bounds_m':[-.395,.015],'supported':True,'nearest_partition_clearance_m':.022}
            rows.append(record)
    return rows

def main():
    ids={'straight':'AST-LIB-STR-001','curved':'AST-LIB-STR-002','terminal':'AST-LIB-STR-003'}
    for kind,cid in ids.items():
        wipe(); objects,collision=create(kind); bpy.context.view_layer.update()
        sc=bpy.context.scene;sc['catalogue_id']=cid;sc['component_only']=True
        sc['scope']='Independent collection component; no original ship fit/headroom/engine acceptance'
        end=[2.4,0,0] if kind=='straight' else [1.8,1.8,0] if kind=='curved' else None
        joins=[{'id':'start','position_m':[0,0,0],'tangent_unit':[1,0,0],'outward_normal':[-1,0,0],'profile':'collection_shelter_3400'}]
        if end:joins.append({'id':'end','position_m':end,'tangent_unit':[1,0,0] if kind=='straight' else [0,1,0],
                    'outward_normal':[1,0,0] if kind=='straight' else [0,1,0],'profile':'collection_shelter_3400'})
        for ob in objects:ob['catalogue_id']=cid;ob['pivot_description']='Floor-height nominal start seam';ob['seams']=json.dumps(joins)
        stock=anchors(kind) if kind!='terminal' else []
        for a in stock:
            ob=bpy.data.objects.new('ANCHOR_'+a['id'],None); bpy.context.collection.objects.link(ob)
            ob.location=a['position_m'];ob.rotation_euler.z=math.radians(a['rotation_z_degrees']);ob.empty_display_size=.07
            ob['stock_envelope_m']=[.68,.24,.29];ob['exported']=False
        source=BASE/'source'/f'{cid}.blend'; glb=BASE/'exports'/f'{cid}.glb'
        bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True); export(objects,glb)
        bounds,triangles=measured(objects)
        meta={'catalogue_id':cid,'kind':kind,'source_blend':str(source.relative_to(BASE)),'runtime_glb':str(glb.relative_to(BASE)),
              'bounds':bounds,'triangles_evaluated':triangles,'material_roles':sorted(set(o['material_role'] for o in objects)),
              'editable_semantic_parts':[o.name for o in objects],'modifiers_retained':['Bevel','Weighted Normal'],
              'pivot_m':[0,0,0],'pivot_description':'Floor-height nominal start seam; geometry inset 1 mm at either join',
              'seams':joins,'nominal_seam_air_gap_m':.002,'shelf_top_stock_anchors':stock,
              'closed_end':kind=='terminal','intended_use':{'straight':'Repeatable three-cell bookwall with continuous sheltered collection/study edge',
              'curved':'Quarter-turn collection return; tangent stock envelopes fully supported by curved boards',
              'terminal':'Closed, framed end face terminating shelves, plinth and continuous canopy'}[kind],
              'component_height_m':3.4,
              'shelter_underside':{'forward_extent_from_back_datum_m':1.015,
                    'plinth_forward_extent_m':.445,'clear_component_envelope_forward_of_plinth_z_min_m':2.835,
                    'central_open_span_soffit_min_z_m':3.025,
                    'meaning':'Geometry-only local overhang envelope; no original room/headroom or actor fit claim'},
              'source_method':'New original script-assisted intentional profile design; editable semantic mesh parts and retained modifiers',
              'export':{'format':'GLB','Y_up':True,'unit_scale':1,'apply_modifiers':True,'consolidation':'By shared material role',
              'UV':'metric_material_uv normalized before join; metric real end-cap UV; evaluated bevel repair'},
              'limitations':['Independent component size only; original room fit and headroom untested','Upper collections need staff access planning',
              'No engine, rig, physics, lighting, scene or performance acceptance'],
              'hashes':{'blend_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256(glb.read_bytes()).hexdigest()}}
        RECORDS.append(meta); COLLISIONS[cid]={'status':'Numeric proposal only; not engine-tested','units':'Blender local metres','parts':collision}
    stock_api={'coordinate_system':'Blender metres, Z up, X across, front −Y; GLB uses standard glTF Y-up conversion',
       'anchor_origin':'Centre of nominal .68 × .24 m footprint at book bases; Z=exact shelf top',
       'stock_envelope_m':[.68,.24,.29],'shelf_tops_m':TOPS,
       'assets':{r['catalogue_id']:r['shelf_top_stock_anchors'] for r in RECORDS},
       'assembly_instances':[{'id':ids['straight'],'translation_m':[0,0,0],'rotation_z_degrees':0},
           {'id':ids['curved'],'translation_m':[2.4,0,0],'rotation_z_degrees':0},
           {'id':ids['terminal'],'translation_m':[4.2,1.8,0],'rotation_z_degrees':90}],
       'caveats':['Stock grouping original origin must be converted to this centre-base convention if different',
                 'No stock or user remains suspended; boards support every proposed footprint','Upper access planning pending']}
    (BASE/'stock_anchors.json').write_text(json.dumps(stock_api,indent=2)+'\n')
    (BASE/'collision_proposals.json').write_text(json.dumps(COLLISIONS,indent=2)+'\n')
    manifest={'family':'AST-LIB-STR','unique_assets':3,'assets':RECORDS,
        'assembly':{'instances':stock_api['assembly_instances'],'triangles_evaluated':sum(r['triangles_evaluated'] for r in RECORDS)},
        'material_revision':'astraea-catalogue-materials-02; unchanged shared helper and textures',
        'reference_pixels_inspected':json.loads((CAT/'batches/batch02/reference_manifest.json').read_text())['inputs'],
        'scope':'Blender independent component evidence only; not missing original ship reconstruction'}
    manifest['dependency_sha256']={str(p.relative_to(CAT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [Path(__file__),CAT/'standards/materials.py',CAT/'materials/material_manifest.json']}
    (BASE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('LIBRARY_STRUCTURE_COMPLETE',json.dumps({r['catalogue_id']:{'triangles':r['triangles_evaluated'],'bounds':r['bounds']} for r in RECORDS}))

if __name__=='__main__':main()
