"""Exact installed-core successor: supported rail apertures, original light moved.
No original file, global material or production selection is changed.
"""
import bpy,json,hashlib,pathlib,math
from mathutils import Vector, Matrix
R=pathlib.Path(__file__).resolve().parents[2];D=R/'Game/grand_arrivals_tram_20261026/r003';N=R/'BlenderCatalogue/assets/grand_arrivals_tram_20261026/r003'
assert not D.exists() and not N.exists()
source=R/'Game/assets/models/AST-CIR-005_fore_midship_cinema2_d11.glb'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='29ad1d35569bfb4e99b544717a0257966b791ce9fbfc333af8deaa05f2e4d5cd'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(source))
def game(p):return Vector((p.x,p.z,-p.y))
def native(p):return Vector((p.x,-p.z,p.y))
def inside(p,lo,hi):return all(lo[i]-1e-5<=p[i]<=hi[i]+1e-5 for i in range(3))
def clip(poly,axis,plane,above):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  aa=a['p'][axis]>=plane if above else a['p'][axis]<=plane;bb=b['p'][axis]>=plane if above else b['p'][axis]<=plane
  if aa:out.append(a)
  if aa!=bb:
   f=(plane-a['p'][axis])/(b['p'][axis]-a['p'][axis]);out.append({'p':a['p'].lerp(b['p'],f),'uv':a['uv'].lerp(b['uv'],f)})
 return out
def subtract(poly,lo,hi):
 # Preserve fully separated triangles exactly, without retriangulating them.
 if any(max(v['p'][i] for v in poly)<lo[i] or min(v['p'][i] for v in poly)>hi[i] for i in range(3)):return [poly],False
 interior=poly;out=[]
 for axis,plane,above in [(i,p,a) for i in range(3) for p,a in [(lo[i],True),(hi[i],False)]]:
  if not interior:break
  piece=clip(interior,axis,plane,not above)
  if len(piece)>2:out.append(piece)
  interior=clip(interior,axis,plane,above)
 return (out,True) if len(interior)>2 else ([poly],False)
