"""Immutable aquatic successor. Run with Blender Python bpy 5.1.2 matching the retained original native.
Original native objects are preserved; two runout wall objects are retained but
excluded from exchange in favour of precisely bounded exit jambs.
"""
import bpy, bmesh, math, json, hashlib, importlib.util
from pathlib import Path
from mathutils import Vector,Matrix

P=Path(__file__).resolve().parent; R=P.parents[2]
ORIGINAL=R/'external_packages/aquatic_district_20261009/source/aquatic_district.blend'
assert not (P/'AquaticCompletion_r015.blend').exists(), 'Choose a new unique revision before authoring; retained natives are immutable'
assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()=='80c7c1756d4bbe9e74b37e150797115eff5f200977718b4f661f50a3849c9a28'
bpy.ops.wm.open_mainfile(filepath=str(ORIGINAL))
S=bpy.context.scene
def digest(o):
    if o.type!='MESH': return None
    m=o.data
    return hashlib.sha256(json.dumps({'vertices':[list(v.co) for v in m.vertices],'faces':[list(f.vertices) for f in m.polygons],'matrix':[list(x) for x in o.matrix_world],'uv':[[list(x.uv) for x in l.data] for l in m.uv_layers],'materials':[x.name for x in m.materials],'modifiers':[(x.name,x.type) for x in o.modifiers]},separators=(',',':')).encode()).hexdigest()
before={o.name:digest(o) for o in S.objects if o.type=='MESH'}
packed={im.name:hashlib.sha256(im.packed_file.data).hexdigest() for im in bpy.data.images if im.packed_file}
NEW=[]; LIGHTS=[]
def xyz(p): return Vector((p[0],-p[2],p[1]))
def mat(name):return bpy.data.materials[name]
M={k:mat(v) for k,v in {'stone':'ASTRAEA_warm_stone','ivory':'ASTRAEA_ivory_enamel','wood':'ASTRAEA_warm_walnut','metal':'ASTRAEA_champagne_metal','teal':'ASTRAEA_teal_weave','clay':'ASTRAEA_clay_weave','oat':'ASTRAEA_oatmeal_weave','grip':'ASTRAEA_dark_rubber','lens':'AQD_opal'}.items()}
def finish(o,n,role='stone',kind='architecture',bevel=0):
    o.name='AQ6__'+n;o['kind']=kind;o['programme_key']='D08_directory_08';o['support_owner']='retained_annex';o['construction_status']='group6_inactive_handoff'
    o.data.materials.clear();o.data.materials.append(M[role]);bpy.context.view_layer.objects.active=o
    if bevel:
        q=o.modifiers.new('Crafted source edges','BEVEL');q.width=bevel;q.segments=2;bpy.ops.object.modifier_apply(modifier=q.name)
    o.data.update();uv=o.data.uv_layers.new(name='UV0')
    for f in o.data.polygons:
        axes=[i for i in range(3) if i!=max(range(3),key=lambda i:abs(f.normal[i]))]
        for li in f.loop_indices:
            v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*.5,v[axes[1]]*.5)
    NEW.append(o);return o
def box(n,p,d,role='stone',kind='architecture',bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(p));o=bpy.context.object;o.dimensions=(d[0],d[2],d[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,role,kind,min(bevel,min(d)*.2))
def mesh(n,vs,fs,role='stone',kind='architecture'):
    m=bpy.data.meshes.new(n);m.from_pydata([xyz(v) for v in vs],[],fs);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();o=bpy.data.objects.new(n,m);S.collection.objects.link(o);return finish(o,n,role,kind)
def rod(n,a,b,r=.035,role='metal',kind='architecture'):
    a,b=xyz(a),xyz(b);d=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=d.length,location=(a+b)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,role,kind)
def band(n,c,rx,rz,a0,a1,width,bottom,top,role='stone'):
    vs=[];steps=16
    for y in [bottom,top]:
        for i in range(steps+1):
            a=a0+(a1-a0)*i/steps
            for w in [-width/2,width/2]:vs.append((c[0]+(rx+w)*math.cos(a),y,c[1]+(rz+w)*math.sin(a)))
    t=2*(steps+1);fs=[]
    for i in range(steps):
        k=2*i;fs.extend([(k,k+2,k+3,k+1),(k+t,k+1+t,k+3+t,k+2+t),(k,k+t,k+2+t,k+2),(k+1,k+3,k+3+t,k+1+t)])
    fs.extend([(0,1,t+1,t),(t-2,2*t-2,2*t-1,t-1)]);return mesh(n,vs,fs,role,'lounge_asset')
