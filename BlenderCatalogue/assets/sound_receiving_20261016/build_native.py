from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
from mathutils.geometry import tessellate_polygon
D=Path(__file__).resolve().parent;G=Path('/workspace/Astraea/Game');plan=json.loads((D/'NATIVE_PLAN.json').read_text());assert bpy.app.version[:3]==(4,3,2)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);made=[];rows=[]
B=lambda p:Vector((p[0],-p[2],p[1]));GV=lambda p:Vector((p.x,p.z,-p.y));origin=Vector((0,0,0))

# Bounded successor of the exact installed Sound north wall.
src=G/'assets/models/SOL_D11_directory_12_source001.glb';assert hashlib.sha256(src.read_bytes()).hexdigest()==plan['source_pins']['assets/models/SOL_D11_directory_12_source001.glb'];bpy.ops.import_scene.gltf(filepath=str(src))
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
 for axis,plane,less in[(1,69.5,False),(1,72.7,True),(0,-23.2,False),(0,-20.8,True)]:
  outside=clip(inside,axis,plane,not less)
  if len(outside)>=3:pieces.append(outside)
  inside=clip(inside,axis,plane,less)
  if not inside:break
 return pieces
for name,zlo,zhi,top in[('E_outer_north',465.68,465.92,76.4)]:
 obj=bpy.data.objects[name];obj.data.calc_loop_triangles();pre=[]
 for t in obj.data.loop_triangles:pre.append([{'p':GV(obj.matrix_world@obj.data.vertices[vi].co),'uv':obj.data.uv_layers.active.data[li].uv.copy()if obj.data.uv_layers.active else Vector((0.,0.))}for vi,li in zip(t.vertices,t.loops)])
 polys=[part for poly in pre for part in cut(poly)];triangles=[(poly[0],poly[i],poly[i+1])for poly in polys for i in range(1,len(poly)-1)];head=min(72.7,top)
 for x,n in[(-23.2,Vector((1,0,0))),(-20.8,Vector((-1,0,0)))]:
  vs=[Vector((x,69.5,zlo)),Vector((x,69.5,zhi)),Vector((x,head,zhi)),Vector((x,head,zlo))]
  if (vs[1]-vs[0]).cross(vs[2]-vs[0]).dot(n)<0:vs.reverse()
  triangles += [[{'p':vs[i],'uv':Vector((vs[i].z,vs[i].y))}for i in ids]for ids in[(0,1,2),(0,2,3)]]
 if top>72.7:
  vs=[Vector((-23.2,72.7,zlo)),Vector((-20.8,72.7,zlo)),Vector((-20.8,72.7,zhi)),Vector((-23.2,72.7,zhi))]
  if (vs[1]-vs[0]).cross(vs[2]-vs[0]).y>0:vs.reverse()
  triangles += [[{'p':vs[i],'uv':Vector((vs[i].x,vs[i].z))}for i in ids]for ids in[(0,1,2),(0,2,3)]]
 flat=[v for t in triangles for v in t];matrix=obj.matrix_world.copy();inverse=matrix.inverted();data=bpy.data.meshes.new('ISR_SUCCESSOR_'+name);data.from_pydata([inverse@B(v['p'])for v in flat],[],[tuple(range(i,i+3))for i in range(0,len(flat),3)]);data.update()
 for mat in obj.data.materials:data.materials.append(mat)
 uv=data.uv_layers.new(name='UVMap')
 for i,v in enumerate(flat):uv.data[i].uv=v['uv']
 new=bpy.data.objects.new('ISR_SUCCESSOR_'+name,data);bpy.context.collection.objects.link(new);new.matrix_world=matrix;made.append(new);pts=[GV(v.co)for v in obj.data.vertices]
 rows.append({'source_name':name,'replacement_name':new.name,'source_triangles':len(pre),'replacement_triangles':len(triangles),'source_local_translation':list(GV(matrix.translation)),'input_bounds_local':[[min(v[i]for v in pts)for i in range(3)],[max(v[i]for v in pts)for i in range(3)]],'reveal_z':[zlo,zhi],'source_top_y':top})
for o in list(bpy.data.objects):
 if o not in made:bpy.data.objects.remove(o,do_unlink=True)
