"""Imported-GLB component arrangement. No game room or physics acceptance."""
from pathlib import Path
import bpy,math,json,sys,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch04/arrangement';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'standards'));from qa_frame import assert_full_frame,frame_report
bpy.ops.wm.read_factory_settings(use_empty=True)
rows=[];component=[];plants=[];soil=[]
def bring(rel,name,pos,angle=0):
 p=ROOT/rel;before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(p));obs=list(set(bpy.data.objects)-before)
 a=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(a)
 for o in obs:
  if o.parent is None:o.parent=a
 a.location=pos;a.rotation_euler.z=angle;bpy.context.view_layer.update()
 meshes=[o for o in obs if o.type=='MESH'];component.extend(meshes)
 pts=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
 rows.append({'file':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'position_z_up_m':pos,'rotation_z_rad':angle,'min_m':[min(q[i] for q in pts) for i in range(3)],'max_m':[max(q[i] for q in pts) for i in range(3)]})
 return meshes
for ident,pos,ang in [('004',(0,0,0),0),('005',(2.4,0,0),0),('006',(3.8,1.4,0),math.pi/2)]:
 soil.extend(bring('assets/botanical_planter/AST-BOT-'+ident+'.glb','Planted seat '+ident,pos,ang))
# The author supplies a same-design mirrored start terminal after verified lateral matching.
start='assets/botanical_planter/derived/AST-BOT-006_START.glb'
if not (ROOT/start).exists():raise RuntimeError('Validated start closure export is not available')
soil.extend(bring(start,'Derived start closure',(0,0,0)))
placements=[('assets/botanical_canopy/AST-BOT-001.glb','Canopy',(.56,.51,.39),0),('assets/botanical_understory/exports/AST-BOT-002.glb','Understory',(1.76,.51,.39),0),('assets/botanical_understory/exports/AST-BOT-003.glb','Rosette',(3.0435,.7565,.39),math.pi/4)]
for rel,name,pos,ang in placements:plants.extend(bring(rel,name,pos,ang))

def bvh_for(objs,role=None):
 verts=[];polys=[]
 for o in objs:
  me=o.data;me.calc_loop_triangles()
  for t in me.loop_triangles:
   mat=me.materials[t.material_index] if t.material_index<len(me.materials) else None
   if role and (not mat or role not in mat.name):continue
   base=len(verts);verts.extend(o.matrix_world@me.vertices[v].co for v in t.vertices);polys.append((base,base+1,base+2))
 assert verts and polys,(role,'empty geometry')
 return BVHTree.FromPolygons(verts,polys,all_triangles=True),len(polys)
soil_bvh,soil_triangles=bvh_for(soil,'botanical_soil');plant_bvh,plant_triangles=bvh_for(plants)
contacts=[]
for _,name,pos,_ in placements:
 hit,normal,index,distance=soil_bvh.ray_cast(Vector((pos[0],pos[1],pos[2]+.02)),Vector((0,0,-1)),.05)
 assert hit is not None and abs(hit.z-pos[2])<1e-5,(name,hit,pos)
 contacts.append({'plant':name,'root':pos,'soil_hit':list(hit),'contact_error_m':abs(hit.z-pos[2])})
base_contacts=[]
for ob in plants:
 for vertex in ob.data.vertices:
  point=ob.matrix_world@vertex.co
  if abs(point.z-.39)>1e-6:continue
  hit=soil_bvh.ray_cast(point+Vector((0,0,.015)),Vector((0,0,-1)),.03)[0]
  assert hit and abs(hit.z-.39)<1e-5,(ob.name,list(point),'root contact is outside actual soil')
  base_contacts.append({'mesh':ob.name,'point_m':list(point),'contact_error_m':abs(hit.z-.39)})
assert base_contacts
# Actual usable bench point, looking outward from planting. These rays prove only this proposed component outlook.
seat_eye=Vector((1.15,-.255,1.19));rays=[]
for az in (-45,-30,-15,0,15,30,45):
 for el in (-10,0,10,20):
  a,e=map(math.radians,(az,el));direction=Vector((math.sin(a)*math.cos(e),-math.cos(a)*math.cos(e),math.sin(e)))
  hit=plant_bvh.ray_cast(seat_eye,direction,8)[0]
  rays.append({'azimuth_deg':az,'elevation_deg':el,'blocked':hit is not None})