def lamp(n,x,y,z,mount_y,reach=6):
    rod(n+'_mount',(x,mount_y,z),(x,y+.13,z),.025)
    box(n+'_hood',(x,y+.13,z),(.55,.18,.55),'metal','fixture_mount')
    box(n+'_lens',(x,y,z),(.4,.055,.4),'lens','fixture_lens')
    LIGHTS.append({'id':n,'xyz':[x,y-.06,z],'range_m':reach,'energy':1.4,'receiver_xyz':[x,45.48,z]})

# Exit openings are within their original 6 m north runout edges.
excluded=[]
for i,x in enumerate([64,77.5],1):
    n='AQD__AQD_slide_'+str(i)+'_runout_wall_3';assert n in bpy.data.objects,n
    o=bpy.data.objects[n];o['group6_exchange_excluded']='exit opening replaces original continuous north wall';o.hide_render=True;excluded.append(n)
    # The dry recovery seats retain their original positions. Shift the exit
    # flight west 1 m so the parked seats do not block the walkable path.
    for j in range(4):
        old='AQD__AQD_slide_'+str(i)+'_exit_tread_'+str(j);assert old in bpy.data.objects
        bpy.data.objects[old]['group6_exchange_excluded']='replaced by six-riser recovery flight clear of original seat'
        bpy.data.objects[old].hide_render=True;excluded.append(old)
    # A visibly continuous wet recovery surface supports ordinary controller motion.
    # Original steps remain preserved in the native and failed revisions remain intact.
    front=191.25;back=193.1;top=45.45;low=44.35
    vs=[(x-.7,44.3,front),(x+.7,44.3,front),(x+.7,44.3,back),(x-.7,44.3,back),(x-.7,top,front),(x+.7,top,front),(x+.7,low,back),(x-.7,low,back)]
    mesh('slide_'+str(i)+'_continuous_recovery_path',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'stone','basin_entry')
    for j in range(9):
        z=front+.18+j*.20;y=top-(top-low)*(z-front)/(back-front)
        mesh('slide_'+str(i)+'_recovery_grip_'+str(j),[(x+dx,top-(top-low)*(zz-front)/(back-front)+.002,zz) for dx,zz in [(-.625,z-.0325),(.625,z-.0325),(.625,z+.0325),(-.625,z+.0325)]],[(0,1,2,3)],'grip','finish_visual')
    for label,a,b in [('west',x-1,x-.9),('east',x+.9,x+5)]:
        box('slide_'+str(i)+'_exit_jamb_'+label,((a+b)/2,44.875,191.25),(b-a,1.15,.16))
    for side in [-1,1]:
        rod('slide_'+str(i)+'_exit_grab_'+str(side),(x+side*.85,46.25,190.6),(x+side*.85,45.8,192.6),.045)
        rod('slide_'+str(i)+'_exit_grab_bearing_'+str(side),(x+side*.85,44.3,192.6),(x+side*.85,45.8,192.6),.045)
    # Clear recovery path is west of each parked transfer seat, which is retained.
    lamp('slide_exit_'+str(i),x-1.5,47.85,190.4,51.7,6)

# Remove the original top landing's intrusion into the last 1.6 m of ascent.
# The new polygon retains the same height, fits inside the original octagon and
# provides a complete 2.4 m deep turn beyond the ramp end.
for old in ['AQD__launch_top_landing','AQD__island_bridge']:
    assert old in bpy.data.objects
    bpy.data.objects[old].hide_render=True;excluded.append(old)
    bpy.data.objects[old]['group6_exchange_excluded']='source successor creates flush ramp connection'
