"""Three retained dining service belts: local gateway,hygiene and source fixtures; immutable retained sources untouched."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,sys
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];C=R/'BlenderCatalogue'
AID='AST-G8-SYN-001';FAMILY='group8_synthesis_plant_20261012';ROOM='D01_directory_05';F=0.0
assert all(a['catalogue_id']!=AID or a['family']==FAMILY for a in json.load(open(C/'catalogue_manifest.json'))['assets'])
native=W/'SynthesisPlant_r001.blend';out=W/'G8_SYNTHESIS_PLANT_r001_unbatched.glb'
assert not native.exists()and not out.exists(),'Immutable revision already exists'
bpy.ops.wm.read_factory_settings(use_empty=True);sys.path.insert(0,str(C/'standards'))
import staff_materials,materials
mats=staff_materials.materials();mats.update(materials.materials())
for m in mats.values():
    for node in m.node_tree.nodes:
        if node.type=='TEX_IMAGE':node.interpolation='Closest'
mat=bpy.data.materials.new('G8_MED_IndicatorLens');mat.use_nodes=True;mat.diffuse_color=(.75,.9,.9,1)
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Emission Color'].default_value=mat.diffuse_color;bs.inputs['Emission Strength'].default_value=.35;bs.inputs['Roughness'].default_value=.65
mat['meters_per_tile_uv']=[1,1];mats['light_lens']=mat
records=[];instances=[];lights=[];supports=[];contacts=[];source_copies=[];UNIT=''
FACES=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def mesh(name,verts,faces,role='staff_white_paint',category='fitting',permitted_context=None):
    name='G8S_'+UNIT+'_'+name;me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y)for x,y,z in verts],[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(mats[role]);uv=me.uv_layers.new(name='MetreScaled');scale=mats[role].get('meters_per_tile_uv',[1,1])
    for face in me.polygons:
        n=face.normal.normalized();u=Vector((1,0,0))-n*n.x if abs(n.z)>.7 else Vector((-n.y,n.x,0));u.normalize();v=n.cross(u)
        for li in face.loop_indices:
            q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
    ob['programme_key']=ROOM;ob['unit']=UNIT;ob['category']=category
    records.append({'name':ob.name,'programme_key':ROOM,'unit':UNIT,'role':role,'category':category,'collide':category!='light_source','permitted_retained_context':permitted_context or [],'world_aabb':[min(v[0]for v in verts),max(v[0]for v in verts),min(v[1]for v in verts),max(v[1]for v in verts),min(v[2]for v in verts),max(v[2]for v in verts)]});return ob
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
    assert top>lo,'Footer top must be an absolute elevation above the retained floor'
    box(name,x,(lo+top)/2,z,w,top-lo,d,'dark_rubber');supports.append({'unit':UNIT,'kind':'floor','at':[x,lo,z],'expected_retained':'Group1RequiredSynthesisFloorProposal'})
def begin(name,kind,at):
    global UNIT;UNIT=name;instances.append({'name':name,'type':kind,'at':at})
def plate(name,x,y,z,sx,sz,h=.06,role='staff_zinc'):
    return round_slab(name,x,y,z,sx,sz,h,min(.12,sx*.15,sz*.15),role)
def datum(name,at):
    ob=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(ob);ob.location=(at[0],-at[2],at[1]);ob['programme_key']=ROOM;return ob
def console(name,x,z):
    begin(name,'passive plant work/records console',[x,0,z])
    for a in [-.8,.8]:
        for b in [-.32,.32]:foot('Foot'+str((a,b)),x+a,z+b,.12)
    box('Cabinet',x,.53,z,1.85,.84,.72);plate('Worktop',x,1.0,z,2.05,.86,.12)
    box('DisplayBacking',x,1.35,z-.26,1.32,.52,.10,'staff_bluegrey_paint');box('InactiveDisplay',x,1.35,z-.195,1.16,.36,.025,'dark_rubber')
    for i in range(5):pipe('ExistingControlStyleDial'+str(i),(x+(i-2)*.2,1.05,z+.28),(x+(i-2)*.2,1.09,z+.28),.045,'champagne_metal',12)
    for a in [-.84,.84]:pipe('CounterPost'+str(a),(x+a,.91,z-.28),(x+a,1.64,z-.28),.025)
    box('TaskNoticeBacking',x,1.60,z-.28,1.7,.23,.06,'staff_bluegrey_paint')
def bank(name,x,z,kind):
    begin(name,kind+' candidate process hub',[x,0,z])
    for a in [-2.85,2.85]:
        for b in [-4.15,4.15]:foot('AnchoredFoot'+str((a,b)),x+a,z+b,.18,.32,.32)
    plate('SkidDeck',x,.25,z,6.3,9.0,.18)
    for a in [-2.5,2.5]:
        box('FramePost'+str(a),x+a,2.19,z,.18,3.70,.18,'staff_zinc');box('FrameYoke'+str(a),x+a,3.97,z,.20,.18,8.4,'staff_zinc')
    for b in [-3.9,3.9]:box('CrossTie'+str(b),x,3.97,z+b,5.2,.18,.18,'staff_zinc')
    # Fictional sealed architectural vessels. No reaction, biological production or plant simulator.
    for i,b in enumerate([-2.8,0,2.8]):
        xx=x+(-.55 if i!=1 else .45);zz=z+b
        pipe('Vessel'+str(i),(xx,.43,zz),(xx,3.27,zz),1.06,'staff_white_paint',24)
        for h in [.54,2.50,3.22]:pipe('VesselBand'+str((i,h)),(xx,h-.045,zz),(xx,h+.045,zz),1.09,'staff_zinc',24)
        pipe('ClosedServiceCap'+str(i),(xx,3.25,zz),(xx,3.48,zz),.46,'staff_bluegrey_paint',20)
        pipe('ContainedHeaderStem'+str(i),(xx,3.42,zz),(xx,3.90,zz),.12,'staff_zinc')
        pipe('LowerTransferReturn'+str(i),(xx,.78,zz),(x+2.36,.78,zz),.10)
        pipe('ServiceValve'+str(i),(x+2.10,.78,zz),(x+2.10,1.04,zz),.12,'champagne_metal',16)
    pipe('HeaderRun',(x+1.85,3.82,z-3.9),(x+1.85,3.82,z+3.9),.13)
    pipe('LowReturnRun',(x+2.36,.78,z-3.9),(x+2.36,.78,z+3.9),.10)
    for b in [-3.85,3.85]:
        box('ServiceStand'+str(b),x+2.78,1.15,z+b,.18,1.82,.18,'staff_zinc');box('FrontControlCase'+str(b),x+2.91,1.63,z+b,.42,.65,.76,'staff_bluegrey_paint')
        for j in [-1,1]:pipe('InactivePhysicalDial'+str((b,j)),(x+3.13,1.68,z+b+j*.19),(x+3.17,1.68,z+b+j*.19),.075,'champagne_metal',12)
    # A removable-panel shape is construction only: it is not a working machine control.
    for b in [-3.1,3.1]:box('ClosedEquipmentPanel'+str(b),x-2.76,1.75,z+b,.16,2.75,1.2,'staff_bluegrey_paint')
def bench(name,x,z,w=4.8,depth=1.1):
    begin(name,'clean packing or receiving workbench',[x,0,z])
    for a in [-w/2+.18,w/2-.18]:
        for b in [-depth/2+.13,depth/2-.13]:foot('Foot'+str((a,b)),x+a,z+b,.15)
    box('Case',x,.53,z,w,.76,depth);plate('Top',x,1.0,z,w+.15,depth+.12,.12)
    for i in [-1,0,1]:
        plate('WorkBoard'+str(i),x+i*w*.29,1.09,z,w*.24,depth*.7,.05,'ivory_enamel')
        box('ClosedOutputContainer'+str(i),x+i*w*.29,1.29,z+.16,w*.19,.36,depth*.50,'staff_bluegrey_paint')
        box('ContainerIdentityPlate'+str(i),x+i*w*.29,1.29,z-.135,w*.14,.12,.02,'staff_white_paint')
def storage(name,x,z):
    begin(name,'enclosed ingredient or sealed output stock',[x,0,z])
    for a in [-.72,.72]:
        for b in [-.5,.5]:foot('Foot'+str((a,b)),x+a,z+b,.16)
    for a in [-.81,.81]:box('Side'+str(a),x+a,1.31,z,.08,2.48,1.22)
    box('Back',x,1.31,z+.57,1.64,2.48,.08,'staff_bluegrey_paint')
    for h in [.20,.80,1.4,2.0,2.52]:box('Shelf'+str(h),x,h,z,1.64,.065,1.22,'staff_zinc')
    for h in [.47,1.08,1.67,2.23]:
        for a in [-.42,.42]:plate('SealedStockBin'+str((h,a)),x+a,h,z,.67,.99,.42,'staff_bluegrey_paint')
def wash(name,x,z):
    begin(name,'wash and used-return construction',[x,0,z])
    for a in [-1.35,1.35]:
        for b in [-.5,.5]:foot('Foot'+str((a,b)),x+a,z+b,.18)
    box('LowShelf',x,.30,z,2.9,.07,1.14,'staff_zinc')
    for i in [-1,1]:
        xx=x+i*.73
        for a in [-.62,.62]:box('BasinSide'+str((i,a)),xx+a,.96,z,.06,.26,1.15,'staff_zinc')
        for b in [-.56,.56]:box('BasinEnd'+str((i,b)),xx,.96,z+b,1.22,.26,.06,'staff_zinc')
        box('ActualRecessedBasinBottom'+str(i),xx,.83,z,1.22,.045,1.15,'staff_zinc')
        pipe('TapRiser'+str(i),(xx+.42,1.08,z+.38),(xx+.42,1.51,z+.38),.026)
        pipe('TapSpout'+str(i),(xx+.42,1.51,z+.38),(xx,1.51,z+.38),.026)
        pipe('TapDrop'+str(i),(xx,1.51,z+.38),(xx,1.35,z+.38),.026)
        pipe('VisibleDrain'+str(i),(xx,.83,z),(xx,.36,z),.035)
    for i in [-1,1]:plate('UsedReturnTub'+str(i),x+i*.70,.58,z,.99,.86,.40,'staff_bluegrey_paint')
def fixture(name,x,z,height=4.88,aim=None):
    begin(name,'supported housed task source',[x,height,z]);top=5.27
    for a in [-.22,.22]:pipe('RoofStem'+str(a),(x+a,height+.10,z),(x+a,top,z),.025)
    box('Case',x,height+.10,z,.64,.10,1.44,'staff_bluegrey_paint');box('RetainedStyleLens',x,height+.032,z,.55,.018,1.30,'light_lens','light_source')
    marker='G8S_LIGHT_'+name;datum(marker,[x,height,z]);lights.append({'name':marker,'programme_key':ROOM,'at':[x,height,z],'aim':aim or[x,.95,z],'range':6.8,'energy':1.3,'colour':[.84,.93,1],'spot_angle':75})
begin('PlantEnclosure','local washable plant architecture',[-75.5,0,0])
# Leave a broad existing-service entrance at the east edge. No new gate consumes the old approach.
for x in [-95,-56]:
    spans=[(-30,30)]if x==-95 else[(-30,-2.4),(2.4,30)]
    for i,(lo,hi)in enumerate(spans):box('LongWall'+str((x,i)),x,2.62,(lo+hi)/2,.22,5.24,hi-lo)
for z in [-30,30]:box('EndWall'+str(z),-75.5,2.62,z,39,5.24,.22)
box('EastArrivalHeader',-56,3.93,0,.22,2.62,4.8)
# Four local roof panels and supported folded ribs stay below the untouched D02 deck.
for lo,hi in[(-95,-85),(-85,-75),(-75,-65),(-65,-56)]:
    box('LocalRoof'+str(lo),(lo+hi)/2,5.35,0,hi-lo,.20,60,'staff_white_paint','support')
for x in [-94.5,-85,-75,-65,-56.5]:
    for z in [-29.5,29.5]:
        foot('PerimeterFoot'+str((x,z)),x,z,.20,.30,.30)
        pipe('SlenderRoofPier'+str((x,z)),(x,.20,z),(x,5.28,z),.12)
    box('TransverseRoofRib'+str(x),x,5.11,0,.18,.28,59.2,'staff_zinc','support')
for name,x,z,kind in [('NorthWest',-86,16,'ingredient conditioning'),('NorthEast',-75,16,'sealed blend'),('SouthWest',-86,-16,'thermal finishing'),('SouthEast',-75,-16,'portion transfer')]:bank(name,x,z,kind)
console('PlantRecords',-89,0);console('OutputDesk',-73,0)
for i,x in enumerate([-91,-87,-83]):storage('IngredientStock'+str(i),x,26.4)
for i,x in enumerate([-91,-87,-83]):storage('SealedOutput'+str(i),x,-26.4)
bench('CleanPacking',-64.8,27.2);bench('CleanHandoff',-73.8,26.4,3.6)
wash('WashAndReturn',-64.8,-27);bench('UsedReceiving',-73.8,-26.4,3.6)
doors=[]
for label,z in [('CleanPacking',23),('WashReturn',-23)]:
    begin(label+'Threshold','local packing/wash threshold',[-64.8,0,z]);centre=-64.8
    for lo,hi in[(-69.8,centre-1.125),(centre+1.125,-56.11)]:box('Screen'+str(lo),(lo+hi)/2,1.68,z,hi-lo,3.36,.24)
    box('GatewayHeader',centre,3.10,z,2.25,.52,.24)
    marker='G8S_DOOR_'+label;datum(marker,[centre,0,z])
    doors.append({'name':'Synthesis'+label+'Door','persistent_id':'D01_synthesis_g8_'+label.lower()+'_001','marker':marker,'at':[centre,0,z],'yaw':0,'scale':[.8,1,1],'default_open':True,'new_aperture_m':[2.25,2.84],'scaled_exact_outer_frame_m':[2.208,2.82],'pressure_food_hygiene_permission_acceptance':False})
for z in [-7,7]:
    for x in [-91,-81,-71,-58]:fixture(('South'if z<0 else'North')+'Street'+str(abs(x)),x,z)
for x,z,name in[(-91,24,'Ingredients'),(-91,-24,'Outputs'),(-64.8,26.4,'Packing'),(-64.8,-26.4,'Wash'),(-89,0,'Records'),(-73,0,'Handoff')]:fixture(name,x,z,3.16 if name in['Packing','Wash','Records','Handoff'] else 4.88)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
plan={'schema':1,'root_name':'Group8SynthesisPlant_Candidate','programme_key':ROOM,'native':native.name,'native_sha256':sha(native),'model_file':out.name,'model_sha256':sha(out),'meshes':records,'instances':instances,'supports':supports,'lights':lights,'doors':doors,'new_capacity':0,'new_programmes':0,'new_shared_backends':0,'active_new_floor_owners':0,'candidate_process_hubs':4,'printed_hub_quantity_allocation_acceptance':False,'external_service_and_supporting_floor_adoption':False,'original_bay_and_service_door_unchanged':True,'plant_pressure_production_food_hygiene_species_cart_engineering_final_art_acceptance':False}
(W/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('SYNTHESIS SOURCE',len(records),'new meshes',len(instances),'assemblies',len(lights),'housed task sources; 4 candidate process hubs,original bay preserved')
