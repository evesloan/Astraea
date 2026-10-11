"""New Orchard work-bay and receiving fittings; immutable retained sources untouched."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,sys
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];C=R/'BlenderCatalogue'
AID='AST-G8-DIN-001';FAMILY='group8_orchard_service_20261011';ROOM='D10_directory_04';F=61.0
assert all(a['catalogue_id']!=AID or a['family']==FAMILY for a in json.load(open(C/'catalogue_manifest.json'))['assets'])
native=W/'OrchardService_r003.blend';out=W/'G8_ORCHARD_SERVICE_r003_unbatched.glb'
assert not native.exists()and not out.exists(),'Immutable revision already exists'
bpy.ops.wm.read_factory_settings(use_empty=True);sys.path.insert(0,str(C/'standards'))
import staff_materials,materials
mats=staff_materials.materials();mats.update(materials.materials())
for m in mats.values():
    for node in m.node_tree.nodes:
        if node.type=='TEX_IMAGE':node.interpolation='Closest'
mat=bpy.data.materials.new('G8_ORCH_OpalLens');mat.use_nodes=True;mat.diffuse_color=(.75,.9,.9,1)
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Emission Color'].default_value=mat.diffuse_color;bs.inputs['Emission Strength'].default_value=.35;bs.inputs['Roughness'].default_value=.65
mat['meters_per_tile_uv']=[1,1];mats['light_lens']=mat
records=[];instances=[];lights=[];supports=[];contacts=[];source_copies=[];UNIT=''
FACES=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def mesh(name,verts,faces,role='staff_white_paint',category='fitting',permitted_context=None):
    name='G8O_'+UNIT+'_'+name;me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y)for x,y,z in verts],[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(mats[role]);uv=me.uv_layers.new(name='MetreScaled');scale=mats[role].get('meters_per_tile_uv',[1,1])
    for face in me.polygons:
        n=face.normal.normalized();u=Vector((1,0,0))-n*n.x if abs(n.z)>.7 else Vector((-n.y,n.x,0));u.normalize();v=n.cross(u)
        for li in face.loop_indices:
            q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
    ob['programme_key']=ROOM;ob['unit']=UNIT;ob['category']=category
    records.append({'name':name,'programme_key':ROOM,'unit':UNIT,'role':role,'category':category,'collide':category!='light_source','permitted_retained_context':permitted_context or [],'world_aabb':[min(v[0]for v in verts),max(v[0]for v in verts),min(v[1]for v in verts),max(v[1]for v in verts),min(v[2]for v in verts),max(v[2]for v in verts)]});return ob
def box(name,x,y,z,sx,sy,sz,role='staff_white_paint',category='fitting',permitted=None):
    return mesh(name,[(x+a,y+c,z+b)for c in [-sy/2,sy/2]for a,b in [(-sx/2,-sz/2),(sx/2,-sz/2),(sx/2,sz/2),(-sx/2,sz/2)]],FACES,role,category,permitted)
def round_slab(name,x,y,z,w,d,h,r,role='staff_zinc'):
    pts=[]
    for cx,cz,angle in [(x+w/2-r,z+d/2-r,0),(x-w/2+r,z+d/2-r,90),(x-w/2+r,z-d/2+r,180),(x+w/2-r,z-d/2+r,270)]:
        for j in range(4):
            a=math.radians(angle+j*30);pts.append((cx+r*math.cos(a),cz+r*math.sin(a)))
    n=len(pts);vs=[(px,y+dy,pz)for dy in [-h/2,h/2]for px,pz in pts]
    return mesh(name,vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)],role)
def pipe(name,a,b,r=.025,role='staff_zinc',sides=10):
    a=Vector(a);b=Vector(b);axis=(b-a).normalized();u=axis.cross(Vector((0,1,0))if abs(axis.y)<.9 else Vector((1,0,0))).normalized();v=axis.cross(u)
    vs=[tuple(p+r*(math.cos(math.tau*i/sides)*u+math.sin(math.tau*i/sides)*v))for p in [a,b]for i in range(sides)]
    return mesh(name,vs,[tuple(reversed(range(sides))),tuple(range(sides,2*sides))]+[(i,(i+1)%sides,(i+1)%sides+sides,i+sides)for i in range(sides)],role)
def foot(name,x,z,top=F+.15,w=.10,d=.10,lo=F):
    box(name,x,(lo+top)/2,z,w,top-lo,d,'dark_rubber');supports.append({'unit':UNIT,'kind':'floor','at':[x,lo,z],'expected_retained':'ORCH_StaffFloorFinish_'if lo>F else'CompiledStructuralFloors_NotFinishedRooms'})
def store(name,x,z,w=.95,d=2.3,mode='cold'):
    global UNIT;UNIT=name;instances.append({'name':name,'type':mode+'_store','at':[x,F,z]})
    for a in [-w/2+.10,w/2-.10]:
        for b in [-d/2+.13,d/2-.13]:foot('Foot_%s_%s'%(a,b),x+a,z+b)
    round_slab('Toe',x,F+.17,z,w,d,.10,.06,'dark_rubber')
    for a in [-1,1]:box('Side'+str(a),x+a*(w/2-.04),F+1.20,z,.08,2.08,d,'staff_white_paint')
    box('Back',x-w/2+.05,F+1.20,z,.10,2.08,d,'staff_bluegrey_paint')
    for h in [.24,.78,1.33,1.87,2.27]:box('Shelf'+str(h),x,F+h,z,w,.07,d,'staff_zinc')
    if mode=='cold':
        for k in [-1,1]:
            zz=z+k*d/4;box('ClosedDoor'+str(k),x+w/2+.01,F+1.22,zz,.055,1.98,d/2-.055,'staff_white_paint')
            box('DoorReveal'+str(k),x+w/2+.042,F+1.22,zz,.02,1.72,d/2-.20,'staff_bluegrey_paint')
            pipe('Handle'+str(k),(x+w/2+.09,F+.98,zz),(x+w/2+.09,F+1.42,zz),.018)
    else:
        for h in [.48,1.03,1.58,2.07]:
            for k in [-1,0,1]:
                zz=z+k*d/3;round_slab('SealedBin_%s_%s'%(h,k),x,F+h,zz,w-.18,d/3-.13,.34,.04,'staff_bluegrey_paint');box('BinID_%s_%s'%(h,k),x+w/2-.07,F+h,zz,.014,.10,.16,'staff_white_paint')
def hood(name,x,z,w,canopy_y=64.8):
    global UNIT;previous=UNIT;UNIT=name;instances.append({'name':name,'type':'profiled_task_hood','at':[x,64.1,z]})
    # Sloped extraction-shaped cover; no ventilation or food-safety claim.
    vs=[(x+a,y,z+b)for y,ww,dd in [(64.08,w,1.03),(64.42,w-.28,.72)]for a,b in [(-ww/2,-dd/2),(ww/2,-dd/2),(ww/2,dd/2),(-ww/2,dd/2)]]
    mesh('Shroud',vs,FACES,'staff_bluegrey_paint')
    for a in [-w/2+.22,w/2-.22]:
        box('CanopyTie'+str(a),x+a,(64.41+canopy_y+.005)/2,z,.06,canopy_y+.005-64.41,.06,'staff_zinc','support',['ORCH_ServeryCanopy_'])
        contacts.append({'unit':UNIT,'at':[x+a,canopy_y+.002,z],'expected_prefix':'ORCH_ServeryCanopy_','kind':'hood_to_original_canopy'})
    for j in [-1,1]:
        xx=x+j*w/4;box('Case'+str(j),xx,64.072,z,.9,.07,.22,'staff_zinc');box('Lens'+str(j),xx,64.026,z,.8,.018,.15,'light_lens','light_source')
        marker='G8O_LIGHT_'+name+'_'+str(j);ob=bpy.data.objects.new(marker,None);bpy.context.collection.objects.link(ob);ob.location=(xx,-z,64.012)
        lights.append({'name':marker,'programme_key':ROOM,'at':[xx,64.012,z],'range':4.8,'energy':.8,'colour':[.82,.92,1]})
    UNIT=previous
def range_line(name,x,z,kind='hot'):
    global UNIT;UNIT=name;instances.append({'name':name,'type':kind+'_counter_finish','at':[x,61.921,z]})
    # Four source-derived contacts sit on the original stone counter.
    for a in [-2.5,2.5]:
        for b in [-.26,.26]:
            box('Pad_%s_%s'%(a,b),x+a,61.946,z+b,.14,.05,.12,'dark_rubber');supports.append({'unit':UNIT,'kind':'counter','at':[x+a,61.921,z+b],'expected_retained':'ORCH_CounterTop_'})
    round_slab('WeightedDeck',x,62.02,z,5.7,.78,.13,.08,'staff_zinc')
    for k in range(3):
        xx=x+(k-1)*1.75;round_slab('InsetTray'+str(k),xx,62.10,z,1.53,.62,.035,.05,'dark_rubber')
        if kind=='hot':
            for q in [-1,1]:
                pipe('Hob'+str((k,q)),(xx+q*.32,62.112,z),(xx+q*.32,62.13,z),.20,'staff_zinc',16)
            box('ControlRail'+str(k),xx,62.13,z+.39,1.40,.17,.10,'staff_bluegrey_paint')
            for q in range(4):pipe('Dial'+str((k,q)),(xx+(q-1.5)*.25,62.13,z+.445),(xx+(q-1.5)*.25,62.13,z+.47),.04,'staff_opal')
        else:
            for q in [-1,0,1]:round_slab('LiddedWell'+str((k,q)),xx+q*.38,62.17,z,.33,.45,.11,.035,'staff_white_paint')
    hood(name+'_Hood',x,z,6.0)
def prep(name,x,z):
    global UNIT;UNIT=name;instances.append({'name':name,'type':'prep_and_handoff','at':[x,61.921,z]})
    for k in [-1,0,1]:
        xx=x+k*.96;round_slab('Board'+str(k),xx,61.954,z,.84,.66,.064,.06,'staff_white_paint')
        supports.append({'unit':UNIT,'kind':'counter','at':[xx,61.921,z],'expected_retained':'ORCH_CounterTop_'})
        for j in [-1,1]:box('BoardGrip'+str((k,j)),xx+j*.36,61.97,z,.025,.035,.28,'staff_bluegrey_paint')
    box('BackUpstand',x,62.25,z+.34,3.1,.56,.08,'staff_zinc')
    for h in [62.52,63.05]:box('ShallowShelf'+str(h),x,h,z+.25,3.1,.065,.28,'staff_zinc')
    for xx in [x-1.43,x+1.43]:pipe('RackLeg'+str(xx),(xx,61.94,z+.30),(xx,63.12,z+.30),.025)
    hood(name+'_TaskHood',x,z,3.3)
def wash(name,x,z):
    global UNIT;UNIT=name;instances.append({'name':name,'type':'wash_and_drain','at':[x,F,z]})
    for a in [-.36,.36]:
        for b in [-.96,.96]:foot('Foot'+str((a,b)),x+a,z+b,F+.18)
    box('RearPanel',x+.40,F+.57,z,.07,.75,2.25,'staff_white_paint')
    box('EndNorth',x,F+.57,z-1.08,.83,.75,.08,'staff_white_paint');box('EndSouth',x,F+.57,z+1.08,.83,.75,.08,'staff_white_paint')
    box('LowShelf',x,F+.26,z,.83,.065,2.20,'staff_zinc')
    # Basin consists of four walls and an actual recessed bottom; no solid fake cap.
    bottom=F+.83;top=F+1.06
    for xx in [x-.39,x+.39]:box('BasinSide'+str(xx),xx,(bottom+top)/2,z-.30,.06,top-bottom,1.20,'staff_zinc')
    for zz in [z-.90,z+.30]:box('BasinEnd'+str(zz),x,(bottom+top)/2,zz,.78,top-bottom,.06,'staff_zinc')
    box('BasinBottom',x,bottom,z-.30,.80,.04,1.22,'staff_zinc');round_slab('DrainBoard',x,F+1.04,z+.72,.86,.78,.055,.045,'staff_zinc')
    for k in range(6):box('DrainFlute'+str(k),x,F+1.079,z+.47+k*.085,.70,.012,.025,'staff_bluegrey_paint')
    pipe('TapRiser',(x+.30,F+1.02,z-.72),(x+.30,F+1.49,z-.72),.025);pipe('TapArc',(x+.30,F+1.49,z-.72),(x-.05,F+1.49,z-.72),.025);pipe('TapDrop',(x-.05,F+1.49,z-.72),(x-.05,F+1.36,z-.72),.025)
    pipe('WasteDrop',(x,F+.85,z-.3),(x,F+.33,z-.3),.035)
    for k in [-1,1]:round_slab('RemovableTub'+str(k),x,F+.40,z+k*.50,.60,.62,.23,.06,'staff_bluegrey_paint')
def receiving(name,x,z,mode):
    global UNIT;UNIT=name;instances.append({'name':name,'type':mode+'_receiving','at':[x,F,z]})
    for dz in [-1.15,1.15]:foot('Foot'+str(dz),x,z+dz,F+.18,.46,.16,F+.007)
    box('Rear',x+.26,F+1.28,z,.08,2.25,2.7,'staff_bluegrey_paint')
    for dz in [-1.30,1.30]:box('End'+str(dz),x,F+1.28,z+dz,.60,2.25,.08,'staff_white_paint')
    for h in [.25,.75,1.28,1.81,2.34]:box('Shelf'+str(h),x,F+h,z,.62,.065,2.7,'staff_zinc')
    for h in [.50,1.03,1.56,2.09]:
        for j in [-1,0,1]:
            zz=z+j*.82;round_slab('Container'+str((h,j)),x,F+h,zz,.48,.68,.38,.05,'staff_bluegrey_paint'if mode=='used'else'staff_white_paint');box('ContainerStripe'+str((h,j)),x-.25,F+h,zz,.018,.11,.55,'staff_white_paint'if mode=='used'else'staff_bluegrey_paint')
    # Staff fixtures project only0.62m from the retained outer wall, preserving2.6m lane.
def wall_task(name,x,z,top=64.6):
    global UNIT;UNIT=name;instances.append({'name':name,'type':'wall_supported_task_fixture','at':[x,top-.3,z]})
    box('WallBracket',53.89,top-.22,z,.06,.22,.28,'staff_zinc','support',['ORCH_PerimeterWall_'])
    pipe('Arm',(53.87,top-.22,z),(x,top-.22,z),.025)
    box('Case',x,top-.23,z,.66,.12,.36,'staff_white_paint');box('Lens',x,top-.303,z,.54,.018,.26,'light_lens','light_source')
    contacts.append({'unit':UNIT,'at':[53.91,top-.22,z],'expected_prefix':'ORCH_PerimeterWall_','kind':'fixture_to_original_wall'})
    marker='G8O_LIGHT_'+name;ob=bpy.data.objects.new(marker,None);bpy.context.collection.objects.link(ob);ob.location=(x,-z,top-.32)
    lights.append({'name':marker,'programme_key':ROOM,'at':[x,top-.32,z],'range':5.8,'energy':.7,'colour':[.82,.92,1]})
# Retain all existing serving counters, two original credenzas, beverage machines and doors.
for n,(north,south,kind)in enumerate([(-229,-218,'hot'),(-214,-203,'cold')]):
    center=(north+south)/2;prefix='North'if n==0 else'South'
    range_line(prefix+'Finish',34.0,north+.47,kind);prep(prefix+'Prep',32.5,south-.48)
    store(prefix+'Chill',31.0,center-3.2,1.0,2.15,'cold');store(prefix+'Dry',37.15,center-3.25,.90,2.1,'dry')
    wash(prefix+'Wash',33.50,center+2.7)
# Exact rigid original dish-return copies, facing the work-bay approach.
source_path=C/'assets/hospitality_stations/source/AST-HSP-004.blend'
with bpy.data.libraries.load(str(source_path),link=False)as(src,dst):dst.objects=src.objects
for ob in dst.objects:
    if ob:bpy.context.collection.objects.link(ob)
bpy.context.view_layer.update();sources=[o for o in dst.objects if o and o.type=='MESH'];poses={o.name:o.matrix_world.copy()for o in sources}
for index,z in enumerate([-220.3,-205.3]):
    UNIT='NorthUsedReturn'if index==0 else'SouthUsedReturn';placement=Matrix.Translation((31.0,-z,F))@Matrix.Rotation(math.pi/2,4,'Z')
    instances.append({'name':UNIT,'type':'original_dish_return_rigid_copy','at':[31,F,z],'yaw':math.pi/2})
    for original in sources:
        ob=original.copy();ob.data=original.data.copy();bpy.context.collection.objects.link(ob);ob.parent=None;ob.name='G8O_'+UNIT+'_'+original.name;ob.matrix_world=placement@poses[original.name]
        vs=[ob.matrix_world@Vector(c)for c in ob.bound_box];v=[(q.x,q.z,-q.y)for q in vs]
        records.append({'name':ob.name,'programme_key':ROOM,'unit':UNIT,'role':'original_dish_return','category':'furniture','collide':True,'permitted_retained_context':[],'world_aabb':[min(q[0]for q in v),max(q[0]for q in v),min(q[1]for q in v),max(q[1]for q in v),min(q[2]for q in v),max(q[2]for q in v)]})
        source_copies.append({'name':ob.name,'source_name':original.name,'source_native':str(source_path.relative_to(R)),'placement_blender':[[float(q)for q in row]for row in placement]})
    for dz in [-.44,.44]:supports.append({'unit':UNIT,'kind':'floor','at':[31,F,z+dz],'expected_retained':'CompiledStructuralFloors_NotFinishedRooms'})
for ob in dst.objects:
    if ob:bpy.data.objects.remove(ob,do_unlink=True)
for name,z,mode in [('CleanDelivery',-228,'clean'),('DryDelivery',-222,'clean'),('UsedReturn',-209,'used')]:
    receiving(name,53.47,z,mode);wall_task(name+'Task',52.96,z,64.5)
# Empty parking/turning bays and all existing staff spines remain deliberately free.
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan={'schema':1,'baseline_commit':'affc5c807087ff87da29f3642c2d6e418241b896','latest_main_inspected':'bc731d6d6d54bb2595331ee2f4368558d4d24fda','catalogue_id_candidate':AID,'family':FAMILY,'active':False,'root_name':'Group8OrchardService_WIP','programme_keys':[ROOM],'historical_room_id':'D10_banquet3','retained_candidate_seats':240,'shipwide_passenger_dining_places':2200,'native':native.name,'native_sha256':sha(native),'model_file':out.name,'model_sha256':sha(out),'new_floor_owners':0,'new_programmes':0,'new_capacity':0,'new_doors':0,'new_controllers':0,'meshes':records,'instances':instances,'lights':lights,'supports':supports,'retained_contacts':contacts,'source_copies':source_copies,'collision_policy':{q['name']:{'collide':q['collide'],'category':q['category'],'role':q['role']}for q in records},'floor_y':F,'operational_acceptance':False,'hygiene_or_species_acceptance':False,'structural_capacity_acceptance':False,'final_art_acceptance':False,'limits':['First-pass hot finishing/cold assembly/wash/clean-used staging architecture only','No meal processing,stock,save,inventory or species-diet assumptions','Existing three service doors and240 seats remain unchanged','Local service spine only; Group3 external network and clean-used transfer controllers held','No whole galley throughput,hygiene,cart-driving,engineering or final visual acceptance']}
(W/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('ORCHARD SOURCE BUILD',len(records),'meshes',len(instances),'activity assemblies',len(lights),'physical lights',len(source_copies),'original source meshes')