assert not any(x['blocked'] for x in rays)
# Conservative whole-mesh AABB rejection for a proposed clear approach in front of the seat.
# Passing proves separation; a broad-phase overlap is deliberately not called collision.
approach={'min':[.45,-1.90,0.01],'max':[2.05,-.70,2.65]};approach_tests=[]
for o in component:
 pts=[o.matrix_world@Vector(c) for c in o.bound_box];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
 overlaps=[min(hi[i],approach['max'][i])-max(lo[i],approach['min'][i]) for i in range(3)]
 separate=any(x<=0 for x in overlaps);approach_tests.append({'mesh':o.name,'separate':separate,'overlap_axis_m':overlaps})
assert all(r['separate'] for r in approach_tests),'Proposed clear approach has unresolved broad-phase geometry'
# Known-occluded control uses a real canopy vertex centroid and cannot pass an empty test.
o=next(x for x in plants if x.data.polygons);poly=o.data.polygons[0];target=o.matrix_world@poly.center
v=target-seat_eye;control=plant_bvh.ray_cast(seat_eye,v.normalized(),v.length+.1)[0]
assert control is not None,'Known actual plant triangle must be hit'
# Check the actual seat receiver's downward support, using visible imported timber triangles.
seat_bvh,seat_triangles=bvh_for(soil,'warm_walnut');seat_hit=seat_bvh.ray_cast(Vector((seat_eye.x,seat_eye.y,.51)),Vector((0,0,-1)),.12)[0]
assert seat_hit and abs(seat_hit.z-.47)<1e-5
mat=bpy.data.materials.new('QA neutral support');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.19,.215,.21,1);bs.inputs['Roughness'].default_value=.95
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.006));bpy.context.object.name='QA floor';bpy.context.object.data.materials.append(mat)
sc=bpy.context.scene;sc.world=bpy.data.worlds.new('QA neutral world');sc.render.engine='BLENDER_EEVEE_NEXT';sc.render.threads_mode='FIXED';sc.render.threads=4;sc.world.color=(.18,.18,.18);sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=0
for name,pos,energy,size,col in [('neutral key',(-2,-4,6),1100,5,(1,.97,.93)),('fill',(5,-1,4),750,4,(.92,.97,1)),('canopy return',(2,4,5),900,4,(1,1,1))]:
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=col;o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((1.5,.3,1.0))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('QA camera');cam=bpy.data.objects.new('QA camera',d);bpy.context.collection.objects.link(cam);sc.camera=cam;d.clip_start=.04;d.clip_end=200;d.sensor_width=36
views=[('standing_640',(6.0,-7.8,1.65),(1.6,.35,1.40),640,360,32,True),('seated_eye_640',(5.6,-7.2,1.19),(1.5,.35,1.3),640,360,30,True),('seated_bench_glance_640',tuple(seat_eye),(3.3,.55,.95),640,360,24,False),('assembly_detail_1280',(6.2,-7.9,3.8),(1.6,.35,1.35),1280,720,34,True)]
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
frames=[]
for name,pos,target,w,h,lens,full in views:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;sc.render.resolution_x=w;sc.render.resolution_y=h;sc.render.resolution_percentage=100
 report=assert_full_frame(sc,cam,component,.025) if full else frame_report(sc,cam,component)
 frames.append({'name':name,'eye_height_m':pos[2],'actual_bench_point':name.startswith('seated_bench'),'frame':report,'full_object_view':full})
 if '--preflight' in selected:continue
 if selected and name not in selected:continue
 sc.render.image_settings.file_format='PNG';sc.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'component_arrangement.blend'),compress=True)
(OUT/'evidence.json').write_text(json.dumps({'scope':'Imported GLB component arrangement only, not recovered game or installed courtyard. Inspection lights are not runtime fixtures.','source_exports':rows,'plant_soil_contacts':contacts,'actual_root_base_vertex_contacts':base_contacts,'soil_triangles_tested':soil_triangles,'plant_triangles_tested':plant_triangles,'seat_surface_triangles_tested':seat_triangles,'seat_support_hit':list(seat_hit),'proposed_clear_approach_m':approach,'approach_mesh_separation':approach_tests,'proposed_seated_eye_m':list(seat_eye),'outward_view_rays':rays,'known_occluded_plant_control':list(control),'views':frames,'game_contact_and_collision':'Pending; visible triangle rays are component measurements, not physics or actor tests.'},indent=2)+'\n')
