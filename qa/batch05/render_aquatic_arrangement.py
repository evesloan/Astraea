"""Actual-GLB aquatic component inspection on neutral support fixtures.
No water, buoyancy, player, room or missing-game reconstruction is used.
"""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,sys
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch05/arrangement';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'standards'));from qa_frame import assert_full_frame,frame_report
bpy.ops.wm.read_factory_settings(use_empty=True)
component=[];records=[];instances={};fixture=[];pads=[]
def bring(rel,name,pos,yaw=0):
 p=ROOT/rel;before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(p));obs=list(set(bpy.data.objects)-before)
 a=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(a)
 for ob in obs:
  if ob.parent is None:ob.parent=a
 a.location=pos;a.rotation_euler.z=yaw;bpy.context.view_layer.update()
 meshes=[o for o in obs if o.type=='MESH'];component.extend(meshes);instances[name]=meshes
 verts=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
 records.append({'file':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'name':name,'position_m':pos,'yaw_rad':yaw,'min_m':[min(v[k] for v in verts) for k in range(3)],'max_m':[max(v[k] for v in verts) for k in range(3)]})
 return meshes

def mat(name,col):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.92;return m
QA=mat('QA neutral inspection fixtures',(.21,.235,.24));LOW=mat('QA lower display surface, not water',(.15,.19,.20))
def box(name,lo,hi,material=QA):
 bpy.ops.mesh.primitive_cube_add(size=1,location=tuple((lo[i]+hi[i])/2 for i in range(3)));o=bpy.context.object;o.name='QA ONLY '+name;o.dimensions=tuple(hi[i]-lo[i] for i in range(3));bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material);fixture.append(o);return o

def prism(name,xy,zlo,zhi):
 n=len(xy);verts=[(x,y,z) for z in (zlo,zhi) for x,y in xy];faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new('QA ONLY '+name,me);bpy.context.collection.objects.link(o);o.data.materials.append(QA);fixture.append(o);return o

# Source-owned connections. Every terminal stays an explicit same-design derivative.
edge='assets/aquatic_edges/'
place=[('AST-AQU-003.glb','Left straight',(-1.928,0,0),0,'003'),('AST-AQU-003.glb','Right straight',(.728,0,0),0,'003'),('AST-AQU-004.glb','Right curve',(1.928,0,0),0,'004'),('AST-AQU-005.glb','Entry',(0,0,0),0,'005')]
for rel,name,pos,ang,ident in place:
 bring(edge+rel,name,pos,ang);j=json.load(open(ROOT/edge/('AST-AQU-'+ident+'.manifest.json')))
 for pad in j['host_contact_pads']:
  lo=pad['bounds_min_m'];hi=pad['bounds_max_m'];z=pad['receiving_z_m']+pos[2]
  # These placements have zero yaw. The curved pad's recorded bounds are already in its source coordinates.
  assert ang==0
  worldlo=[lo[0]+pos[0],lo[1]+pos[1],z];worldhi=[hi[0]+pos[0],hi[1]+pos[1],z]
  if z>-.859:box(name+' pad support '+pad['name'],(worldlo[0],worldlo[1],-.86),(worldhi[0],worldhi[1],z))
  pads.append({'asset':name,'pad':pad['name'],'min_xy_m':worldlo[:2],'max_xy_m':worldhi[:2],'receiving_z_m':z,'inspection_support_top_m':z if z>-.859 else -.86})
curve=json.load(open(ROOT/edge/'AST-AQU-004.manifest.json'));end=curve['connections'][1];angle=math.radians(end['tangent_yaw_degrees']);cx=1.928+end['position_m'][0];cy=end['position_m'][1]
for rel,name,pos,ang in [('derived/AST-AQU-003_START.glb','Left outer closed start',(-1.928,0,0),0),('derived/AST-AQU-003_END.glb','Left shoulder closure',(-.728,0,0),0),('derived/AST-AQU-003_START.glb','Right shoulder closure',(.728,0,0),0),('derived/AST-AQU-003_END.glb','Right curve closure',(cx,cy,0),angle)]:bring(edge+rel,name,pos,ang)
bring('assets/aquatic_lounge/exports/AST-AQU-001.glb','Lounger',(-1.85,-2.35,0),math.pi)
bring('assets/aquatic_lounge/exports/AST-AQU-002.glb','Table',(-2.72,-2.45,0))
f=json.load(open(ROOT/'assets/aquatic_float/AST-AQU-006.manifest.json'));fz=-.72-f['bounds_blender_z_up']['min_m'][2]
bring('assets/aquatic_float/exports/AST-AQU-006.glb','Float on lower display',(1.7,2.7,fz),math.radians(-20))
# Neutral inspection fixture: surfaces support parts at the declared host datums.
box('upper dry platform',(-3.5,-4.1,-.86),(3.5,-.64,0))
box('left dry receiving lip',(-1.956,-.64,-.25),(-.70,-.56,0));box('right dry receiving lip',(.70,-.64,-.25),(1.928,-.56,0))
r=curve['curve_centerline_radius_m'];outer=r+.56
arc=[(1.928+outer*math.sin(angle*i/20),r-outer*math.cos(angle*i/20)) for i in range(21)]
poly=[(1.928,-.64),(arc[-1][0],-.64)]+list(reversed(arc));prism('curved dry receiving wedge',poly,-.25,0)
box('lower display platform, no water',(-3.5,1.58,-.86),(3.5,4.1,-.72),LOW)
box('neutral base foundation',(-8,-8,-.88),(8,8,-.86),LOW)

