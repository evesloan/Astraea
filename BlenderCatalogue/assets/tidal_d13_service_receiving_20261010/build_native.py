from pathlib import Path
import bpy,json,hashlib,numpy as np
from mathutils import Vector
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');P=json.loads((W/'D13_RECEIVING_PLAN.json').read_text());F=R/'BlenderCatalogue/assets/group3_crew_service_20261009';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in P['source_pins'].items():assert sha(R/p)==h,p
bpy.context.preferences.filepaths.save_version=0
# Exact retained editable source; only this new derivative is saved/exported.
bpy.ops.wm.open_mainfile(filepath=str(F/'source/AST-STF-G3-003.blend'))
keep={p['name'] for p in P['retained_source_parts']}|{p['name']for p in P['fixtures']}
for o in list(bpy.data.objects):
 if o.name not in keep:bpy.data.objects.remove(o,do_unlink=True)
assert len([o for o in bpy.context.scene.objects if o.type=='MESH'])==64
mats={o.data.materials[0].name:o.data.materials[0]for o in bpy.context.scene.objects if o.type=='MESH'}
# Zinc is retained by fixture housing, white by screen walls.
def gv(p):return(p[0],-p[2],p[1])
for p in P['additive_parts']:
 x0,x1,y0,y1,z0,z1=p['aabb'];v=[gv((x,y,z))for y in[y0,y1]for z in[z0,z1]for x in[x0,x1]];fs=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
 me=bpy.data.meshes.new(p['name']);me.from_pydata(v,[],fs);me.update();o=bpy.data.objects.new(p['name'],me);bpy.context.collection.objects.link(o);me.materials.append(mats[p['role']]);o['category']=p['category'];o['role']=p['role'];o['receiving_derivative']=P['catalogue_id'];o['construction_wip']=True
 uv=me.uv_layers.new(name='MetricUV')
 for poly in me.polygons:
  axes=[i for i in range(3)if i!=max(range(3),key=lambda a:abs(poly.normal[a]))]
  for li in poly.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]]/2,q[axes[1]]/2)
for o in bpy.context.scene.objects:o['d13_only_derivative']=True
bpy.data.orphans_purge(do_recursive=True)
for image in bpy.data.images:
 if image.source=='FILE'and not image.packed_file:image.pack()
native=W/'TidalD13ServiceReceiving.blend';asset=W/'AST-RES-TIDAL_D13_service_receiving_r001.glb';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.export_scene.gltf(filepath=str(asset),export_format='GLB',export_yup=True,export_extras=True,export_cameras=False,export_lights=False)
nh=sha(native);ah=sha(asset);bpy.ops.wm.open_mainfile(filepath=str(native));assert len([o for o in bpy.context.scene.objects if o.type=='MESH'])==73
repeat=W/'_repeat_receiving.glb';bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_extras=True,export_cameras=False,export_lights=False);assert sha(repeat)==ah;repeat.unlink()
rec={'blender_version':bpy.app.version_string,'derivative_native':native.name,'derivative_native_sha256':nh,'derivative_export':asset.name,'derivative_export_sha256':ah,'retained_editable_parts':64,'additive_parts':9,'editable_meshes':73,'retained_fixture_markers':7,'repeat_export_byte_identical':True}
# Small two-mesh patch of original Tidal guard/glass; earlier specialty patches do not target these names.
bpy.ops.wm.read_factory_settings(use_empty=True);src=R/'Game/assets/models/AST-RES-TIDAL_lift_fit_r003.glb';bpy.ops.import_scene.gltf(filepath=str(src));keep=[];changed=[];unaffected={}
def side(poly,ax,value,less):
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
  outside=side(rem,ax,lo[ax],True)if rem else[]
  if len(outside)>=3:pieces.append(outside)
  rem=side(rem,ax,lo[ax],False)if rem else[]
  outside=side(rem,ax,hi[ax],False)if rem else[]
  if len(outside)>=3:pieces.append(outside)
  rem=side(rem,ax,hi[ax],True)if rem else[]
 area=sum((Vector(rem[i][:3])-Vector(rem[0][:3])).cross(Vector(rem[i+1][:3])-Vector(rem[0][:3])).length/2 for i in range(1,len(rem)-1))if len(rem)>=3 else 0
 return pieces,area>1e-9
