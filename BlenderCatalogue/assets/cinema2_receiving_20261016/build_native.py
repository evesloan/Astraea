from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
from mathutils.geometry import tessellate_polygon
D=Path(__file__).resolve().parent;G=Path('/workspace/Astraea/Game');plan=json.loads((D/'NATIVE_PLAN.json').read_text());assert bpy.app.version[:3]==(4,3,2)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);made=[];rows=[]
B=lambda p:Vector((p[0],-p[2],p[1]));GV=lambda p:Vector((p.x,p.z,-p.y));origin=Vector((0,0,0))

# Bounded successor of the exact installed Salon north wall.
src=G/'assets/models/SOL_D11_directory_03_source001.glb';assert hashlib.sha256(src.read_bytes()).hexdigest()==plan['source_pins']['assets/models/SOL_D11_directory_03_source001.glb'];bpy.ops.import_scene.gltf(filepath=str(src))
def clip(poly,axis,plane,less):
 if not poly:return []
 out=[];s=poly[-1];ds=s['p'][axis]-plane
 for e in poly:
  de=e['p'][axis]-plane;ins=ds<=0 if less else ds>=0;ine=de<=0 if less else de>=0
  if ins!=ine:
   t=ds/(ds-de);out.append({k:s[k].lerp(e[k],t)for k in['p','uv']})
  if ine:out.append(e)
  s=e;ds=de
 return out
def cut(poly):
 pieces=[];inside=poly
 for axis,plane,less in[(1,69.5,False),(1,72.7,True),(2,-249.2,False),(2,-246.8,True)]:
  outside=clip(inside,axis,plane,not less)
  if len(outside)>=3:pieces.append(outside)
  inside=clip(inside,axis,plane,less)
  if not inside:break
 return pieces
offset=Vector((0,0,0))
for name,xlo,xhi,top in[('E_outer_west1',11.33,11.57,76.7)]:
 obj=bpy.data.objects[name];obj.data.calc_loop_triangles();pre=[]
 for t in obj.data.loop_triangles:pre.append([{'p':GV(obj.matrix_world@obj.data.vertices[vi].co)+offset,'uv':obj.data.uv_layers.active.data[li].uv.copy()if obj.data.uv_layers.active else Vector((0.,0.))}for vi,li in zip(t.vertices,t.loops)])
 polys=[part for poly in pre for part in cut(poly)];triangles=[(poly[0],poly[i],poly[i+1])for poly in polys for i in range(1,len(poly)-1)];head=min(72.7,top)
 for z,n in[(-249.2,Vector((0,0,1))),(-246.8,Vector((0,0,-1)))]:
  vs=[Vector((xlo,69.5,z)),Vector((xhi,69.5,z)),Vector((xhi,head,z)),Vector((xlo,head,z))]
  if (vs[1]-vs[0]).cross(vs[2]-vs[0]).dot(n)<0:vs.reverse()
  triangles += [[{'p':vs[i],'uv':Vector((vs[i].x,vs[i].y))}for i in ids]for ids in[(0,1,2),(0,2,3)]]
 vs=[Vector((xlo,72.7,-249.2)),Vector((xhi,72.7,-249.2)),Vector((xhi,72.7,-246.8)),Vector((xlo,72.7,-246.8))]
 if (vs[1]-vs[0]).cross(vs[2]-vs[0]).y>0:vs.reverse()
 triangles += [[{'p':vs[i],'uv':Vector((vs[i].x,vs[i].z))}for i in ids]for ids in[(0,1,2),(0,2,3)]]
 flat=[v for t in triangles for v in t];matrix=obj.matrix_world.copy();inverse=matrix.inverted();data=bpy.data.meshes.new('C2R_SUCCESSOR_'+name);data.from_pydata([inverse@B(v['p']-offset)for v in flat],[],[tuple(range(i,i+3))for i in range(0,len(flat),3)]);data.update()
 for mat in obj.data.materials:data.materials.append(mat)
 uv=data.uv_layers.new(name='UVMap')
 for i,v in enumerate(flat):uv.data[i].uv=v['uv']
 new=bpy.data.objects.new('C2R_SUCCESSOR_'+name,data);bpy.context.collection.objects.link(new);new.matrix_world=matrix;made.append(new);pts=[GV(v.co)for v in obj.data.vertices]
 rows.append({'source_name':name,'replacement_name':new.name,'source_triangles':len(pre),'replacement_triangles':len(triangles),'source_local_translation':list(GV(matrix.translation)+offset),'input_bounds_local':[[min(v[i]for v in pts)for i in range(3)],[max(v[i]for v in pts)for i in range(3)]],'reveal_x':[xlo,xhi],'source_top_y':top})
