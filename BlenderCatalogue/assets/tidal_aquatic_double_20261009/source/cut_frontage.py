from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
O=Path(__file__).resolve().parents[1];R=O.parents[2];P=O/'BATCH_PLAN.json';d=json.load(open(P));src=R/'Game/assets/models/AST-RES-TIDAL_lift_fit_r003.glb';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert h(src)==d['source_house_sha256']
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(src))
cuts=d['entry_cuts_including_retained_102'];changed=[];keep=[]
def side(poly,ax,v,less):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[ax]<=v if less else a[ax]>=v;ib=b[ax]<=v if less else b[ax]>=v
  if ia:out.append(a)
  if ia!=ib:
   t=(v-a[ax])/(b[ax]-a[ax]);out.append(tuple(a[j]+(b[j]-a[j])*t for j in range(5)))
 return out
for ob in list(bpy.context.scene.objects):
 if ob.type!='MESH' or ob.get('category')not in ['guard','public_glass']:continue
 me=ob.data;me.calc_loop_triangles();uv=me.uv_layers.active;vs=[];fs=[];mats=[];uvs=[];removed=0;before=len(me.loop_triangles)
 for tr in me.loop_triangles:
  poly=[]
  for vi,li in zip(tr.vertices,tr.loops):
   v=ob.matrix_world@me.vertices[vi].co;tc=uv.data[li].uv if uv else (0,0);poly.append((v.x,v.z,-v.y,tc[0],tc[1]))
  pieces=[poly]
  for cut in cuts:
   lo=cut['min'];hi=cut['max'];next_pieces=[]
   for pp in pieces:
    if any(max(v[a]for v in pp)<lo[a]-1e-7 or min(v[a]for v in pp)>hi[a]+1e-7 for a in range(3)):next_pieces.append(pp);continue
    rem=pp
    for ax in range(3):
     outside=side(rem,ax,lo[ax],True)if rem else[]
     if len(outside)>=3:next_pieces.append(outside)
     rem=side(rem,ax,lo[ax],False)if rem else[]
     outside=side(rem,ax,hi[ax],False)if rem else[]
     if len(outside)>=3:next_pieces.append(outside)
     rem=side(rem,ax,hi[ax],True)if rem else[]
    if len(rem)>=3:
     area=sum((Vector(rem[i][:3])-Vector(rem[0][:3])).cross(Vector(rem[i+1][:3])-Vector(rem[0][:3])).length/2 for i in range(1,len(rem)-1))
     if area>1e-9:removed+=1
   pieces=next_pieces
  for pp in pieces:
   for i in range(1,len(pp)-1):
    q=[pp[0],pp[i],pp[i+1]]
    if (Vector(q[1][:3])-Vector(q[0][:3])).cross(Vector(q[2][:3])-Vector(q[0][:3])).length<1e-9:continue
    k=len(vs);vs.extend([(v[0],-v[2],v[1])for v in q]);uvs.extend([v[3:]for v in q]);fs.append((k,k+1,k+2));mats.append(tr.material_index)
 if removed:
  nm=bpy.data.meshes.new(ob.name+'_DoorwayCut');nm.from_pydata(vs,[],fs);nm.update()
  for mat in me.materials:nm.materials.append(mat)
  lay=nm.uv_layers.new(name='RetainedInterpolatedUV')
  for f,mi in zip(nm.polygons,mats):
   f.material_index=mi
   for li in f.loop_indices:lay.data[li].uv=uvs[nm.loops[li].vertex_index]
  name=ob.name;ob.data=nm;ob.matrix_world.identity();ob['original_export_sha256']=h(src);ob['portal_source_indices']=str([102,108,114,120,126,132,138,144,150,156]+[q['source_index']for q in d['rooms']])
  keep.append(ob);changed.append({'batch':name,'triangles_before':before,'triangles_after':len(fs),'original_triangles_intersecting_cut':removed})
assert changed,'No frontage guard found'
for ob in list(bpy.context.scene.objects):
 if ob not in keep:bpy.data.objects.remove(ob,do_unlink=True)
for image in bpy.data.images:
 if image.source=='FILE' and not image.packed_file:image.pack()
(O/'exports').mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'source/TidalAquaticDoubleFrontagePatch.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(O/'exports/TidalAquaticDoubleFrontagePatch.glb'),export_format='GLB',export_yup=True,export_extras=True)
rec={'source_sha256':h(src),'cut_world_bounds':cuts,'changed_batches':changed,'scope':'Guard triangle surfaces clipped only inside fifteen retained D13/D14 specialty entry boxes; retained original GLB unchanged; cut ends meet new entry enclosure','native_sha256':h(O/'source/TidalAquaticDoubleFrontagePatch.blend'),'export_sha256':h(O/'exports/TidalAquaticDoubleFrontagePatch.glb')};(O/'FRONTAGE_RECEIPT.json').write_text(json.dumps(rec,indent=2));print('FRONTAGE_PATCH',json.dumps(rec),flush=True)
