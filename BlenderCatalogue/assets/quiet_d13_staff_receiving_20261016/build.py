from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
from mathutils.geometry import tessellate_polygon
D=Path(__file__).resolve().parent;R=Path('/workspace/Astraea');p=json.loads((D/'PLAN.json').read_text());bpy.context.preferences.filepaths.save_version=0
for f,h in p['source_pins'].items():assert hashlib.sha256((R/f).read_bytes()).hexdigest()==h
bpy.ops.wm.open_mainfile(filepath=str(R/'BlenderCatalogue/assets/quiet_d15_staff_receiving_20261016/QuietD15StaffReceiving_r001.blend'))
parts=[o for o in bpy.data.objects if o.type=='MESH'];col=bpy.context.collection;B=lambda p:Vector((p[0],-p[2],p[1]));GV=lambda p:Vector((p.x,p.z,-p.y));metal=bpy.data.materials['ASTRAEA_staff_zinc'];white=bpy.data.materials['ASTRAEA_staff_white_paint'];blue=bpy.data.materials['ASTRAEA_staff_bluegrey_paint']
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

for i,x in enumerate([20,21,22]):box(f'Q13_LobbySlabTie{i}',(x-.09,92.80,-484.3),(x+.09,92.91,-483.7),metal)
for i,x in enumerate([42.7,43.8,45]):box(f'Q13_HouseSlabTie{i}',(x-.09,92.80,-482.5),(x+.09,92.91,-481.9),metal)
for i,(x,z)in enumerate([(19.45,-482.35),(23.36,-485.47),(41.99,-482.33),(45.55,-485.47)]):box(f'Q13_RoofBearingPost{i}',(x-.07,92.90,z-.07),(x+.07,95.90,z+.07),metal)
# Retained fixture meshes are rigid clones, with their native image payloads intact.
donor=json.loads((R/'BlenderCatalogue/assets/cinema1_receiving_20261016/NATIVE_PLAN.json').read_text());native=R/donor['source_native'];assert hashlib.sha256(native.read_bytes()).hexdigest()==donor['source_native_sha256'];source=json.loads((R/'Game/data/architecture/group8/orchard_service.json').read_text());names=[r['name']for r in source['meshes']if r['unit']=='NorthFinish_Hood']
with bpy.data.libraries.load(str(native),link=False)as(a,b):b.objects=names
clones=[];lights=[]
for i,x in enumerate([29,37]):
 transform=Matrix.Translation(B((x,95.1,-483.9)))@Matrix.Translation(-B((34,64.1,-228.53)));objs=[]
 for src in b.objects:
  o=src.copy();o.data=src.data;o.parent=None;o.matrix_world=transform@src.matrix_world;o.name=f'Q13_Hood{i}__'+src.name;col.objects.link(o);parts.append(o);objs.append(o);clones.append({'name':o.name,'source':src.name,'rigid_matrix_blender':[list(r)for r in transform]})
 for row in source['lights']:
  if row['name']not in ['G8O_LIGHT_NorthFinish_Hood_-1','G8O_LIGHT_NorthFinish_Hood_1']:continue
  suffix=row['name'].split('_')[-1];lights.append({'name':f'Q13_LIGHT{i}_{suffix}','at':list(GV(transform@B(row['at']))),'colour':row['colour'],'energy':row['energy'],'range':row['range'],'lens':next(o.name for o in objs if o.name.endswith('Lens'+suffix))})
for o in b.objects:bpy.data.objects.remove(o,do_unlink=True)
for i,x in enumerate([26.22,31.78,34.22,39.78]):box(f'Q13_FixtureRoofSocket{i}',(x-.09,95.795,-483.99),(x+.09,95.86,-483.81),metal)
box('Q13_LobbyRevealLeft',(19.575,93,-484.155),(19.605,95.73,-483.985),metal)
box('Q13_LobbyRevealRight',(22.795,93,-484.155),(22.825,95.73,-483.985),metal)
box('Q13_LobbyRevealHeader',(19.575,95.69,-484.155),(22.825,95.73,-483.985),metal)
for i,x in enumerate([42.25,45.5]):box(f'Q13_GuardCutCap{i}',(x-.005,94.055,-482.237),(x+.005,94.145,-482.162),metal)
placement=Matrix.Translation(Vector((0,0,-9.0)))
for o in parts:o.matrix_world=placement@o.matrix_world;o.name=o.name.replace('Q15_','Q13_')
for row in clones:row['rigid_matrix_blender']=[list(v)for v in placement@Matrix(row['rigid_matrix_blender'])]
for row in lights:row['at'][1]-=9.0
# Import each immutable owner separately and clip only the exact selected world-space boxes.
def clip(poly,axis,plane,less):
 if not poly:return []
 out=[];s=poly[-1];ds=s['p'][axis]-plane
 for e in poly:
  de=e['p'][axis]-plane;ins=ds<=0 if less else ds>=0;ine=de<=0 if less else de>=0
  if ins!=ine:
   t=ds/(ds-de);out.append({k:s[k].lerp(e[k],t)for k in ['p','uv']})
  if ine:out.append(e)
  s=e;ds=de
 return out
