"""Two original Astraea study assets. Blender 4.3, metres, editable semantic parts.
Run: blender -b -t 4 --python build_study.py
Only writes assets/library_study. No game files or reference pixels are used.
"""
from pathlib import Path
import math, json, sys, hashlib
import bpy, bmesh
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent.parent
sys.path.insert(0,str(BASE/'standards'))
from materials import materials
M={}; PARTS=[]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system='METRIC'
    bpy.context.scene.unit_settings.scale_length=1
    global M,PARTS
    M=materials(); PARTS=[]

def uv_metric(mesh,role,grain='x'):
    uv=mesh.uv_layers.active or mesh.uv_layers.new(name='UV_Metric_Metres')
    uv.name='UV_Metric_Metres'; uv.active_render=True
    tile=M[role].get('meters_per_tile_uv',[1,1])
    g={'x':0,'y':1,'z':2}[grain]
    for p in mesh.polygons:
        normal_axis=max(range(3),key=lambda k:abs(p.normal[k]))
        axes=[a for a in range(3) if a!=normal_axis]
        if g in axes: axes.remove(g); axes.append(g)
        for li in p.loop_indices:
            co=mesh.vertices[mesh.loops[li].vertex_index].co
            uv.data[li].uv=(co[axes[0]]/tile[0],co[axes[1]]/tile[1])

def mesh_obj(name,verts,faces,role,grain='x',bevel=.003):
    me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
    me.materials.append(M[role]);ob['semantic_role']=role;ob['grain_axis']=grain
    uv_metric(me,role,grain)
    if bevel:
        mod=ob.modifiers.new('Retained edge easing','BEVEL');mod.width=bevel;mod.segments=1
        mod=ob.modifiers.new('Retained weighted normals','WEIGHTED_NORMAL');mod.keep_sharp=True
    PARTS.append(ob);return ob

def extrusion(name,profile,lo,hi,role,axis='z',grain='x',bevel=.003):
    if axis=='z':vs=[(a,b,c) for c in (lo,hi) for a,b in profile]
    elif axis=='x':vs=[(c,a,b) for c in (lo,hi) for a,b in profile]
    n=len(profile);fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]
    fs += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh_obj(name,vs,fs,role,grain,bevel)

def rounded(w,d,r=.09,n=5,center=(0,0)):
    pts=[]
    for cx,cy,angle in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
        for j in range(n):
            a=math.radians(angle+90*j/(n-1));pts.append((center[0]+cx+r*math.cos(a),center[1]+cy+r*math.sin(a)))
    return pts

def slab(name,w,d,z0,z1,role,center=(0,0),r=.05,grain='x',bevel=.003):
    return extrusion(name,rounded(w,d,r,4,center),z0,z1,role,grain=grain,bevel=bevel)