R=G.parent;donor=R/plan['source_native'];assert hashlib.sha256(donor.read_bytes()).hexdigest()==plan['source_native_sha256'];source=json.loads((G/'data/architecture/group8/orchard_service.json').read_text());hoodrows=[r for r in source['meshes']if r['unit']=='NorthFinish_Hood'];hoodnames=[r['name']for r in hoodrows]
with bpy.data.libraries.load(str(donor),link=False)as(data_from,data_to):
 data_to.objects=hoodnames;data_to.materials=[n for n in data_from.materials if n in ['ASTRAEA_staff_zinc','ASTRAEA_staff_white_paint','ASTRAEA_staff_bluegrey_paint','ASTRAEA_dark_rubber']]
col=bpy.data.collections.new('SOUND_SERVICE_RECEIVING_AUTHORING_R001');bpy.context.scene.collection.children.link(col);parts=[];clones=[];lights=[]
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
 for suffix,w,lo,hi in[('Lower',.18,77.54,77.58),('Web',.035,77.57,77.79),('Upper',.18,77.78,77.82)]:line(name+'_'+suffix,a,b,w,lo,hi,metal)

outline=[[4.00005,181.8],[23.8,181.8],[23.8,184.79995],[4.00005,184.79995]];prism('ISR_MissingOnlyFloor',outline,77.76,78,blue);prism('ISR_SourceJoinedRoof',outline,81.8,81.98,white)
for i,(a,b)in enumerate(zip(outline,outline[1:]+outline[:1])):
 if abs(a[1]-184.8)<.001 and abs(b[1]-184.8)<.001:
  wall('ISR_NorthReturn',(20.2,184.64),(4.00005,184.64));girder('ISR_NorthGirder',(4.00005,184.65),(23.8,184.65));continue
 if abs(a[0]-4)<.001 and abs(b[0]-4)<.001:
  wall('ISR_AxialReturn0',(4,181.8),(4,182.05));wall('ISR_AxialReturn1',(4,184.45),(4,184.79995));line('ISR_AxialHeader',(4,182.05),(4,184.45),.18,81.2,81.82,white);continue
 a,b=Vector(a),Vector(b);n=max(1,math.ceil((b-a).length/5))
 for j in range(n):wall(f'ISR_Edge{i}_{j}',a.lerp(b,j/n),a.lerp(b,(j+1)/n))
 girder(f'ISR_EdgeGirder{i}',a,b)
# Fitted end pieces span the measured original floor edge to its actual wall face.
for k,x in enumerate([23.8,20.2]):wall(f'ISR_SourceWallJoin{k}',(x,184.64),(x,184.885))
box('ISR_SourceRoofJoin',(23.8,81.8,184.79995),(20.2,81.98,184.885),white)
for j,x in enumerate([23.0,22.0,21.0]):box(f'ISR_EmbeddedRoomTie{j}',(x-.1,77.78,184.45),(x+.1,77.86,185.05),metal)
for j,z in enumerate([182.3,183.25,184.2]):box(f'ISR_EmbeddedAxialTie{j}',(4.3,77.78,z-.12),(3.7,77.86,z+.12),metal)
for j in range(6):girder(f'ISR_AxialCross{j}',(4+j*3.92,181.9),(4+j*3.92,184.65))
for k,(za,zb,ya,yb)in enumerate([(184.15,184.55,78.003,78.028),(184.55,184.95,78.028,78.028),(184.95,185.35,78.028,78.003)]):
 o=box(f'ISR_Threshold_Leaf{k}',(23.0,ya-.003,za),(21.0,ya,zb),metal)
 for v in o.data.vertices:v.co.z+=(-v.co.y-za)/(zb-za)*(yb-ya)
 o.data.update()
for k,z in enumerate([184.6,184.9]):box(f'ISR_Threshold_EmbeddedBearing{k}',(22.9,77.9,z-.045),(21.1,78.025,z+.045),metal)
for i,target in enumerate([(9,81.1,183.25),(19,81.1,183.25)]):
 transform=Matrix.Translation(B(target))@Matrix.Identity(4)@Matrix.Translation(-B((34,64.1,-228.53)));madehood=[]
 for src in data_to.objects:
  o=src.copy();o.data=src.data;o.parent=None;o.matrix_world=transform@src.matrix_world;o.name=f'ISR_Hood{i}__'+src.name;col.objects.link(o);parts.append(o);madehood.append(o);clones.append({'name':o.name,'source':src.name,'rigid_matrix_blender':[list(r)for r in transform]})
 for row in source['lights']:
  if row['name']not in ['G8O_LIGHT_NorthFinish_Hood_-1','G8O_LIGHT_NorthFinish_Hood_1']:continue
  suffix=str(row['name']).split('_')[-1];lens=next(o for o in madehood if o.name.endswith('Lens'+suffix));lights.append({'name':f'ISR_LIGHT_{i}_{suffix}','at':list(GV(transform@B(row['at']))),'colour':row['colour'],'energy':row['energy'],'range':row['range'],'lens':lens.name})