for o in list(bpy.data.objects):
 if o not in made:bpy.data.objects.remove(o,do_unlink=True)
R=G.parent;donor=R/plan['source_native'];assert hashlib.sha256(donor.read_bytes()).hexdigest()==plan['source_native_sha256'];source=json.loads((G/'data/architecture/group8/orchard_service.json').read_text());hoodrows=[r for r in source['meshes']if r['unit']=='NorthFinish_Hood'];hoodnames=[r['name']for r in hoodrows]
with bpy.data.libraries.load(str(donor),link=False)as(data_from,data_to):
 data_to.objects=hoodnames;data_to.materials=[n for n in data_from.materials if n in ['ASTRAEA_staff_zinc','ASTRAEA_staff_white_paint','ASTRAEA_staff_bluegrey_paint','ASTRAEA_dark_rubber']]
col=bpy.data.collections.new('CINEMA2_SERVICE_RECEIVING_AUTHORING_R001');bpy.context.scene.collection.children.link(col);parts=[];clones=[];lights=[]
mat=lambda token:next(m for m in bpy.data.materials if m.name==token)
metal=mat('ASTRAEA_staff_zinc');zinc=mat('ASTRAEA_staff_zinc');white=mat('ASTRAEA_staff_white_paint');blue=mat('ASTRAEA_staff_bluegrey_paint');rubber=mat('ASTRAEA_dark_rubber')
def mesh(name,vs,fs,material):
 data=bpy.data.meshes.new(name);data.from_pydata(vs,[],fs);data.update();data.materials.append(material);uv=data.uv_layers.new(name='AuthoredMetreUV')
 for polygon in data.polygons:
  normal=polygon.normal;axis=max(range(3),key=lambda i:abs(normal[i]));axes=[i for i in range(3)if i!=axis]
  for loop in polygon.loop_indices:
   p=data.vertices[data.loops[loop].vertex_index].co;uv.data[loop].uv=(p[axes[0]]/2,p[axes[1]]/2)
 o=bpy.data.objects.new(name,data);col.objects.link(o);parts.append(o);return o

def prism(name,points,lo,hi,material):
 ring=[Vector((x,-z,lo))for x,z in points];area=sum(ring[i].x*ring[(i+1)%len(ring)].y-ring[(i+1)%len(ring)].x*ring[i].y for i in range(len(ring)))
 if area<0:ring.reverse()
 n=len(ring);vs=[tuple(p)for p in ring]+[(p.x,p.y,hi)for p in ring];lookup={tuple(v):i for i,v in enumerate(ring)};faces=[]
 for tri in tessellate_polygon([ring]):
  ix=[v if isinstance(v,int)else lookup[tuple(v)]for v in tri]
  if (ring[ix[1]]-ring[ix[0]]).cross(ring[ix[2]]-ring[ix[0]]).z<0:ix.reverse()
  faces.extend([tuple(reversed(ix)),tuple(i+n for i in ix)])
 for i in range(n):j=(i+1)%n;faces.append((i,j,j+n,i+n))
 return mesh(name,vs,faces,material)
def box(name,lo,hi,material):
 lo,hi=tuple(min(a,b)for a,b in zip(lo,hi)),tuple(max(a,b)for a,b in zip(lo,hi));return prism(name,[(lo[0],lo[2]),(hi[0],lo[2]),(hi[0],hi[2]),(lo[0],hi[2])],lo[1],hi[1],material)
