"""New additive crown fittings. Never rewrites a retained source or shared registry.
Blender (X,-Z,Y), metres, world origin; immutable r001 output refuses overwrite.
"""
from pathlib import Path
import bpy, bmesh, json, math, sys, hashlib
from mathutils import Vector, Matrix

W = Path(__file__).resolve().parent
R = W.parents[2]
C = R / 'BlenderCatalogue'
AID = 'AST-G8-CROWN-001'
FAMILY = 'group8_destinations_20261011'
assert all(a['catalogue_id'] != AID or a['family'] == FAMILY
           for a in json.loads((C/'catalogue_manifest.json').read_text())['assets'])
for p in [W/'CrownInteriors_r004.blend', W/'G8_CROWN_INTERIORS_r004_unbatched.glb']:
    assert not p.exists(), 'Immutable output already exists: '+str(p)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
sys.path.insert(0, str(C/'standards'))
import staff_materials, materials
mats = staff_materials.materials()
mats.update(materials.materials())
for m in mats.values():
    for n in m.node_tree.nodes:
        if n.type == 'TEX_IMAGE': n.interpolation = 'Closest'
for role, colour in [('task_glass', (.66,.82,.79,1)), ('status_glass', (.34,.58,.59,1))]:
    m = bpy.data.materials.new('G8_'+role);m.use_nodes=True;m.diffuse_color=colour
    p = m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=colour
    p.inputs['Roughness'].default_value=.38;p.inputs['Emission Color'].default_value=colour
    p.inputs['Emission Strength'].default_value=.25
    m['meters_per_tile_uv']=[1,1];m['astraea_material_role']=role;mats[role]=m
records=[];lights=[];instances=[];labels=[]
ROOM=None
FACES=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]

def mesh(name, verts, faces, role, category='fitting'):
    name='G8_'+ROOM+'_'+name
    me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y) for x,y,z in verts],[],faces);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(mats[role])
    uv=me.uv_layers.new(name='MetreScaled');scale=mats[role].get('meters_per_tile_uv',[1,1])
    for f in me.polygons:
        n=f.normal.normalized();u=Vector((1,0,0))-n*n.x if abs(n.z)>.7 else Vector((-n.y,n.x,0));u.normalize();v=n.cross(u)
        for li in f.loop_indices:
            q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
    ob['catalogue_id_candidate']=AID;ob['programme_key']=ROOM;ob['category']=category
    records.append({'name':name,'programme_key':ROOM,'role':role,'category':category,'collide':category!='light_source',
                    'world_aabb':[min(v[0] for v in verts),max(v[0] for v in verts),min(v[1] for v in verts),max(v[1] for v in verts),min(v[2] for v in verts),max(v[2] for v in verts)]})
    return ob

def box(name, x,y,z, sx,sy,sz,role='staff_bluegrey_paint',category='fitting',yaw=0):
    co,si=math.cos(yaw),math.sin(yaw)
    verts=[(x+co*a+si*b,y+c,z-si*a+co*b) for c in [-sy/2,sy/2] for a,b in [(-sx/2,-sz/2),(sx/2,-sz/2),(sx/2,sz/2),(-sx/2,sz/2)]]
    return mesh(name,verts,FACES,role,category)

def panel(name,x,z,w=3.2,yaw=0):
    # Physical sloped worktop, paired foot pedestals, recessed knee void and controls.
    co,si=math.cos(yaw),math.sin(yaw)
    def b(n,a,c,h,sx,sy,sz,role,category='fitting'):
        return box(name+'_'+n,x+co*a+si*c,106.5+h,z-si*a+co*c,sx,sy,sz,role,category,yaw)
    for side in [-1,1]:
        b('Foot'+str(side),side*(w/2-.35),0,.055,.58,.11,1.2,'dark_rubber')
        b('Pedestal'+str(side),side*(w/2-.35),0,.48,.45,.85,.96,'staff_bluegrey_paint')
        b('FrontRib'+str(side),side*(w/2-.35),-.49,.48,.25,.65,.04,'staff_zinc')
    prof=[(-.68,1.08),(.65,.90),(.65,1.04),(-.68,1.22)]
    verts=[(x+co*a+si*c,106.5+h,z-si*a+co*c) for a in [-w/2,w/2] for c,h in prof]
    mesh(''+name+'_Wedge',verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'staff_zinc')
    b('Fascia',0,.665,.91,w,.22,.07,'staff_bluegrey_paint')
    b('UpperRim',0,-.70,1.24,w+.08,.12,.08,'staff_bluegrey_paint')
    for n in range(max(1,int(w/1.45))):
        a=(n-(max(1,int(w/1.45))-1)/2)*1.45
        b('ScreenFrame'+str(n),a,-.15,1.245,1.14,.08,.68,'dark_rubber')
        b('Screen'+str(n),a,-.15,1.294,1.02,.018,.56,'status_glass')
        for q in range(5):b('Readout_%d_%d'%(n,q),a-.38+q*.19,-.18,1.31,.06,.008,.25+q%2*.10,'staff_opal')
        b('ControlRail'+str(n),a,.45,1.105,1.05,.05,.15,'dark_rubber')
        for q in range(6):b('Key_%d_%d'%(n,q),a-.40+q*.16,.45,1.139,.07,.018,.06,'staff_white_paint')
    instances.append({'type':'console','programme_key':ROOM,'name':name,'at':[x,106.5,z],'yaw':yaw,'width':w})

