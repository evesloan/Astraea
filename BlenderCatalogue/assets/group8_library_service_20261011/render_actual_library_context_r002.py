"""Actual exact retained Library plus new sources; documentary fill, no Game equivalence."""
from pathlib import Path
import bpy,json,math,hashlib,sys
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];p=json.load(open(W/'PLAN.json'));rec=json.load(open(W/'EXACT_RETAINED_LIBRARY_RECOVERY.json'));original=Path(rec['exact_native'])
assert hashlib.sha256(original.read_bytes()).hexdigest()==rec['exact_native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(W/p['native']))
with bpy.data.libraries.load(str(original),link=False)as(src,dst):dst.objects=src.objects
for ob in dst.objects:
 if ob:bpy.context.collection.objects.link(ob)
bpy.context.view_layer.update();poses={ob:ob.matrix_world.copy()for ob in dst.objects if ob};world=Matrix.Translation((8,466,78))
for ob,pose in poses.items():
 ob.parent=None;ob.matrix_world=world@pose
 if ob.name=='SOURCE_PREVIEW_ONLY_floor':bpy.data.objects.remove(ob,do_unlink=True)
# Exact sole receiving floor and connector; never use the omitted source preview.
sys.path.insert(0,str(R/'BlenderCatalogue/standards'));import materials
mats=materials.materials();definition=json.load(open(R/'Game/data/architecture/REMAINING_BATCH_FLOORS.json'));floors=[]
for row in definition['regions']:
 if not row['id'].startswith('D12_directory_02_'):continue
 floors.append(row['id']);verts=[];faces=[];roles=[];y=row['floor_y'];th=row['thickness']
 for tri in [tri for chunk in row['render_chunks']for tri in chunk['triangles']]:
  for yy,reverse,role in [(y,False,0),(y-th,True,1)]:
   start=len(verts);verts.extend((q[0],-q[1],yy)for q in tri);indices=list(range(start,start+3));normal=(Vector(verts[start+1])-Vector(verts[start])).cross(Vector(verts[start+2])-Vector(verts[start])).z
   if (normal>0)==reverse:indices.reverse()
   faces.append(tuple(indices));roles.append(role)
 for ring in row['rings']:
  for a,b in zip(ring,ring[1:]+ring[:1]):
   start=len(verts);verts.extend([(a[0],-a[1],y),(b[0],-b[1],y),(b[0],-b[1],y-th),(a[0],-a[1],y-th)]);faces.append(tuple(range(start,start+4)));roles.append(1)
 me=bpy.data.meshes.new(row['id']);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('ExactOriginalFloor_'+row['id'],me);bpy.context.collection.objects.link(o);me.materials.append(mats['warm_stone']);me.materials.append(mats['ivory_enamel']);uv=me.uv_layers.new(name='ExactOriginalRuntimeUV')
 for face,role in zip(me.polygons,roles):
  face.material_index=role
  for li in face.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.x*.3,-q.y*.3)if abs(face.normal.z)>.9 else((q.x-q.y)*.3,q.z*.3)
for mat in bpy.data.materials:
 if mat.use_nodes:
  for node in mat.node_tree.nodes:
   if node.type=='TEX_IMAGE':node.interpolation='Closest'
for ob in bpy.context.scene.objects:
 if ob.type=='MESH'and any(t in ob.name.lower()for t in ['lens','opal']):ob.visible_shadow=False
lights=[]
for row in p['lights']:
 data=bpy.data.lights.new('ActualNewFixture_'+row['name'],'SPOT');data.energy=140;data.color=row['colour'];data.spot_size=math.radians(120);data.spot_blend=.5;data.shadow_soft_size=.12
 o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=(row['at'][0],-row['at'][2],row['at'][1]);lights.append({'name':o.name,'blender_position':list(o.location),'source_only_watts':140,'actual_native_exit':True})
for name,at,power in [('Public',(46,448.0,80.5),500),('Care',(46.5,458.5,80.7),550),('Conservation',(41.8,459.0,80.8),180),('UpperInspection',(46.2,457.0,82.25),180)]:
 data=bpy.data.lights.new('DocumentationFill_'+name,'POINT');data.energy=power;data.color=(.98,.99,1);data.shadow_soft_size=2;data.use_shadow=False
 o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=at;lights.append({'name':o.name,'blender_position':list(at),'watts':power,'documentation_only':True})
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=32;scene.eevee.shadow_pool_size='4096';scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
if scene.world is None:scene.world=bpy.data.worlds.new('DocumentaryReviewWorld')
scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.08,.09,.11,1);scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.08;scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.3
camera=bpy.data.cameras.new('ActualSourceReviewCamera');o=bpy.data.objects.new(camera.name,camera);bpy.context.collection.objects.link(o);scene.camera=o;images=[]
def photo(name,at,target,lens):
 path=W/name;assert not path.exists(),'Preserve earlier source views';camera.lens=lens;o.location=(at[0],-at[2],at[1]);t=Vector((target[0],-target[2],target[1]));o.rotation_euler=(t-o.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);images.append(name)
photo('SOURCE_LIBRARY_PUBLIC_RETURNS_WIDE002.png',[44.0,79.75,-449.2],[48.1,79.4,-450.0],20)
photo('SOURCE_LIBRARY_CARE_CONSERVATION_WIDE002.png',[46.4,79.75,-452.7],[45.6,79.5,-461.4],20)
photo('SOURCE_LIBRARY_CEILING_TIES_WIDE002.png',[44.8,82.5,-448.7],[46.4,82.1,-459.2],22)
assert hashlib.sha256(original.read_bytes()).hexdigest()==rec['exact_native_sha256']and hashlib.sha256((W/p['native']).read_bytes()).hexdigest()==p['native_sha256']
(W/'SOURCE_CONTEXT_PHOTO_RECEIPT002.json').write_text(json.dumps({'original_native':str(original),'original_native_sha256':rec['exact_native_sha256'],'candidate_native':p['native'],'candidate_native_sha256':p['native_sha256'],'exact_original_floor_owners':floors,'omitted_only_original_nonruntime_preview_floor':'SOURCE_PREVIEW_ONLY_floor','images':images,'renderer':'Blender Eevee source documentation; Godot Compatibility unchanged','additional_source_review_lights':lights,'source_geometry_or_native_file_mutations':0,'limits':['Additional fill and source-review watts/exposure are documentary,not Godot radiometric/CRT acceptance','All actual retained architecture/materials included; no fabricated facade or cutaway','No Game/final-art/structural-capacity/clinical/stock/cart/species acceptance from these views']},indent=2)+'\n')
