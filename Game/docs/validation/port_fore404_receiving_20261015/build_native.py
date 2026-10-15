from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
from mathutils.geometry import tessellate_polygon
D=Path(__file__).resolve().parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');src=G/'assets/models/AST-AQU-016.glb';plan=json.loads((D/'NATIVE_PLAN.json').read_text());expected=plan['source_pins']['assets/models/AST-AQU-016.glb'];assert hashlib.sha256(src.read_bytes()).hexdigest()==expected;assert bpy.app.version[:3]==(4,3,2)
assert not(D/'native/PORT_FORE404_RECEIVER_r001.blend').exists()and not(D/'import/Game/assets/port_fore404_receiving_20261015/PORT_FORE404_RECEIVER_r001.glb').exists(),'Immutable r001 exists; author a new revision in isolated staging'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(src));bpy.context.preferences.filepaths.save_version=0
names=plan['original_wall_names'];sources={name:bpy.data.objects[name]for name in names};made=[];rows=[]

def godot(p):return Vector((p.x,p.z,-p.y))
def blender(p):return Vector((p.x,-p.z,p.y))
def clip(poly,axis,plane,less):
 if not poly:return []
 out=[];s=poly[-1];ds=s['p'][axis]-plane
 for e in poly:
  de=e['p'][axis]-plane;ins=ds<=0 if less else ds>=0;ine=de<=0 if less else de>=0
  if ins!=ine:
   t=ds/(ds-de);out.append({k:s[k].lerp(e[k],t)for k in ['p','n','uv']})
  if ine:out.append(e)
  s=e;ds=de
 return out
def subtract(tri):
 pieces=[];inside=tri
 for axis,plane,less in[(0,cutx[0],False),(0,cutx[1],True),(1,52.5,False),(1,55.7,True),(2,cutz[0],False),(2,cutz[1],True)]:
  outside=clip(inside,axis,plane,not less)
  if len(outside)>=3:pieces.append(outside)
  inside=clip(inside,axis,plane,less)
  if not inside:break
 return pieces
for name,obj in sources.items():
 staff=False;cutx=(-54.1,-53.7);cutz=(-404.75,-401.65)
 obj.data.calc_loop_triangles();uvlayer=obj.data.uv_layers.active;triangles=[];pre=[]
 normal_matrix=obj.matrix_world.to_3x3().inverted().transposed()
 for tri in obj.data.loop_triangles:
  poly=[]
  for li,vi in zip(tri.loops,tri.vertices):
   p=godot(obj.matrix_world@obj.data.vertices[vi].co);n=godot(normal_matrix@obj.data.corner_normals[li].vector).normalized();uv=uvlayer.data[li].uv.copy()if uvlayer else Vector((0.,0.));poly.append({'p':p,'n':n,'uv':uv})
  pre.append(poly)
  for poly in subtract(poly):
   for i in range(1,len(poly)-1):triangles.append([poly[0],poly[i],poly[i+1]])
 # Close the newly exposed jambs and head using this exact wall's thickness and retained material.
 points=[v['p']for t in pre for v in t];lo=Vector(tuple(min(p[i]for p in points)for i in range(3)));hi=Vector(tuple(max(p[i]for p in points)for i in range(3)));ya=52.5;yb=55.7;reveal_lo=-54.;reveal_hi=-53.720001220703125
 if yb>ya and not staff:
  for z,normal in[(cutz[0],Vector((0,0,1))),(cutz[1],Vector((0,0,-1)))]:
   vs=[Vector((reveal_lo,ya,z)),Vector((reveal_hi,ya,z)),Vector((reveal_hi,yb,z)),Vector((reveal_lo,yb,z))]
   if (vs[1]-vs[0]).cross(vs[2]-vs[0]).dot(normal)<0:vs.reverse()
   for ids in[(0,1,2),(0,2,3)]:triangles.append([{'p':vs[i],'n':normal,'uv':Vector((vs[i].x,vs[i].y))}for i in ids])
  if lo.y<55.7<hi.y:
   vs=[Vector((reveal_lo,55.7,cutz[0])),Vector((reveal_hi,55.7,cutz[0])),Vector((reveal_hi,55.7,cutz[1])),Vector((reveal_lo,55.7,cutz[1]))];normal=Vector((0,-1,0))
   if (vs[1]-vs[0]).cross(vs[2]-vs[0]).dot(normal)<0:vs.reverse()
   for ids in[(0,1,2),(0,2,3)]:triangles.append([{'p':vs[i],'n':normal,'uv':Vector((vs[i].x,vs[i].z))}for i in ids])
 flat=[v for t in triangles for v in t];mesh=bpy.data.meshes.new(name+'_PORT_FORE404_GATEWAY');mesh.from_pydata([blender(v['p'])for v in flat],[],[tuple(range(i,i+3))for i in range(0,len(flat),3)]);mesh.update();new=bpy.data.objects.new(name+'_PORT_FORE404_GATEWAY',mesh);bpy.context.collection.objects.link(new)
 for mat in obj.data.materials:mesh.materials.append(mat)
 uv=mesh.uv_layers.new(name='UVMap')
 for i,v in enumerate(flat):uv.data[i].uv=v['uv']
 for p in mesh.polygons:p.use_smooth=True
 mesh.normals_split_custom_set([blender(v['n']).normalized()for v in flat]);made.append(new);rows.append({'source_name':name,'replacement_name':new.name,'source_triangles':len(pre),'replacement_triangles':len(triangles),'input_bounds_local':[list(lo),list(hi)],'source_file':'AST-AQU-016.glb','source_origin':[0,0,0]})