def slab_polygon(n,poly,top,thickness,kind):
    vs=[(x,top-thickness,z) for x,z in poly]+[(x,top,z) for x,z in poly];count=len(poly)
    # Concave top/bottom polygons are triangulated by the exchange exporter.
    fs=[tuple(range(count-1,-1,-1)),tuple(range(count,count*2))]
    fs += [(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    return mesh(n,vs,fs,'stone',kind)
slab_polygon('flush_launch_top_landing',[(93.7,244),(98.9,244),(96.6,246.4),(93.7,246.4)],49.35,.24,'ramp_asset')
for a,b in [((93.7,246.4),(96.6,246.4)),((96.6,246.4),(98.9,244))]:
    rod('top_landing_edge_guard_'+str(a),(a[0],50.45,a[1]),(b[0],50.45,b[1]),.035)
    for x,z in [a,b]:rod('top_landing_guard_post_'+str((x,z)),(x,49.35,z),(x,50.45,z),.035)
slab_polygon('flush_island_bridge',[(59.1,200.7),(74.8,200.7),(74.8,202),(72,202),(72,203.3),(61.9,203.3),(61.9,202),(59.1,202)],47.7,.24,'bridge_asset')

# The retained rear rail closes the T junction across the east gallery.
for old in ['AQD__launch_rear_guard_top_0','AQD__launch_rear_guard_low_0','AQD__launch_rear_guard_end']:
    assert old in bpy.data.objects
    bpy.data.objects[old].hide_render=True;excluded.append(old)
    bpy.data.objects[old]['group6_exchange_excluded']='shortened rail leaves original east-gallery T junction open'
for tag,y,r in [('top',50.45,.035),('low',49.85,.025)]:rod('launch_rear_guard_clear_'+tag,(63,y,197.5),(96.9,y,197.5),r)
rod('launch_rear_guard_clear_end',(96.9,49.35,197.5),(96.9,50.45,197.5),.04)

for old in ['AQD__upper_east_guard_west_top_0','AQD__upper_east_guard_west_low_0','AQD__upper_east_guard_west_post_0']:
    assert old in bpy.data.objects
    bpy.data.objects[old].hide_render=True;excluded.append(old)
    bpy.data.objects[old]['group6_exchange_excluded']='guard starts at actual north-gallery rear edge, preserving open T junction'
for tag,y,r in [('top',50.45,.035),('low',49.85,.025)]:rod('upper_east_guard_west_clear_'+tag,(96.9,y,197.5),(96.9,y,242.2),r)
# New rear-guard end and retained south end provide the two corner bearings.

# Join the original intersecting gallery slabs into one exact exposed surface.
# Internal/coplanar side faces at their overlap blocked reverse traversal.
for old in ['AQD__launch_east_gallery','AQD__launch_north_gallery']:
    assert old in bpy.data.objects
    bpy.data.objects[old].hide_render=True;excluded.append(old)
    bpy.data.objects[old]['group6_exchange_excluded']='unified solid gallery surface removes internal overlap and closes top-landing seam'
slab_polygon('continuous_launch_gallery',[(63,194.9),(98.2,194.9),(98.2,195),(99.5,195),(99.5,244),(96.9,244),(96.9,197.5),(63,197.5)],49.35,.24,'ramp_asset')
rod('top_landing_east_guard_extension',(99.5,50.45,243.6),(99.5,50.45,244),.035)
rod('top_landing_east_guard_corner',(99.5,50.45,244),(98.9,50.45,244),.035)
rod('top_landing_east_guard_corner_post',(99.5,49.35,244),(99.5,50.45,244),.04)

# High privacy transoms, fixed handle targets and deep reveals use original rooms.
DOORS=[]
for i,z in enumerate([231,233.6]):
    leaf='AQD__assisted_rinse_'+str(i)+'_privacy_leaf';assert leaf in bpy.data.objects
    original_leaf=bpy.data.objects[leaf];original_leaf.hide_render=True;excluded.append(leaf)
    original_leaf['group6_exchange_excluded']='paired source-derived leaves retain closed outline and permit inside privacy'
    leaves=[]
    for side in [-1,1]:
        q=original_leaf.copy();q.data=original_leaf.data.copy();S.collection.objects.link(q);q.hide_render=False;q.hide_viewport=False
        q.name='AQ6__rinse_'+str(i)+'_leaf_'+('north' if side<0 else 'south');q['kind']='privacy_door_proposal';q['source_derivative']=leaf
        bm=bmesh.new();bm.from_mesh(q.data)
        cut=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=q.matrix_world.inverted()@xyz((60.1,46.62,z)),plane_no=Vector((0,1,0)),clear_inner=side<0,clear_outer=side>0)
        bmesh.ops.holes_fill(bm,edges=[e for e in cut['geom_cut'] if isinstance(e,bmesh.types.BMEdge) and e.is_boundary],sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(q.data);bm.free();NEW.append(q)
        leaves.append({'mesh':'G6_'+q.name,'pivot':[60.1,45.45,z+side*1.1],'contact_center':[0,1.17,-side*.55],'open_radians':-side*math.pi/2})
    box('rinse_'+str(i)+'_opaque_transom',(60.1,48.07,z),(.18,.56,2.2),'ivory')
    for side in [-1,1]:
        box('rinse_'+str(i)+'_portal_cheek_'+str(side),(60.1,46.95,z+side*1.25),(.12,3,.12),'wood')
        box('rinse_'+str(i)+'_fixed_control_'+str(side),(60.46 if side>0 else 59.76,46.65,z+.85),(.09,.22,.18),'metal','door_control')
    box('rinse_'+str(i)+'_towel_hook',(57.25,47.1,z-.55),(.22,.12,.16),'metal')
    box('rinse_'+str(i)+'_soap_tray',(57.32,46.35,z+.65),(.28,.08,.34),'ivory')
    lamp('rinse_task_'+str(i),58.65,48.18,z,48.35,4)
    DOORS.append({'id':'aquatic_assisted_rinse_'+str(i)+'_privacy_001','leaves':leaves,'center_z':z,'control_names':['G6_AQ6__rinse_'+str(i)+'_fixed_control_'+str(s) for s in [-1,1]]})

# Flush wet/dry transitions and real recovery provisions, no extra floor or capacity.
for j,x in enumerate([59,60,61]):
    box('arrival_grip_'+str(j),(x,44.004,240),(.95,.008,2.2),'grip','finish_visual',0)
for n,x,z in [('arrival',59,240),('south_boarding',78,239.4),('north_boarding',75,193.25)]:
    box(n+'_drain',(x,45.454 if n!='arrival' else 44.004,z),(1.65,.008,.16),'grip','finish_visual',0)
    for k in range(8):box(n+'_drain_slot_'+str(k),(x-.7+k*.2,45.461 if n!='arrival' else 44.011,z),(.035,.008,.13),'metal','finish_visual',0)
for i,(x,z) in enumerate([(94,238),(63,210),(93,200)]):
    rod('recovery_'+str(i)+'_standard',(x,45.45,z),(x,47.2,z),.045)
    box('recovery_'+str(i)+'_cradle',(x,46.95,z),(.62,.08,.38),'metal')
    rod('recovery_'+str(i)+'_reach_pole',(x-.12,46.99,z),(x+.12,49.0,z),.025,'wood')
    box('recovery_'+str(i)+'_closed_aid_case',(x,46.1,z),(.65,.55,.3),'ivory')

# Three distinct social pockets: curved river overlook, paired rest, task/refreshment.
for i,(c,rx,rz,a0,a1,role) in enumerate([((64.15,218),1,2.1,math.pi/2,3*math.pi/2,'teal'),((69.5,242.5),3.2,1.35,math.pi,2*math.pi,'clay'),((97.7,200),1.1,2.1,math.pi/2,3*math.pi/2,'oat')]):
    band('rest_'+str(i)+'_plinth',c,rx,rz,a0,a1,.7,45.45,45.83,'wood')
    band('rest_'+str(i)+'_seat',c,rx,rz,a0,a1,.8,45.83,46.03,role)
    band('rest_'+str(i)+'_back',c,rx+.3,rz+.3,a0,a1,.15,46.0,46.8,role)
    tx=c[0]-.35;tz=c[1]
    box('rest_'+str(i)+'_table_base',(tx,45.73,tz),(.55,.55,.65),'wood',bevel=.08)
    box('rest_'+str(i)+'_table',(tx,46.12,tz),(1.3,.18,1.35),'stone',bevel=.09)
    lamp('rest_'+str(i)+'_pendant',tx,48.4,tz,49.11 if i==2 else 51.7,8)

# Sheltered dry changing/towel threshold within the retained lower arrival apron.
box('arrival_dry_canopy',(58.5,47.0,242.7),(3.5,.22,1.25),'ivory')
for x in [57.15,59.85]:rod('arrival_canopy_bearing_'+str(x),(x,44,242.7),(x,46.89,242.7),.08,'wood')
box('arrival_dry_perch',(58.5,44.52,242.7),(2.3,.16,.68),'teal')
for x in [57.6,59.4]:box('arrival_perch_bearing_'+str(x),(x,44.22,242.7),(.18,.44,.55),'wood')
lamp('arrival_dry_light',58.5,46.72,242.7,46.89,5)
# Additive labelled clean and closed used bins; existing storage remains untouched.
for n,z,role in [('clean_linen',218,'oat'),('used_linen',221.2,'clay')]:
    box(n+'_cabinet',(98.6,46.18,z),(1.15,1.46,1.15),'ivory')
    box(n+'_front',(97.98,46.18,z),(.07,1.22,.93),role)
    box(n+'_handle',(97.90,46.45,z),(.11,.09,.38),'metal')
    box(n+'_cap',(98.6,46.96,z),(1.25,.1,1.25),'wood')

# Thermal entry courts use the two original basins; no new parent or water target.
THERMAL=[]
for i,cz in [(5,211.5),(6,223.5)]:
    prefix='AQD__AQD_spa_'+str(i)
    for j in range(21,27):
        old=prefix+'_wall_'+str(j);assert old in bpy.data.objects
        bpy.data.objects[old].hide_render=True;excluded.append(old)
        bpy.data.objects[old]['group6_exchange_excluded']='west entry opening retains basin identity and original water boundary'
    for j in range(4):
        old=prefix+'_wet_tread_'+str(j);assert old in bpy.data.objects
        bpy.data.objects[old].hide_render=True;excluded.append(old)
        bpy.data.objects[old]['group6_exchange_excluded']='continuous visible entry surface replaces overlapping original tread boxes'
    old=prefix+'_adaptive_handhold_-1';assert old in bpy.data.objects
    bpy.data.objects[old].hide_render=True;excluded.append(old)
    bpy.data.objects[old]['group6_exchange_excluded']='side handholds keep the actual entry clear'
    # 1.6 m wide, real sloped slab inside the retained basin. The bank is flush.
    a=78.90;b=81.10;top=45.45;low=44.40
    # The bank join follows the exact retained island-floor hole, not a straight
    # slab crossing its curved boundary and creating another raised lip.
    plan_path=R/'Game/data/architecture/AQUATIC_ANNEX_PLAN.json'
    assert hashlib.sha256(plan_path.read_bytes()).hexdigest()=='7609dc6ef9f2e564713ba8bcc5a5030a305eba12e7a8401ad16be3fd7283e836'
    island=next(q for q in json.loads(plan_path.read_text())['floor_records'] if q['id']=='AQD_island_terrace')
    holes=[h for poly in island['boundary_polygons_xz'] for h in poly['holes']]
    hole=min(holes,key=lambda h:abs(sum(q[1] for q in h)/len(h)-cz))
    def bank_at(z):
        hits=[]
        for p0,p1 in zip(hole,hole[1:]+hole[:1]):
            if abs(p1[1]-p0[1])<1e-8:continue
            if min(p0[1],p1[1])-1e-7<=z<=max(p0[1],p1[1])+1e-7:
                t=(z-p0[1])/(p1[1]-p0[1]);hits.append(p0[0]+t*(p1[0]-p0[0]))
        assert hits
        return min(hits)
    rows=[cz-.8+j*.2 for j in range(9)];vs=[]
    for z in rows:
        ax=bank_at(z);vs.extend([(ax,44.4,z),(b,44.4,z),(ax,top,z),(b,low,z)])
    fs=[]
    for j in range(8):
        q=j*4;r=q+4;fs += [(q,r,r+1,q+1),(q+2,q+3,r+3,r+2),(q,q+2,r+2,r),(q+1,r+1,r+3,q+3)]
    fs += [(0,1,3,2),(32,34,35,33)]
    mesh('spa_'+str(i)+'_continuous_entry_surface',vs,fs,'stone','basin_entry')
    for j in range(10):
        vs=[]
        for z in [cz-.725+k*.18125 for k in range(9)]:
            ax=bank_at(z)
            for t in [(j+.32)/10,(j+.68)/10]:vs.append((ax+t*(b-ax),top-(top-low)*t+.002,z))
        mesh('spa_'+str(i)+'_entry_grip_'+str(j),vs,[(k*2,k*2+1,k*2+3,k*2+2) for k in range(8)],'grip','finish_visual')
    for side in [-1,1]:
        rod('spa_'+str(i)+'_entry_rail_'+str(side),(78.85,46.55,cz+side*.87),(80.95,45.55,cz+side*.87),.035)
        for x,y in [(78.85,45.45),(80.95,44.4)]:rod('spa_'+str(i)+'_rail_bearing_'+str((side,x)),(x,y,cz+side*.87),(x,y+1.1,cz+side*.87),.035)
    # Two distinguishable quiet courts, suspended canopies without route columns.
    role='teal' if i==5 else 'clay'
    band('spa_'+str(i)+'_quiet_canopy',(81.5,cz),3.0,2.9,-math.pi/3,math.pi*5/3,.38,48.72,48.9,'ivory')
    for angle in [math.pi/2,math.pi,3*math.pi/2]:
        x=81.5+3*math.cos(angle);z=cz+2.9*math.sin(angle)
        rod('spa_'+str(i)+'_canopy_hanger_'+str(angle),(x,51.7,z),(x,48.9,z),.028)
    band('spa_'+str(i)+'_quiet_backdrop',(81.5,cz),2.92,2.92,-math.pi/3,math.pi/3,.10,45.70,48.35,role)
    for angle in [-math.pi/3,0,math.pi/3]:
        x=81.5+2.92*math.cos(angle);z=cz+2.92*math.sin(angle)
        rod('spa_'+str(i)+'_backdrop_hanger_'+str(angle),(x,48.35,z),(x,48.72,z),.028)
    # Physical dry support edge north-west of entry, clear of transfer equipment.
    box('spa_'+str(i)+'_support_base',(76.2,45.79,cz-2.7),(.7,.68,.65),'wood')
    box('spa_'+str(i)+'_support_counter',(76.2,46.15,cz-2.7),(.85,.12,.8),'stone')
    box('spa_'+str(i)+'_closed_linen',(76.2,46.45,cz-2.7),(.64,.48,.55),role,'stock_asset')
    box('spa_'+str(i)+'_support_handle',(75.835,46.48,cz-2.7),(.07,.09,.30),'metal')
    rod('spa_'+str(i)+'_support_task_bearing',(76.2,51.7,cz-2.7),(76.2,48.3,cz-2.7),.025)
    box('spa_'+str(i)+'_support_task_hood',(76.2,48.15,cz-2.7),(.45,.18,.45),'metal','fixture_mount')
    box('spa_'+str(i)+'_support_task_lens',(76.2,48.04,cz-2.7),(.34,.04,.34),'lens','fixture_lens')
    LIGHTS.append({'id':'spa_'+str(i)+'_support_task','xyz':[76.2,47.98,cz-2.7],'range_m':5,'energy':1.2,'receiver_xyz':[76.2,45.48,cz-2.7]})
    THERMAL.append({'source_id':'AQD_spa_'+str(i),'center_xz':[81.5,cz],'west_opening_wall_segments':list(range(21,27)),'entry_surface_x':[a,b],'clear_width_m':1.6,'floor_top_range':[top,low],'dry_turn_center_xyz':[77.0,45.45,cz-1.5],'dry_turn_proposal_diameter_m':1.5,'support_approach_xyz':[75.2,45.45,cz-2.7],'original_seat_hoist_and_east_adaptive_handhold_preserved':True,'gravity_and_water_control_operation_implemented':False,'wheelchair_broad_species_or_loaded_cart_accepted':False})

# Real handset, grab bars and hardware complete the two retained rinse interiors.
for i,z in enumerate([231,233.6]):
    rod('rinse_'+str(i)+'_vertical_grab',(57.30,46.25,z-.7),(57.30,47.25,z-.7),.033)
    for y in [46.25,47.25]:rod('rinse_'+str(i)+'_grab_standoff_'+str(y),(57.18,y,z-.7),(57.30,y,z-.7),.035)
    box('rinse_'+str(i)+'_handset_mount',(57.23,47.28,z+.6),(.08,.20,.20),'metal')
    rod('rinse_'+str(i)+'_handset_stem',(57.35,47.20,z+.6),(57.65,47.55,z+.6),.035)
    box('rinse_'+str(i)+'_handset_head',(57.68,47.56,z+.6),(.24,.11,.32),'ivory')
    for j in range(7):
        a=j/7;b=(j+1)/7
        p0=(57.35+.25*math.sin(a*math.pi),47.20-1.05*a,z+.6)
        p1=(57.35+.25*math.sin(b*math.pi),47.20-1.05*b,z+.6)
        rod('rinse_'+str(i)+'_hose_segment_'+str(j),p0,p1,.018)
    box('rinse_'+str(i)+'_water_control_hardware',(57.23,46.2,z+.6),(.12,.32,.32),'metal')
    box('rinse_'+str(i)+'_low_control_paddle',(57.36,46.2,z+.6),(.14,.08,.2),'ivory')

# Internal water-care cell: under the retained gallery, between unchanged
# refreshments and wet-service stock. The X100 onward interface remains shared.
PLANT_GATE={'id':'aquatic_water_care_gate_001','xyz':[94.8,45.45,210.6],'yaw_radians':-math.pi/2,'source_asset':'AST-STF-008.glb','source_sha256':'d3ab5143760df1d68958cf063cc1b57ff3e4988cbea8d0a632757a5102a1da97','mechanical_gate_only':True,'permissions_and_persistence_implemented':False}
VALVES=[]
# Enclosure is deliberately technical: inspection aisle and visible working edge.
for tag,z in [('north',208.6),('south',212.6)]:
    box('water_care_'+tag+'_wall',(97.3,47.02,z),(5.0,3.14,.16),'ivory')
for tag,a,b in [('north',208.6,209.18),('south',212.02,212.6)]:
    box('water_care_front_'+tag,(94.8,47.02,(a+b)/2),(.16,3.14,b-a),'wood')
for z in [209.2,212.0]:rod('water_care_gate_reveal_'+str(z),(94.8,45.45,z),(94.8,48.59,z),.042,'wood')
box('water_care_gate_header',(94.8,48.34,210.6),(.2,.14,2.9),'wood')
box('water_care_ceiling',(97.285,48.50,210.6),(4.97,.18,4.0),'ivory')
# Slotted floor finish is flush with the original owner; it adds no floor collider.
for j in range(12):box('water_care_drain_'+str(j),(96.8,45.454,209.0+j*.25),(1.7,.008,.05),'grip','finish_visual',0)
# Two vessels, two separate headers, formed elbows, saddles and readable gauges.
def vessel(n,x,z):
    box(n+'_skid',(x,45.575,z),(1.05,.25,1.15),'metal')
    vs=[];fs=[];rings=[(45.70,.36),(45.85,.48),(47.18,.48),(47.42,.32),(47.51,.13)]
    for y,r in rings:
        for k in range(16):
            a=k*math.tau/16;vs.append((x+r*math.cos(a),y,z+r*math.sin(a)))
    for j in range(4):
        for k in range(16):fs.append((j*16+k,j*16+(k+1)%16,(j+1)*16+(k+1)%16,(j+1)*16+k))
    fs += [tuple(range(15,-1,-1)),tuple(range(64,80))]
    mesh(n+'_housing',vs,fs,'ivory')
    for y in [46.0,47.05]:
        band(n+'_collar_'+str(y),(x,z),.49,.49,0,math.tau,.045,y-.025,y+.025,'metal')
    box(n+'_drain_port',(x-.56,45.92,z),(.18,.16,.16),'metal')
    rod(n+'_gauge_stem',(x-.49,47.0,z),(x-.70,47.0,z),.035)
    # West-facing gauge body is a real cylinder and pointer, no fluid reading claim.
    rod(n+'_gauge',(x-.70,47.0,z),(x-.77,47.0,z),.13,'ivory')
    rod(n+'_gauge_pointer',(x-.779,47.0,z),(x-.779,47.08,z+.05),.013,'metal')
for i,z in enumerate([209.4,211.7]):vessel('water_care_filter_'+str(i),98.6,z)
for n,z in [('supply',208.87),('return',212.32)]:
    rod('water_care_'+n+'_header',(95.3,47.90,z),(99.65,47.90,z),.065)
    for x in [95.5,97.2,99.3]:
        rod('water_care_'+n+'_wall_bearing_'+str(x),(x,47.90,z),(x,47.90,208.68 if n=='supply' else 212.52),.035)
for i,z in enumerate([209.4,211.7]):
    # Pipe joints avoid a fictional continuous network beyond the annex.
    rod('water_care_filter_'+str(i)+'_riser',(98.6,47.51,z),(98.6,47.90,z),.06)
    rod('water_care_filter_'+str(i)+'_elbow',(98.6,47.90,z),(98.6,47.90,208.87 if i==0 else 212.32),.06)
    rod('water_care_filter_'+str(i)+'_valve_branch',(98.10,46.65,z),(97.65,46.65,z),.06)
    center=(97.62,46.65,z);radius=.19;vs=[];fs=[]
    for x in [center[0]-.028,center[0]+.028]:
        for k in range(16):
            a=k*math.tau/16
            for r in [radius-.028,radius+.028]:vs.append((x,center[1]+r*math.cos(a),center[2]+r*math.sin(a)))
    for k in range(16):
        a=k*2;b=((k+1)%16)*2;fs += [(a,b,b+1,a+1),(a+32,a+33,b+33,b+32),(a,a+32,b+32,b),(a+1,b+1,b+33,a+33)]
    # An asymmetric spoke/pointer makes the bounded mechanical turn visible.
    a=len(vs);vs += [(center[0]-.03,center[1]-.13,center[2]-.022),(center[0]-.03,center[1]+.13,center[2]-.022),(center[0]-.03,center[1]+.13,center[2]+.022),(center[0]-.03,center[1]-.13,center[2]+.022)];fs.append((a,a+1,a+2,a+3))
    mesh('water_care_valve_'+str(i)+'_handwheel_source',vs,fs,'metal','valve_wheel')
    rod('water_care_valve_'+str(i)+'_hub',(97.57,46.65,z),(97.68,46.65,z),.055)
    VALVES.append({'id':'aquatic_water_care_isolator_'+str(i)+'_001','mesh':'G6_AQ6__water_care_valve_'+str(i)+'_handwheel_source','pivot_xyz':list(center),'axis':'x','travel_radians':math.pi/2,'circuit':'supply' if i==0 else 'return','mechanical_only':True,'water_flow_pressure_or_temperature_implemented':False})
# Local tool/closed-ordinary-return edge stays distinct from retained clean stock.
box('water_care_tool_back',(95.48,46.75,212.45),(.85,1.8,.12),'wood')
for j in range(3):
    rod('water_care_tool_hook_'+str(j),(95.25+j*.23,46.75,212.31),(95.25+j*.23,46.9,212.31),.02)
    rod('water_care_tool_handle_'+str(j),(95.25+j*.23,46.1,212.30),(95.25+j*.23,46.72,212.30),.025)
box('water_care_closed_return',(95.8,45.84,212.06),(.65,.78,.60),'clay','stock_asset')
for i,z in enumerate([209.35,211.35]):lamp('water_care_task_'+str(i),96.8,48.05,z,48.41,5)
# Source-only native reference uses the exact registered door. Runtime reuses the
# same asset/state machine rather than exporting a second static door copy.
asset=R/'Game/assets/models/AST-STF-008.glb';assert hashlib.sha256(asset.read_bytes()).hexdigest()==PLANT_GATE['source_sha256']
before_import=set(S.objects);bpy.ops.import_scene.gltf(filepath=str(asset));imported=set(S.objects)-before_import
transform=Matrix.Translation(xyz(PLANT_GATE['xyz']))@Matrix.Rotation(PLANT_GATE['yaw_radians'],4,'Z')
for o in imported:
    if o.parent not in imported:o.matrix_world=transform@o.matrix_world
bpy.context.view_layer.update()
reference={}
for i,o in enumerate(sorted([o for o in imported if o.type=='MESH'],key=lambda o:o.name)):
    o.name='AQ6__water_care_gate_reference_'+str(i);o['kind']='runtime_service_gate_reference';o['source_asset']='AST-STF-008.glb';NEW.append(o);reference[o.name]=digest(o)
# Both future circuit flanges terminate inside the original 2.4m portal.
for circuit,z0,z1 in [('supply',208.87,209.10),('return',212.32,210.90)]:
    rod('water_care_'+circuit+'_portal_elbow',(99.45,47.90,z0),(99.45,47.90,z1),.065)
    rod('water_care_'+circuit+'_portal_terminal',(99.45,47.90,z1),(99.65,47.90,z1),.065)
    rod('water_care_'+circuit+'_terminal_flange',(99.60,47.90,z1),(99.67,47.90,z1),.10)
WATER_CARE={'id':'aquatic_water_care_cell_001','bounds_xz':[94.8,99.77,208.6,212.6],'floor_y':45.45,'clear_ceiling_y':48.41,'gate':PLANT_GATE,'valves':VALVES,'native_registered_gate_reference_mesh_hashes':reference,'pipe_interfaces':[{'circuit':'supply','terminal_xyz':[99.67,47.90,209.10],'radius_m':.10},{'circuit':'return','terminal_xyz':[99.67,47.90,210.90],'radius_m':.10}],'onward_service_portal_xyz':[100,45.45,210],'onward_route_or_fluid_network_implemented':False,'restaurant_cascade_connection_owned_here':False}

# Discreet pool/spa handrail lighting below the original crossing soffit.
for i,(x,z) in enumerate([(82.6,211.5),(82.6,223.5),(78,239),(63.5,216),(86,217)]):lamp('wet_edge_'+str(i),x,48.45,z,51.7,7)

bpy.context.view_layer.update()
assert all(digest(bpy.data.objects[n])==d for n,d in before.items()),'Original object geometry or transform changed'
assert all(hashlib.sha256(bpy.data.images[n].packed_file.data).hexdigest()==h for n,h in packed.items())
audit={'status':'PASS','original_native_sha256':hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),'original_meshes_preserved':len(before),'original_mesh_semantics_sha256':hashlib.sha256(json.dumps(before,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'packed_images_preserved':packed,'original_mesh_hashes':before,'exchange_exclusions':excluded,'added_meshes':len(NEW),'added_light_fittings':len(LIGHTS),'native_engine':'Blender '+bpy.app.version_string,'geometry_transform_uv_material_modifiers_preserved':True}
(P/'NATIVE_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
(P/'FIT_CONTRACT.json').write_text(json.dumps({'schema':1,'status':'inactive Group6 handoff','programme_key':'D08_directory_08','doors':DOORS,'additional_lights':LIGHTS,'exclusions':excluded,'original_source':str(ORIGINAL.relative_to(R)),'new_floor_area_m2':0,'new_capacity':0,'thermal_entry_courts':THERMAL,'water_care_cell':WATER_CARE},indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'AquaticCompletion_r015.blend'))

# Exchange has explicit roles; originals and new meshes share unchanged materials.
dg=bpy.context.evaluated_depsgraph_get();exchange=bpy.data.scenes.new('Group6Exchange');bpy.context.window.scene=exchange;groups={};policy={};parts={}
for o in list(S.objects):
    if o.type!='MESH' or not o.name.startswith(('AQD__','AQ6__')) or o.name in excluded or o.get('kind') in ['compiler_floor_proposal','runtime_service_gate_reference']:continue
    kind=o.get('kind','architecture');material=o.data.materials[0].name if o.data.materials else 'none'
    key='G6_'+o.name if kind in ['water_visual','tube_static_visual','privacy_door_proposal','door_control','valve_wheel'] else 'AQ6_BATCH_'+str(kind)+'_'+material
    me=bpy.data.meshes.new_from_object(o.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg);q=bpy.data.objects.new('EX_'+o.name,me);q.matrix_world=o.matrix_world.copy();exchange.collection.objects.link(q);groups.setdefault(key,[]).append((q,o.name,kind))
for key,obs in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for q,n,k in obs:q.select_set(True)
    bpy.context.view_layer.objects.active=obs[0][0];names=[n for q,n,k in obs]
    if len(obs)>1:bpy.ops.object.join()
    q=bpy.context.view_layer.objects.active;q.name=key
    role='privacy_leaf' if 'privacy_leaf' in key else obs[0][2]
    q['kind']=role;parts[key]=names;policy[key]=role
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(P/'AquaticCompletion_r015.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_apply=True,export_extras=True,export_lights=False,export_cameras=False)
(P/'EXCHANGE_PARTS.json').write_text(json.dumps(parts,indent=2)+'\n');(P/'COLLISION_POLICY.json').write_text(json.dumps(policy,indent=2)+'\n')
print('GROUP6 SOURCE PASS',audit['original_meshes_preserved'],audit['added_meshes'],len(policy))
