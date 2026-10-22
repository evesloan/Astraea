from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector
W=Path(__file__).resolve().parent;R=W.parents[2];G=R/'Game';P=G/'sunset_specialty_bank_20261022';plan=json.loads((W/'GUARD_PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(R/plan['source'])==plan['source_sha256'];bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/plan['source']))
def B(p):return Vector((p[0],-p[2],p[1]))
def corners(p):
 a,b=Vector(p['a']),Vector(p['b']);t=(b-a).normalized();s=Vector((0,0,1))if abs(t.z)<.95 else Vector((1,0,0));s=(s-t*s.dot(t)).normalized();u=t.cross(s).normalized()
 return [B(q+s*w+u*h)for q in [a,b]for w,h in [(-p['width']/2,-p['depth']/2),(p['width']/2,-p['depth']/2),(p['width']/2,p['depth']/2),(-p['width']/2,p['depth']/2)]]
faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];records=[];keep=[]
for name in sorted({c['batch']for c in plan['changes']}):
 ob=bpy.data.objects.get(name);assert ob and ob.type=='MESH';changes=[c for c in plan['changes']if c['batch']==name];verts=[ob.matrix_world@v.co for v in ob.data.vertices];removed=set();counts=[]
 for c in changes:
  cs=corners(c['original']);hits=[]
  for f in ob.data.polygons:
   if all(any((verts[j]-co).length<.0002 for co in cs)for j in f.vertices):hits.append(f.index)
  assert len(hits)==12,(c['original']['name'],len(hits));assert not removed.intersection(hits);removed.update(hits);counts.append(dict(name=c['original']['name'],removed_triangles=12))
 polys=[];uvs=[]
 for f in ob.data.polygons:
  if f.index in removed:continue
  polys.append(tuple(f.vertices));uvs.extend(tuple(ob.data.uv_layers.active.data[j].uv)for j in f.loop_indices)
 original_kept=len(polys)
 for c in changes:
  for seg in c['replacements']:
   off=len(verts);vs=corners(seg);verts.extend(vs)
   for face in faces:
    polys.append(tuple(off+j for j in face));n=(vs[face[1]]-vs[face[0]]).cross(vs[face[2]]-vs[face[0]]).normalized();u=Vector((1,0,0))if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u);uvs.extend((vs[j].dot(u),vs[j].dot(v))for j in face)
 me=bpy.data.meshes.new(name+'_SC47Receiving_r001');me.from_pydata(verts,[],polys);me.update()
 for mat in ob.data.materials:me.materials.append(mat)
 uv=me.uv_layers.new(name='MetreScaled');assert len(uv.data)==len(uvs)
 for a,b in zip(uv.data,uvs):a.uv=b
 ob.data=me;ob.matrix_world.identity();ob['sunset_47_guard_successor']=True;ob['source_sha256']=plan['source_sha256'];ob['runtime_collision']=True;keep.append(ob);records.append(dict(batch=name,removed_parts=counts,retained_triangles=original_kept,retained_segment_count=sum(len(c['replacements'])for c in changes)))
# Close the12cm bearing interval below each new room floor; entirely inside its allocation.
pack=json.loads((W/'PLAN.json').read_text());mat=bpy.data.materials.new('SC47_BearingStone');mat.diffuse_color=(.48,.45,.39,1)
for r in pack['rooms']:
 a=r['allocation'];x,X=a['allocation_x'];z,Z=a['allocation_z'];y=a['floor_y'];v=[B(p)for p in [(x,y-.24,z),(X,y-.24,z),(X,y-.12,z),(x,y-.12,z),(x,y-.24,Z),(X,y-.24,Z),(X,y-.12,Z),(x,y-.12,Z)]];me=bpy.data.meshes.new('SC47Bearing');me.from_pydata(v,[],faces);me.materials.append(mat);ob=bpy.data.objects.new('SC47_Bearing_'+str(a['source_envelope_index']),me);bpy.context.collection.objects.link(ob);ob['runtime_collision']=True;ob['construction_role']='allocated_floor_bearing';keep.append(ob)
for ob in list(bpy.data.objects):
 if ob not in keep:bpy.data.objects.remove(ob,do_unlink=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all();native=W/'Sunset47Receiving_r001.blend';assert not native.exists();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);export=P/'runtime/Sunset47Receiving_r001.glb';bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_extras=True,export_apply=True)
(W/'RECEIVING_BUILD.json').write_text(json.dumps(dict(native=str(native.relative_to(R)),native_sha256=sha(native),export=str(export.relative_to(G)),export_sha256=sha(export),guard_batches=records,new_bearings=47,source_unchanged=sha(R/plan['source'])==plan['source_sha256'],engineering_load_acceptance=False),indent=2)+'\n');print('GUARD_SUCCESSOR_COMPLETE',len(records),len(plan['changes']),flush=True)
