from pathlib import Path
import bpy,json,hashlib,math,sys
from mathutils import Matrix,Vector
W=Path(__file__).resolve().parent;R=W.parents[2];p=json.load(open(W/'PLAN.json'));rec=json.load(open(W/'EXACT_RETAINED_DINING_RECOVERY.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();assert sha(W/p['native'])==p['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(W/p['native']));originals=[]
for row in rec['families']:
 f=Path(row['native']);assert sha(f)==row['native_sha256']
 with bpy.data.libraries.load(str(f),link=False)as(src,dst):dst.objects=src.objects
 for ob in dst.objects:
  if ob:bpy.context.collection.objects.link(ob)
 originals.append({'programme_key':row['programme_key'],'native_sha256':row['native_sha256'],'source_objects':len(dst.objects)})
# Exactly the same retained standard source instance scale/default-open pose as the tested model.
f=R/p['retained_standard_door_source']['native'];assert sha(f)==p['retained_standard_door_source']['native_sha256']
for row in p['doors']:
 with bpy.data.libraries.load(str(f),link=False)as(src,dst):dst.objects=src.objects
 for ob in dst.objects:
  if ob:bpy.context.collection.objects.link(ob)
 for ob in dst.objects:
  if ob and ob.name.startswith('HINGE_LEFT'):ob.rotation_euler.z=math.pi/2
  if ob and ob.name.startswith('HINGE_RIGHT'):ob.rotation_euler.z=-math.pi/2
 bpy.context.view_layer.update();poses={ob:ob.matrix_world.copy()for ob in dst.objects if ob};world=Matrix.Translation((row['at'][0],-row['at'][2],row['at'][1]))@Matrix.Diagonal((.8,1,1,1))
 for ob,pose in poses.items():ob.parent=None;ob.matrix_world=world@pose
# Render only exact retained compiler regions intersecting the three source rooms.
sys.path.insert(0,str(R/'BlenderCatalogue/standards'));import materials
mats=materials.materials();selection=json.load(open(W/'SOURCE_CONTEXT_FLOOR_SELECTION.json'));floors=[]
for definition in ['Game/data/generated/structural_meshes.json','Game/data/architecture/REMAINING_BATCH_FLOORS.json']:
 assert sha(R/definition)==selection[definition]['sha256']
 for row in json.load(open(R/definition))['regions']:
  if abs(float(row['floor_y'])-61)>.0001:continue
  if row['id']not in selection[definition]['exact_region_ids']:continue
  if row['id']in floors:continue
  floors.append(row['id']);verts=[];faces=[];roles=[];y=row['floor_y'];th=row['thickness']
  for tri in [tri for chunk in row['render_chunks']for tri in chunk['triangles']]:
   for yy,reverse,role in[(y,False,0),(y-th,True,1)]:
    start=len(verts);verts.extend((q[0],-q[1],yy)for q in tri);indices=list(range(start,start+3));normal=(Vector(verts[start+1])-Vector(verts[start])).cross(Vector(verts[start+2])-Vector(verts[start])).z
    if(normal>0)==reverse:indices.reverse()
    faces.append(tuple(indices));roles.append(role)
  for ring in row['rings']:
   for a,b in zip(ring,ring[1:]+ring[:1]):
    start=len(verts);verts.extend([(a[0],-a[1],y),(b[0],-b[1],y),(b[0],-b[1],y-th),(a[0],-a[1],y-th)]);faces.append(tuple(range(start,start+4)));roles.append(1)
  me=bpy.data.meshes.new(row['id']);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new('ExactCompilerFloor_'+row['id'],me);bpy.context.collection.objects.link(ob);me.materials.append(mats['warm_stone']);me.materials.append(mats['ivory_enamel']);uv=me.uv_layers.new(name='RetainedRuntimeFloorUV')
  for face,role in zip(me.polygons,roles):
   face.material_index=role
   for li in face.loop_indices:
    q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.x*.3,-q.y*.3)if abs(face.normal.z)>.9 else((q.x-q.y)*.3,q.z*.3)
lights=[]
for row in p['lights']:
 data=bpy.data.lights.new('NewPhysicalSource_'+row['name'],'SPOT');data.energy=140;data.spot_size=math.radians(row['spot_angle']);data.spot_blend=.5;data.color=row['colour'];data.shadow_soft_size=.10
 ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=(row['at'][0],-row['at'][2],row['at'][1]);target=Vector((row['aim'][0],-row['aim'][2],row['aim'][1]));ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler();lights.append({'name':ob.name,'actual_source_exit':True,'documentation_watts':140})
for key,side,z0 in[('Shared',-1,-466),('Sunward',1,-466),('Lantern',-1,-250)]:
 for name,u,v,y,power in[('Staff',44.4,31,63.2,400),('Wash',44.7,26,62.8,220),('Public',39.3,35.5,63.5,900),('DiningContext',32,35.5,64.5,1800)]:
  data=bpy.data.lights.new('DocumentationFill_'+key+'_'+name,'POINT');data.energy=power;data.shadow_soft_size=2;data.use_shadow=False;data.color=(.99,.98,.96);ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=(side*(8+u),-(z0+v),y);lights.append({'name':ob.name,'documentation_only':True,'watts':power})
for mat in bpy.data.materials:
 if mat.use_nodes:
  for node in mat.node_tree.nodes:
   if node.type=='TEX_IMAGE':node.interpolation='Closest'
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=32;scene.eevee.shadow_pool_size='1024';scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
if scene.world is None:scene.world=bpy.data.worlds.new('SourceDocumentaryWorld')
scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.08,.09,.11,1);scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.08;scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.35
camera=bpy.data.cameras.new('ActualSourceReview');ob=bpy.data.objects.new(camera.name,camera);bpy.context.collection.objects.link(ob);scene.camera=ob;images=[]
def photo(name,at,target,lens):
 path=W/name;assert not path.exists();camera.lens=lens;ob.location=(at[0],-at[2],at[1]);t=Vector((target[0],-target[2],target[1]));ob.rotation_euler=(t-ob.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);images.append(name)
photo('SOURCE_SHARED_TABLE_DINING_SERVICE_WIDE002.png',[-44.0,62.75,-429.5],[-49.8,62.2,-433.7],18)
photo('SOURCE_SUNWARD_HYGIENE_WIDE002.png',[52.4,62.65,-435.7],[51.3,62.0,-445.0],20)
photo('SOURCE_LANTERN_SERVICE_CONTEXT_WIDE002.png',[-46.5,62.75,-211.0],[-50.3,62.2,-217.0],18)
assert sha(W/p['native'])==p['native_sha256'];assert sha(f)==p['retained_standard_door_source']['native_sha256']
for row in rec['families']:assert sha(Path(row['native']))==row['native_sha256']
(W/'SOURCE_CONTEXT_PHOTO_RECEIPT002.json').write_text(json.dumps({'actual_immutable_originals':originals,'new_native_sha256':p['native_sha256'],'exact_standard_source_sha256':p['retained_standard_door_source']['native_sha256'],'source_instance_scale_and_open_pose':'Exact tested0.8 X scale;left+90/right-90 source hinges;original files never saved or modified','exact_original_compiler_floor_owners':floors,'images':images,'additional_documentary_lights':lights,'original_mutations':0,'limits':'Actual native source geometry and textures,not generated concept or Game screenshot. Additional Eevee documentary fill/watts and floor material rendering are disclosed;no Godot/CRT/hardware/final-art/food/hygiene/engineering acceptance.'},indent=2)+'\n')
