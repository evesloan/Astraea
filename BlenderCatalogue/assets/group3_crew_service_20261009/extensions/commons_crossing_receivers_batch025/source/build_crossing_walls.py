"""Six exact current wall derivatives; original geometry/material/UV outside cuts retained."""
from pathlib import Path
import bpy,json,hashlib,numpy as np
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[4]
p=json.load(open(HERE/'source/CROSSING_PREIMAGES_AND_CONTRACT.json'));sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for q in p['source_files'].values():assert sha(ROOT/q['input_path'])==q['sha256'],q['input_path']
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
lookup={}
for index,file in enumerate(sorted({q['input_path']for q in p['preimage_meshes']})):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(ROOT/file));objects=set(bpy.context.scene.objects)-before
 for o in objects:
  name=o.name;lookup[file,name]=o;o.name='Input'+str(index)+'_'+name
def split(poly,axis,sign,bound):
 inside=[];outside=[]
 for i,A in enumerate(poly):
  B=poly[(i+1)%len(poly)];da=sign*(A[0][axis]-bound);db=sign*(B[0][axis]-bound);(inside if da>=0 else outside).append(A)
  if(da<0)!=(db<0):
   t=da/(da-db);q=(A[0]+(B[0]-A[0])*t,A[1]+(B[1]-A[1])*t);inside.append(q);outside.append(q)
 return inside,outside
def area(poly):return sum(np.linalg.norm(np.cross(poly[i][0]-poly[0][0],poly[i+1][0]-poly[0][0]))/2 for i in range(1,len(poly)-1))
def canon(points):return sorted(tuple(round(float(v),5)for v in q)for q in points)
audits=[];keep=[]
for item in p['preimage_meshes']:
 o=lookup[item['input_path'],item['native_name']];o.data.calc_loop_triangles();uv=o.data.uv_layers.active;assert uv
 triangles=[([(np.array(o.matrix_world@o.data.vertices[o.data.loops[k].vertex_index].co,dtype=np.float64),np.array(uv.data[k].uv,dtype=np.float64))for k in t.loops],t.material_index)for t in o.data.loop_triangles]
 assert canon([a for tri,_ in triangles for a,u in tri])==canon([(v[0],-v[2],v[1])for v in item['world_triangle_vertices']])
 lo=(item['cut_min'][0],-item['cut_max'][2],item['cut_min'][1]);hi=(item['cut_max'][0],-item['cut_min'][2],item['cut_max'][1]);planes=[(a,s,b)for a in range(3)for s,b in[(1,lo[a]),(-1,hi[a])]]
 vertices=[];faces=[];tex=[];materials=[];unchanged=clipped=0;removed=0
 for triangle,material in triangles:
  current=triangle;pieces=[]
  for axis,sign,bound in planes:
   if not current:break
   current,out=split(current,axis,sign,bound)
   if len(out)>=3 and area(out)>1e-10:pieces.append(out)
  lost=area(current)if len(current)>=3 else 0
  if lost<1e-10:pieces=[triangle];unchanged+=1
  else:clipped+=1;removed+=lost
  assert abs(sum(area(q)for q in pieces)+lost-area(triangle))<1e-7
  for poly in pieces:
   for i in range(1,len(poly)-1):
    t=[poly[0],poly[i],poly[i+1]]
    if area(t)<1e-10:continue
    k=len(vertices);vertices.extend(tuple(v)for v,u in t);tex.extend(tuple(u)for v,u in t);faces.append((k,k+1,k+2));materials.append(material)
 assert clipped>0
 mesh=bpy.data.meshes.new(item['native_name']+'_ExactAperture');mesh.from_pydata(vertices,[],faces);mesh.update()
 for m in o.data.materials:mesh.materials.append(m)
 layer=mesh.uv_layers.new(name='OriginalSurfaceUV')
 for i,u in enumerate(tex):layer.data[i].uv=u
 for i,f in enumerate(mesh.polygons):f.material_index=materials[i];f.use_smooth=False
 o.data=mesh;o.parent=None;o.matrix_world.identity();o.name=item['native_name'];o['source_asset']='AST-STF-G3-061';o['exact_original_file']=item['source_file'];o['exact_original_sha256']=p['source_files'][item['source_file']]['sha256'];o['existing_mesh_replacement_only']=True;keep.append(o)
 audits.append(dict(name=o.name,original_triangles=len(triangles),exact_unchanged_triangles=unchanged,clipped_triangles=clipped,removed_surface_m2=removed,output_triangles=len(faces),linear_original_UV_interpolation_only=True,original_material_and_texture_payload_preserved=True))
for o in list(bpy.data.objects):
 if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
assert len(keep)==6
native=HERE/'source/AST-STF-G3-061.blend';export=HERE/'exports/AST-STF-G3-061.glb';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_extras=True,export_yup=True,export_lights=False,export_cameras=False)
q=dict(status='SIX_EXACT_WALL_APERTURE_DERIVATIVES_EXPORTED',integration_source_commit=p['integration_source_commit'],native_sha256=sha(native),export_sha256=sha(export),walls=audits,unrelated_original_meshes_preserved=sum(p['unrelated_meshes_preserved_by_source'].values()),original_files_or_roofs_or_piers_or_shared_branch_modified=False,installed_or_13_criteria_resolved=False)
(HERE/'qa/WALL_DERIVATIVE_PROVENANCE.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='walls'}))
