"""Actual exported hospitality components on a neutral interoperability fixture."""
from pathlib import Path
import bpy,json,hashlib,math,sys
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch07/arrangement';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'standards'));from qa_frame import assert_full_frame,frame_report
bpy.ops.wm.read_factory_settings(use_empty=True)
instances={};meshes=[];imports=[]

def bvh(objects):
 verts=[];tris=[]
 for ob in objects:
  mesh=ob.data;mesh.calc_loop_triangles()
  for tri in mesh.loop_triangles:
   base=len(verts);verts.extend(ob.matrix_world@mesh.vertices[i].co for i in tri.vertices);tris.append((base,base+1,base+2))
 assert tris
 return BVHTree.FromPolygons(verts,tris,all_triangles=True)

def bring(family,ident,pos,yaw=0):
 base=ROOT/'assets'/family;m=json.loads((base/(ident+'.manifest.json')).read_text());path=base/m['export'];before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path));objects=list(set(bpy.data.objects)-before)
 root=bpy.data.objects.new('QA placement '+ident,None);bpy.context.collection.objects.link(root)
 for ob in objects:
  if ob.parent is None:ob.parent=root
 root.location=pos;root.rotation_euler.z=math.radians(yaw);bpy.context.view_layer.update()
 owned=[o for o in objects if o.type=='MESH'];meshes.extend(owned)
 data={'root':root,'objects':objects,'meshes':owned,'manifest':m,'bvh':bvh(owned)};instances[ident]=data
 imports.append({'id':ident,'source':str((base/m['source']).relative_to(ROOT)),'source_sha256':hashlib.sha256((base/m['source']).read_bytes()).hexdigest(),'export':str(path.relative_to(ROOT)),'export_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'placement_source_m':pos,'yaw_source_degrees':yaw})

def point(ident,p):return instances[ident]['root'].matrix_world@Vector(p)

def bounds(ob):
 p=[ob.matrix_world@Vector(c) for c in ob.bound_box];return ([min(v[k] for v in p) for k in range(3)],[max(v[k] for v in p) for k in range(3)])

counter=json.loads((ROOT/'assets/hospitality_counters/counter_interface.json').read_text())
exit_point=counter['AST-HSP-001']['exit_source_m'];host=counter['AST-HSP-001']['proposed_beverage_origin_source_m']
bring('hospitality_counters','AST-HSP-001',(0,0,0))
bring('hospitality_counters','AST-HSP-002',exit_point)
bring('hospitality_stations','AST-HSP-003',host)
bring('hospitality_stations','AST-HSP-004',(-1.50,0,0))
bring('hospitality_serviceware','AST-HSP-005',(.60,2.40,0),180)
bring('hospitality_serviceware','AST-HSP-006',(2.40,2.40,0))

# Actual exported counter end faces retain the declared 2 mm construction joint.
seams=[]
for label,depth,z in [('stone',0,.878),('closed_bulkhead',0,.50),('walnut',-.341,.696),('upper_ivory',-.336,.823)]:
 p=Vector((exit_point[0],depth,z));left=instances['AST-HSP-001']['bvh'].ray_cast(p,Vector((-1,0,0)),.04)[0];right=instances['AST-HSP-002']['bvh'].ray_cast(p,Vector((1,0,0)),.04)[0]
 assert left is not None and right is not None,(label,'empty seam sample')
 gap=(right-left).length;assert abs(gap-.002)<.00002,(label,gap)
 seams.append({'part':label,'left_actual_m':list(left),'right_actual_m':list(right),'measured_gap_m':gap})

# Beverage support feet meet real exported stone, with positive surface hits.
contacts=[]
for contact in instances['AST-HSP-003']['manifest']['physical_contacts']:
 p=point('AST-HSP-003',contact['source_m']);hit=instances['AST-HSP-001']['bvh'].ray_cast(p+Vector((0,0,.025)),Vector((0,0,-1)),.05)[0]
 assert hit is not None and abs(hit.z-p.z)<1e-5
 contacts.append({'name':contact['name'],'point_world_m':list(p),'actual_host_hit_m':list(hit),'gap_m':abs(hit.z-p.z)})

floors=[]
for ident,data in instances.items():
 if ident=='AST-HSP-003':continue
 low=min(bounds(o)[0][2] for o in data['meshes']);assert abs(low)<1e-5,(ident,low)
 floors.append({'id':ident,'actual_lowest_mesh_z_m':low,'qa_floor_z_m':0})

# Record conservative reservations in world coordinates and exclude only their own asset.
reservations=[]
def reserve(ident,name,lo,hi,scope):
 corners=[point(ident,(x,y,z)) for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])]
 a=[min(v[k] for v in corners) for k in range(3)];b=[max(v[k] for v in corners) for k in range(3)];tested=0
 for other,data in instances.items():
  if other==ident:continue
  for ob in data['meshes']:
   c,d=bounds(ob);overlap=[min(b[k],d[k])-max(a[k],c[k]) for k in range(3)];assert any(v<=.000001 for v in overlap),(ident,name,other,ob.name,overlap);tested+=1
 reservations.append({'owner':ident,'name':name,'min_world_m':a,'max_world_m':b,'other_meshes_tested':tested,'scope':scope})