# Exact actual-mesh probes and conservative clear-space bounds. No physics claim.
def bvh(obs):
 vs=[];ts=[]
 for ob in obs:
  me=ob.data;me.calc_loop_triangles()
  for t in me.loop_triangles:
   n=len(vs);vs.extend(ob.matrix_world@me.vertices[i].co for i in t.vertices);ts.append((n,n+1,n+2))
 assert ts
 return BVHTree.FromPolygons(vs,ts,all_triangles=True),len(ts)
entry,entrytris=bvh(instances['Entry']);tread=[]
for y,z in [(-.3,0),(.16,-.18),(.48,-.36),(.80,-.54),(1.25,-.72)]:
 hit=entry.ray_cast(Vector((0,y,1.2)),Vector((0,0,-1)),3)[0];assert hit and abs(hit.z-z)<1e-5,(y,z,hit);tread.append({'y_m':y,'top_z_m':hit.z})
# Real rail is an occluded control; central torso-height ray should remain clear.
clear=entry.ray_cast(Vector((0,-.4,.6)),Vector((0,1,0)),1.9)[0];assert clear is None
rail=entry.ray_cast(Vector((0,-.35,.9)),Vector((1,0,0)),1.0)[0];assert rail is not None,'Known rail control failed'
transfer={'min':[-1.42,-2.6,.03],'max':[-.70,-1.8,1.9]};separations=[]
# Table, pool edges and float must not occupy the free opposite transfer strip. Lounger itself bounds the side.
for name in ['Table','Left straight','Right straight','Right curve','Entry','Float on lower display']:
 for ob in instances[name]:
  vv=[ob.matrix_world@Vector(c) for c in ob.bound_box];lo=[min(v[k] for v in vv) for k in range(3)];hi=[max(v[k] for v in vv) for k in range(3)];ov=[min(hi[k],transfer['max'][k])-max(lo[k],transfer['min'][k]) for k in range(3)];assert any(x<=0 for x in ov),(name,ob.name,ov);separations.append({'asset':name,'mesh':ob.name,'separate':True})
assert all(abs(p['receiving_z_m']-p['inspection_support_top_m'])<1e-6 for p in pads)
# Export floor support after placement, including the float resting on a display, not floating.
support=[]
for name,z in [('Lounger',0),('Table',0),('Float on lower display',-.72)]:
 row=next(x for x in records if x['name']==name);assert abs(row['min_m'][2]-z)<1e-6;support.append({'asset':name,'lowest_surface_z_m':row['min_m'][2],'fixture_top_z_m':z})
sc=bpy.context.scene;sc.world=bpy.data.worlds.new('QA world');sc.world.color=(.18,.18,.18);sc.render.engine='BLENDER_EEVEE_NEXT';sc.render.threads_mode='FIXED';sc.render.threads=4;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
for name,pos,power,size,col in [('key',(-3,-2,6),1200,5,(1,.97,.93)),('fill',(5,2,5),900,5,(.94,.98,1)),('return',(-2,5,4),700,4,(1,1,1))]:
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=col;o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,.1))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('QA camera');cam=bpy.data.objects.new('QA camera',d);bpy.context.collection.objects.link(cam);sc.camera=cam;d.sensor_width=36;d.clip_start=.05;d.clip_end=100
views=[('overview_1280',(6.7,7.1,4.6),(-.3,-.45,-.1),1280,720,27,True),('lower_standing_640',(6.2,6.7,.93),(-.3,-.4,.1),640,360,30,True),('dry_entry_640',(3.8,-5.6,1.65),(-.1,.5,-.1),640,360,27,False)]
selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];frames=[]
for name,pos,target,w,h,lens,full in views:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;sc.render.resolution_x=w;sc.render.resolution_y=h;sc.render.resolution_percentage=100
 fr=assert_full_frame(sc,cam,component,.025) if full else frame_report(sc,cam,component);frames.append({'name':name,'camera_m':pos,'target_m':target,'full_component_view':full,'frame':fr,'height_above_named_fixture_m':1.65 if name in ('lower_standing_640','dry_entry_640') else None})
 if '--preflight' in selected or (selected and name not in selected):continue
 sc.render.image_settings.file_format='PNG';sc.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'inspection_fixture.blend'),compress=True)
(OUT/'evidence.json').write_text(json.dumps({'scope':'Actual exported components on neutral two-level inspection supports. No water surface, buoyancy, recovered room, gameplay or engine validation. Float rests on lower display surface.','imports':records,'host_pad_contacts':pads,'entry_triangle_count':entrytris,'actual_tread_top_rays':tread,'clear_center_ray':clear is None,'real_rail_control_hit':list(rail),'free_transfer_proposal_m':transfer,'transfer_separations':separations,'floor_support':support,'views':frames,'inspection_geometry':'Neutral platforms and individual pad stands are QA-only, excluded from exported asset catalogue.'},indent=2)+'\n')
