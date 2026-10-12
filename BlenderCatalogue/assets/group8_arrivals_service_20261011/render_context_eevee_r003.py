"""Actual original+candidate textured source scene; fixture-positioned review lighting.
No native saved, no Godot radiometric/render/CRT or final-art equivalence claimed.
"""
from pathlib import Path
import bpy,json,math,hashlib,sys
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];C=R/'BlenderCatalogue';p=json.load(open(W/'PLAN.json'))
bpy.ops.wm.open_mainfile(filepath=str(W/p['native']))
all_source_paths=[]
def append(relative,at,yaw=0):
    path=C/relative;all_source_paths.append(str(path.relative_to(R)))
    with bpy.data.libraries.load(str(path),link=False)as(src,dst):dst.objects=src.objects
    for ob in dst.objects:
        if ob:bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.update();poses={ob:ob.matrix_world.copy()for ob in dst.objects if ob};transform=Matrix.Translation((at[0],-at[2],at[1]))@Matrix.Rotation(yaw,4,'Z');result={}
    for ob,matrix in poses.items():
        key=ob.name;ob.parent=None;ob.matrix_world=transform@matrix;result[key]=ob
    return result
arch=append('assets/arrivals_fusion/source/AST-ARR-002.blend',[-31,0,-432])
append('assets/arrivals_reception/source/AST-ARR-003.blend',[-30,0,-456])
reception=append('assets/arrivals_reception_alcove/source/AST-ARR-004.blend',[-30,0,-456])
for index in range(2):
    at=arch['DATUM_exhibit_center_'+str(index)].matrix_world.translation
    append('assets/fusion_exhibit/source/AST-ENG-007.blend',[at.x,at.z,-at.y])
for group,cx in enumerate([-38,-24]):
    append('assets/furniture/AST-FUR-001_day_window_bench.blend',[cx,0,-402.6],math.pi)
    append('assets/furniture/AST-FUR-003_day_table.blend',[cx,0,-404.5])
    for side in [-1,1]:append('assets/furniture/AST-FUR-002_day_reading_chair.blend',[cx+side*2.4,0,-405.6],-side*.95)
for i,z in enumerate([-444.2,-419.8]):append('assets/furniture/AST-FUR-001_day_window_bench.blend',[-31,6,z],0 if i==0 else math.pi)
append('assets/staff_threshold/source/AST-STF-008.blend',p['door']['at'],p['door']['yaw'])
# Exact original floor tops,undersides and region edges with the actual .3 metre UV rule.
sys.path.insert(0,str(C/'standards'));import materials,staff_materials
palette=materials.materials();palette.update(staff_materials.materials())
definition=json.load(open(R/'Game/data/generated/structural_meshes.json'))
floor_ids=['D01_arrivals_ground','D02_fusion_visitor_galleries','D02_fusion_screened_service','D03_protected_crew_cover']
for region in definition['regions']:
    if region['id']not in floor_ids:continue
    verts=[];faces=[];roles=[];fy=region['floor_y'];th=region['thickness']
    for tri in region['triangles']:
        for y,reverse,role in [(fy,False,0),(fy-th,True,1)]:
            start=len(verts);verts.extend((q[0],-q[1],y)for q in tri);indices=list(range(start,start+3))
            normal=(Vector(verts[start+1])-Vector(verts[start])).cross(Vector(verts[start+2])-Vector(verts[start])).z
            if (normal>0)==reverse:indices.reverse() # Godot clockwise to Blender CCW front convention.
            faces.append(tuple(indices));roles.append(role)
    for ring in region['rings']:
        for a,b in zip(ring,ring[1:]+ring[:1]):
            start=len(verts);verts.extend([(a[0],-a[1],fy),(b[0],-b[1],fy),(b[0],-b[1],fy-th),(a[0],-a[1],fy-th)]);faces.append(tuple(range(start,start+4)));roles.append(1)
    me=bpy.data.meshes.new(region['id']);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new('ExactRetainedCompiler_'+region['id'],me);bpy.context.collection.objects.link(ob)
    me.materials.append(palette['staff_floor']if region['material_role']=='staff_floor'else palette['warm_stone']);me.materials.append(palette['ivory_enamel']);layer=me.uv_layers.new(name='ExactOriginalRuntimeUV')
    for face,role in zip(me.polygons,roles):
        face.material_index=role
        for li in face.loop_indices:
            q=me.vertices[me.loops[li].vertex_index].co;layer.data[li].uv=(q.x*.3,-q.y*.3)if abs(face.normal.z)>.9 else((q.x-q.y)*.3,q.z*.3)
