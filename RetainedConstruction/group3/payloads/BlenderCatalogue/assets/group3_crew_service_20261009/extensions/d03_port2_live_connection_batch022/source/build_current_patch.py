"""Bounded current-source triangle clipping; every outside triangle/UV retained."""
from pathlib import Path
import bpy,json,hashlib,sys,numpy as np
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
p=json.load(open(HERE/'source/D03_PORT2_CONNECTION_CONTRACT.json'));pre=json.load(open(HERE/'source/CURRENT_SPINE_PREIMAGES.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for f,h in p['source_pins'].items():assert sha(ROOT/f)==h,f
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;bpy.ops.import_scene.gltf(filepath=str(ROOT/p['current_spine_source']))
lo=(p['cut_min'][0],-p['cut_max'][2],p['cut_min'][1]);hi=(p['cut_max'][0],-p['cut_min'][2],p['cut_max'][1]);planes=[(a,s,b)for a in range(3)for s,b in[(1,lo[a]),(-1,hi[a])]]
def split(poly,axis,sign,bound):
 inside=[];outside=[]
 for i,A in enumerate(poly):
  B=poly[(i+1)%len(poly)];da=sign*(A[0][axis]-bound);db=sign*(B[0][axis]-bound);(inside if da>=0 else outside).append(A)
  if(da<0)!=(db<0):
   t=da/(da-db);q=(A[0]+(B[0]-A[0])*t,A[1]+(B[1]-A[1])*t);inside.append(q);outside.append(q)
 return inside,outside
def area(poly):return sum(np.linalg.norm(np.cross(poly[i][0]-poly[0][0],poly[i+1][0]-poly[0][0]))/2 for i in range(1,len(poly)-1))
def canon(points):return sorted(tuple(round(float(v),5)for v in p)for p in points)
audits=[];modified=[]
for item in pre['preimage_meshes']:
 ob=bpy.data.objects.get(item['name']);assert ob and ob.type=='MESH';ob.data.calc_loop_triangles();uv=ob.data.uv_layers.active;assert uv
 triangles=[([(np.array(ob.matrix_world@ob.data.vertices[ob.data.loops[k].vertex_index].co,dtype=np.float64),np.array(uv.data[k].uv,dtype=np.float64))for k in tri.loops],tri.material_index)for tri in ob.data.loop_triangles]
 expected=[(v[0],-v[2],v[1])for v in item['world_triangle_vertices']];actual=[v for tri,_ in triangles for v,u in tri];assert canon(expected)==canon(actual),item['name']
 verts=[];faces=[];uvs=[];mats=[];removed=0;unchanged=partial=0
 for triangle,material in triangles:
  current=triangle;pieces=[]
  for axis,sign,bound in planes:
   if not current:break
   current,out=split(current,axis,sign,bound)
   if len(out)>=3 and area(out)>1e-10:pieces.append(out)
  lost=area(current)if len(current)>=3 else 0
  if lost<1e-10:pieces=[triangle];unchanged+=1
  else:removed+=lost;partial+=1
  assert abs(sum(area(q)for q in pieces)+lost-area(triangle))<1e-7
  for poly in pieces:
   for i in range(1,len(poly)-1):
    tri=[poly[0],poly[i],poly[i+1]]
    if area(tri)<1e-10:continue
    k=len(verts);verts.extend(tuple(v)for v,u in tri);uvs.extend(tuple(u)for v,u in tri);faces.append((k,k+1,k+2));mats.append(material)
 assert partial>0,item['name']
 me=bpy.data.meshes.new(ob.name+'_D03Port2BoundedCut');me.from_pydata(verts,[],faces);me.update()
 for m in ob.data.materials:me.materials.append(m)
 layer=me.uv_layers.new(name='RetainedSourceUV')
 for i,u in enumerate(uvs):layer.data[i].uv=u
 for i,q in enumerate(me.polygons):q.material_index=mats[i];q.use_smooth=False
 ob.data=me;ob.parent=None;ob.matrix_world.identity();ob['source_asset']='AST-STF-G3-052';ob['category']='current_source_local_wall_patch';ob['original_current_composite_sha256']=p['current_spine_sha256'];modified.append(ob.name)
 audits.append(dict(name=ob.name,input_triangles=len(triangles),unchanged_exact_triangles=unchanged,clipped_triangles=partial,removed_surface_m2=removed,output_triangles=len(faces),UV_linear_interpolation_only=True,original_material_resources_and_texture_bytes_preserved=True))
for o in list(bpy.data.objects):
 if o.name not in modified:bpy.data.objects.remove(o,do_unlink=True)
assert len(modified)==len(pre["preimage_meshes"])
native=HERE/'source/AST-STF-G3-052.blend';export=HERE/'exports/AST-STF-G3-052.glb';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_extras=True,export_yup=True,export_cameras=False,export_lights=False)
q=dict(status='PASS_BOUNDED_CURRENT_SOURCE_CLIPPING',current_source_sha256=p['current_spine_sha256'],native_sha256=sha(native),export_sha256=sha(export),cells=audits,current_unrelated_cells_retained=pre["unrelated_current_meshes_to_preserve"],original_source_glb_or_registered_ids_modified=False,original_native_recovery_claim=False)
(HERE/'qa/CURRENT_PATCH_NATIVE_PROVENANCE.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='cells'}))
