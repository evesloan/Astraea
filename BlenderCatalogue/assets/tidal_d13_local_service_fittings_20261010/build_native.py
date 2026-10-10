from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.loads((W/'FITTINGS_PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1])
bpy.ops.wm.read_factory_settings(use_empty=True)
counts=[]
for item in P['assemblies']:
 a=next(a for a in P['sources']if a['catalogue_id']==item['catalogue_id']);path=R/'BlenderCatalogue'/a['source'];assert sha(path)==a['source_sha256']
 with bpy.data.libraries.load(str(path),link=False)as(src,dst):dst.objects=src.objects
 obs=[o for o in dst.objects if o is not None];root=bpy.data.objects.new(item['name'],None);bpy.context.collection.objects.link(root)
 for o in obs:
  bpy.context.collection.objects.link(o)
 for o in obs:
  if o.parent not in obs:o.parent=root
  o.name=item['name']+'__'+o.name
 root.location=B(item['position']);root.rotation_euler.z=item['yaw'];root['persistent_id']=item['persistent_id'];root['operation_hold']=P['operations'];bpy.context.view_layer.update()
 meshes=[o for o in obs if o.type=='MESH'];coords=[o.matrix_world@Vector(c)for o in meshes for c in o.bound_box]
 counts.append({'name':item['name'],'source_id':item['catalogue_id'],'meshes':len(meshes),'bounds_blender':[[min(v[i]for v in coords)for i in range(3)],[max(v[i]for v in coords)for i in range(3)]]})
# Empty dead-end parking, shaped low bumper returns; no floor, vehicle or stock instances.
rubber=bpy.data.materials.new('D13_ParkingRubber');rubber.diffuse_color=(.055,.065,.07,1);rubber.use_nodes=True;bs=rubber.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=rubber.diffuse_color;bs.inputs['Roughness'].default_value=.88
for name,lo,hi in [('D13_ParkingWestBumper',[-61.76,84,-486.2],[-61.7,84.16,-484.5]),('D13_ParkingEastBumper',[-60.3,84,-486.2],[-60.24,84.16,-484.5]),('D13_ParkingEndStop',[-61.76,84,-484.5],[-60.24,84.16,-484.44])]:
 bpy.ops.mesh.primitive_cube_add(size=1,location=B([(lo[i]+hi[i])/2 for i in range(3)]));o=bpy.context.object;o.name=name;o.dimensions=(hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(rubber);o['role']='empty_parking_bumper'
# Physical raised-letter labels face the approach west. Their shallow faces are still collision geometry.
mat=bpy.data.materials.new('D13_LabelIvory');mat.diffuse_color=(.78,.79,.72,1)
for name,text,p in [('CleanProduct','CLEAN SUPPLY',[-60.06,85.28,-493]),('CleanLinen','DRY LINEN',[-60.04,85.98,-490]),('Returns','CLOSED RETURNS',[-60.06,85.28,-487])]:
 bpy.ops.object.text_add(location=B(p));o=bpy.context.object;o.name='D13_PhysicalLabel_'+name;o.data.body=text;o.data.size=.1;o.data.align_x='CENTER';o.data.extrude=.001;o.rotation_euler=(math.pi/2,0,-math.pi/2);o.data.materials.append(mat);bpy.ops.object.convert(target='MESH')
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('SourceWorld');scene.world.color=(.06,.07,.08)
# Pack retained images into portable editable derivative.
bpy.ops.file.pack_all();native=W/'TidalD13LocalServiceFittings.blend';out=W/P['model_file'];bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_extras=True,export_yup=True,export_apply=True)
first=sha(out);bpy.ops.wm.open_mainfile(filepath=str(native));bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_extras=True,export_yup=True,export_apply=True);assert sha(out)==first
receipt={'status':'PASS','source_blender_version':bpy.app.version_string,'native':native.name,'native_sha256':sha(native),'export':out.name,'export_sha256':sha(out),'fresh_native_repeat_identical':True,'assemblies':counts,'new_bumpers':3,'physical_labels':3,'mesh_count':sum(o.type=='MESH'for o in bpy.data.objects),'no_cart_created':True,'no_floor_created':True,'all_sources_unchanged':True}
for a in P['sources']:
 assert sha(R/'BlenderCatalogue'/a['source'])==a['source_sha256'];assert sha(R/'BlenderCatalogue'/a['export'])==a['export_sha256']
(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n');P.update(model_sha256=receipt['export_sha256'],mesh_count=receipt['mesh_count']);(R/'Game/data/architecture/TIDAL_D13_LOCAL_SERVICE_FITTINGS.json').write_text(json.dumps(P,indent=2)+'\n')
import shutil
shutil.copy2(out,R/'Game/assets/models'/P['model_file']);print('PASS: source-derived local fittings',receipt['mesh_count'])
