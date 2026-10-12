from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2]
p=json.load(open(W/'PLAN.json'));recovery=json.load(open(W/'EXACT_RETAINED_DINING_FIXTURE_RECOVERY.json'))
selection=json.load(open(W/'SOURCE_CONTEXT_FLOOR_SELECTION.json'));receipts=[]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for record in p['rooms']:
 key=record['programme_key'];original=Path(next(r['native']for r in recovery['families']if r['programme_key']==key))
 assert sha(original)==record['native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(original));original_objects=len(bpy.context.scene.objects)
 floor_ids=[]
 for file,chosen in selection.items():
  assert sha(R/file)==chosen['sha256']
  for row in json.load(open(R/file))['regions']:
   if row['id']not in chosen['exact_region_ids']or not row['id'].startswith(key+'_'):continue
   floor_ids.append(row['id']);verts=[];faces=[];y=row['floor_y'];th=row['thickness']
   for tri in [tri for chunk in row['render_chunks']for tri in chunk['triangles']]:
    for yy,reverse in[(y,False),(y-th,True)]:
     start=len(verts);verts.extend((q[0],-q[1],yy)for q in tri);ids=list(range(start,start+3))
     normal=(Vector(verts[start+1])-Vector(verts[start])).cross(Vector(verts[start+2])-Vector(verts[start])).z
     if(normal>0)==reverse:ids.reverse()
     faces.append(tuple(ids))
   for ring in row['rings']:
    for a,b in zip(ring,ring[1:]+ring[:1]):
     start=len(verts);verts.extend([(a[0],-a[1],y),(b[0],-b[1],y),(b[0],-b[1],y-th),(a[0],-a[1],y-th)])
     faces.append(tuple(range(start,start+4)))
   me=bpy.data.meshes.new(row['id']);me.from_pydata(verts,[],faces);me.update()
   ob=bpy.data.objects.new('ExactCompilerFloor_'+row['id'],me);bpy.context.collection.objects.link(ob)
   mat=bpy.data.materials.new('DocumentaryExactFloorWarmStone');mat.diffuse_color=(.58,.54,.46,1);mat.use_nodes=True
   mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=mat.diffuse_color;mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.78;me.materials.append(mat)
 actual_lights=[]
 for row in record['lights']:
  data=bpy.data.lights.new('ActualHousing_'+row['name'],'SPOT');data.energy=row['original_documentary_power_watts'];data.spot_size=math.radians(row['angle']*2);data.spot_blend=.5;data.color=row['colour'];data.shadow_soft_size=.16
  ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=(row['at'][0],-row['at'][2],row['at'][1]);actual_lights.append({'name':ob.name,'actual_source_exit':row['at'],'documentation_watts':data.energy})
 fills=[(62,64,0),(78,64,0),(92,64,0)]if key.endswith('06')else[(17,64,432),(32,64,438),(46,64,432)]
 for i,at in enumerate(fills):
  data=bpy.data.lights.new('DocumentationFill_'+str(i),'POINT');data.energy=950;data.shadow_soft_size=3;data.use_shadow=False;data.color=(1,.96,.88)
  ob=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(ob);ob.location=(at[0],-at[2],at[1])
 for mat in bpy.data.materials:
  if mat.use_nodes:
   for node in mat.node_tree.nodes:
    if node.type=='TEX_IMAGE':node.interpolation='Closest'
 scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=32;scene.eevee.shadow_pool_size='1024'
 scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 if scene.world is None:scene.world=bpy.data.worlds.new('SourceDocumentaryWorld')
 scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.11,.10,.08,1);scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.15
 scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.8
 camera=bpy.data.cameras.new('ActualDiningSourceContext');ob=bpy.data.objects.new(camera.name,camera);bpy.context.collection.objects.link(ob);scene.camera=ob;camera.lens=18
 at,target=((54.5,62.85,-1.3),(86,63.1,0))if key.endswith('06')else((11,62.85,432),(32,63.1,432))
 ob.location=(at[0],-at[2],at[1]);t=Vector((target[0],-target[2],target[1]));ob.rotation_euler=(t-ob.location).to_track_quat('-Z','Y').to_euler()
 name='SOURCE_'+('MINERAL_BROTH_HALL'if key.endswith('06')else'OBSERVATION_CAFE')+'_WIDE001.png';path=W/name;assert not path.exists();scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 assert sha(original)==record['native_sha256']
 receipts.append({'programme_key':key,'exact_native_sha256':record['native_sha256'],'original_objects':original_objects,'exact_compiler_floor_owners':floor_ids,'image':name,'actual_positioned_sources':actual_lights,'documentation_fill_game_xyz':fills,'documentation_fill_watts_each':950,'original_mutations':0})
(W/'SOURCE_CONTEXT_PHOTO_RECEIPT001.json').write_text(json.dumps({'rooms':receipts,'scope':'Actual retained native sources and exact current compiler floors. Original textures, no concept geometry. Documentary Eevee fill/watts/floor color, not Game/CRT/hardware/food operation/hull vista/structural/final-art acceptance.'},indent=2)+'\n')