walls=[];patches=[];evidence=[]
for path in sorted(set(r['path']for r in p['walls'])):
 previous=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(R/path));imported=set(bpy.data.objects)-previous
 for row in [r for r in p['walls']if r['path']==path]:
  o=next(o for o in imported if o.name==row.get('import_name',row['name']));o.data.calc_loop_triangles();old=[];new=[]
  for t in o.data.loop_triangles:
   poly=[{'p':GV(o.matrix_world@o.data.vertices[vi].co),'uv':o.data.uv_layers.active.data[li].uv.copy()}for vi,li in zip(t.vertices,t.loops)];old.append(poly);remaining=[poly]
   for cut in [{'min':row['cut_min'],'max':row['cut_max']}]+row.get('additional_cuts',[]):
    next_remaining=[]
    for piece in remaining:
     inside=piece
     for axis in range(3):
      for plane,less in [(cut['min'][axis],False),(cut['max'][axis],True)]:
       outside=clip(inside,axis,plane,not less)
       if len(outside)>=3:next_remaining.append(outside)
       inside=clip(inside,axis,plane,less)
    remaining=next_remaining
   for poly in remaining:
    for i in range(1,len(poly)-1):
     tri=[poly[0],poly[i],poly[i+1]]
     if (tri[1]['p']-tri[0]['p']).cross(tri[2]['p']-tri[0]['p']).length>1e-9:new.append(tri)
  flat=[v for t in new for v in t];data=bpy.data.meshes.new('PATCH_'+row['name']);data.from_pydata([B(v['p'])for v in flat],[],[tuple(range(i,i+3))for i in range(0,len(flat),3)]);data.update()
  for m in o.data.materials:data.materials.append(m)
  uv=data.uv_layers.new(name='UVMap')
  for i,v in enumerate(flat):uv.data[i].uv=v['uv']
  obj=bpy.data.objects.new('PATCH_'+row['name'],data);col.objects.link(obj);patches.append(obj);bounds=[GV(o.matrix_world@Vector(v))for v in o.bound_box];walls.append(dict(row,replacement_name=obj.name,source_triangles=len(old),replacement_triangles=len(new),min=[min(v[i]for v in bounds)for i in range(3)],max=[max(v[i]for v in bounds)for i in range(3)]))
  evidence.append({'name':row['name'],'cut_min':row['cut_min'],'cut_max':row['cut_max'],'additional_cuts':row.get('additional_cuts',[]),'before':[[{'p':list(v['p']),'uv':list(v['uv'])}for v in t]for t in old],'after':[[{'p':list(v['p']),'uv':list(v['uv'])}for v in t]for t in new]})
 for o in imported:bpy.data.objects.remove(o,do_unlink=True)
(D/'PATCH_TRIANGLES.json').write_text(json.dumps(evidence)+'\n')
# New components are retained individually in the native; no original model is overwritten.
for image in bpy.data.images:
 if image.source=='FILE'and not image.packed_file:image.pack()
bounds=[]
for o in parts:
 vs=[GV(o.matrix_world@Vector(v))for v in o.bound_box];bounds.append({'name':o.name,'min':[min(v[i]for v in vs)for i in range(3)],'max':[max(v[i]for v in vs)for i in range(3)],'collide':'Lens'not in o.name})
bpy.ops.object.select_all(action='DESELECT')
for o in parts+patches:o.select_set(True)
model=D/'QUIET_D13_STAFF_RECEIVING_r001.glb';bpy.ops.export_scene.gltf(filepath=str(model),export_format='GLB',use_selection=True,export_yup=True,export_extras=False);nativeout=D/'QuietD13StaffReceiving_r001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(nativeout),compress=True)
receipt={'file':model.name,'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'native_sha256':hashlib.sha256(nativeout.read_bytes()).hexdigest(),'source_pins':p['source_pins'],'walls':walls,'parts':bounds,'lights':lights,'rigid_clones':clones,'fixture_source_native':donor['source_native'],'fixture_source_native_sha256':donor['source_native_sha256'],'floor_m2':p['new_floor_area_m2'],'status':'CANDIDATE_NOT_INSTALLED'};(D/'RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print('EXPORTED',len(parts),len(walls),len(lights))
