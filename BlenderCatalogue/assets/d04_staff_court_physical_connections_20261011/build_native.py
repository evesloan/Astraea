from pathlib import Path
import bpy,json,hashlib,math,sys
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();B=lambda p:(p[0],-p[2],p[1])
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
F=R/'BlenderCatalogue/assets/d04_port_forward_homes_first_20261010';ns={'__file__':str(F/'build_native.py')};s=(F/'build_native.py').read_text();exec(s[:s.index('\nrecords=[];structure=[]')],ns);ns.update(W=W,R=R,P=P);mats=ns['start']();ns['add_parts'](P['parts'],mats)
revision=P.get('revision','r001');owned=ns['export']('D04PhysicalFittings_'+revision+'.blend','D04_PHYSICAL_FITTINGS_'+revision+'.glb')
ns['start']();changes=[]
def clip(poly,axis,bound,greater):
 out=[]
 for prev,now in zip(poly[-1:]+poly[:-1],poly):
  a=prev[0][axis]>=bound if greater else prev[0][axis]<=bound;b=now[0][axis]>=bound if greater else now[0][axis]<=bound
  if a!=b:
   t=(bound-prev[0][axis])/(now[0][axis]-prev[0][axis]);out.append(([prev[0][i]+t*(now[0][i]-prev[0][i])for i in range(3)],[prev[1][i]+t*(now[1][i]-prev[1][i])for i in range(2)]))
  if b:out.append(now)
 return out
for source in sorted(set(c['source_model']for c in P['cuts'])):
 bpy.ops.import_scene.gltf(filepath=str(R/'Game/assets/models'/source));bpy.context.view_layer.update();rows=[c for c in P['cuts']if c['source_model']==source];found={c['name']:bpy.data.objects.get(c['name'])for c in rows};assert all(found.values()),found
 imported=set(o for o in bpy.data.objects if not o.get('retained_cut_successor',False));worlds={o:o.matrix_world.copy()for o in found.values()}
 for ob in imported:
  if ob not in worlds:bpy.data.objects.remove(ob,do_unlink=True)
 for row in rows:
  ob=found[row['name']];old=ob.data;old.calc_loop_triangles();m=worlds[ob];uv=old.uv_layers.active;vs=[];fs=[];uvs=[];mis=[];kept=changed=0
  def emit(poly,mi):
   for i in range(1,len(poly)-1):
    tri=[poly[0],poly[i],poly[i+1]];a,b,c=[Vector(v[0])for v in tri]
    if (b-a).cross(c-a).length<1e-10:continue
    k=len(vs);vs.extend([B(v[0])for v in tri]);uvs.extend(v[1]for v in tri);fs.append((k,k+1,k+2));mis.append(mi)
  for tri in old.loop_triangles:
   raw=[m@old.vertices[i].co for i in tri.vertices];points=[(v.x,v.z,-v.y)for v in raw];initial=[(list(v),list(uv.data[l].uv)if uv else[0,0])for v,l in zip(points,tri.loops)];polys=[initial];touched=False
   initial_normal=(Vector(points[1])-Vector(points[0])).cross(Vector(points[2])-Vector(points[0])).normalized();axis=max(range(3),key=lambda a:abs(initial_normal[a]))
   for cut in row['volumes']:
    lo=cut['min'];hi=cut['max'];out=[]
    for poly in polys:
     if any(max(v[0][a]for v in poly)<lo[a]-1e-7 or min(v[0][a]for v in poly)>hi[a]+1e-7 for a in range(3)):out.append(poly);continue
     assert abs(initial_normal[axis])>.9999,(row['name'],initial_normal)
     remainder=poly
     for a in [a for a in range(3)if a!=axis]:
      for bound,greater in [(lo[a],True),(hi[a],False)]:
       if not remainder:break
       outside=clip(remainder,a,bound,not greater)
       if outside:out.append(outside)
       remainder=clip(remainder,a,bound,greater)
     if remainder:touched=True
    polys=out
   for poly in polys:emit(poly,tri.material_index)
   if touched:changed+=1
   else:kept+=1
  # New cap faces are exact rectangular cross-sections of the surveyed solid.
  # The staff batches have disconnected opposite walls/ceilings: only the
  # measured EAST wall prism is capped, never a whole-batch bounding box.
  lo,hi=[list(v)for v in row['bounds']]
  if row['kind']=='staff_wall':
   if 'bluegrey'in row['name']:lo=[-55.32,12,-460];hi=[-55.2,13.03,-440]
   elif 'white'in row['name']:lo=[-55.32,13.03,-460];hi=[-55.2,15.2,-440]
   else:lo=[-55.345,12.73,-460];hi=[-55.32,12.86,-440]
  caps=0
  for cut in row['volumes']:
   a=[max(lo[i],cut['min'][i])for i in range(3)];b=[min(hi[i],cut['max'][i])for i in range(3)]
   for axis in range(3):
    for bound in [cut['min'][axis],cut['max'][axis]]:
     if bound<=lo[axis]+.00004 or bound>=hi[axis]-.00004:continue
     u,v=[i for i in range(3)if i!=axis];quad=[]
     for U,V in [(a[u],a[v]),(b[u],a[v]),(b[u],b[v]),(a[u],b[v])]:
      q=[0,0,0];q[axis]=bound;q[u]=U;q[v]=V;quad.append((q,[U,V]))
     normal=(Vector(quad[1][0])-Vector(quad[0][0])).cross(Vector(quad[2][0])-Vector(quad[0][0]));desired=1 if bound==cut['min'][axis]else-1
     if normal[axis]*desired<0:quad.reverse()
     emit(quad,0);caps+=1
  mesh=bpy.data.meshes.new(row['name']+'_ContainedSuccessor');mesh.from_pydata(vs,[],fs);mesh.update()
  for mat in old.materials:mesh.materials.append(mat)
  layer=mesh.uv_layers.new(name='RetainedSourceUV')
  for face,mi in zip(mesh.polygons,mis):
   face.material_index=mi
   for li in face.loop_indices:layer.data[li].uv=uvs[mesh.loops[li].vertex_index]
  ob.parent=None;ob.data=mesh;ob.matrix_world=Matrix.Identity(4);ob.name='D04PC_Successor_'+row['name'];ob['retained_cut_successor']=True;ob['runtime_collision']=True;ob['role']='retained_source';ob['category']='bounded_source_successor';ob['exact_source_sha256']=P['source_pins']['Game/assets/models/'+source]
  changes.append({'source_model':source,'source_name':row['name'],'successor':ob.name,'source_triangle_count':len(old.loop_triangles),'untouched_triangles':kept,'modified_triangles':changed,'new_cap_quads':caps})