def line(name,a,b,width,lo,hi,material):
 a,b=Vector(a),Vector(b);u=Vector((-(b-a).y,(b-a).x)).normalized()*width/2;return prism(name,[a-u,b-u,b+u,a+u],lo,hi,material)
def wall(name,a,b):
 if (Vector(a)-Vector(b)).length<.001:return
 for suffix,w,lo,hi,material in[('Toe',.14,78,78.14,zinc),('Dado',.12,78.14,79.05,blue),('Reveal',.15,79.05,79.12,metal),('Enamel',.12,79.12,81.55,white),('Cove',.18,81.55,81.82,white)]:line(name+'_'+suffix,a,b,w,lo,hi,material)
def girder(name,a,b):
 for suffix,w,lo,hi in[('Lower',.18,77.765,77.78),('Web',.035,77.775,77.815),('Upper',.18,77.81,77.835)]:line(name+'_'+suffix,a,b,w,lo,hi,metal)

outline=plan['floor_outline_xz'];prism('C2R_MissingOnlyFloor',outline,77.76,78,blue);prism('C2R_SourceJoinedRoof',outline,81.8,81.98,white)
for i,z in enumerate([-249.5,-246.5]):
 wall(f'C2R_Edge{i}',(4.09,z),(10.91,z));girder(f'C2R_EdgeGirder{i}',(4.09,z),(10.91,z))
 wall(f'C2R_SourceWallJoin{i}',(10.91,z),(11.38,z))
wall('C2R_AxialReturn0',(4.09,-249.5),(4.09,-249.2));wall('C2R_AxialReturn1',(4.09,-246.8),(4.09,-246.5));line('C2R_AxialHeader',(4.09,-249.2),(4.09,-246.8),.18,81.2,81.82,white)
box('C2R_SourceRoofJoin',(10.99995,81.8,-249.5),(11.38,81.98,-246.5),white)
for j,z in enumerate([-248.8,-248,-247.2]):
 box(f'C2R_EmbeddedRoomTie{j}',(10.7,77.78,z-.1),(11.3,77.86,z+.1),metal)
 box(f'C2R_EmbeddedAxialTie{j}',(3.7,77.78,z-.1),(4.3,77.86,z+.1),metal)
for j,x in enumerate([4.1,7.5,10.9]):girder(f'C2R_Cross{j}',(x,-249.4),(x,-246.6))
for k,(xa,xb,ya,yb)in enumerate([(10.8,11.2,78.003,78.028),(11.2,11.6,78.028,78.028),(11.6,12,78.028,78.003)]):
 o=box(f'C2R_Threshold_Leaf{k}',(xa,ya-.003,-249),(xb,ya,-247),metal)
 for v in o.data.vertices:v.co.z+=(v.co.x-xa)/(xb-xa)*(yb-ya)
 o.data.update()
for j,x in enumerate([11.3,11.5]):box(f'C2R_Threshold_EmbeddedBearing{j}',(x-.045,77.9,-248.9),(x+.045,78.025,-247.1),metal)
for i,target in enumerate([(7.5,81.1,-248)]):
 transform=Matrix.Translation(B(target))@Matrix.Identity(4)@Matrix.Translation(-B((34,64.1,-228.53)));madehood=[]
 for src in data_to.objects:
  o=src.copy();o.data=src.data;o.parent=None;o.matrix_world=transform@src.matrix_world;o.name=f'C2R_Hood{i}__'+src.name;col.objects.link(o);parts.append(o);madehood.append(o);clones.append({'name':o.name,'source':src.name,'rigid_matrix_blender':[list(r)for r in transform]})
 for row in source['lights']:
  if row['name']not in ['G8O_LIGHT_NorthFinish_Hood_-1','G8O_LIGHT_NorthFinish_Hood_1']:continue
  suffix=str(row['name']).split('_')[-1];lens=next(o for o in madehood if o.name.endswith('Lens'+suffix));lights.append({'name':f'C2R_LIGHT_{i}_{suffix}','at':list(GV(transform@B(row['at']))),'colour':row['colour'],'energy':row['energy'],'range':row['range'],'lens':lens.name})
