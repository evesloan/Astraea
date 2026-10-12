from pathlib import Path
import bpy,json,math,hashlib,sys
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];p=json.load(open(W/'PLAN.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(W/p['native']));assert sha(W/p['native'])==p['native_sha256']
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
context=json.load(open(W/'SYNTHESIS_ACTUAL_CONTEXT.json'));original_triangles=0;original_meshes=0
# Exact world triangles from the actual retained source bay; documentary role/UV mapping only.
for row in context['old_meshes']:
 if '/D01_SynthesisServiceBay_WIP/'not in row['path']:continue
 verts=[];faces=[]
 for tri in row['triangles']:
  start=len(verts);verts.extend((v[0],-v[2],v[1])for v in tri);faces.append((start+2,start+1,start))
 me=bpy.data.meshes.new(row['path']);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new('ActualRetainedBay_'+str(original_meshes),me);bpy.context.collection.objects.link(ob)
 role=next((r for r in ['staff_zinc','staff_bluegrey_paint','staff_white_paint','staff_opal','dark_rubber','champagne_metal']if r in row['path']),'ivory_enamel')
 if role not in bpy.data.materials:role='ivory_enamel'
 me.materials.append(bpy.data.materials[role]);uv=me.uv_layers.new(name='DocumentaryRetainedContextUV')
 for face in me.polygons:
  for li in face.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v.x*.3,-v.y*.3)if abs(face.normal.z)>.9 else((v.x-v.y)*.3,v.z*.3)
 original_triangles+=len(faces);original_meshes+=1
lights=[]
for row in p['lights']:
 data=bpy.data.lights.new('ActualHousing_'+row['name'],'SPOT');data.energy=420;data.spot_size=math.radians(row['spot_angle']*2);data.spot_blend=.45;data.color=row['colour'];data.shadow_soft_size=.14
 ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=(row['at'][0],-row['at'][2],row['at'][1]);lights.append({'name':ob.name,'actual_source_exit':row['at'],'documentation_watts':420})
for i,at in enumerate([(-90,3.6,0),(-78,3.6,0),(-69,3.6,8),(-58,3.8,0),(-72,3.6,-8),(-65,3.8,26),(-65,3.8,-26)]):
 data=bpy.data.lights.new('DocumentationFill_'+str(i),'POINT');data.energy=1100;data.shadow_soft_size=3;data.use_shadow=False;data.color=(.92,.97,1)
 ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=(at[0],-at[2],at[1]);lights.append({'name':ob.name,'game_xyz':at,'watts':1100,'documentation_only':True})
for mat in bpy.data.materials:
 if mat.use_nodes:
  for node in mat.node_tree.nodes:
   if node.type=='TEX_IMAGE':node.interpolation='Closest'
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=32;scene.eevee.shadow_pool_size='1024'
scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
if scene.world is None:scene.world=bpy.data.worlds.new('SourceDocumentaryWorld')
scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.11,.12,.13,1);scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.12;scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.7
camera=bpy.data.cameras.new('ActualSynthesisSourceContext');ob=bpy.data.objects.new(camera.name,camera);bpy.context.collection.objects.link(ob);scene.camera=ob;camera.lens=17;images=[]
for name,at,target in [('SOURCE_SYNTHESIS_PROCESS_STREET_WIDE001.png',[-70,1.90,7.5],[-88,2.1,0]),('SOURCE_SYNTHESIS_RETAINED_BAY_CONTEXT001.png',[-57.5,1.90,1.65],[-81,2.2,0])]:
 path=W/name;assert not path.exists();ob.location=(at[0],-at[2],at[1]);t=Vector((target[0],-target[2],target[1]));ob.rotation_euler=(t-ob.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);images.append(name)
assert sha(W/p['native'])==p['native_sha256']
(W/'SOURCE_CONTEXT_PHOTO_RECEIPT001.json').write_text(json.dumps({'native_sha256':p['native_sha256'],'runtime_sha256':p['model_sha256'],'actual_retained_context_meshes':original_meshes,'actual_retained_context_triangles':original_triangles,'retained_context_method':'Exact actual-main world triangles; documentary material-role and UV mapping, no fabricated historical native','exact_original_and_proposed_floor_owners':floors,'images':images,'documentation_lights':lights,'original_mutations':0,'scope':'New real native source construction, exact retained bay triangles and explicit missing-only proposed floor. Eevee documentary fill/watts and old-context UV mapping disclosed. Not shared floor adoption, Game/CRT/hardware, plant operation, structural engineering or final-art acceptance.'},indent=2)+'\n')
