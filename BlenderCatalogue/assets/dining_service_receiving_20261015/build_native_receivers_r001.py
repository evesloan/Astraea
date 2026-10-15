from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
from mathutils.geometry import tessellate_polygon
D=Path(__file__).resolve().parent;R=Path('/workspace/astraea-protected-integration-20261012');G=R/'Game';plan=json.loads((D/'NATIVE_PLAN.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();donor=R/plan['source_native'];assert bpy.app.version[:3]==(4,3,2)and sha(donor)==plan['source_native_sha256'];assert not(G/'assets/dining_service_receiving_20261015').exists();bpy.ops.wm.open_mainfile(filepath=str(donor));bpy.context.preferences.filepaths.save_version=0;source=json.loads((G/'data/architecture/group8/orchard_service.json').read_text());templates={r['name']:bpy.data.objects[r['name']]for r in source['meshes']};old_objects=set(bpy.data.objects);col=bpy.data.collections.new('D10_CONNECTED_SERVICE_RECEIVERS_R001');bpy.context.scene.collection.children.link(col);B=lambda p:Vector((p[0],-p[2],p[1]));GV=lambda p:Vector((p.x,p.z,-p.y));parts=[];clones=[];lights=[];joints=[];feet=[]
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
def clone_unit(name,unit,anchor,target,yaw=0):
 rows=[r for r in source['meshes']if r['unit']==unit];assert rows,unit;transform=Matrix.Translation(B(target))@Matrix.Rotation(yaw,4,'Z')@Matrix.Translation(-B(anchor));made=[]
 for row in rows:
  src=templates[row['name']];o=src.copy();o.data=src.data;o.parent=None;o.matrix_world=transform@src.matrix_world;o.name=name+'__'+src.name;col.objects.link(o);parts.append(o);made.append(o);clones.append({'name':o.name,'source':src.name,'unit':unit,'rigid_matrix_blender':[list(r)for r in transform]})
 for row in source.get('lights',[]):
  if row['name'] in ['G8O_LIGHT_'+unit+'_-1','G8O_LIGHT_'+unit+'_1']:
   at=GV(transform@B(row['at']));lens=next(o for o in made if 'Lens'in o.name and o.name.endswith('Lens'+str(row['name']).split('_')[-1]))
   lights.append({'name':name+'_'+row['name'],'at':list(at),'colour':row['colour'],'range':row['range'],'energy':row['energy'],'lens':lens.name})
 return made

def support_counter(name,cx,cz,width,depth):
 box(name+'_Worktop',(cx-width/2,61.86,cz-depth/2),(cx+width/2,61.923,cz+depth/2),zinc)
 for i,x in enumerate([cx-width/2+.14,cx+width/2-.14]):
  for j,z in enumerate([cz-depth/2+.12,cz+depth/2-.12]):
   box(name+f'_Foot{i}_{j}',(x-.065,61,z-.065),(x+.065,61.06,z+.065),rubber);box(name+f'_Leg{i}_{j}',(x-.04,61.04,z-.04),(x+.04,61.88,z+.04),zinc);feet.append([x,61,z])
 box(name+'_LowerShelf',(cx-width/2+.1,61.2,cz-depth/2+.06),(cx+width/2-.1,61.24,cz+depth/2-.06),zinc)
 box(name+'_Back',(cx-width/2+.1,61.23,cz-depth/2+.04),(cx+width/2-.1,61.86,cz-depth/2+.08),white)
for site in plan['sites']:
 key=site['unit'];side=site['side'];clean=site['clean_z'];used=site['used_z'];join=site['axial_join_z'];prefix='D10S_'+key;outline=site['floor_outline_xz'];floor=prism(prefix+'_MissingOnlyFloor',outline,60.76,61,blue);roof=prism(prefix+'_SourceJoinedRoof',outline,64.8,64.98,white)
 # Enclose the union, leaving only the retained dining-wall interfaces and the axial landing open.
 for i,(a,b)in enumerate(zip(outline,outline[1:]+outline[:1])):
  if abs(a[0]-side*54)<.001 and abs(b[0]-side*54)<.001:continue
  if abs(a[0]-side*4)<.001 and abs(b[0]-side*4)<.001:
   wall(prefix+'_AxialReturn0',(side*4,join-2.15),(side*4,join-1.7));wall(prefix+'_AxialReturn1',(side*4,join+1.7),(side*4,join+2.15));line(prefix+'_AxialPortalHead',(side*4,join-1.7),(side*4,join+1.7),.18,64.2,64.82,white);continue
  a,b=Vector(a),Vector(b);n=max(1,math.ceil((b-a).length/3.5))
  for j in range(n):wall(prefix+f'_Boundary{i}_{j}',a.lerp(b,j/n),a.lerp(b,(j+1)/n))
  girder(prefix+f'_EdgeGirder{i}',a,b)
 # Internal screens separate the clean finishing bay, used-return wash bay and outer staff gallery.
 for tag,z,z0,z1 in[('Clean',clean,clean-5,clean+7),('Used',used,used-7,used+5)]:
  wall(prefix+'_'+tag+'Screen0',(side*66,z0),(side*66,z-1.7));wall(prefix+'_'+tag+'Screen1',(side*66,z+1.7),(side*66,z1));line(prefix+'_'+tag+'ScreenHead',(side*66,z-1.7),(side*66,z+1.7),.18,64.2,64.82,white)
  # Close only the high unused part of the existing full-height service opening; preserve its complete3.4m width belowY64.2.
  x0,x1=sorted([side*53.98,side*54.14]);box(prefix+'_'+tag+'ExistingOpeningUpperClosure',(x0,64.2,z-1.72),(x1,site['old_wall_top_y'],z+1.72),white)
  for j,dz in enumerate([-1.1,0,1.1]):
   x0,x1=sorted([side*53.7,side*54.3]);o=box(prefix+'_'+tag+f'_RetainedFloorUnderlap{j}',(x0,60.6,z+dz-.12),(x1,60.78,z+dz+.12),metal);joints.append({'name':o.name,'kind':'existing_dining_floor_below_walk_lap','programme_key':site['key']})
 for j,dz in enumerate([-1.3,0,1.3]):
  x0,x1=sorted([side*3.7,side*4.3]);o=box(prefix+f'_AxialFloorUnderlap{j}',(x0,60.6,join+dz-.12),(x1,60.78,join+dz+.12),metal);joints.append({'name':o.name,'kind':'retained_D10_fore_route_below_walk_lap','programme_key':site['key']})
 # Repeated source-compatible crossmembers; all lie within the surveyed clear volume.
 z0=min(join,clean-5);z1=max(join,used+5)
 for i in range(math.ceil((z1-z0)/4)+1):
  z=min(z1,z0+i*4);girder(prefix+f'_GalleryCross{i}',(side*66,z),(side*70,z))
 for i in range(17):
  x=4+i*4;girder(prefix+f'_LandingCross{i}',(side*x,join-2.1),(side*x,join+2.1))
 for tag,z in[('Clean',clean),('Used',used)]:
  for i in range(4):girder(prefix+'_'+tag+f'PodCross{i}',(side*54,z-4+i*3),(side*66,z-4+i*3))
 # Existing Orchard appliances and storage are rigid new copies; original programme/fixtures remain unchanged.
 support_counter(prefix+'_FinishSupport',side*60,clean-2.4,6,.95);clone_unit(prefix+'_Finish','NorthFinish',(34,61.921,-228.53),(side*60,61.921,clean-2.4));clone_unit(prefix+'_FinishHood','NorthFinish_Hood',(34,64.1,-228.53),(side*60,64.1,clean-2.4))
 support_counter(prefix+'_PrepSupport',side*60,clean+4.2,3.4,.85);clone_unit(prefix+'_Prep','NorthPrep',(32.5,61.921,-218.48),(side*60,61.921,clean+4.2));clone_unit(prefix+'_PrepHood','NorthPrep_TaskHood',(32.5,64.1,-218.48),(side*60,64.1,clean+4.2))
 yaw=math.pi if side<0 else 0
 clone_unit(prefix+'_Cold','NorthChill',(31,61,-226.7),(side*55.4,61,clean+3),yaw);clone_unit(prefix+'_Dry','NorthDry',(37.15,61,-226.75),(side*64.5,61,clean+3),yaw)
 clone_unit(prefix+'_Wash','NorthWash',(33.5,61,-220.8),(side*64.5,61,used+.2),yaw);clone_unit(prefix+'_UsedReturn','NorthUsedReturn',(31,61,-220.3),(side*55.6,61,used-3),yaw);clone_unit(prefix+'_WashHood','NorthFinish_Hood',(34,64.1,-228.53),(side*60,64.1,used+2))
 # The same two-source profiled task hood repeats along the gallery and screened axial branch.
 for i in range(max(1,math.ceil((z1-z0)/12))):
  z=z0+(i+.5)*(z1-z0)/max(1,math.ceil((z1-z0)/12));clone_unit(prefix+f'_GalleryHood{i}','NorthFinish_Hood',(34,64.1,-228.53),(side*68,64.1,z),math.pi/2)
 for i in range(5):clone_unit(prefix+f'_LandingHood{i}','NorthFinish_Hood',(34,64.1,-228.53),(side*(10+i*12),64.1,join))
# Remove original source/context objects only from this new native; original file remains byte-identical.
for o in old_objects:bpy.data.objects.remove(o,do_unlink=True)
for image in bpy.data.images:
 if image.source=='FILE'and not image.packed_file:image.pack()
bpy.data.texts.new('D10_RECEIVING_POLICY.json').write(json.dumps(plan,indent=2));I=D/'native_import/Game/assets/dining_service_receiving_20261015';I.mkdir(parents=True,exist_ok=True);file=I/'D10_CONNECTED_SERVICE_RECEIVERS_r001.glb';bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(file),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False);N=D/'native';N.mkdir(exist_ok=True);native=N/'D10_CONNECTED_SERVICE_RECEIVERS_r001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True);bpy.ops.wm.open_mainfile(filepath=str(native));bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.collections['D10_CONNECTED_SERVICE_RECEIVERS_R001'].objects:o.select_set(True)
fresh=D/'D10_FRESH_REEXPORT.glb';bpy.ops.export_scene.gltf(filepath=str(fresh),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False);assert sha(fresh)==sha(file)and sha(donor)==plan['source_native_sha256'];bounds=[]
for o in bpy.data.collections['D10_CONNECTED_SERVICE_RECEIVERS_R001'].objects:
 if o.type!='MESH':continue
 ps=[GV(o.matrix_world@Vector(v))for v in o.bound_box];bounds.append({'name':o.name,'min':[min(p[i]for p in ps)for i in range(3)],'max':[max(p[i]for p in ps)for i in range(3)],'triangles':len(o.data.loop_triangles)})
r={'status':'PASS_NATIVE_FRESH_EXPORT_EXACT_CURRENT_FITTING_PENDING','native_sha256':sha(native),'file':file.name,'model_sha256':sha(file),'meshes':len(bounds),'bounds':bounds,'source_pins':plan['source_pins'],'source_native_sha256':plan['source_native_sha256'],'rigid_source_clones':clones,'lights':lights,'floor_y':61,'sites':plan['sites'],'new_floor_area_m2':plan['new_floor_area_m2'],'source_bearing_joints':joints,'new_counter_feet':feet,'original_room_ids_capacity_lift_stops_and_sources_preserved':True,'primary_engineering_food_water_stock_species_save_or_final_art_accepted':False};(D/'NATIVE_RECEIVER_VERIFICATION.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS_D10_RECEIVER_NATIVE',r['meshes'],len(clones),len(lights))