for ob in list(bpy.context.scene.objects):
 if ob.name not in P['named_guard_replacement_map']:continue
 assert ob.type=='MESH'and ob.get('category')in['guard','public_glass'];me=ob.data;me.calc_loop_triangles();uv=me.uv_layers.active;vs=[];fs=[];matis=[];uvs=[];affected=0;uncut=0;before=len(me.loop_triangles)
 for tri in me.loop_triangles:
  poly=[]
  for vi,li in zip(tri.vertices,tri.loops):
   v=ob.matrix_world@me.vertices[vi].co;tc=uv.data[li].uv if uv else(0,0);poly.append((v.x,v.z,-v.y,tc[0],tc[1]))
  pieces=[poly];hit=False
  for cut in P['guard_cut_boxes']:
   nxt=[]
   for pp in pieces:q,b=minus(pp,cut);nxt.extend(q);hit|=b
   pieces=nxt
  if hit:affected+=1
  else:uncut+=1
  for pp in pieces:
   for i in range(1,len(pp)-1):
    q=[pp[0],pp[i],pp[i+1]]
    if(Vector(q[1][:3])-Vector(q[0][:3])).cross(Vector(q[2][:3])-Vector(q[0][:3])).length<1e-9:continue
    k=len(vs);vs.extend([gv(v)for v in q]);uvs.extend([v[3:]for v in q]);fs.append((k,k+1,k+2));matis.append(tri.material_index)
 nm=bpy.data.meshes.new(ob.name+'_D13_ServiceDoorOpenings');nm.from_pydata(vs,[],fs);nm.update()
 for mat in me.materials:nm.materials.append(mat)
 lay=nm.uv_layers.new(name='RetainedInterpolatedUV')
 for face,mi in zip(nm.polygons,matis):
  face.material_index=mi
  for li in face.loop_indices:lay.data[li].uv=uvs[nm.loops[li].vertex_index]
 ob.data=nm;ob.matrix_world.identity();ob['receiving_derivative']=P['catalogue_id'];ob['original_export_sha256']=sha(src);keep.append(ob);changed.append({'batch':ob.name,'triangles_before':before,'triangles_after':len(fs),'original_triangles_affected':affected,'unaffected_original_triangles_retained':uncut})
assert len(keep)==2 and all(x['original_triangles_affected']for x in changed)
for ob in list(bpy.data.objects):
 if ob not in keep:bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.orphans_purge(do_recursive=True)
for image in bpy.data.images:
 if image.source=='FILE'and not image.packed_file:image.pack()
patchnative=W/'TidalD13ServiceGuardPatch.blend';patch=W/'TidalD13ServiceGuardPatch.glb';bpy.ops.wm.save_as_mainfile(filepath=str(patchnative),compress=True);bpy.ops.export_scene.gltf(filepath=str(patch),export_format='GLB',export_yup=True,export_extras=True)
pnh=sha(patchnative);pah=sha(patch);bpy.ops.wm.open_mainfile(filepath=str(patchnative));repeat=W/'_repeat_guard.glb';bpy.ops.export_scene.gltf(filepath=str(repeat),export_format='GLB',export_yup=True,export_extras=True);assert sha(repeat)==pah;repeat.unlink();assert sha(patchnative)==pnh and sha(native)==nh
rec.update({'guard_patch_native':patchnative.name,'guard_patch_native_sha256':pnh,'guard_patch_export':patch.name,'guard_patch_export_sha256':pah,'guard_repeat_export_byte_identical':True,'named_guard_replacements':changed,'source_originals_unchanged':all(sha(R/p)==h for p,h in P['source_pins'].items())})
(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps(rec,indent=2)+'\n');print('D13_NATIVE_EXPORT_PASS',json.dumps(rec),flush=True)
