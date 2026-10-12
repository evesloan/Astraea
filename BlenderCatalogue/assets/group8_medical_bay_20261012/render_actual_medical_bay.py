from pathlib import Path
import bpy,json,math,hashlib,sys
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];p=json.load(open(W/'PLAN.json'))
rec=json.load(open(W/'EXACT_RETAINED_MEDICAL_BAY_RECOVERY.json'));original=Path(rec['native'])
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(original)==p['original_native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(W/p['native']))
with bpy.data.libraries.load(str(original),link=False) as (src,dst):dst.objects=list(src.objects)
for ob in dst.objects:
 if ob:bpy.context.collection.objects.link(ob)
sys.path.insert(0,str(R/'BlenderCatalogue/standards'));import materials
mats=materials.materials();selection=json.load(open(W/'SOURCE_CONTEXT_FLOOR_SELECTION.json'));floors=[]
for f,chosen in selection.items():
 assert sha(R/f)==chosen['sha256']
 for row in json.load(open(R/f))['regions']:
  if row['id']not in chosen['exact_region_ids']:continue
  floors.append(row['id']);verts=[];faces=[];roles=[];y=row['floor_y'];th=row['thickness']
  for tri in [tri for chunk in row['render_chunks']for tri in chunk['triangles']]:
   for yy,reverse,role in[(y,False,0),(y-th,True,1)]:
    start=len(verts);verts.extend((q[0],-q[1],yy)for q in tri);ids=list(range(start,start+3))
    normal=(Vector(verts[start+1])-Vector(verts[start])).cross(Vector(verts[start+2])-Vector(verts[start])).z
    if(normal>0)==reverse:ids.reverse()
    faces.append(tuple(ids));roles.append(role)
  for ring in row['rings']:
   for a,b in zip(ring,ring[1:]+ring[:1]):
    start=len(verts);verts.extend([(a[0],-a[1],y),(b[0],-b[1],y),(b[0],-b[1],y-th),(a[0],-a[1],y-th)])
    faces.append(tuple(range(start,start+4)));roles.append(1)
  me=bpy.data.meshes.new(row['id']);me.from_pydata(verts,[],faces);me.update()
  ob=bpy.data.objects.new('ExactCompilerFloor_'+row['id'],me);bpy.context.collection.objects.link(ob)
  me.materials.append(mats['warm_stone']);me.materials.append(mats['ivory_enamel']);uv=me.uv_layers.new(name='RetainedRuntimeFloorUV')
  for face,role in zip(me.polygons,roles):
   face.material_index=role
   for li in face.loop_indices:
    v=me.vertices[me.loops[li].vertex_index].co
    uv.data[li].uv=(v.x*.3,-v.y*.3)if abs(face.normal.z)>.9 else((v.x-v.y)*.3,v.z*.3)
lights=[]
for row in p['lights']:
 data=bpy.data.lights.new('ActualHousing_'+row['name'],'SPOT');data.energy=140;data.spot_size=math.radians(row['angle'])
 data.spot_blend=.5;data.color=row['colour'];data.shadow_soft_size=.12
 ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=(row['at'][0],-row['at'][2],row['at'][1])
 lights.append({'name':ob.name,'actual_source_exit':True,'documentation_watts':140})
for name,at,power in [('WardFore',(28,450,23.8),800),('WardAft',(28,431,23.8),700),('SurgicalSpine',(28,415,23.7),600),('LeftSuite',(21,418,23.5),350),('RightSuite',(36,418,23.5),350),('Wash',(28,404,23.5),350)]:
 data=bpy.data.lights.new('DocumentationFill_'+name,'POINT');data.energy=power;data.shadow_soft_size=2;data.use_shadow=False;data.color=(.98,.99,1)
 ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=at
 lights.append({'name':ob.name,'blender_xyz':list(at),'watts':power,'documentation_only':True})
for mat in bpy.data.materials:
 if mat.use_nodes:
  for node in mat.node_tree.nodes:
   if node.type=='TEX_IMAGE':node.interpolation='Closest'
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=32;scene.eevee.shadow_pool_size='1024'
scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
if scene.world is None:scene.world=bpy.data.worlds.new('SourceDocumentaryWorld')
scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.08,.09,.11,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.08;scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.35
camera=bpy.data.cameras.new('ActualMedicalSourceReview');ob=bpy.data.objects.new(camera.name,camera);bpy.context.collection.objects.link(ob);scene.camera=ob;images=[]
def photo(name,at,target,lens):
 path=W/name;assert not path.exists();camera.lens=lens;ob.location=(at[0],-at[2],at[1]);t=Vector((target[0],-target[2],target[1]))
 ob.rotation_euler=(t-ob.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(path)
 bpy.ops.render.render(write_still=True);images.append(name)
photo('SOURCE_MEDICAL_BAY_SURGICAL_SPINE_WIDE001.png',[28,22.65,-423],[28,22.2,-408],20)
photo('SOURCE_MEDICAL_BAY_WARD_LIGHTING_WIDE001.png',[28,22.65,-431],[28,22.2,-460],23)
assert sha(original)==p['original_native_sha256']and sha(W/p['native'])==p['native_sha256']
(W/'SOURCE_CONTEXT_PHOTO_RECEIPT001.json').write_text(json.dumps({'exact_original_native_sha256':p['original_native_sha256'],'candidate_native_sha256':p['native_sha256'],'original_objects':len(dst.objects),'exact_compiler_floor_owners':floors,'images':images,'additional_documentary_lights':lights,'original_mutations':0,'scope':'Actual exact native source and new native-derived fittings;default-open geometry. Documentary Eevee fill/watts,not Game/CRT/hardware/clinical/pressure/engineering/final-art acceptance.'},indent=2)+'\n')