def cabinet(name,x,z,w=2.8,yaw=0,mode='records'):
    co,si=math.cos(yaw),math.sin(yaw)
    def b(n,a,c,h,sx,sy,sz,role):return box(name+'_'+n,x+co*a+si*c,106.5+h,z-si*a+co*c,sx,sy,sz,role,yaw=yaw)
    b('Plinth',0,0,.08,w+.12,.16,.85,'dark_rubber')
    b('Back',0,-.32,1.25,w,2.36,.08,'staff_bluegrey_paint')
    for s in [-1,1]:b('Side'+str(s),s*(w/2-.055),0,1.25,.11,2.36,.72,'staff_white_paint')
    for h in [.17,.76,1.35,1.94,2.43]:b('Shelf'+str(h),0,0,h,w,.10,.75,'staff_zinc')
    for row in range(4):
        for col in range(4):
            a=(col-1.5)*w/4
            if mode=='records':
                b('File_%d_%d'%(row,col),a,.02,.45+row*.58,w/4-.10,.43,.52,'staff_bluegrey_paint')
                b('Label_%d_%d'%(row,col),a,.29,.45+row*.58,.22,.12,.018,'staff_white_paint')
            else:
                b('Pack_%d_%d'%(row,col),a,.02,.45+row*.58,w/4-.14,.40,.52,'ivory_enamel')
                b('RescueBand_%d_%d'%(row,col),a,.29,.45+row*.58,w/4-.18,.13,.025,'staff_safety_ochre' if 'staff_safety_ochre' in mats else 'champagne_metal')
    instances.append({'type':mode+'_cabinet','programme_key':ROOM,'name':name,'at':[x,106.5,z]})

def wallboard(name,x,z,w=6,yaw=0):
    co,si=math.cos(yaw),math.sin(yaw)
    def b(n,a,c,h,sx,sy,sz,role):return box(name+'_'+n,x+co*a+si*c,106.5+h,z-si*a+co*c,sx,sy,sz,role,yaw=yaw)
    b('Back',0,0,2.4,w,2.1,.20,'staff_bluegrey_paint')
    b('Glass',0,.115,2.4,w-.3,1.80,.024,'status_glass')
    for q in range(9):
        a=(q-4)*w/11;b('Datum'+str(q),a,.143,2.4,.12,1.36-.1*(q%3),.017,'staff_opal')
        b('Marker'+str(q),a,.159,2.12+(q%3)*.23,.24,.10,.021,'champagne_metal')
    instances.append({'type':'passive_status_board','programme_key':ROOM,'name':name,'at':[x,108.9,z]})

def task(name,x,z):
    box(name+'_WeightedBase',x,106.55,z,.46,.10,.46,'dark_rubber')
    box(name+'_Stem',x,107.73,z,.08,2.36,.08,'staff_zinc')
    box(name+'_Shade',x,108.96,z,.66,.16,.40,'staff_bluegrey_paint')
    box(name+'_Lens',x,108.862,z,.53,.018,.28,'task_glass','light_source')
    p=[x,108.83,z];marker='G8_LIGHT_'+ROOM+'_'+name
    ob=bpy.data.objects.new(marker,None);bpy.context.collection.objects.link(ob);ob.location=(p[0],-p[2],p[1])
    lights.append({'name':marker,'programme_key':ROOM,'at':p,'range':5.5,'energy':.65,'colour':[.82,.94,1.0] if ROOM!='D18_directory_09' else [1.0,.91,.77]})

