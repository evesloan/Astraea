from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
from mathutils.geometry import tessellate_polygon
D=Path(__file__).resolve().parent;G=Path('/workspace/Astraea/Game');plan=json.loads((D/'NATIVE_PLAN.json').read_text());assert bpy.app.version[:3]==(4,3,2)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);made=[];rows=[]
B=lambda p:Vector((p[0],-p[2],p[1]));GV=lambda p:Vector((p.x,p.z,-p.y));origin=Vector((8,61,-250))

R=G.parent;donor=R/plan['source_native'];assert hashlib.sha256(donor.read_bytes()).hexdigest()==plan['source_native_sha256'];source=json.loads((G/'data/architecture/group8/orchard_service.json').read_text());hoodrows=[r for r in source['meshes']if r['unit']=='NorthFinish_Hood'];hoodnames=[r['name']for r in hoodrows]
with bpy.data.libraries.load(str(donor),link=False)as(data_from,data_to):
 data_to.objects=hoodnames;data_to.materials=[n for n in data_from.materials if n in ['ASTRAEA_staff_zinc','ASTRAEA_staff_white_paint','ASTRAEA_staff_bluegrey_paint','ASTRAEA_dark_rubber']]
col=bpy.data.collections.new('OBSERVATION_CAFE_SERVICE_RECEIVING_AUTHORING_R001');bpy.context.scene.collection.children.link(col);parts=[];clones=[];lights=[]
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
def wall(name,a,b):
 if (Vector(a)-Vector(b)).length<.001:return
 for suffix,w,lo,hi,material in[('Toe',.14,61,61.14,zinc),('Dado',.12,61.14,62.05,blue),('Reveal',.15,62.05,62.12,metal),('Enamel',.12,62.12,64.55,white),('Cove',.18,64.55,64.82,white)]:line(name+'_'+suffix,a,b,w,lo,hi,material)
def girder(name,a,b):
 for suffix,w,lo,hi in[('Lower',.18,60.54,60.58),('Web',.035,60.57,60.79),('Upper',.18,60.78,60.82)]:line(name+'_'+suffix,a,b,w,lo,hi,metal)

outline=plan['floor_outline_xz'];prism('OCS_MissingOnlyFloor',outline,60.76,61,blue);prism('OCS_SourceJoinedRoof',outline,64.8,64.98,white)
for i,(a,b)in enumerate(zip(outline,outline[1:]+outline[:1])):
 if abs(a[0]-54)<.001 and abs(b[0]-54)<.001:continue
 if abs(a[0]-4)<.001 and abs(b[0]-4)<.001:
  wall('OCS_AxialReturn0',(4,390),(4,390.3));wall('OCS_AxialReturn1',(4,393.7),(4,394));line('OCS_AxialHeader',(4,390.3),(4,393.7),.18,64.2,64.82,white);continue
 a,b=Vector(a),Vector(b);n=max(1,math.ceil((b-a).length/5))
 for j in range(n):wall(f'OCS_Edge{i}_{j}',a.lerp(b,j/n),a.lerp(b,(j+1)/n))
 girder(f'OCS_EdgeGirder{i}',a,b)
for j,z in enumerate([430.7,432.,433.3]):box(f'OCS_EmbeddedDiningTie{j}',(53.7,60.78,z-.12),(54.3,60.86,z+.12),metal)
for j,z in enumerate([390.7,392.,393.3]):box(f'OCS_EmbeddedAxialTie{j}',(3.7,60.78,z-.12),(4.3,60.86,z+.12),metal)
for j in range(16):girder(f'OCS_AxialCross{j}',(4+j*4,390.1),(4+j*4,393.9))
for j in range(11):girder(f'OCS_GalleryCross{j}',(60,394+j*3.8),(64,394+j*3.8))
for j,z in enumerate([430.5,432.,433.5]):girder(f'OCS_GatewayCross{j}',(54,z),(64,z))
# Four rigid source-profile task hoods light the approach without changing the original stock or kitchen fixtures.
for i,target in enumerate([(59,64.1,432),(62,64.1,418),(62,64.1,402),(42,64.1,392),(16,64.1,392)]):
 transform=Matrix.Translation(B(target))@Matrix.Rotation(-math.pi/2 if i in [1,2] else 0,4,'Z')@Matrix.Translation(-B((34,64.1,-228.53)));madehood=[]
 for src in data_to.objects:
  o=src.copy();o.data=src.data;o.parent=None;o.matrix_world=transform@src.matrix_world;o.name=f'OCS_Hood{i}__'+src.name;col.objects.link(o);parts.append(o);madehood.append(o);clones.append({'name':o.name,'source':src.name,'rigid_matrix_blender':[list(r)for r in transform]})
 for row in source['lights']:
  if row['name']not in ['G8O_LIGHT_NorthFinish_Hood_-1','G8O_LIGHT_NorthFinish_Hood_1']:continue
  suffix=str(row['name']).split('_')[-1];lens=next(o for o in madehood if o.name.endswith('Lens'+suffix));lights.append({'name':f'OCS_LIGHT_{i}_{suffix}','at':list(GV(transform@B(row['at']))),'colour':row['colour'],'energy':row['energy'],'range':row['range'],'lens':lens.name})
