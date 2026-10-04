"""Original engineering utility modules. Blender 4.3, metres, Z-up.
Run: blender -b -t 2 --python assets/utility_pipework/source/build_utility_pipework.py
Fixed pipe inlets are the origin. No room, fluid solve or operating rating.
"""
import bpy,bmesh,math,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,CAT/'standards'/f'{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
ports=load('utility_ports');MATS=load('staff_materials').materials()
ROLE={'paint':'staff_bluegrey_paint','zinc':'staff_zinc','rubber':'staff_rubber','label':'staff_label','red':'staff_cable_red','white':'staff_white_paint','blue':'staff_cable_blue'}

def reset():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
def mesh(name,v,f,role='paint',bevel=0):
    o=ports.mesh(name,v,f,MATS[ROLE[role]])
    if bevel:
        m=o.modifiers.new('Editable edge radii','BEVEL');m.width=bevel;m.segments=2;m.limit_method='ANGLE'
        m=o.modifiers.new('Editable weighted normals','WEIGHTED_NORMAL');m.keep_sharp=True
    return o
def box(name,c,d,role='zinc',bevel=.002):
    v=[(c[0]+x*d[0]/2,c[1]+y*d[1]/2,c[2]+z*d[2]/2) for x,y,z in[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    return mesh(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel)
def cylinder(name,a,b,r,role='zinc',n=24):return ports.solid_cylinder(name,a,b,r,MATS[ROLE[role]],n)
def ring(name,face,normal,stations,role='paint',n=48):return ports.annular(name,face,normal,stations,MATS[ROLE[role]],n)
def tube_curve(name,stations,ri=.08,ro=.10,role='paint',n=48):
    v=[];f=[]
    for p,t in stations:
        p=Vector(p);t,u,w=ports.basis(t)
        for r in(ro,ri):v.extend(tuple(p+r*(u*math.cos(2*math.pi*i/n)+w*math.sin(2*math.pi*i/n))) for i in range(n))
    for k in range(len(stations)-1):
        for i in range(n):
            j=(i+1)%n;a=2*n*k;b=a+2*n
            f.extend([(a+i,a+j,b+j,b+i),(a+n+j,a+n+i,b+n+i,b+n+j)])
    for i in range(n):
        j=(i+1)%n;a=2*n*(len(stations)-1)
        f.extend([(j,i,n+i,n+j),(a+i,a+j,a+n+j,a+n+i)])
    return mesh(name,v,f,role)
def torus(name,c,major,minor,role='rubber',major_n=64,minor_n=12):
    v=[];f=[]
    for i in range(major_n):
        t=2*math.pi*i/major_n
        for j in range(minor_n):
            q=2*math.pi*j/minor_n;r=major+minor*math.cos(q)
            v.append((c[0]+r*math.cos(t),c[1]+r*math.sin(t),c[2]+minor*math.sin(q)))
    for i in range(major_n):
        for j in range(minor_n):f.append((i*minor_n+j,((i+1)%major_n)*minor_n+j,((i+1)%major_n)*minor_n+(j+1)%minor_n,i*minor_n+(j+1)%minor_n))
    return mesh(name,v,f,role)
def empty(name,p,metadata):
    o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.location=p;o.empty_display_size=.035;o.empty_display_type='ARROWS'
    for k,v in metadata.items():
        if isinstance(v,dict) or (isinstance(v,list) and v and isinstance(v[0],(dict,list))):o[k+'_json']=json.dumps(v)
        else:o[k]=v
    return o
def attach_ports(objects,specs):
    records=[]
    for name,face,normal in specs:
        row=ports.add_flange(name,face,normal,MATS);objects+=row['objects'];records.append(row['record'])
        ports.add_port_marker(name,face,normal,row['record'])
    return records
def identify(objects,x,axis=(1,0,0),face=(0,0,0)):
    objects.append(ring('flow_family_identification_band',face,axis,[(x,.1001,.102),(x+.021,.1001,.102)],'blue'))
    objects.append(ring('maintenance_identifier_band',face,axis,[(x+.025,.1001,.102),(x+.037,.1001,.102)],'label'))

def straight():
    obj=[ring('continuous_open_straight_shell',(0,0,0),(1,0,0),[(.085,.08,.1),(.715,.08,.1)])]
    identify(obj,.255)
    rec=attach_ports(obj,[('INLET',(0,0,0),(-1,0,0)),('OUTLET',(.8,0,0),(1,0,0))])
    return obj,rec,[],{'face_to_face_pitch_m':.8,'shell_wall_thickness_m':.02,'external_mounting':'Plain pipe shell accepts separately engineered saddles; no fixed floor legs; module can rotate into horizontal, vertical or overhead routes','contact_containment':'Two hollow necks overlap the pipe by .010 m without entering the .08 m radius bore or exterior finished shell'},[]
def elbow():
    r=.45;lead=.12
    # Short tangent necks blend into a true constant-radius quarter turn.
    stations=[((.085,0,0),(1,0,0))]
    for i in range(33):
        t=(math.pi/2)*i/32;stations.append(((lead+r*math.sin(t),r*(1-math.cos(t)),0),(math.cos(t),math.sin(t),0)))
    stations.append(((lead+r,lead+r-.085,0),(0,1,0)))
    obj=[tube_curve('continuous_quarter_turn_hollow_shell',stations)]
    # Neck overlap is intentional. Full-radius arc stays behind both front planes.
    rec=attach_ports(obj,[('INLET',(0,0,0),(-1,0,0)),('OUTLET',(r+lead,r+lead,0),(0,1,0))])
    return obj,rec,[],{'centreline_radius_m':r,'centreline_arc_length_m':r*math.pi/2,'tangent_length_each_m':lead,'total_centreline_length_m':r*math.pi/2+2*lead,'turn_degrees':90,'shell_wall_thickness_m':.02,'external_mounting':'No fixed supports: compatible with source +Z roll for horizontal routes and source +X roll into a vertical turn','contact_containment':'Straight tangents keep each .095 m hollow flange neck behind the start of curvature; .010 m coaxial neck-shell overlap preserves the continuous bore'},[]
def valve():
    obj=[ring('valve_shaped_open_body',(0,0,0),(1,0,0),[(.085,.08,.1),(.15,.08,.1),(.22,.08,.146),(.27,.08,.152),(.38,.08,.152),(.43,.08,.146),(.50,.08,.1),(.565,.08,.1)])]
    # Raised split-body flanges preserve the open .16 m passage and read as serviceable casing.
    for x in(.245,.385):obj.append(ring('valve_split_body_service_rim_'+str(x),(0,0,0),(1,0,0),[(x-.009,.081,.153),(x+.009,.081,.163)],'zinc'))
    for i in range(8):
        a=2*math.pi*i/8;y=.155*math.cos(a);z=.155*math.sin(a)
        obj.append(cylinder(f'body_tie_rod_{i}',(.233,y,z),(.404,y,z),.005,'zinc',10))
        for x in(.228,.405):obj.append(cylinder(f'body_service_nut_{i}_{x}',(x,y,z),(x+.012,y,z),.010,'zinc',6))
    # Bonnet socket penetrates only the thick upper body wall, above the open bore.
    obj.append(cylinder('bonnet_pressure_housing',( .325,0,.128),(.325,0,.265),.073,'paint',32))
    obj.append(box('bonnet_bolted_service_cover',(.325,0,.269),(.184,.174,.026),'zinc',.008))
    obj.append(box('bonnet_dark_joint',(.325,0,.251),(.166,.159,.012),'rubber',.004))
    for sx in(-1,1):
        for sy in(-1,1):obj.append(cylinder(f'bonnet_captive_hex_{sx}_{sy}',(.325+sx*.065,sy*.060,.281),(.325+sx*.065,sy*.060,.294),.011,'zinc',6))
    # Two closed tapered cast uprights form a yoke. Inner opening leaves stem visible.
    for sy in(-1,1):
        y0=sy*.055;y1=sy*.067
        verts=[(.28,y0,.279),(.37,y0,.279),(.354,y0,.399),(.296,y0,.399),(.28,y1,.279),(.37,y1,.279),(.354,y1,.399),(.296,y1,.399)]
        obj.append(mesh(f'closed_tapered_yoke_cheek_{sy}',verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'paint',.002))
    obj.append(box('yoke_upper_bridge',(.325,0,.397),(.065,.139,.026),'paint',.005))
    obj.append(cylinder('stem_guide_gland',(.325,0,.386),(.325,0,.425),.029,'zinc',24))
    obj.append(cylinder('exposed_manual_stem',(.325,0,.279),(.325,0,.469),.012,'zinc',24))
    obj.append(box('manual_identification_plate',(.325,-.075,.332),(.061,.006,.046),'label',.002))
    # Raised three-line score is an original symbol, deliberately not an operating readout.
    for z in(.319,.329,.339):obj.append(box('manual_plate_score_'+str(z),(.325,-.079,z),(.040,.002,.003),'blue',.0005))
    wp=(.325,0,.466);wheel=[]
    wheel.append(torus('manual_wheel_continuous_grip',wp,.165,.015,'rubber'))
    wheel.append(cylinder('manual_wheel_hub',(.325,0,.448),(.325,0,.485),.037,'red',32))
    for i in range(6):
        a=2*math.pi*i/6
        wheel.append(cylinder(f'manual_wheel_spoke_{i}',(.325+.030*math.cos(a),.030*math.sin(a),.466),(.325+.163*math.cos(a),.163*math.sin(a),.466),.011,'red',12))
        wheel.append(torus(f'manual_wheel_grip_land_{i}',(.325+.165*math.cos(a),.165*math.sin(a),.466),.017,.004,'red',20,8))
    rec=attach_ports(obj,[('INLET',(0,0,0),(-1,0,0)),('OUTLET',(.65,0,0),(1,0,0))])
    grips=[{'name':'wheel_grip_'+str(i+1),'kind':'physical grip centreline, not pose centre','position_blender_source_m':[.325+.165*math.cos(2*math.pi*i/6),.165*math.sin(2*math.pi*i/6),.466],'position_gltf_yup_m':ports.exchange([.325+.165*math.cos(2*math.pi*i/6),.165*math.sin(2*math.pi*i/6),.466]),'grip_minor_radius_m':.015}for i in range(6)]
    meta={'metadata_revision':'utility-wheel-frame-01','source_frame':'Blender Z-up asset source, metres','exchange_frame':'GLB Y-up asset exchange, metres','pivot_blender_source_m':list(wp),'pivot_gltf_yup_m':ports.exchange(wp),'wheel_axis_blender_source':[0,0,1],'wheel_axis_gltf_yup':[0,1,0],'grip_records':grips,'default_visual_pose':'Open bore geometric inspection state','motion_scope':'Rotatable wheel mesh only; no rig, valve travel mapping or simulation'}
    root=empty('VALVE_CONTROL_WHEEL',wp,meta)
    for o in wheel:
        o.parent=root;o.location=-Vector(wp);o['moving_part']='VALVE_CONTROL_WHEEL'
    return obj+wheel,rec,[meta],{'face_to_face_pitch_m':.65,'bore_state':'open, continuous .16 m nominal passage','wheel_maximum_outer_span_m':.372,'continuous_grip_ring_outer_diameter_m':.36,'wheel_pivot_height_above_pipe_axis_m':.466,'wheel_lowest_surface_above_yoke_m':.041,'contact_containment':'Bonnet begins Z .128 in top wall; bore top Z .080. Yoke toes end inside service cover, tips inside bridge. Stem passes actual guide and hub; no support crosses the bare flange plane.','service_envelope_blender_source_m':{'min':[.105,-.25,.25],'max':[.545,.25,.75]},'service_envelope_gltf_yup_m':{'min':[.105,.25,-.25],'max':[.545,.75,.25]},'service_envelope_scope':'Proposed hand and maintenance space, no actor usability claim'},grips

def measure(objects):
    dep=bpy.context.evaluated_depsgraph_get();points=[];tris=0
    for ob in objects:
        ev=ob.evaluated_get(dep);me=ev.to_mesh();me.calc_loop_triangles();tris+=len(me.loop_triangles);points.extend(ob.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
    low=[min(p[k] for p in points)for k in range(3)];high=[max(p[k]for p in points)for k in range(3)]
    return {'min_m':low,'max_m':high,'dimensions_m':[high[k]-low[k]for k in range(3)]},tris
def export(objects,ident):
    # Source saved first: keep all editable original parts. Export copy consolidates by role/motion group.
    groups={}
    for ob in objects:
        key=(ob.get('moving_part','static'),ob['material_role']);groups.setdefault(key,[]).append(ob)
    for (motion,role),group in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for ob in group:ob.select_set(True)
        bpy.context.view_layer.objects.active=group[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();ob=bpy.context.object;ob.name=ident+'__'+motion+'__'+role
        ports.metric_uv(ob,ob.data.materials[0]);ob['material_role']=role
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(BASE/'exports'/f'{ident}.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
def collision_record(kind,portsrec,meta):
    return {'source_frame':'Blender Z-up asset source, metres','exchange_frame':'GLB Y-up asset exchange, metres','proposal':'static triangle mesh using exported shell geometry; retain openings. Do not replace entire asset by a convex hull or box. Separate wheel mesh if interactive.','geometry_source':'matching exports/AST-ENG-'+{'straight':'004','elbow':'005','valve':'006'}[kind]+'.glb','preserve_open_bore_diameter_m':.16,'pipe_outer_diameter_m':.20,'port_records':portsrec,'moving_part':'VALVE_CONTROL_WHEEL' if kind=='valve' else None,'wheel_axes_and_pivot':meta,'status':'unimplemented proposal; receiving engine scale, contact tolerances and dynamic collision pending'}
def main():
    records=[];collision={}
    for kind,ident,title,fn in [('straight','AST-ENG-004','Flanged straight utility pipe',straight),('elbow','AST-ENG-005','Quarter-turn flanged utility elbow',elbow),('valve','AST-ENG-006','Yoke-supported manual isolation valve',valve)]:
        reset();objs,pr,motion,design,grips=fn();bpy.context.view_layer.update();bounds,tri=measure(objs)
        sc=bpy.context.scene;sc['catalogue_id']=ident;sc['source_frame']='Blender Z-up metres; inlet bare mating-face centre is origin';sc['scope']='Original independent artistic component, no original game geometry, real rating or flow simulation'
        rec={'catalogue_id':ident,'title':title,'revision':'utility-pipework-01','family':'Engineering utilities','provenance':'Original script-authored geometry informed by inspected technical blueprint and staff corridor purpose; no copied reference pixels or game assets','source_frame':'Blender Z-up, +X inlet to outlet for straight/valve; elbow turns +X to +Y; ordinary viewing front -Y','exchange_frame':'GLB Y-up, source (x,y,z) maps to (x,z,-y)','datum':'Inlet bare mating-face centre at source and GLB (0,0,0); no floor mount datum','bounds_blender_source':bounds,'bounds_gltf_yup':{'min_m':[bounds['min_m'][0],bounds['min_m'][2],-bounds['max_m'][1]],'max_m':[bounds['max_m'][0],bounds['max_m'][2],-bounds['min_m'][1]]},'evaluated_source_triangles':tri,'ports':pr,'motion':motion,'grips':grips,'design':design,'source_file':f'source/{ident}.blend','generator':'source/build_utility_pipework.py','export_file':f'exports/{ident}.glb','materials_library':'../../materials/staff/manifest.json','material_library_unchanged':True,'used_material_roles':sorted(set(o['material_role'] for o in objs)),'uv':{'layer':'metric_material_uv','method':'Metric dominant-face projection at unchanged staff material metres-per-tile; normalized on every mesh before role joins','status':'actual GLB accessor QA pending'},'normal_policy':'Closed oriented surface mesh; Boolean holes use exact solver, bevels and weighted normals on formed casework; actual GLB zero-area/finite normal QA pending','collision':'collision_proposals.json','ratings':'None. Artistic modular interface only. No pressure, flow, load, safety or material certification.','verification_limits':['Actual ship room fit pending','Receiving-engine collision and interactions pending','Wheel rotation has no valve-travel mapping','No pressure/fluid behavior or target-PC performance claim'],'references':'../../batches/batch06/reference_manifest.json'}
        bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'source'/f'{ident}.blend'),compress=True);export(objs,ident)
        rec['source_sha256']=hashlib.sha256((BASE/'source'/f'{ident}.blend').read_bytes()).hexdigest();rec['glb_sha256']=hashlib.sha256((BASE/'exports'/f'{ident}.glb').read_bytes()).hexdigest()
        (BASE/f'{ident}.manifest.json').write_text(json.dumps(rec,indent=2)+'\n');records.append(rec);collision[ident]=collision_record(kind,pr,motion)
    (BASE/'manifest.json').write_text(json.dumps({'family':'Engineering utility pipework','unique_design_count':3,'assets':records},indent=2)+'\n')
    (BASE/'collision_proposals.json').write_text(json.dumps(collision,indent=2)+'\n')
    api={'revision':'utility-pipework-01','source_frame':'Blender Z-up, metres','exchange_frame':'GLB Y-up, metres','mating_rule':'Coincident bare annular front faces with opposed normal; holes phase matched; no overlap of flange bodies or hardware','ports_by_asset':{r['catalogue_id']:r['ports']for r in records},'source_inspection_assembly':[{'instance':'approach','id':'AST-ENG-004','translation_m':[-.8,0,.75],'rotation_axis_blender_source':[0,0,1],'rotation_degrees':0},{'instance':'turn','id':'AST-ENG-005','translation_m':[0,0,.75],'rotation_axis_blender_source':[0,0,1],'rotation_degrees':0},{'instance':'valve','id':'AST-ENG-006','translation_m':[.57,.57,.75],'rotation_axis_blender_source':[0,0,1],'rotation_degrees':90}], 'exchange_inspection_assembly':[{'instance':'approach','id':'AST-ENG-004','translation_m':[-.8,.75,0],'rotation_axis_gltf_yup':[0,1,0],'rotation_degrees':0},{'instance':'turn','id':'AST-ENG-005','translation_m':[0,.75,0],'rotation_axis_gltf_yup':[0,1,0],'rotation_degrees':0},{'instance':'valve','id':'AST-ENG-006','translation_m':[.57,.75,-.57],'rotation_axis_gltf_yup':[0,1,0],'rotation_degrees':90}], 'seams':[{'a':'approach.OUTLET','b':'turn.INLET','position_blender_source_m':[0,0,.75],'position_gltf_yup_m':[0,.75,0]},{'a':'turn.OUTLET','b':'valve.INLET','position_blender_source_m':[.57,.57,.75],'position_gltf_yup_m':[.57,.75,-.57]}],'scope':'Bounded neutral component inspection; QA stands are absent from component exports'}
    (BASE/'port_and_seam_api.json').write_text(json.dumps(api,indent=2)+'\n');print('PIPEWORK_GENERATION_COMPLETE',[(r['catalogue_id'],r['evaluated_source_triangles'])for r in records])
if __name__=='__main__':main()
