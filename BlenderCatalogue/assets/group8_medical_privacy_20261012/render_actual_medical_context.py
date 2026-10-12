"""Photograph exact retained source and new fittings; source documentary lighting only."""
from pathlib import Path
import bpy,json,hashlib,sys,math
from mathutils import Matrix,Vector
W=Path(__file__).resolve().parent;R=W.parents[2];p=json.load(open(W/'PLAN.json'));rec=json.load(open(W/'EXACT_RETAINED_SOURCE_RECOVERY.json'));original=Path(rec['native']);sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(original)==p['original_native_sha256'];bpy.ops.wm.open_mainfile(filepath=str(W/p['native']))
with bpy.data.libraries.load(str(original),link=False)as(src,dst):dst.objects=src.objects
for ob in dst.objects:
 if ob:bpy.context.collection.objects.link(ob)
bpy.context.view_layer.update();poses={ob:ob.matrix_world.copy()for ob in dst.objects if ob};root=Matrix.Translation((-28,446,21))
for ob,pose in poses.items():ob.parent=None;ob.matrix_world=root@pose
sys.path.insert(0,str(R/'BlenderCatalogue/standards'));import materials
mats=materials.materials();definition=json.load(open(R/'Game/data/generated/structural_meshes.json'));floors=[]
for row in definition['regions']:
 if row['id']not in['D05_forward_waiting_support_floor','D05_connected_triage_wing_floor']:continue
 floors.append(row['id']);verts=[];faces=[];roles=[];y=row['floor_y'];th=row['thickness']
 for tri in [tri for chunk in row['render_chunks']for tri in chunk['triangles']]:
  for yy,reverse,role in[(y,False,0),(y-th,True,1)]:
   start=len(verts);verts.extend((q[0],-q[1],yy)for q in tri);indices=list(range(start,start+3));normal=(Vector(verts[start+1])-Vector(verts[start])).cross(Vector(verts[start+2])-Vector(verts[start])).z
   if(normal>0)==reverse:indices.reverse()
   faces.append(tuple(indices));roles.append(role)
 for ring in row['rings']:
  for a,b in zip(ring,ring[1:]+ring[:1]):
   start=len(verts);verts.extend([(a[0],-a[1],y),(b[0],-b[1],y),(b[0],-b[1],y-th),(a[0],-a[1],y-th)]);faces.append(tuple(range(start,start+4)));roles.append(1)
 me=bpy.data.meshes.new(row['id']);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('ExactOriginalFloor_'+row['id'],me);bpy.context.collection.objects.link(o);me.materials.append(mats['warm_stone']);me.materials.append(mats['ivory_enamel']);uv=me.uv_layers.new(name='ExactOriginalRuntimeUV')
 for face,role in zip(me.polygons,roles):
  face.material_index=role
  for li in face.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q.x*.3,-q.y*.3)if abs(face.normal.z)>.9 else((q.x-q.y)*.3,q.z*.3)
assert len(floors)==2
for mat in bpy.data.materials:
 if mat.use_nodes:
  for n in mat.node_tree.nodes:
   if n.type=='TEX_IMAGE':n.interpolation='Closest'
lights=[]
for i,x in enumerate([-14,-21,-28,-35,-40]):
 data=bpy.data.lights.new('DocumentationFill_CrossStreet%02d'%i,'POINT');data.energy=400;data.color=(.99,.99,1);data.shadow_soft_size=2;data.use_shadow=False
 o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=(x,458,23.6);lights.append({'name':o.name,'world_xyz':[x,23.6,-458],'watts':400,'documentation_only':True})
for number,row in enumerate(p['doors']):
 at=Vector(row['at']);rot=Matrix.Rotation(row['yaw'],4,'Y');where=at+rot.to_3x3()@Vector((0,2.6,-3.5))
 data=bpy.data.lights.new('DocumentationFill_Pod%02d'%(number+1),'POINT');data.energy=240;data.shadow_soft_size=1.5;data.use_shadow=False;data.color=(.97,.99,1)
 o=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(o);o.location=(where.x,-where.z,where.y);lights.append({'name':o.name,'world_xyz':list(where),'watts':240,'documentation_only':True})
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=32;scene.eevee.shadow_pool_size='1024';scene.render.resolution_x=1600;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
if scene.world is None:scene.world=bpy.data.worlds.new('DocumentaryWorld')
scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.08,.09,.11,1);scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.08;scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.35
camera=bpy.data.cameras.new('ActualSourceReviewCamera');o=bpy.data.objects.new(camera.name,camera);bpy.context.collection.objects.link(o);scene.camera=o;images=[]
def photo(name,at,target,lens):
 path=W/name;assert not path.exists();camera.lens=lens;o.location=(at[0],-at[2],at[1]);t=Vector((target[0],-target[2],target[1]));o.rotation_euler=(t-o.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);images.append(name)
photo('SOURCE_MEDICAL_CLINICAL_STREET_WIDE001.png',[-12.7,22.65,-458],[-38,22.35,-458],23)
photo('SOURCE_MEDICAL_POD_PRIVACY_WIDE001.png',[-15.45,22.65,-463.25],[-18,22.2,-460],20)
assert sha(original)==p['original_native_sha256']and sha(W/p['native'])==p['native_sha256']
(W/'SOURCE_CONTEXT_PHOTO_RECEIPT001.json').write_text(json.dumps({'exact_original_native_sha256':p['original_native_sha256'],'new_native_sha256':p['native_sha256'],'exact_compiler_floors':floors,'original_source_objects':len(poses),'images':images,'documentary_lights':lights,'source_mutations':0,'scope':'Actual retained native source and new source fittings; original source-open state,not Game motion screenshot. Eevee documentary fill,not Godot/CRT/target-hardware/final-art or clinical operation acceptance.'},indent=2)+'\n')