for src in data_to.objects:bpy.data.objects.remove(src,do_unlink=True)
# Rigid180-degree plan turn and deck translation place the receiving family north of Sound.
placement=Matrix.Translation(Vector((0,-650.8,-8.5)))@Matrix.Rotation(math.pi,4,'Z')
for o in parts:o.matrix_world=placement@o.matrix_world
for row in clones:row['rigid_matrix_blender']=[list(v)for v in placement@Matrix(row['rigid_matrix_blender'])]
for row in lights:row['at']=list(GV(placement@B(row['at'])))
for image in bpy.data.images:
 if image.source=='FILE'and not image.packed_file:image.pack()
bpy.data.texts.new('EXACT_SOURCE_POLICY.json').write(json.dumps(plan,indent=2));bounds=[]
for o in parts:
 o.data.calc_loop_triangles();ps=[GV(o.matrix_world@Vector(v))for v in o.bound_box];bounds.append({'name':o.name,'min':[min(p[i]for p in ps)for i in range(3)],'max':[max(p[i]for p in ps)for i in range(3)],'triangles':len(o.data.loop_triangles)})
# Retain editable components; runtime batches combine only new receiving parts by material/collision class.
runtime=bpy.data.collections.new('SOUND_SERVICE_RECEIVING_RUNTIME_R001');bpy.context.scene.collection.children.link(runtime);groups={};batchrows=[]
for o in parts:
 for polygon in o.data.polygons:
  material=o.data.materials[polygon.material_index];key=(material.name,'Lens'not in o.name);g=groups.setdefault(key,{'vs':[],'fs':[],'uvs':[],'members':set()});g['members'].add(o.name);ix=[]
  for li in polygon.loop_indices:
   ix.append(len(g['vs']));g['vs'].append(tuple(o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co));g['uvs'].append(tuple(o.data.uv_layers.active.data[li].uv))
  g['fs'].append(ix)
for i,(key,g)in enumerate(sorted(groups.items())):
 name=f'ISR_BATCH_{i:03d}';data=bpy.data.meshes.new(name);data.from_pydata(g['vs'],[],g['fs']);data.update();data.materials.append(bpy.data.materials[key[0]]);uv=data.uv_layers.new(name='UVMap')
 for li in range(len(data.loops)):uv.data[li].uv=g['uvs'][data.loops[li].vertex_index]
 o=bpy.data.objects.new(name,data);runtime.objects.link(o);ps=[GV(Vector(v))for v in o.bound_box];batchrows.append({'name':name,'material':key[0],'collide':key[1],'members':sorted(g['members']),'min':[min(p[j]for p in ps)for j in range(3)],'max':[max(p[j]for p in ps)for j in range(3)]})
for row in lights:row['lens_batch']=next(b['name']for b in batchrows if row['lens']in b['members'])
I=D/'exports';I.mkdir(parents=True,exist_ok=True);model=I/'SOUND_SERVICE_RECEIVER_r001.glb';bpy.ops.object.select_all(action='DESELECT')
for o in list(runtime.objects)+made:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(model),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False);col.hide_render=True;N=D/'source';N.mkdir(exist_ok=True);native=N/'SOUND_SERVICE_RECEIVER_r001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.wm.open_mainfile(filepath=str(native));fresh=D/'FRESH_REEXPORT.glb';bpy.ops.export_scene.gltf(filepath=str(fresh),export_format='GLB',use_selection=True,export_yup=True,export_extras=False,export_cameras=False,export_lights=False);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(fresh)==sha(model)
receipt={'status':'PASS_NATIVE_EXACT_FRESH_EXPORT_CANDIDATE','file':model.name,'native_sha256':sha(native),'model_sha256':sha(model),'walls':rows,'batches':batchrows,'bounds':bounds,'lights':lights,'rigid_clones':clones,'authoring_meshes':len(parts),'runtime_meshes':len(batchrows),'source_pins':plan['source_pins'],'new_floor_area_m2':plan['new_floor_area_m2'],'native_file':native.name,'new_room_ids_capacity_or_lift_stops':0,'operational_or_final_acceptance':False};(D/'NATIVE_VERIFICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS_SOUND_NATIVE',receipt['authoring_meshes'],receipt['runtime_meshes'],len(lights))