cuts=[{'role':'warm_walnut','lo':[3.6,11.49,z-.13],'hi':[7.6,11.77,z+.13],'purpose':'Only obstructing D02 crossbeam span'} for z in [-3.5,3.5]]
cuts += [{'role':'champagne_metal','lo':[3.6,11.99,z-.05],'hi':[7.6,13.15,z+.05],'purpose':'Superseded D03 wing guard inside continuous guarded rail aperture'} for z in [-13,20]]
rows=[];materials={};unchanged=[]
for obj in list(bpy.data.objects):
 if obj.type!='MESH':continue
 role=obj.data.materials[0].name.split('.')[0];materials[role]=obj.data.materials[0]
 obj.data.calc_loop_triangles();original=[]
 for tri in obj.data.loop_triangles:
  original.append([{'p':game(obj.matrix_world@obj.data.vertices[vi].co),'uv':obj.data.uv_layers.active.data[li].uv.copy() if obj.data.uv_layers.active else Vector((0,0))} for vi,li in zip(tri.vertices,tri.loops)])
 polys=[];cut_count=0;moved=0;preserved=0
 for tri in original:
  # Move the complete existing right-hand light case AND lens. Same shape,
  # materials, UVs, marker ID and light count; no fabricated extra light.
  if all(inside(v['p'],[5.279,11.539,-.281],[5.921,11.761,.281]) for v in tri):
   tri=[{'p':v['p']+Vector((-3,0,0)),'uv':v['uv']} for v in tri];polys.append(tri);moved+=1;continue
  pieces=[tri];changed=False
  for cut in cuts:
   if cut['role']!=role:continue
   new=[]
   for piece in pieces:
    result,edited=subtract(piece,cut['lo'],cut['hi']);new.extend(result);changed|=edited
   pieces=new
  polys.extend(pieces)
  if changed:cut_count+=1
  else:preserved+=1
 if not cut_count and not moved:unchanged.append(obj.name);continue
 flat=[v for p in polys for i in range(1,len(p)-1) for v in [p[0],p[i],p[i+1]]]
 mesh=bpy.data.meshes.new(obj.name+'_ScopedRailSuccessor');mesh.from_pydata([native(v['p']) for v in flat],[],[(i,i+1,i+2) for i in range(0,len(flat),3)]);mesh.update();mesh.materials.append(materials[role]);uv=mesh.uv_layers.new(name='OriginalUVPreserved')
 for i,v in enumerate(flat):uv.data[i].uv=v['uv']
 obj.data=mesh;obj.matrix_world=Matrix.Identity(4);obj['source_original']=source.relative_to(R).as_posix()
 rows.append({'object':obj.name,'source_triangles':len(original),'cut_triangles':cut_count,'moved_fixture_triangles':moved,'unchanged_triangles':preserved,'runtime_triangles':len(flat)//3})
assert sum(r['cut_triangles'] for r in rows)>16 and sum(r['moved_fixture_triangles'] for r in rows)==24,rows
marker=bpy.data.objects.get('DATUM_light_01_1');assert marker is not None
before=game(marker.matrix_world.translation);assert (before-Vector((5.6,11.53,0))).length<.001,before
matrix=marker.matrix_world.copy();matrix.translation.x-=3;marker.matrix_world=matrix
new_parts=[]
def mesh_part(name,verts,faces,role):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata([native(Vector(v)) for v in verts],[],faces);mesh.update();mesh.materials.append(materials[role]);uv=mesh.uv_layers.new(name='SourceMetreUV')
 for p in mesh.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
  for li in p.loop_indices:
   v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
 obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj['selected']=False;new_parts.append(name)
def box(name,lo,hi,role):
 x,y,z=lo;X,Y,Z=hi
 mesh_part(name,[[x,y,z],[X,y,z],[x,Y,z],[X,Y,z],[x,y,Z],[X,y,Z],[x,Y,Z],[X,Y,Z]],[[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]],role)
for k,z in enumerate([-3.5,3.5]):
 # Raised header has 2.7m clearance above the retained D03 guest datum and
 # remains below the D04 slab. Piers continue the existing core receivers.
 box('ArrivalsRail_RaisedHeader_'+str(k),[3.25,14.7,z-.15],[7.8,15.0,z+.15],'warm_walnut')
 for side,x in [('Inner',3.35),('Outer',7.7)]:box('ArrivalsRail_HeaderReceiver_'+side+'_'+str(k),[x-.10,11.5,z-.12],[x+.10,14.8,z+.12],'champagne_metal')
 # Close the newly exposed exact original beam ends, rather than leave an
 # open triangle soup or suppress their contact policy.
 for x,order in [(3.6,[0,1,2,3]),(7.6,[3,2,1,0])]:
  vs=[[x,11.5,z-.12],[x,11.76,z-.12],[x,11.76,z+.12],[x,11.5,z+.12]];mesh_part('ArrivalsRail_BeamReveal_%d_%s'%(k,x),vs,[order],'warm_walnut')
for z in [-13,20]:
 for h in [.14,1.06]:
  vs=[[7.6,12+h,z-.04],[7.6,12+h+.08,z-.04],[7.6,12+h+.08,z+.04],[7.6,12+h,z+.04]]
  mesh_part('ArrivalsRail_GuardReveal_%s_%s'%(z,h),vs,[[3,2,1,0]],'champagne_metal')
for image in bpy.data.images:
 if image.source=='FILE' and image.has_data:image.pack()
D.mkdir(parents=True);N.mkdir(parents=True)
native_file=N/'ForeMidCoreEnclosure_r003.blend';runtime=D/'ForeMidCoreEnclosure.glb'
bpy.ops.wm.save_as_mainfile(filepath=str(native_file));bpy.ops.export_scene.gltf(filepath=str(runtime),export_format='GLB',export_extras=True,export_yup=True)
receipt={'selected':False,'source':source.relative_to(R).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'changes':rows,'untouched_mesh_objects':unchanged,'new_supported_members_and_reveals':new_parts,'fixture':{'id':marker.name,'before_local':list(before),'after_local':list(game(marker.matrix_world.translation)),'additional_lights':0},'cut_volumes_local':cuts,'preserved':['Original lift shaft, every stop/controller/ID','All staircase geometry and staircase guards','D11 Cinema2 receiving alteration','All original material resources and source UVs outside exact clipped spans'],'holds':['Independent outside-geometry/native-runtime verification','Original vehicle/cart/door/truck sweep','Complete connected route receiving and actual rider operation'],'outputs':{p.relative_to(R).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [native_file,runtime]}}
(D/'BUILD.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print('ARRIVALS_CORE_ENCLOSURE '+json.dumps(receipt))