# Preserve source textures; source-only lamps use the exact existing/native exits.
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    for node in mat.node_tree.nodes:
        if node.type=='TEX_IMAGE':node.interpolation='Closest'
for ob in bpy.context.scene.objects:
    if ob.type=='MESH'and any(s in ob.name.lower()for s in ['lens','opal']):ob.visible_shadow=False
sources=[]
def light(name,at,colour=(1,.94,.85),power=230,target=None):
    data=bpy.data.lights.new(name,'SPOT');data.energy=power;data.color=colour;data.spot_size=math.radians(82);data.spot_blend=.5;data.shadow_soft_size=.14
    ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob);ob.location=at
    if target is not None:ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    sources.append({'name':name,'actual_source_blender_position':list(at),'source_only_watts':power})
for key,marker in arch.items():
    if key.startswith('DATUM_light_'):light('Review_'+key,marker.matrix_world.translation,power=550 if marker.matrix_world.translation.z>5 else 250)
    if key.startswith('DATUM_wallwash_'):light('Review_'+key,marker.matrix_world.translation,power=550,target=(-46.6,432,7.5))
for key,marker in reception.items():
    if key.startswith('DATUM_light_'):light('Review_Reception_'+key,marker.matrix_world.translation,power=180)
for row in p['lights']:light('Review_'+row['name'],(row['at'][0],-row['at'][2],row['at'][1]),tuple(row['colour']),220)
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT';scene.cycles.device='CPU';scene.cycles.samples=128;scene.cycles.use_denoising=False;scene.cycles.use_adaptive_sampling=True;scene.cycles.adaptive_threshold=.02
if scene.world is None:scene.world=bpy.data.worlds.new('SourceReviewWorld')
scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.07,.08,.11,1);scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.045
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.75
scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
camera=bpy.data.cameras.new('ActualSourceContextCamera');ob=bpy.data.objects.new('ActualSourceContextCamera',camera);bpy.context.collection.objects.link(ob);scene.camera=ob
def photo(name,at,target,lens):
    path=W/name;assert not path.exists(),'Preserve earlier image attempts';camera.lens=lens;ob.location=(at[0],-at[2],at[1]);t=Vector((target[0],-target[2],target[1]));ob.rotation_euler=(t-ob.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
photo('SOURCE_ARRIVALS_COURT_AND_BAGGAGE_WIDE001.png',[-22,2.3,-428],[-38.5,3.1,-452.5],20)
photo('SOURCE_ARRIVALS_HANDOFF_RECEPTION_WIDE001.png',[-22,1.75,-447],[-38,1.8,-457],24)
photo('SOURCE_ARRIVALS_HOLDING_INTERIOR_WIDE001.png',[-41.7,1.75,-452],[-50,1.65,-459],20)
(W/'SOURCE_CONTEXT_PHOTO_RECEIPT.json').write_text(json.dumps({'native':p['native'],'native_sha256':p['native_sha256'],'original_context_sources':sorted(set(all_source_paths)),'compiler_region_ids_exact':floor_ids,'images':['SOURCE_ARRIVALS_COURT_AND_BAGGAGE_WIDE001.png','SOURCE_ARRIVALS_HANDOFF_RECEPTION_WIDE001.png','SOURCE_ARRIVALS_HOLDING_INTERIOR_WIDE001.png'],'renderer':'Blender Eevee textured source review; no Game renderer changes;source textures,actual fixture positions; no native/export saved or changed','sources':sources,'source_review_exposure':.75,'limits':['Fixture watts/exposure are source-review composition settings,not Godot radiometric comparison','No ordinary Godot/CRT/target hardware,occupied use,pressure/species/engineering/final-art acceptance','Other ship districts omitted from photographed source context']},indent=2)+'\n')