patch=ns['export']('D04BoundedPhysicalCuts_'+revision+'.blend','D04_BOUNDED_PHYSICAL_CUTS_'+revision+'.glb')
P['owned_model']={'model_file':owned['export'],'model_sha256':owned['export_sha256'],'collision_policy':owned['collision_policy']};P['patch_model']={'model_file':patch['export'],'model_sha256':patch['export_sha256'],'collision_policy':patch['collision_policy']};P['model_pins']={q['export']:q['export_sha256']for q in [owned,patch]};P['native_export_records']=P.get('previous_native_export_records',[])+[owned,patch];P['cut_changes']=changes
if 'reach_tool'in P:
 rec=next(q for q in P['native_export_records']if q['export']==P['reach_tool']['model']);P['model_pins'][rec['export']]=rec['export_sha256']
# Derive each guard from EVERY authored moving member across a full quarter-turn.
for gate in P['gates']:
 pivot=Vector(gate['pivot']);points=[]
 for part in P['parts']:
  if part['name']not in gate['members']:continue
  for deg in range(91):
   rot=Matrix.Rotation(math.radians(deg if gate['candidate_open_degrees']>0 else-deg),3,'Y')
   points.extend(pivot+rot@(Vector(p)-pivot)for p in part['verts'])
 gate['sweep_min']=[min(v[i]for v in points)-.09 for i in range(3)];gate['sweep_max']=[max(v[i]for v in points)+.09 for i in range(3)]
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
(W/'RUNTIME_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');(R/'Game/data/architecture/D04_PHYSICAL_CONNECTIONS_CANDIDATE.json').write_text(json.dumps(P,indent=2)+'\n');(W/'NATIVE_EXPORT_CHECK.json').write_text(json.dumps({'status':'PASS','blender_version':bpy.app.version_string,'records':P['native_export_records'],'source_changes':changes,'production_active':False},indent=2)+'\n');print('PHYSICAL_NATIVE_PASS',len(changes),len(P['gates']))