for src in data_to.objects:bpy.data.objects.remove(src,do_unlink=True)
placement=Matrix.Translation(Vector((0,0,-8.5)))
for o in parts:o.matrix_world=placement@o.matrix_world
for row in clones:row['rigid_matrix_blender']=[list(v)for v in placement@Matrix(row['rigid_matrix_blender'])]
for row in lights:row['at']=list(GV(placement@B(row['at'])))
for image in bpy.data.images:
 if image.source=='FILE'and not image.packed_file:image.pack()
bpy.data.texts.new('EXACT_SOURCE_POLICY.json').write(json.dumps(plan,indent=2));bounds=[]
for o in parts:
 o.data.calc_loop_triangles();ps=[GV(o.matrix_world@Vector(v))for v in o.bound_box];bounds.append({'name':o.name,'min':[min(p[i]for p in ps)for i in range(3)],'max':[max(p[i]for p in ps)for i in range(3)],'triangles':len(o.data.loop_triangles)})
# Retain editable components; runtime batches combine only new receiving parts by material/collision class.
runtime=bpy.data.collections.new('CINEMA2_SERVICE_RECEIVING_RUNTIME_R001');bpy.context.scene.collection.children.link(runtime);groups={};batchrows=[]
for o in parts:
 for polygon in o.data.polygons:
  material=o.data.materials[polygon.material_index];key=(material.name,'Lens'not in o.name);g=groups.setdefault(key,{'vs':[],'fs':[],'uvs':[],'members':set()});g['members'].add(o.name);ix=[]
  for li in polygon.loop_indices:
   ix.append(len(g['vs']));g['vs'].append(tuple(o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co));g['uvs'].append(tuple(o.data.uv_layers.active.data[li].uv))
  g['fs'].append(ix)
for i,(key,g)in enumerate(sorted(groups.items())):
 name=f'C2R_BATCH_{i:03d}';data=bpy.data.meshes.new(name);data.from_pydata(g['vs'],[],g['fs']);data.update();data.materials.append(bpy.data.materials[key[0]]);uv=data.uv_layers.new(name='UVMap')
 for li in range(len(data.loops)):uv.data[li].uv=g['uvs'][data.loops[li].vertex_index]
 o=bpy.data.objects.new(name,data);runtime.objects.link(o);ps=[GV(Vector(v))for v in o.bound_box];batchrows.append({'name':name,'material':key[0],'collide':key[1],'members':sorted(g['members']),'min':[min(p[j]for p in ps)for j in range(3)],'max':[max(p[j]for p in ps)for j in range(3)]})
for row in lights:row['lens_batch']=next(b['name']for b in batchrows if row['lens']in b['members'])
I=D/'exports';I.mkdir(parents=True,exist_ok=True);model=I/'CINEMA2_SERVICE_RECEIVER_r001.glb';bpy.ops.object.select_all(action='DESELECT')
for o in list(runtime.objects)+made:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(model),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False);col.hide_render=True;N=D/'source';N.mkdir(exist_ok=True);native=N/'CINEMA2_SERVICE_RECEIVER_r001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.wm.open_mainfile(filepath=str(native));fresh=D/'FRESH_REEXPORT.glb';bpy.ops.export_scene.gltf(filepath=str(fresh),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(fresh)==sha(model)
receipt={'status':'PASS_NATIVE_EXACT_FRESH_EXPORT_CANDIDATE','file':model.name,'native_sha256':sha(native),'model_sha256':sha(model),'walls':rows,'batches':batchrows,'bounds':bounds,'lights':lights,'rigid_clones':clones,'authoring_meshes':len(parts),'runtime_meshes':len(batchrows),'source_pins':plan['source_pins'],'new_floor_area_m2':plan['new_floor_area_m2'],'native_file':native.name,'new_room_ids_capacity_or_lift_stops':0,'operational_or_final_acceptance':False};(D/'NATIVE_VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS_CINEMA2_NATIVE',receipt['authoring_meshes'],receipt['runtime_meshes'],len(lights))