# Append immutable source chairs, retaining original mesh/modifiers/materials/packed images.
chair_path=C/'assets/furniture/AST-FUR-002_day_reading_chair.blend'
with bpy.data.libraries.load(str(chair_path),link=False) as (src,dst): dst.objects=src.objects
chair_source=[o for o in dst.objects if o and o.type=='MESH']
for o in dst.objects:
    if o: bpy.context.collection.objects.link(o)
bpy.context.view_layer.update()
chair_poses={o.name:o.matrix_world.copy() for o in chair_source}
for o in chair_source:
    pose=chair_poses[o.name];o.parent=None;o.matrix_world=pose
def chair(name,x,z,yaw=math.pi):
    mat=Matrix.Translation((x,-z,106.5)) @ Matrix.Rotation(-yaw,4,'Z')
    for src in chair_source:
        ob=src.copy();ob.data=src.data.copy();bpy.context.collection.objects.link(ob)
        ob.name='G8_'+ROOM+'_'+name+'_'+src.name;ob.matrix_world=mat @ src.matrix_world
        corners=[ob.matrix_world @ Vector(c) for c in ob.bound_box]
        vs=[(v.x,v.z,-v.y) for v in corners]
        records.append({'name':ob.name,'programme_key':ROOM,'role':'source_chair','category':'furniture','collide':True,
                        'world_aabb':[min(v[0] for v in vs),max(v[0] for v in vs),min(v[1] for v in vs),max(v[1] for v in vs),min(v[2] for v in vs),max(v[2] for v in vs)]})
    instances.append({'type':'original_reading_chair_rigid_copy','programme_key':ROOM,'name':name,'at':[x,106.5,z],'yaw':yaw})

ROOM='D18_directory_01'
for x,yaw in [(-16,-.22),(16,.22)]:
    for n,z in enumerate([-159,-140]):
        panel('BridgeBank_'+str(x)+'_'+str(n),x,z,6.4,yaw)
        for a in [-1.7,1.7]:chair('BridgeOperator_%s_%s_%s'%(x,n,a),x+a,z+2.9,yaw+math.pi)
        task('BridgeTask_%s_%s'%(x,n),x-3.8,z+1.3)
for x in [-27,27]:cabinet('BridgeRecords_'+str(x),x,-125,3.2)
wallboard('ForePlanningPort',-15,-170.7,8);wallboard('ForePlanningStarboard',15,-170.7,8)
labels.append({'programme_key':ROOM,'text':'COMMAND • WATCH STATIONS','at':[0,109.5,-119.5],'yaw':math.pi})

ROOM='D18_directory_03'
for n,z in enumerate([-64,-39]):
    panel('VoiceDesk'+str(n),-23,z,5.0)
    for x in [-24.5,-21.5]:chair('VoiceOperator_%d_%s'%(n,x),x,z+2.8)
    # Three-sided acoustic screens, open rear and accessible side approach.
    box('VoiceScreenBack'+str(n),-23,108.0,z-1.3,6.5,3,.14,'teal_weave')
    for x in [-26.25,-19.75]:box('VoiceScreenWing_%d_%s'%(n,x),x,108.0,z-.25,.14,3,2.1,'teal_weave')
    task('VoiceTask'+str(n),-18.2,z)
for z in [-65,-38]:cabinet('CommsRecords'+str(z),-33,z,4.2,math.pi/2)
wallboard('DispatchWall',-33.8,-52,7,math.pi/2)
panel('CommsDispatch',-23,-31.5,4.5);chair('DispatchOperator',-23,-34,0)
labels.append({'programme_key':ROOM,'text':'COMMUNICATIONS • DISPATCH / QUIET VOICE','at':[-11,109.1,-52],'yaw':math.pi/2})

ROOM='D18_directory_08'
wallboard('ShipSystemsWall',-23,67.0,13)
for x in [-29,-17]:
    panel('StatusDesk'+str(x),x,73,4.0)
    for a in [-1.15,1.15]:chair('StatusOperator_%s_%s'%(x,a),x+a,76)
    task('StatusTask'+str(x),x-2.9,74)
