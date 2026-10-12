"""New Long Library returns/conservation fittings; immutable retained sources untouched."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,sys
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];C=R/'BlenderCatalogue'
AID='AST-G8-LIB-001';FAMILY='group8_library_service_20261011';ROOM='D12_directory_02';F=78.0
assert all(a['catalogue_id']!=AID or a['family']==FAMILY for a in json.load(open(C/'catalogue_manifest.json'))['assets'])
native=W/'LibraryService_r003.blend';out=W/'G8_LIBRARY_SERVICE_r003_unbatched.glb'
assert not native.exists()and not out.exists(),'Immutable revision already exists'
bpy.ops.wm.read_factory_settings(use_empty=True);sys.path.insert(0,str(C/'standards'))
import staff_materials,materials
mats=staff_materials.materials();mats.update(materials.materials())
for m in mats.values():
    for node in m.node_tree.nodes:
        if node.type=='TEX_IMAGE':node.interpolation='Closest'
mat=bpy.data.materials.new('G8_LIBRARY_OpalLens');mat.use_nodes=True;mat.diffuse_color=(.75,.9,.9,1)
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=mat.diffuse_color;bs.inputs['Emission Color'].default_value=mat.diffuse_color;bs.inputs['Emission Strength'].default_value=.35;bs.inputs['Roughness'].default_value=.65
mat['meters_per_tile_uv']=[1,1];mats['light_lens']=mat
records=[];instances=[];lights=[];supports=[];contacts=[];source_copies=[];UNIT=''
FACES=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def mesh(name,verts,faces,role='staff_white_paint',category='fitting',permitted_context=None):
    name='G8L_'+UNIT+'_'+name;me=bpy.data.meshes.new(name);me.from_pydata([(x,-z,y)for x,y,z in verts],[],faces);me.update()
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
    box(name,x,(lo+top)/2,z,w,top-lo,d,'dark_rubber');supports.append({'unit':UNIT,'kind':'floor','at':[x,lo,z],'expected_retained':'RemainingBatchStructuralFloors'})
def begin(name,kind,at):
    global UNIT;UNIT=name;instances.append({'name':name,'type':kind,'at':at})
def table(name,x,z,w,d):
    begin(name,'supported_conservation_work_surface',[x,F,z])
    for a in [-w/2+.14,w/2-.14]:
        for b in [-d/2+.14,d/2-.14]:
            foot('Pad'+str((a,b)),x+a,z+b)
            box('Leg'+str((a,b)),x+a,F+.49,z+b,.09,.70,.09,'staff_zinc')
    box('LongRail',x,F+.75,z,w-.16,.14,.08,'staff_bluegrey_paint')
    round_slab('ProfiledTop',x,F+.925,z,w,d,.10,.07,'staff_zinc')
    round_slab('ConservationMat',x,F+.984,z,w-.32,d-.30,.018,.035,'dark_rubber')
    for a in [-1,1]:box('TopApron'+str(a),x+a*(w/2-.04),F+.86,z,.055,.18,d-.12,'staff_white_paint')
def archive(name,x,z,w=.70,d=1.60):
    begin(name,'collection_hold_shelving',[x,F,z])
    for a in [-w/2+.10,w/2-.10]:
        for b in [-d/2+.10,d/2-.10]:foot('Pad'+str((a,b)),x+a,z+b)
    for a in [-1,1]:
        box('BackFrontPost'+str(a),x+a*(w/2-.04),F+1.18,z,.065,2.13,d,'staff_bluegrey_paint')
    box('Back',x-w/2+.04,F+1.16,z,.06,2.10,d,'staff_white_paint')
    for y in [.24,.74,1.24,1.74,2.20]:round_slab('Shelf'+str(y),x,F+y,z,w,d,.065,.045,'staff_zinc')
    for y in [.47,.97,1.47,1.97]:
        for dz in [-.43,.43]:
            round_slab('CollectionTray'+str((y,dz)),x+.025,F+y-.025,z+dz,w-.16,.60,.27,.03,'staff_bluegrey_paint')
            box('BlankID'+str((y,dz)),x+w/2+.008,F+y,z+dz,.016,.075,.13,'staff_white_paint')
def tray(name,x,z,w=.60,d=.42,y=F+.99):
    begin(name,'passive_folio_inspection_tray',[x,y,z]);round_slab('Base',x,y+.025,z,w,d,.05,.035,'staff_bluegrey_paint')
    for a in [-1,1]:box('Side'+str(a),x+a*(w/2-.027),y+.11,z,.054,.17,d,'staff_white_paint')
    box('End',x,y+.11,z-d/2+.025,w,.17,.05,'staff_white_paint')
    for i in range(3):round_slab('InactiveBoundFolio'+str(i),x,y+.076+i*.042,z,w-.16,d-.14,.038,.013,'warm_walnut'if i==0 else'ivory_enamel')
def task_fixture(name,x,z,base=F+.99,h=F+2.30,warm=False):
    begin(name,'supported_task_fixture',[x,h,z]);box('SourceFoot',x,base+.04,z,.30,.08,.22,'staff_zinc')
    pipe('Stem',(x,base+.06,z),(x,h-.04,z),.027)
    box('Hood',x,h,z+.20,.65,.16,.52,'warm_walnut'if warm else'staff_bluegrey_paint')
    box('Lip',x,h-.095,z+.20,.68,.05,.55,'champagne_metal'if warm else'staff_zinc')
    box('Lens',x,h-.126,z+.20,.54,.018,.40,'light_lens','light_source')
    marker='G8L_EXIT_'+name;ob=bpy.data.objects.new(marker,None);bpy.context.collection.objects.link(ob);ob.location=(x,-z-.20,h-.153)
    lights.append({'name':marker,'unit':name,'at':[x,h-.153,z+.20],'colour':[1,.94,.84]if warm else[.83,.92,1.0],'energy':1.15,'range':5.0,'marker':marker})
# Public closed-return furniture belongs in front of the retained privacy wall.
begin('PublicReturns','passive_public_returns_and_information_stand',[47.6,F,-450.0])
for a in [-1.0,1.0]:
    for b in [-.28,.28]:foot('Pad'+str((a,b)),47.6+a,-450+b,.17)
round_slab('LowerPlinth',47.6,F+.20,-450,2.45,.85,.10,.06,'warm_walnut')
for a in [-1.15,0,1.15]:box('Vertical'+str(a),47.6+a,F+.57,-450,.08,.65,.75,'warm_walnut')
box('ClosedBack',47.6,F+.57,-450.33,2.38,.65,.08,'staff_bluegrey_paint')
round_slab('PublicLowTop',47.6,F+.91,-450,2.6,.92,.10,.075,'warm_stone')
for a in [-.62,.62]:
    box('ReturnBinFace'+str(a),47.6+a,F+.66,-449.58,1.0,.38,.025,'staff_bluegrey_paint')
    box('PassiveSlot'+str(a),47.6+a,F+.76,-449.56,.70,.075,.015,'dark_rubber')
    box('BlankPanel'+str(a),47.6+a,F+.56,-449.55,.30,.12,.015,'ivory_enamel')
box('GuideSupport',48.52,F+1.03,-450.22,.055,.28,.10,'champagne_metal')
box('GuideFace',48.52,F+1.20,-450.22,.47,.23,.12,'staff_bluegrey_paint')
table('ConservationBench',41.55,-458.5,1.95,1.15)
table('ReturnsInspection',49.75,-459.05,1.14,3.05)
archive('InspectionFolioHold',40.05,-462.8,.68,1.62)
archive('ReadyCollectionHold',40.05,-456.7,.68,1.62)
archive('DispatchCollectionHold',50.70,-453.3,.78,1.70)
tray('ConservationTray',41.45,-458.45,.82,.48)
tray('InspectionTrayNorth',49.75,-459.9,.73,.52)
tray('InspectionTraySouth',49.75,-458.2,.73,.52)
# All are passive collection props. No infection/sterilization,stock or save claims.
for name,x,z,base,h,warm in [('PublicReturnLight',46.64,-450.27,F+.96,F+2.35,True),('ConservationLight',40.86,-458.8,F+.975,F+2.40,False),('InspectionNorthLight',49.95,-460.21,F+.975,F+2.45,False),('InspectionSouthLight',49.95,-457.88,F+.975,F+2.45,False)]:task_fixture(name,x,z,base,h,warm)
# Measured overhead ties only; no new slab or intrusion above the original roof.
for x in [40.8,51.6]:
    for z in [-462.0,-454.0]:
        begin('CareCeilingTie_'+str((x,z)),'measured_existing_ceiling_to_existing_roof_tie',[x,81.8,z])
        box('LowerShoe',x,81.79,z,.32,.06,.32,'staff_zinc','support',['CARE_ceiling'])
        pipe('VerticalTie',(x,81.80,z),(x,82.893,z),.035)
        box('UpperShoe',x,82.907,z,.48,.044,.48,'staff_zinc','support',['ROOF_closed_assembly'])
        contacts.extend([{'unit':UNIT,'kind':'shoe_to_original_ceiling','at':[x,81.795,z],'direction':[0,-1,0],'expected_prefix':'CARE_ceiling'},{'unit':UNIT,'kind':'shoe_to_original_roof','at':[x,82.905,z],'direction':[0,1,0],'expected_prefix':'ROOF_closed_assembly'}])
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan={'schema':1,'baseline_commit':'affc5c807087ff87da29f3642c2d6e418241b896','catalogue_id_candidate':AID,'family':FAMILY,'active':False,'root_name':'Group8LongLibraryService_WIP','programme_keys':[ROOM],'native':native.name,'native_sha256':sha(native),'model_file':out.name,'model_sha256':sha(out),'new_floor_owners':0,'new_programmes':0,'new_capacity':0,'new_doors':0,'new_controllers':0,'floor_y':F,'meshes':records,'instances':instances,'lights':lights,'supports':supports,'retained_contacts':contacts,'collision_policy':{q['name']:{'collide':q['collide'],'category':q['category'],'role':q['role']}for q in records},'retained_runtime_sha256':'432baa23a4aa7b9dc422f6d6ec5485cf9826bd252d749ec63039785c252e6c5a','retained_native_sha256':'5cb4388f45401fd2a8c9d5f1788d356dd7eb8f477a122a531bc5a7b29c250128','protected_source_loop_xz':[[10,-456],[22,-456],[22,-424],[22,-409],[26,-409],[42,-409],[46,-409],[46,-446],[40,-451],[22,-451]],'protected_care_dogleg_xz':[[41.8,-450.3],[41.8,-452.9],[46.6,-452.9],[46.6,-458.5],[46.6,-462.0]],'operational_acceptance':False,'species_or_occupied_work_acceptance':False,'structural_capacity_acceptance':False,'final_art_acceptance':False,'limits':['Additive returns/conservation/collection holds and measured care ceiling ties;original furnished reading/study/vault sources retained','Passive bound-folio silhouettes;no inventory,infection,sterilization,transfer or passenger ownership claims','Public furniture is a closed stand;no original privacy-wall aperture or external staff door','Original portal4m/source mainloop3m and care dogleg preserved;no cart/species certification','Ties below original roof with no new floor/capacity or QuietGrove support edit;engineering sizing remains open']}
(W/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('LIBRARY SOURCE BUILD',len(records),'meshes',len(instances),'assemblies',len(lights),'fixtures')