def beam(name,a,b,w,d,role,bevel=.004):
    delta=Vector(b)-Vector(a);mid=(Vector(a)+Vector(b))/2
    vs=[(sx*w/2,sy*d/2,sz*delta.length/2) for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    fs=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    ob=mesh_obj(name,vs,fs,role,'z',bevel);ob.location=mid;ob.rotation_euler=delta.to_track_quat('Z','Y').to_euler();return ob

def ring(name,outer,inner,z0,z1,role,bevel=.003):
    n=len(outer);assert n==len(inner)
    vs=[(x,y,z) for z in (z0,z1) for pts in (outer,inner) for x,y in pts]
    fs=[]
    for i in range(n):
        k=(i+1)%n
        fs.extend([(i,k,n+k,n+i),(2*n+i,3*n+i,3*n+k,2*n+k),(i,2*n+i,2*n+k,k),(n+i,n+k,3*n+k,3*n+i)])
    return mesh_obj(name,vs,fs,role,'x',bevel)

def shared_table():
    outer=rounded(2.24,1.15,.155);inner=rounded(2.102,1.012,.095)
    ring('SHARED_sculpted_walnut_perimeter',outer,inner,.700,.750,'warm_walnut',.004)
    slab('SHARED_flush_stone_reading_surface',2.108,1.018,.721,.750,'warm_stone',r=.098,bevel=.002)
    # Rim has a real lower shoulder and shallow inset ivory reveal.
    ring('SHARED_recessed_ivory_underlip',rounded(2.18,1.09,.13),rounded(2.075,.985,.08),.693,.708,'ivory_enamel',.002)
    for x,lab in [(-1.025,'LEFT'),(1.025,'RIGHT')]:
        for sy,flab in [(-1,'FRONT'),(1,'BACK')]:
            # Dogleg profile makes a load-bearing rib, not a decorated box.
            profile=[(sy*y,z) for y,z in [(.455,.020),(.484,.060),(.455,.139),(.358,.393),(.390,.664),(.478,.692),(.460,.716),(.275,.708),(.276,.618),(.272,.371),(.353,.112),(.355,.028)]]
            extrusion(f'SHARED_{lab}_{flab}_swept_ivory_rib',profile,x-.045,x+.045,'ivory_enamel',axis='x',grain='z',bevel=.005)
            slab(f'SHARED_{lab}_{flab}_floor_pad',.108,.146,0,.028,'dark_rubber',(x,sy*.409),r=.021,grain='y',bevel=.002)
            beam(f'SHARED_{lab}_{flab}_timber_seat', (x,sy*.34,.669),(x,sy*.488,.691),.115,.033,'warm_walnut',.003)
        beam(f'SHARED_{lab}_upper_bearing_rail',(x,-.47,.683),(x,.47,.683),.093,.040,'warm_walnut',.003)
    # The central rail is entirely overhead: no under-table foot stretcher.
    beam('SHARED_high_central_tie',(-1.04,0,.700),(1.04,0,.700),.061,.037,'warm_walnut',.003)
    # Recessed receiver plate is geometry only, usable from either side.
    slab('SHARED_optional_fixture_receiver',.14,.09,.750,.754,'champagne_metal',(0,0),r=.024,bevel=.001)
    chairs=[]
    for x in [-.55,.55]:
        for side in [-1,1]:
            chairs.append({'reference_id':'AST-FUR-002','origin_m':[x,side*1.035,0],'rotation_z_degrees':180 if side<0 else 0,'seat_crown_z_m':.475,'contact_claim':False,
                'outside_table_approach_rectangle_m':[[x-.48,-1.85 if side<0 else .60],[x+.48,-.60 if side<0 else 1.85]],
                'knee_volume_m':{'min':[max(x-.40,-.96),-.515 if side<0 else .04,0],'max':[min(x+.40,.96),-.04 if side<0 else .515,.665]},
                'note':'Chair partly occupies proposed outside-table envelope; movement and user access are untested, not navigation clearance'})
    return {
      'catalogue_id':'AST-LIB-STUDY-01','name':'Astraea Open Shared Study Table',
      'intent':'Four proposed reading positions on two long edges. No seats included, no venue-capacity claim.',
      'surface_z_m':.750,'fixture_receiver_z_m':.754,
      'reading_surface_use_rectangles_m':[{'min':[x-.35,y-.19,.75],'max':[x+.35,y+.19,.75]} for x in [-.55,.55] for y in [-.27,.27]],
      'approach':{'sides':['-Y','+Y'],'candidate_chairs':chairs,'status':'Proposed component placement only; original rig, species fit, reach, collision behavior and room fit untested'},
      'clear_volumes_m':[{'name':'central_knee_and_foot_void','min':[-.960,-.515,0],'max':[.960,.515,.665]}],
      'bookstock_mounts':[{'name':'central_folio_optional','stock_catalogue_id':'AST-LIB-007','origin_m':[.0,.20,.75],'rotation_z_degrees':0,'envelope_m':[.370,.256,.0801],'note':'Optional open folio placement. Four writing rectangles are each .70x.38m and stop at |X|=.20, leaving .015m beyond measured folio bounds. Fixtures and reading reach remain integration proposals.'}],
      'fixture_mounts':[{'name':'central_shared_light_receiver','origin_m':[0,0,.754],'normal':[0,0,1],'plate_size_m':[.14,.09],'status':'Geometry and data only, no fixture, wiring, light or runtime system'}],
      'relationships':[{'members':['floor_pad','swept_ivory_rib'],'minimum_overlap_m':.008},{'members':['swept_ivory_rib','upper_bearing_rail','sculpted_walnut_perimeter'],'intent':'Load path overlaps at end frames; no stretcher across user approach or feet'},{'members':['flush_stone_reading_surface','sculpted_walnut_perimeter'],'inset_overlap_m':.003}]
    }

def single_edge():
    # Wing is a narrow bookcase opening into the reading space, with a porous
    # timber outer screen rising toward the rear. It gives privacy through use.
    for y,label,h in [(-.33,'FRONT',1.205),(.48,'REAR',1.380)]:
        p=[(y-.043,.025),(y+.043,.025),(y+.038,h-.026),(y+.015,h),(y-.032,h-.011)]
        extrusion('SINGLE_'+label+'_shaped_wing_post',p,-.885,-.824,'ivory_enamel',axis='x',grain='z',bevel=.006)
        slab('SINGLE_'+label+'_wing_floor_pad',.117,.13,0,.033,'dark_rubber',(-.837,y),r=.024,bevel=.002)
    # Useful clear internal shelf width .72, depth .27; stock fronts face +X.
    for z,label in [(.385,'LOWER'),(.795,'UPPER')]:
        slab('SINGLE_'+label+'_wing_book_shelf',.318,.82,z,z+.035,'warm_walnut',(-.715,.075),r=.030,grain='y',bevel=.003)
        beam('SINGLE_'+label+'_inboard_shelf_rail',(-.568,-.312,z+.022),(-.568,.459,z+.022),.022,.043,'warm_walnut',.002)
    # Staggered open battens: shelf contents remain legible through the side.
    for j,y in enumerate([-.265,-.139,-.013,.113,.239,.365]):
        top=1.218+(y+.265)/.63*.14
        profile=[(y-.027,.359),(y+.027,.359),(y+.024,top-.025),(y-.008,top),(y-.025,top-.005)]
        extrusion('SINGLE_outer_privacy_batten_%02d'%j,profile,-.854,-.822,'warm_walnut',axis='x',grain='z',bevel=.0025)
    beam('SINGLE_sloping_wing_crown',(-.848,-.346,1.189),(-.848,.484,1.367),.064,.063,'warm_walnut',.005)
    # Small front toe shelf closes the bookcase's own base, never the desk void.
    slab('SINGLE_wing_low_plinth',.317,.818,.086,.119,'ivory_enamel',(-.715,.075),r=.03,grain='y',bevel=.003)
    # Asymmetric outline: broad round outer corner, welcoming shallow scoop at entry.
    p=[(-.582,-.460),(-.410,-.460),(-.205,-.431),(.080,-.421),(.380,-.450),(.634,-.477),(.760,-.444),(.810,-.375),(.823,-.238),(.812,.334),(.768,.419),(.661,.454),(-.582,.454)]
    extrusion('SINGLE_carved_walnut_writing_edge',p,.695,.750,'warm_walnut',grain='x',bevel=.008)
    inset=[(-.507,-.365),(-.35,-.365),(-.18,-.348),(.09,-.335),(.372,-.365),(.627,-.389),(.699,-.365),(.728,-.304),(.737,-.213),(.726,.297),(.696,.336),(.625,.369),(-.507,.369)]
    extrusion('SINGLE_inset_stone_writing_surface',inset,.747,.752,'warm_stone',grain='x',bevel=.002)
    # Two housed side tenons transfer the writing edge to the wing end posts;
    # each sits beyond the declared stock row, preserving its clear height.
    beam('SINGLE_front_wing_desk_tenon',(-.862,-.333,.710),(-.527,-.333,.710),.068,.064,'warm_walnut',.003)
    beam('SINGLE_rear_wing_desk_tenon',(-.862,.472,.710),(-.527,.472,.710),.068,.064,'warm_walnut',.003)
    # A shallow ivory under-edge intersects load points but not knee space.
    beam('SINGLE_rear_ivory_bearing_rail',(-.610,.347,.697),(.742,.347,.697),.067,.059,'ivory_enamel',.004)
    # Open fork at the right side: the central reading entry is wholly open.
    right=[(-.355,.027),(-.399,.045),(-.403,.10),(-.350,.220),(-.185,.457),(-.166,.590),(-.255,.704),(-.194,.713),(-.095,.621),(-.091,.435),(-.253,.183),(-.286,.029)]
    extrusion('SINGLE_right_forward_swept_leg',right,.700,.773,'ivory_enamel',axis='x',grain='z',bevel=.005)
    back=[(.268,.024),(.370,.024),(.395,.071),(.315,.377),(.344,.696),(.289,.718),(.241,.697),(.240,.370)]
    extrusion('SINGLE_right_rear_swept_leg',back,.700,.773,'ivory_enamel',axis='x',grain='z',bevel=.005)
    for y,label in [(-.335,'FRONT'),(.315,'REAR')]:
        slab('SINGLE_right_'+label+'_floor_pad',.104,.128,0,.032,'dark_rubber',(.736,y),r=.024,bevel=.002)
    beam('SINGLE_right_top_bearing',(.738,-.260,.697),(.738,.361,.697),.095,.039,'warm_walnut',.003)
    # Receiver tucked at rear-left; no claim that a separate light is supplied.
    slab('SINGLE_optional_fixture_receiver',.09,.12,.752,.756,'champagne_metal',(-.433,.286),r=.023,bevel=.001)
    return {
      'catalogue_id':'AST-LIB-STUDY-02','name':'Astraea Sheltered Single Study Edge',
      'intent':'One proposed reading position, useful inward-facing two-tier book wing, open central sightline and front approach. No seat or book stock included.',
      'surface_z_m':.752,'fixture_receiver_z_m':.756,
      'approach':{'sides':['-Y'],'candidate_chairs':[{'reference_id':'AST-FUR-002','origin_m':[.105,-.99,0],'rotation_z_degrees':180,'seat_crown_z_m':.475,'contact_claim':False}],
        'clear_floor_entry_rectangle_m':[[-.49,-1.68],[.67,-.48]],'status':'Proposed component placement only; original rig, species fit, reach, collision behavior and room fit untested'},
      'clear_volumes_m':[{'name':'central_knee_and_foot_void','min':[-.495,-.415,0],'max':[.655,.299,.686]},{'name':'central_seated_outlook_above_desk','min':[-.405,-.25,.760],'max':[.650,.40,1.45]}],
      'bookstock_mounts':[{'name':label,'origin_m':[-.711,.075,z],'rotation_z_degrees':90,'envelope_m':[.68,.24,.29], 'shelf_usable_local_m':[.72,.27], 'clear_height_m':clear,'front_axis_world':[1,0,0]} for label,z,clear in [('lower_inward_facing_shelf',.420,.375),('upper_inward_facing_shelf',.830,.342)]],
      'fixture_mounts':[{'name':'rear_left_reading_light_receiver','origin_m':[-.433,.286,.756],'normal':[0,0,1],'plate_size_m':[.09,.12],'status':'Geometry and data only, no fixture, wiring, light or runtime system'}],
      'relationships':[{'members':['wing_floor_pad','shaped_wing_post'],'minimum_overlap_m':.008},{'members':['wing_book_shelf','shaped_wing_post','outer_privacy_batten'],'intent':'Housed shelf junction and porous outside screening'},{'members':['carved_walnut_writing_edge','wing_book_shelf','rear_ivory_bearing_rail','right_top_bearing'],'intent':'Left wing bears desk; right fork and rear rail carry opposite side'},{'members':['inset_stone_writing_surface','carved_walnut_writing_edge'],'overlap_m':.003}]
    }

def stats(objects):
    dg=bpy.context.evaluated_depsgraph_get();allv=[];parts=[];tri=0
    for ob in objects:
        eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles()
        vs=[tuple(ob.matrix_world@v.co) for v in me.vertices];allv+=vs;tri+=len(me.loop_triangles)
        lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
        parts.append({'name':ob.name,'bounds_min_m':lo,'bounds_max_m':hi,'triangles':len(me.loop_triangles),'role':ob['semantic_role'],'grain_axis':ob['grain_axis'],'modifiers':[m.name for m in ob.modifiers]})
        eo.to_mesh_clear()
    lo=[min(v[i] for v in allv) for i in range(3)];hi=[max(v[i] for v in allv) for i in range(3)]
    return {'bounds_min_m':lo,'bounds_max_m':hi,'dimensions_m':[b-a for a,b in zip(lo,hi)],'triangles_evaluated':tri,'parts':parts}

def finish(info,slug):
    origin=bpy.data.objects.new(info['catalogue_id']+'_floor_origin',None);bpy.context.collection.objects.link(origin)
    origin['catalogue_id']=info['catalogue_id'];origin['pivot']='Floor origin; X width, Z up, front -Y'
    for ob in PARTS:
        ob.parent=origin;ob['catalogue_id']=info['catalogue_id'];ob['provenance']='New original independent 2026-10-02 catalogue geometry'
    bpy.context.view_layer.update();info.update(stats(PARTS))
    refs=json.loads((BASE/'batches/batch02/reference_manifest.json').read_text())['inputs']
    info.update({'units':'metres','front_axis':'-Y','source_up_axis':'+Z','pivot_m':[0,0,0],'blender_version':bpy.app.version_string,
       'authoring':'Script-assisted original shaped polygon extrusions and semantic join design, editable meshes and non-destructive bevel/normal modifiers retained.',
       'qa_scope':'Blender component evidence only. Unavailable original game is not restored or edited. Godot, controller, collision behavior, alien contact and room-fit claims are pending.',
       'reference_provenance':[{'library_file_id':r['library_file_id'],'sha256':r['sha256'],'pixels_inspected':True,'use':'Use, spatial edge, silhouette and material guidance only; no copied geometry or texture pixels'} for r in refs],
       'materials_revision':'astraea-catalogue-materials-02','materials':sorted(set(ob['semantic_role'] for ob in PARTS)),
       'source_generator':'build_study.py','source_generator_sha256':sha(Path(__file__)),
       'shared_material_source_sha256':sha(BASE/'standards/materials.py'),'shared_material_manifest_sha256':sha(BASE/'materials/material_manifest.json'),
       'dependencies':['../../standards/materials.py','../../materials/material_manifest.json','../../materials/*.png'],
       'asset_files':[slug+'.blend',slug+'.glb'],
       'floor_contacts':[{'source_part':p['name'],'bounds_min_m':p['bounds_min_m'],'bounds_max_m':p['bounds_max_m']} for p in info['parts'] if p['bounds_min_m'][2]<1e-6]})
    assert abs(info['bounds_min_m'][2])<1e-7
    shapes=[]
    for part in info['parts']:
        # Exact independent per-part volumes; no scene hull and no auto physics.
        if any(x in part['name'] for x in ['receiver','underlip','timber_seat','inboard_shelf_rail']):continue
        lo=part['bounds_min_m'];hi=part['bounds_max_m']
        shapes.append({'source_part':part['name'],'type':'box_proposal','centre_m':[(a+b)/2 for a,b in zip(lo,hi)],'size_m':[b-a for a,b in zip(lo,hi)],'rotation_degrees':[0,0,0],
                       'qualification':'Conservative evaluated part AABB. Refinement for rounded outlines and swept ribs required on engine adoption; central knee/foot openings retained.'})
    collision={'catalogue_id':info['catalogue_id'],'status':'Numeric proposal only; not exported as runtime physics and not engine tested','coordinates':'Blender local metres, Z up', 'parts':shapes,'preserved_clear_volumes_m':info['clear_volumes_m']}
    (ROOT/(slug+'.collision_proposal.json')).write_text(json.dumps(collision,indent=2))
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/(slug+'.blend')),compress=True)
    bpy.ops.object.select_all(action='DESELECT');dg=bpy.context.evaluated_depsgraph_get();copies=[]
    for ob in PARTS:
        eo=ob.evaluated_get(dg);me=bpy.data.meshes.new_from_object(eo,preserve_all_data_layers=True,depsgraph=dg)
        # Every evaluated bevel triangle gets nonzero metric UV; normalize before join.
        uv_metric(me,ob['semantic_role'],ob['grain_axis'])
        keep=me.uv_layers.active
        for layer in list(me.uv_layers):
            if layer!=keep:me.uv_layers.remove(layer)
        keep.name='UV_Metric_Metres';keep.active_render=True
        copy=bpy.data.objects.new('EXPORT_'+ob.name,me);bpy.context.collection.objects.link(copy);copy.matrix_world=ob.matrix_world.copy();copy.select_set(True);copies.append(copy)
    bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();combined=bpy.context.object
    combined.name=info['catalogue_id']+'_static_visual';bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    combined.parent=origin;combined['source_part_count']=len(PARTS);combined['provenance']='Evaluated export copy; editable source is paired blend'
    origin.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(ROOT/(slug+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_materials='EXPORT',export_extras=True)
    info['export']={'format':'GLB','Y_up':True,'static_visual_meshes':1,'material_primitives':len(combined.data.materials),'source_semantic_part_count':len(PARTS),'UVs':'Normalized UV_Metric_Metres before joining; projected in part-local metres; walnut grain V follows named grain axis','textures':'Ordinary shared Principled base-color images embedded','collision':'None, separate numeric proposal only'}
    for ext in ['blend','glb']:info[ext+'_sha256']=sha(ROOT/(slug+'.'+ext))
    (ROOT/(slug+'.manifest.json')).write_text(json.dumps(info,indent=2));return info

if __name__=='__main__':
    records=[]
    for maker,slug in [(shared_table,'AST-LIB-STUDY-01_open_shared_table'),(single_edge,'AST-LIB-STUDY-02_sheltered_single_edge')]:
        reset();records.append(finish(maker(),slug))
    api=[{k:r[k] for k in ['catalogue_id','name','bounds_min_m','bounds_max_m','dimensions_m','surface_z_m','approach','clear_volumes_m','bookstock_mounts','fixture_mounts']} for r in records]
    (ROOT/'integration_api.json').write_text(json.dumps(api,indent=2))
    print('STUDY_COMPLETE',[(r['catalogue_id'],r['dimensions_m'],r['triangles_evaluated']) for r in records])