for z in [89,97]:cabinet('StatusRecords'+str(z),-33,z,4.2,math.pi/2)
panel('ShiftReview',-22,95,7);chair('ShiftReviewPort',-24,98);chair('ShiftReviewStarboard',-20,98)
labels.append({'programme_key':ROOM,'text':'SHIP STATUS • WATCH / SHIFT REVIEW','at':[-11,109.1,82],'yaw':math.pi/2})

ROOM='D18_directory_10'
wallboard('EmergencyAssemblyWall',23,67.0,13)
for x in [17,29]:
    panel('EmergencyDesk'+str(x),x,73,4)
    for a in [-1.15,1.15]:chair('EmergencyOperator_%s_%s'%(x,a),x+a,76)
    task('EmergencyTask'+str(x),x+2.9,74)
for z in [88,96]:cabinet('EmergencyStores'+str(z),33,z,4.2,-math.pi/2,'rescue_stores')
panel('ResponseTable',23,95,8);chair('ResponsePort',20.5,98);chair('ResponseStarboard',25.5,98)
labels.append({'programme_key':ROOM,'text':'EMERGENCY CONTROL • RESPONSE / STORES','at':[11,109.1,82],'yaw':-math.pi/2})

# Upper Horizon arrival-reading edge only. Existing Group1 roofed sitting bays are untouched.
ROOM='D18_directory_09'
for side in [-1,1]:
    x=side*23
    panel('HorizonOrientation'+str(side),x,120,4.8)
    for a in [-1.4,1.4]:chair('HorizonStudy_%s_%s'%(side,a),x+a,123)
    cabinet('HorizonFieldRecords'+str(side),side*28.5,115,3.2,side*-math.pi/2)
    task('HorizonTask'+str(side),x+side*3.1,121)
    # Low, broad, original framed landscape information counter, no new view/window.
    box('HorizonCounterFoot'+str(side),x,106.57,135,5.2,.14,1.2,'dark_rubber')
    box('HorizonCounterBody'+str(side),x,106.97,135,5.0,.70,1.02,'warm_walnut')
    box('HorizonCounterTop'+str(side),x,107.38,135,5.4,.12,1.30,'ivory_enamel')
    box('HorizonCounterReveal'+str(side),x,107.24,135.54,4.8,.07,.04,'champagne_metal')
labels.append({'programme_key':ROOM,'text':'UPPER HORIZON • FIELD NOTES / OVERLOOKS','at':[0,109.0,111],'yaw':math.pi})

# Appended originals are unlinked prototypes, not exported duplicate world objects.
for ob in dst.objects:
    if ob: bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(W/'CrownInteriors_r004.blend'))
bpy.ops.export_scene.gltf(filepath=str(W/'G8_CROWN_INTERIORS_r004_unbatched.glb'),export_format='GLB',export_yup=True,
                          export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan={'schema':1,'baseline_commit':'affc5c807087ff87da29f3642c2d6e418241b896','catalogue_id_candidate':AID,
      'family':FAMILY,'active':False,'root_name':'Group8CrownInteriors_WIP','model_file':'G8_CROWN_INTERIORS_r004_unbatched.glb',
      'model_sha256':sha(W/'G8_CROWN_INTERIORS_r004_unbatched.glb'),'native':'CrownInteriors_r004.blend','native_sha256':sha(W/'CrownInteriors_r004.blend'),
      'programme_keys':['D18_directory_01','D18_directory_03','D18_directory_08','D18_directory_09','D18_directory_10'],
      'new_floor_owners':0,'new_programmes':0,'new_capacity':0,'new_doors':0,'existing_controllers':'unchanged shared service doors',
      'collision_policy':{p['name']:{'collide':p['collide'],'category':p['category'],'role':p['role']} for p in records},
      'meshes':records,'instances':instances,'lights':lights,'labels':labels,
      'source_chair':{'path':str(chair_path.relative_to(R)),'sha256':sha(chair_path)},
      'operational_acceptance':False,'structural_capacity_acceptance':False,'final_art_acceptance':False,
      'overlap_exclusions':['Group1 aft sitting bays X±18..28 Z153..169 and lanterns','five received crown interiors','shared centreline/bypass/public/staff routes'],
      'limits':['No command/navigation simulator','No permission or pressure simulation acceptance','No new assembly/embarkation count','Species/poses, occupied chair use, save/inventory and final target-hardware visual acceptance unfinished']}
(W/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
print('G8 BUILD PASS',len(records),'meshes',len(instances),'activity fittings',len(lights),'fixture lights')