for obj in list(bpy.data.objects):
 if obj not in made:bpy.data.objects.remove(obj,do_unlink=True)
B=lambda p:Vector((p[0],-p[2],p[1]));GV=lambda p:Vector((p.x,p.z,-p.y));origin=Vector((0,0,0))
for o,row in zip(made,rows):o.location=B(row["source_origin"])
R=G.parent;donor=R/plan['source_native'];assert hashlib.sha256(donor.read_bytes()).hexdigest()==plan['source_native_sha256'];source=json.loads((G/'data/architecture/group8/orchard_service.json').read_text());names=[r['name']for r in source['meshes']if r['unit']=='CleanDeliveryTask']
with bpy.data.libraries.load(str(donor),link=False)as(df,dt):dt.objects=names;dt.materials=[n for n in df.materials if n in ['ASTRAEA_staff_zinc','ASTRAEA_staff_white_paint','ASTRAEA_staff_bluegrey_paint','ASTRAEA_dark_rubber']]
col=bpy.data.collections.new('PORT_FORE404_RECEIVER_AUTHORING_R001');bpy.context.scene.collection.children.link(col);parts=[];clones=[];lights=[]
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
def box(name,lo,hi,material):return prism(name,[(lo[0],lo[2]),(hi[0],lo[2]),(hi[0],hi[2]),(lo[0],hi[2])],lo[1],hi[1],material)
def line(name,a,b,width,lo,hi,material):
 a,b=Vector(a),Vector(b);u=Vector((-(b-a).y,(b-a).x)).normalized()*width/2;return prism(name,[a-u,b-u,b+u,a+u],lo,hi,material)

blue=bpy.data.materials['ASTRAEA_staff_bluegrey_paint'];zinc=bpy.data.materials['ASTRAEA_staff_zinc'];white=bpy.data.materials['ASTRAEA_staff_white_paint']
box('PFR_ReceivingFloor',(-60.49995,52.26,-405),(-54.00005,52.5,-401.4),blue)
prism('PFR_SourceJoinedCanopy',[(-60.39995,-405),(-53.8,-405),(-53.8,-401.4),(-60.49995,-401.4),(-60.49995,-402.99995),(-60.39995,-402.99995)],56.05,56.23,white)
def wall(name,a,b):
 for tag,width,lo,hi,material in [('Toe',.14,52.5,52.64,zinc),('Dado',.12,52.64,53.55,blue),('Reveal',.15,53.55,53.62,zinc),('Enamel',.12,53.62,55.45,white),('Cove',.18,55.45,56.05,white)]:line(name+'_'+tag,a,b,width,lo,hi,material)
wall('PFR_NorthSide',(-60.35,-404.9),(-53.8,-404.9));wall('PFR_SouthSide',(-60.35,-401.5),(-53.8,-401.5));bearings=[]
for label,x,owner in [('Staff',-60.5,'STAFFLINK_D09_PF404__floor'),('Market',-54.,'D09_orchard_market_gallery')]:
 for i,z in enumerate([-404.5,-403.2,-401.9]):
  name=f'PFR_{label}EmbeddedTie{i}';box(name,(x-.3,52.28,z-.12),(x+.3,52.36,z+.12),zinc);bearings.append({'name':name,'source_region':owner,'point':[x+(-.15 if label=='Staff'else .15),52.5,z]})
for i,z in enumerate([-404.7,-403.3]):
 name=f'PFR_ExistingRoofEmbeddedSplice{i}';box(name,(-60.55,56.08,z-.08),(-60.25,56.16,z+.08),zinc);bearings.append({'name':name,'source_region':'STAFFLINK_D09_PF404','point':[-60.5,56.18,z]})