for src in data_to.objects:bpy.data.objects.remove(src,do_unlink=True)
for image in bpy.data.images:
 if image.source=='FILE'and not image.packed_file:image.pack()
bpy.data.texts.new('EXACT_SOURCE_POLICY.json').write(json.dumps(plan,indent=2));bounds=[]
for o in parts:
 o.data.calc_loop_triangles();ps=[GV(o.matrix_world@Vector(v))for v in o.bound_box];bounds.append({'name':o.name,'min':[min(p[i]for p in ps)for i in range(3)],'max':[max(p[i]for p in ps)for i in range(3)],'triangles':len(o.data.loop_triangles)})
# Retain editable components; runtime batches combine only new receiving parts by material/collision class.
runtime=bpy.data.collections.new('OBSERVATION_CAFE_SERVICE_RECEIVING_RUNTIME_R001');bpy.context.scene.collection.children.link(runtime);groups={};batchrows=[]
for o in parts:
 for polygon in o.data.polygons:
  material=o.data.materials[polygon.material_index];key=(material.name,'Lens'not in o.name);g=groups.setdefault(key,{'vs':[],'fs':[],'uvs':[],'members':set()});g['members'].add(o.name);ix=[]
  for li in polygon.loop_indices:
   ix.append(len(g['vs']));g['vs'].append(tuple(o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co));g['uvs'].append(tuple(o.data.uv_layers.active.data[li].uv))
  g['fs'].append(ix)
for i,(key,g)in enumerate(sorted(groups.items())):
 name=f'OCS_BATCH_{i:03d}';data=bpy.data.meshes.new(name);data.from_pydata(g['vs'],[],g['fs']);data.update();data.materials.append(bpy.data.materials[key[0]]);uv=data.uv_layers.new(name='UVMap')
 for li in range(len(data.loops)):uv.data[li].uv=g['uvs'][data.loops[li].vertex_index]
 o=bpy.data.objects.new(name,data);runtime.objects.link(o);ps=[GV(Vector(v))for v in o.bound_box];batchrows.append({'name':name,'material':key[0],'collide':key[1],'members':sorted(g['members']),'min':[min(p[j]for p in ps)for j in range(3)],'max':[max(p[j]for p in ps)for j in range(3)]})
for row in lights:row['lens_batch']=next(b['name']for b in batchrows if row['lens']in b['members'])
I=D/'exports';I.mkdir(parents=True,exist_ok=True);model=I/'OBSERVATION_CAFE_SERVICE_RECEIVER_r001.glb';bpy.ops.object.select_all(action='DESELECT')
for o in list(runtime.objects)+made:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(model),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False);col.hide_render=True;N=D/'source';N.mkdir(exist_ok=True);native=N/'OBSERVATION_CAFE_SERVICE_RECEIVER_r001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.wm.open_mainfile(filepath=str(native));fresh=D/'FRESH_REEXPORT.glb';bpy.ops.export_scene.gltf(filepath=str(fresh),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(fresh)==sha(model)
receipt={'status':'PASS_NATIVE_EXACT_FRESH_EXPORT_CANDIDATE','file':model.name,'native_sha256':sha(native),'model_sha256':sha(model),'walls':rows,'batches':batchrows,'bounds':bounds,'lights':lights,'rigid_clones':clones,'authoring_meshes':len(parts),'runtime_meshes':len(batchrows),'source_pins':plan['source_pins'],'new_floor_area_m2':plan['new_floor_area_m2'],'native_file':native.name,'new_room_ids_capacity_or_lift_stops':0,'operational_or_final_acceptance':False};(D/'NATIVE_VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS_OBSERVATION_NATIVE',receipt['authoring_meshes'],receipt['runtime_meshes'],len(lights))
