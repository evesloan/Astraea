from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');P=json.load(open(W/'D14_SHARED_RECEIVER_PLAN.json'));F=R/'BlenderCatalogue/assets/group3_crew_service_20261009';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();gv=lambda p:(p[0],-p[2],p[1])
for p,h in P['source_pins'].items():assert sha(R/p)==h,p
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.open_mainfile(filepath=str(F/'source/AST-STF-G3-003.blend'))
fixture_names=['TidalStaffLightHousing_D14_3','TidalStaffLightDiffuser_D14_3'];mats={o.data.materials[0].name:o.data.materials[0]for o in bpy.context.scene.objects if o.type=='MESH'}
for o in list(bpy.data.objects):
 if o.name not in fixture_names:bpy.data.objects.remove(o,do_unlink=True)
for o in bpy.context.scene.objects:
 o.name='D14SharedReceiver'+('LightHousing' if 'Housing' in o.name else'LightDiffuser');o.location+=Vector(gv((1,0,4)));o['retained_fixture_source']='TidalStaffLight_D14_3';o['d14_receiver_proposal']=True
floor_mat=bpy.data.materials.new('staff_floor');floor_mat.use_nodes=True;n=floor_mat.node_tree.nodes.get('Principled BSDF');n.inputs['Roughness'].default_value=.83;tex=floor_mat.node_tree.nodes.new('ShaderNodeTexImage');tex.interpolation='Closest';tex.image=bpy.data.images.load(str(R/'Game/assets/textures/staff_floor.png'));floor_mat.node_tree.links.new(tex.outputs['Color'],n.inputs['Base Color']);mats['staff_floor']=floor_mat
fs6=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
def mesh(n,vs,fs,role,cat):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);me.materials.append(mats[role]);o['category']=cat;o['role']=role;o['receiving_proposal_id']=P['catalogue_id'];o['construction_wip']=True;o['runtime_collision']=True
 uv=me.uv_layers.new(name='MetricUV')
 for poly in me.polygons:
  axes=[i for i in range(3)if i!=max(range(3),key=lambda a:abs(poly.normal[a]))]
  for li in poly.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*.3,v[axes[1]]*.3)
 return o
for p in P['new_parts']:
 x0,x1,y0,y1,z0,z1=p['aabb'];mesh(p['name'],[gv((x,y,z))for y in[y0,y1]for z in[z0,z1]for x in[x0,x1]],fs6,p['role'],p['category'])
f=P['missing_only_floor'];vs=[];fs=[]
for tri in f['triangles']:
 cross=(tri[1][0]-tri[0][0])*(tri[2][1]-tri[0][1])-(tri[1][1]-tri[0][1])*(tri[2][0]-tri[0][0]);top_reverse=cross>0
 for y,rev in [(88.26,not top_reverse),(88.5,top_reverse)]:
  k=len(vs);vs.extend(gv((x,y,z))for x,z in tri);fs.append(tuple(k+i for i in([2,1,0]if rev else[0,1,2])))
for ring in f['rings']:
 for a,b in zip(ring,ring[1:]+ring[:1]):
  k=len(vs);vs.extend([gv((a[0],88.26,a[1])),gv((b[0],88.26,b[1])),gv((b[0],88.5,b[1])),gv((a[0],88.5,a[1]))]);fs.append((k,k+1,k+2,k+3))
mesh('D14_SharedReceiverMissingFloor',vs,fs,'staff_floor','missing_only_floor')
for name,pos in [('DATUM_D14SharedReceiverDoor',P['door_binding']['position']),('DATUM_D14SharedReceiverLight',P['fixture']['position'])]:
 o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.location=gv(pos);o.empty_display_type='PLAIN_AXES';o['held_source_only']=True
bpy.data.orphans_purge(do_recursive=True)
for im in bpy.data.images:
 if im.source=='FILE'and not im.packed_file:im.pack()
native=W/'TidalD14SharedReceiver.blend';asset=W/'AST-RES-TIDAL_D14_shared_receiver_r001.glb';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.export_scene.gltf(filepath=str(asset),export_format='GLB',export_yup=True,export_extras=True,export_cameras=False,export_lights=False);ah=sha(asset);nh=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native));repeat=W/'_repeat.glb';bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_extras=True,export_cameras=False,export_lights=False);assert sha(repeat)==ah;repeat.unlink();count=sum(o.type=='MESH'for o in bpy.context.scene.objects);assert count==22
# Read two exact native Group3 walls and only the retained street endguard. Save a bounded successor, never modify originals.
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(F/'exports/AST-STF-G3-003.glb'));keepnames={p['mesh']for p in P['named_source_replacements']if p['source_family']=='group3'}
bpy.context.view_layer.update();first_worlds={o.name:o.matrix_world.copy()for o in bpy.context.scene.objects if o.name in keepnames}
for o in list(bpy.data.objects):
 if o.name not in keepnames:bpy.data.objects.remove(o,do_unlink=True)
for o in bpy.context.scene.objects:o.parent=None;o.matrix_world=first_worlds[o.name]
street=json.load(open(R/'Game/data/architecture/TIDAL_AQUATIC_DOUBLE.json'));bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models'/street['street_model']))
keepnames.add('D14_SouthStreetEndGuard');bpy.context.view_layer.update();worlds={o.name:o.matrix_world.copy()for o in bpy.context.scene.objects if o.name in keepnames}
for o in list(bpy.data.objects):
 if o.name not in keepnames:bpy.data.objects.remove(o,do_unlink=True)