# One compact original task fitting is positively wall mounted, with source lens/UV/image payloads intact.
transform=Matrix.Translation(B((-57.3,55.6,-403.97)))@Matrix.Rotation(math.pi/2,4,'Z')@Matrix.Translation(-B((52.96,64.2,-228)));objs=[]
for src in dt.objects:
 o=src.copy();o.data=src.data;o.parent=None;o.matrix_world=transform@src.matrix_world;o.name='PFR_Task__'+src.name;col.objects.link(o);parts.append(o);objs.append(o);clones.append({'name':o.name,'source':src.name,'rigid_matrix_blender':[list(r)for r in transform]})
lr=next(l for l in source['lights']if l['name']=='G8O_LIGHT_CleanDeliveryTask');lens=next(o for o in objs if o.name.endswith('_Lens'));lights.append({'name':'PFR_TaskLight','at':list(GV(transform@B(lr['at']))),'colour':lr['colour'],'energy':lr['energy'],'range':lr['range'],'lens':lens.name})
for o in dt.objects:bpy.data.objects.remove(o,do_unlink=True)
for image in bpy.data.images:
 if image.source=='FILE'and not image.packed_file:image.pack()
bpy.data.texts.new('EXACT_SOURCE_POLICY.json').write(json.dumps(plan,indent=2));bounds=[]
for o in parts:
 o.data.calc_loop_triangles();ps=[GV(o.matrix_world@Vector(v))for v in o.bound_box];bounds.append({'name':o.name,'min':[min(p[i]for p in ps)for i in range(3)],'max':[max(p[i]for p in ps)for i in range(3)],'triangles':len(o.data.loop_triangles)})
# Retain editable components; runtime batches combine only new receiving parts by material/collision class.
runtime=bpy.data.collections.new('PORT_FORE404_RECEIVER_RUNTIME_R001');bpy.context.scene.collection.children.link(runtime);groups={};batchrows=[]
for o in parts:
 for polygon in o.data.polygons:
  material=o.data.materials[polygon.material_index];key=(material.name,'Lens'not in o.name);g=groups.setdefault(key,{'vs':[],'fs':[],'uvs':[],'members':set()});g['members'].add(o.name);ix=[]
  for li in polygon.loop_indices:
   ix.append(len(g['vs']));g['vs'].append(tuple(o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co));g['uvs'].append(tuple(o.data.uv_layers.active.data[li].uv))
  g['fs'].append(ix)
for i,(key,g)in enumerate(sorted(groups.items())):
 name=f'ORX_BATCH_{i:03d}';data=bpy.data.meshes.new(name);data.from_pydata(g['vs'],[],g['fs']);data.update();data.materials.append(bpy.data.materials[key[0]]);uv=data.uv_layers.new(name='UVMap')
 for li in range(len(data.loops)):uv.data[li].uv=g['uvs'][data.loops[li].vertex_index]
 o=bpy.data.objects.new(name,data);runtime.objects.link(o);ps=[GV(Vector(v))for v in o.bound_box];batchrows.append({'name':name,'material':key[0],'collide':key[1],'members':sorted(g['members']),'min':[min(p[j]for p in ps)for j in range(3)],'max':[max(p[j]for p in ps)for j in range(3)]})
for row in lights:row['lens_batch']=next(b['name']for b in batchrows if row['lens']in b['members'])
I=D/'import/Game/assets/port_fore404_receiving_20261015';I.mkdir(parents=True,exist_ok=True);model=I/'PORT_FORE404_RECEIVER_r001.glb';bpy.ops.object.select_all(action='DESELECT')
for o in list(runtime.objects)+made:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(model),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False);col.hide_render=True;N=D/'native';N.mkdir(exist_ok=True);native=N/'PORT_FORE404_RECEIVER_r001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.wm.open_mainfile(filepath=str(native));fresh=D/'FRESH_REEXPORT_r001.glb';bpy.ops.export_scene.gltf(filepath=str(fresh),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(fresh)==sha(model)and sha(src if isinstance(src,Path)else G/'assets/models/AST-AQU-016.glb')==expected
receipt={'status':'PASS_NATIVE_EXACT_FRESH_EXPORT_CANDIDATE','file':model.name,'source_file':'AST-AQU-016.glb','source_sha256':expected,'native_sha256':sha(native),'model_sha256':sha(model),'walls':rows,'batches':batchrows,'bounds':bounds,'lights':lights,'rigid_clones':clones,'authoring_meshes':len(parts)+len(made),'runtime_meshes':len(batchrows)+len(made),'source_pins':plan['source_pins'],'new_floor_area_m2':plan['new_floor_projected_m2'],'source_bearings':bearings,'new_room_ids_capacity_or_lift_stops':0,'operational_or_final_acceptance':False};(D/'NATIVE_VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS_PORT_FORE404_NATIVE',receipt['authoring_meshes'],receipt['runtime_meshes'],len(lights))