for ident in ('AST-HSP-003','AST-HSP-004'):
 for row in instances[ident]['manifest']['clearances']:
  reserve(ident,row['name'],row['min_source_m'],row['max_source_m'],'Other-component AABB separation; own openings/motion separately reviewed. No actor or route certification.')
for ident in ('AST-HSP-005','AST-HSP-006'):
 row=instances[ident]['manifest']['approach']['proposed_clear_zone_source_m'];reserve(ident,'staff_approach',row['min'],row['max'],'Proposed stationary staff approach, not a playable path or trolley controller.')
row=instances['AST-HSP-001']['manifest']['drawer_proposal']['external_proposed_sweep_source_m'];reserve('AST-HSP-001','drawer_external_proposal',row['min'],row['max'],'Finite proposal envelope only; actual drawer and own supports separately reviewed.')

# QA floor only, no room or operational service network.
mat=bpy.data.materials.new('QA neutral floor');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.18,.205,.215,1);bs.inputs['Roughness'].default_value=.95
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,0));bpy.context.object.name='QA neutral floor';bpy.context.object.data.materials.append(mat)
sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.render.threads_mode='FIXED';sc.render.threads=4;sc.world=bpy.data.worlds.new('QA neutral world');sc.world.color=(.20,.20,.20);sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
for name,pos,power,size in [('key',(-4,-4,6),1050,5),('fill',(5,-1,5),750,4),('back',(1,5,5),950,5)]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((.5,1,.7))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('QA camera');cam=bpy.data.objects.new('QA camera',d);bpy.context.collection.objects.link(cam);sc.camera=cam;d.sensor_width=36;d.clip_start=.03;d.clip_end=200
views=[('guest_overview_1280',(6.4,-7.0,4.4),(.55,.80,.75),1280,720,38,True),('guest_standing_640',(6.5,-7.6,1.65),(.5,.7,.7),640,360,34,True),('staff_workside_640',(-4.4,1.2,1.65),(1.0,1.2,.7),640,360,31,False)]
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];frames=[]
for name,pos,target,w,h,lens,full in views:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;sc.render.resolution_x=w;sc.render.resolution_y=h;sc.render.resolution_percentage=100
 fr=assert_full_frame(sc,cam,meshes,.025) if full else frame_report(sc,cam,meshes);frames.append({'name':name,'eye_source_m':pos,'target_source_m':target,'full_assembly':full,'purpose':'Whole guest-facing composition' if full else 'Intentional work-side view of counter and storage approaches; other components may crop','frame':fr})
 if '--preflight' in selected or (selected and name not in selected):continue
 sc.render.image_settings.file_format='PNG';sc.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'component_fixture.blend'),compress=True)
(OUT/'evidence.json').write_text(json.dumps({'scope':'Actual exported hospitality components on a neutral QA floor; no room, device behavior, food simulation or player-cart replacement','imports':imports,'actual_counter_mating_samples':seams,'actual_beverage_support_contacts':contacts,'actual_floor_datums':floors,'other_component_reservations':reservations,'views':frames,'source_geometry_changed':False},indent=2)+'\n')