for o in list(bpy.context.scene.objects):
 o.parent=None;o.matrix_world=worlds[o.name]
# Preserve exact original triangles and interpolated UVs outside each declared cut.
def clip(poly,ax,value,less):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[ax]<=value if less else a[ax]>=value;ib=b[ax]<=value if less else b[ax]>=value
  if ia:out.append(a)
  if ia!=ib:
   t=(value-a[ax])/(b[ax]-a[ax]);out.append(tuple(a[j]+(b[j]-a[j])*t for j in range(5)))
 return out
def minus(poly,cut):
 lo=cut['min'];hi=cut['max']
 if any(max(v[a]for v in poly)<lo[a]-1e-7 or min(v[a]for v in poly)>hi[a]+1e-7 for a in range(3)):return[poly],False
 rem=poly;pieces=[]
 for ax in range(3):
  outside=clip(rem,ax,lo[ax],True)if rem else[]
  if len(outside)>=3:pieces.append(outside)
  rem=clip(rem,ax,lo[ax],False)if rem else[]
  outside=clip(rem,ax,hi[ax],False)if rem else[]
  if len(outside)>=3:pieces.append(outside)
  rem=clip(rem,ax,hi[ax],True)if rem else[]
 area=sum((Vector(rem[i][:3])-Vector(rem[0][:3])).cross(Vector(rem[i+1][:3])-Vector(rem[0][:3])).length/2 for i in range(1,len(rem)-1))if len(rem)>=3 else 0
 return pieces,area>1e-9
changed=[]
for spec in P['named_source_replacements']:
 o=bpy.data.objects[spec['mesh']];old=o.data;old.calc_loop_triangles();uv=old.uv_layers.active;vs=[];fs=[];uvs=[];mis=[];affected=0;uncut=0
 for tri in old.loop_triangles:
  poly=[]
  for vi,li in zip(tri.vertices,tri.loops):
   v=o.matrix_world@old.vertices[vi].co;tc=uv.data[li].uv if uv else(0,0);poly.append((v.x,v.z,-v.y,tc[0],tc[1]))
  pieces,hit=minus(poly,spec['cut']);affected+=int(hit);uncut+=int(not hit)
  for pp in pieces:
   for i in range(1,len(pp)-1):
    q=[pp[0],pp[i],pp[i+1]]
    if(Vector(q[1][:3])-Vector(q[0][:3])).cross(Vector(q[2][:3])-Vector(q[0][:3])).length<1e-9:continue
    k=len(vs);vs.extend(gv(v)for v in q);uvs.extend(v[3:]for v in q);fs.append((k,k+1,k+2));mis.append(tri.material_index)
 me=bpy.data.meshes.new(spec['mesh']+'_D14_SharedReceiverOpening');me.from_pydata(vs,[],fs);me.update()
 for m in old.materials:me.materials.append(m)
 lay=me.uv_layers.new(name='RetainedInterpolatedUV')
 for p,mi in zip(me.polygons,mis):
  p.material_index=mi
  for li in p.loop_indices:lay.data[li].uv=uvs[me.loops[li].vertex_index]
 o.data=me;o.matrix_world.identity();o['receiving_proposal_id']=P['catalogue_id'];o['replacement_of']=spec['mesh'];changed.append({'mesh':spec['mesh'],'source_family':spec['source_family'],'triangles_before':len(old.loop_triangles),'triangles_after':len(fs),'original_affected_triangles':affected,'unaffected_original_triangles_retained':uncut});assert affected>0
bpy.data.orphans_purge(do_recursive=True)
for im in bpy.data.images:
 if im.source=='FILE'and not im.packed_file:im.pack()
pn=W/'TidalD14ReceiverNamedPatch.blend';pa=W/'TidalD14ReceiverNamedPatch.glb';bpy.ops.wm.save_as_mainfile(filepath=str(pn),compress=True);bpy.ops.export_scene.gltf(filepath=str(pa),export_format='GLB',export_yup=True,export_extras=True);ph=sha(pa);pnh=sha(pn);bpy.ops.wm.open_mainfile(filepath=str(pn));repeat=W/'_repeat_patch.glb';bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_extras=True);assert sha(repeat)==ph;repeat.unlink()
assert all(sha(R/p)==h for p,h in P['source_pins'].items());assert sha(native)==nh and sha(pn)==pnh
receipt={'schema':1,'blender_version':bpy.app.version_string,'receiving_native':native.name,'receiving_native_sha256':nh,'receiving_export':asset.name,'receiving_export_sha256':ah,'receiving_editable_meshes':count,'named_patch_native':pn.name,'named_patch_native_sha256':pnh,'named_patch_export':pa.name,'named_patch_export_sha256':ph,'named_patch_meshes':3,'named_replacements':changed,'repeat_exports_byte_identical':True,'unchanged_source_pins_verified':True,'uninstalled_source_only':True}
(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n');print('D14_RECEIVING_NATIVE_PASS',json.dumps(receipt),flush=True)
