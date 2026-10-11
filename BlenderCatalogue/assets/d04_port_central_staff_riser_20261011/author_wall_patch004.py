"""Bounded triangle clipping of the pinned live composite, retaining UVs.
This creates a new local authoring derivative, not a recovered original native.
"""
from pathlib import Path
import bpy,json,hashlib,sys,numpy as np
from mathutils import Vector
W=Path(__file__).resolve().parent; R=W.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=json.load(open(W/'AUDIT_SOURCE_PINS.json'))
for f,h in pins.items():assert sha(R/f)==h,f
source=R/'Game/assets/models/AST-STF-009_pool_market_home_equipment.glb'
pre=json.load(open(W/'SITE_PREFLIGHT.json'))['portal_preimage_meshes']
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source))
# World Blender coordinates correspond to Godot (x, -z, y).
lo=(-55.36,96.4,-.005);hi=(-55.1,102,2.85)
planes=[(a,s,b)for a in range(3)for s,b in [(1,lo[a]),(-1,hi[a])]]
def split(poly,axis,sign,bound):
 inside=[];outside=[]
 for i,A in enumerate(poly):
  B=poly[(i+1)%len(poly)];da=sign*(A[0][axis]-bound);db=sign*(B[0][axis]-bound)
  (inside if da>=0 else outside).append(A)
  if (da<0)!=(db<0):
   t=da/(da-db);q=(A[0]+(B[0]-A[0])*t,A[1]+(B[1]-A[1])*t);inside.append(q);outside.append(q)
 return inside,outside
def area(poly):
 return sum(np.linalg.norm(np.cross(poly[i][0]-poly[0][0],poly[i+1][0]-poly[0][0]))/2 for i in range(1,len(poly)-1))
audits=[];modified=[]
for item in pre:
 ob=bpy.data.objects.get(item['name']);assert ob and ob.type=='MESH',item['name']
 ob.data.calc_loop_triangles();uv=ob.data.uv_layers.active;assert uv
 triangles=[]
 for tri in ob.data.loop_triangles:
  triangles.append(([(np.array(ob.matrix_world@ob.data.vertices[ob.data.loops[k].vertex_index].co,dtype=np.float64),np.array(uv.data[k].uv,dtype=np.float64))for k in tri.loops],tri.material_index))
 # The import must match the actual runtime preimage, including world positions.
 expected=[Vector((v[0],-v[2],v[1]))for v in item['world_triangle_vertices']]
 actual=[v for poly,_ in triangles for v,u in poly]
 assert len(expected)==len(actual),(ob.name,len(expected),len(actual))
 def key(v):return tuple(round(q,4)for q in v)
 ea=np.array(expected);aa=np.array(actual);dist=np.linalg.norm(ea[:,None,:]-aa[None,:,:],axis=2);error=max(float(dist.min(axis=0).max()),float(dist.min(axis=1).max()));print('RUNTIME_COORDINATE_ERROR',ob.name,error);bound=float(np.ptp(aa,axis=0).max())/65535+0.000005;assert error<=bound,(ob.name,error,bound);assert 'meshes/force_disable_compression=false' in (source.with_suffix('.glb.import')).read_text()
 verts=[];faces=[];uvs=[];mats=[];removed=0.;unchanged=0;partial=0
 for triangle,material in triangles:
  current=triangle;pieces=[]
  for axis,sign,bound in planes:
   if not current:break
   current,out=split(current,axis,sign,bound)
   if len(out)>=3 and area(out)>1e-9:pieces.append(out)
  lost=area(current)if len(current)>=3 else 0
  if lost<1e-9:
   pieces=[triangle];unchanged+=1
  else:removed+=lost;partial+=1
  assert abs(sum(area(q)for q in pieces)+lost-area(triangle))<1e-5
  for poly in pieces:
   for i in range(1,len(poly)-1):
    q=[poly[0],poly[i],poly[i+1]];start=len(verts);verts.extend(tuple(v)for v,u in q);uvs.extend(tuple(u)for v,u in q);faces.append((start,start+1,start+2));mats.append(material)
 audits.append({'name':ob.name,'input_triangles':len(triangles),'unchanged_exact_triangles':unchanged,'clipped_triangles':partial,'removed_surface_m2':removed,'output_triangles':len(faces),'runtime_preimage_vertices_verified':True,'runtime_import_max_coordinate_error_m':error,'runtime_import_quantization_bound_m':bound,'source_import_compression_enabled':True,'outside_cut_area_preserved':True,'uvs_linear_interpolation_only':True})
 if partial:
  me=bpy.data.meshes.new(ob.name+'_bounded_cut');me.from_pydata(verts,[],faces);me.update()
  for m in ob.data.materials:me.materials.append(m)
  layer=me.uv_layers.new(name='RetainedSourceUV')
  for i,u in enumerate(uvs):layer.data[i].uv=u
  for i,p in enumerate(me.polygons):p.material_index=mats[i];p.use_smooth=False
  ob.data=me;ob.parent=None;ob.matrix_world.identity();ob['runtime_collision']=True;ob['role']='retained_staff_enclosure';ob['category']='local_wall_patch';modified.append(ob.name)
for ob in list(bpy.data.objects):
 if ob.name not in modified:bpy.data.objects.remove(ob,do_unlink=True)
assert len(modified)>=4,modified
sys.path.insert(0,str(R/'BlenderCatalogue/assets/d04_staff_court_physical_connections_20261011'))
from immutable_revision import export_native
record=export_native(bpy,W,R,'D04PortCentralStaffWallPatch_r001.blend','D04_PORT_CENTRAL_STAFF_WALL_PATCH_r001.glb')
for f,h in pins.items():assert sha(R/f)==h,f
(W/'WALL_PATCH_PROVENANCE.json').write_text(json.dumps({'status':'PASS_BOUNDED_SOURCE_CLIPPING','live_source_glb_sha256':sha(source),'cut_godot_min':[-55.36,-.005,-102],'cut_godot_max':[-55.1,2.85,-96.4],'modified_cells':modified,'cells':audits,'native_export':record,'original_source_glb_unchanged':True,'original_native_recovery_claim':False,'scope':'Only these runtime cells are replaced. Every other original cell remains instantiated from the original live composite.'},indent=2)+'\n')
print('Bounded wall derivative exported:',modified)
