from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2]
B=lambda p:(p[0],-p[2],p[1]);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[W/'StarAtlasD17ReceivingFirst.blend',W/'StarAtlasD17Standard823Recess.blend',R/'BlenderCatalogue/assets/star_atlas_upper_commons_20261009/source/StarAtlasUpperCommons.blend',R/'BlenderCatalogue/assets/guest_entry_door/source/AST-DOR-002.blend']
pins={str(p.relative_to(R)):sha(p)for p in files};P=json.loads((W/'PLAN.json').read_text())
def append(path,exclude=()):
    with bpy.data.libraries.load(str(path),link=False)as(a,b):b.objects=[n for n in a.objects if n not in exclude]
    for ob in b.objects:
        if ob:bpy.context.collection.objects.link(ob)
    return [o for o in b.objects if o]
def setup():
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=False
    s.render.threads_mode='FIXED';s.render.threads=3;s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
    s.world=bpy.data.worlds.new('DiagnosticSourceWorld');s.world.use_nodes=True
    s.world.node_tree.nodes['Background'].inputs[0].default_value=(.24,.27,.32,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
def light(p,energy=220,size=3):
    bpy.ops.object.light_add(type='AREA',location=B(p));o=bpy.context.object;o.data.energy=energy;o.data.size=size
def view(name,p,target,lens=24,ortho=None):
    bpy.ops.object.camera_add(location=B(p));o=bpy.context.object;o.data.lens=lens
    if ortho:o.data.type='ORTHO';o.data.ortho_scale=ortho
    o.rotation_euler=(Vector(B(target))-o.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.scene.camera=o;bpy.context.scene.render.filepath=str(W/name);bpy.ops.render.render(write_still=True);images.append(name)
images=[]
bpy.ops.wm.open_mainfile(filepath=str(files[0]));append(files[2],P['source_wall_replacements'])
doors=append(files[3]);top=[o for o in doors if o.parent not in doors]
for o in top:o.location+=Vector(B(P['commons_door']['origin']))
# Exact compiler slab context is diagnostic and is never exported into production.
owner=next(r for r in json.loads((R/'Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json').read_text())['regions']if r['id']=='D16_STAR_ATLAS_MISSING_STREET_1')
verts=[];faces=[]
for t in owner['triangles']:
    i=len(verts);verts += [B([x,y,z])for y in [97.26,97.5]for x,z in t];faces += [[i,i+2,i+1],[i+3,i+4,i+5]]
for ring in owner['rings']:
    for a,b in zip(ring,ring[1:]+ring[:1]):
        i=len(verts);verts += [B([x,y,z])for x,z,y in [(a[0],a[1],97.26),(b[0],b[1],97.26),(b[0],b[1],97.5),(a[0],a[1],97.5)]];faces.append([i,i+1,i+2,i+3])
me=bpy.data.meshes.new('DiagnosticOriginalD16Slab');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(ob)
mat=bpy.data.materials.new('DiagnosticOriginalSlab');mat.diffuse_color=(.42,.38,.3,1);me.materials.append(mat)
setup()
for p in [(-65,105.8,12),(-65,105.8,15.8),(-61.5,105.8,22),(-61.5,105.8,30),(-61.5,105.8,36),(-57,104,31),(-66,99,30)]:light(p)
view('SOURCE_GATEWAY_CONNECTION.png',[-65,103.6,11.3],[-65,103.25,14.4],24)
view('SOURCE_BRANCH_STANDING.png',[-61.5,103.6,18.9],[-61.5,103.4,35.6],24)
view('SOURCE_BEARINGS_AND_TRUSSES.png',[-53,107.8,39],[-62.2,102.3,27],25)

bpy.ops.wm.open_mainfile(filepath=str(files[1]));append(files[0])
for n in ['D17R_HeldRoom823','D17R_HeldRoom823_Cap','D17R_HeldRoom823_Base']:bpy.data.objects[n].hide_render=True
setup()
for p in [(-61.5,105.7,35.6),(-65,105.6,35.6),(-69,105.6,35.6),(-74,105.6,35.6),(-65,104,37.8)]:light(p)
view('SOURCE_823_CONTAINED_REVEAL.png',[-60.8,103.6,35.6],[-63.175,103.2,35.6],24)
for name,delta in [('EntryDoor__LEAF_LEFT',-.84),('EntryDoor__LEAF_RIGHT',.84)]:bpy.data.objects[name].location.x+=delta
bpy.context.view_layer.update()
view('SOURCE_823_OPEN_POCKETS.png',[-61.5,103.6,35.6],[-67,103.2,35.6],22)
hidden=[]
for o in bpy.data.objects:
    if o.name.startswith('SUI_Ceiling_')or o.name=='SUI_BathCeiling':o.hide_render=True;hidden.append(o.name)
view('SOURCE_823_LAYOUT_CUTAWAY.png',[-69.5,119,35.601],[-69.5,102,35.6],ortho=15)
for p,h in pins.items():assert sha(R/p)==h
(W/'SOURCE_VIEW_RUN.json').write_text(json.dumps({'status':'PASS','images':images,'native_pins_unchanged':pins,'source_only':True,'diagnostic_fill':True,'unsaved_context':True,'first_room_reservation_guard_hidden_in_validation_view_only':True,'first_room_entry_opened_unsaved_for_pocket_review':True,'unsaved_cutaway_hidden':hidden,'actual_first_room_adopted':False,'final_graphical_CRT_hardware_acceptance':False},indent=2)+'\n')
