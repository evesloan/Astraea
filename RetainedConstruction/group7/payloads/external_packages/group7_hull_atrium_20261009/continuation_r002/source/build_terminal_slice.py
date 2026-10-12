"""Discrete terminal wings, framed headwalls and maintained route openings."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];OLD=P.parent;PLAN=json.loads((P/'docs/TERMINAL_PLAN_R002.json').read_text());outline=json.loads((OLD/'dependencies/canonical_77a745/Game/data/hull_envelope.json').read_text())['plan_xz_m'];ring=[Vector(q) for q in outline];normals=[]
for a,b in zip(ring,ring[1:]+ring[:1]):
 t=(b-a).normalized();n=Vector((t.y,-t.x));normals.append(n if n.dot(-a)>0 else -n)
def inset(d):
 out=[]
 for i,a in enumerate(ring):
  n0,n1=normals[i-1],normals[i];c0,c1=n0.dot(a)+d,n1.dot(a)+d;det=n0.x*n1.y-n0.y*n1.x;out.append(Vector(((c0*n1.y-n0.y*c1)/det,(n0.x*c1-c0*n1.x)/det)))
 return out
for folder in ['source/natives','exports/terminal','qa/views']:(P/folder).mkdir(parents=True,exist_ok=True)
rows=[];materials={};parts=[];geometry=[];markers=[];doors=[]
def material(role,texture,color,alpha=1):
 m=bpy.data.materials.new('G7C2_'+role);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,alpha);p.inputs['Roughness'].default_value=.72
 if texture:
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(OLD/'dependencies/canonical_9d6f85/BlenderCatalogue/materials'/texture),check_existing=True);m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
 if alpha<1:p.inputs['Alpha'].default_value=alpha;p.inputs['Roughness'].default_value=.12;p.inputs['Transmission Weight'].default_value=.35;m.surface_render_method='DITHERED'
 materials[role]=m
def mesh(name,world,faces,role,category,extra=None):
 v=[(x,-z,y) for x,y,z in world];me=bpy.data.meshes.new(name);me.from_pydata(v,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name;assert bm.calc_volume()>1e-9,name;bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(materials[role]);uv=me.uv_layers.new(name='MetreScaled')
 for f in me.polygons:
  n=f.normal;u=Vector((0,1,0)) if abs(n.x)>.8 else Vector((1,0,0));w=n.cross(u)
  for k in f.loop_indices:q=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(q.dot(u),q.dot(w))
 o['role']=role;o['contact_category']=category;o['source_slice']='continuation_r002';me.calc_loop_triangles();g={'object':name,'vertices_world_xyz':[(v.co.x,v.co.z,-v.co.y) for v in me.vertices],'triangles':len(me.loop_triangles),'role':role,'contact_category':category}
 if extra:g.update(extra)
 geometry.append(g);parts.append(o);return o
def prism(name,poly,y0,y1,role='roof',category='solid_roof'):
 n=len(poly);return mesh(name,[(x,y,z) for y in [y0,y1] for x,z in poly],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],role,category)
def rect(name,x0,x1,z0,z1,y0,y1,role='metal',category='solid_frame'):return prism(name,[(x0,z0),(x1,z0),(x1,z1),(x0,z1)],y0,y1,role,category)
def beam(name,a,b,r=.05,role='metal',category='solid_guard'):
 a,b=Vector(a),Vector(b);t=(b-a).normalized();u=t.cross(Vector((0,1,0)))
 if u.length<.1:u=t.cross(Vector((1,0,0)))
 u.normalize();w=t.cross(u);v=[tuple(p+r*(u*math.cos(i*math.tau/8)+w*math.sin(i*math.tau/8))) for p in [a,b] for i in range(8)]
 return mesh(name,v,[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)],role,category)
def facet(name,tri,n0,n1,role,category):
 v=[Vector(q) for q in tri];n=(v[1]-v[0]).cross(v[2]-v[0]).normalized();c=sum(v,Vector((0,0,0)))/3
 if n.dot(Vector((-c.x,0,-c.z)))<0:n=-n
 horizontal=Vector((n.x,0,n.z));assert horizontal.length_squared>.2;delta=horizontal/horizontal.length_squared
 world=[tuple(q+delta*d) for d in [n0,n1] for q in v]
 return mesh(name,world,[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],role,category,{'true_inward_unit_normal':tuple(n),'normal_material_interval_m':[n0,n1]})
def patch(name,point,u0,u1,y0,y1,role,n0=0,n1=.18,category='solid_skin'):
 q=[point(u0,y0),point(u1,y0),point(u1,y1),point(u0,y1)];facet(name+'_a',[q[0],q[1],q[2]],n0,n1,role,category);facet(name+'_b',[q[0],q[2],q[3]],n0,n1,role,category)
def field_grid(name,point,width,y0,y1,skip=None):
 columns=max(1,math.ceil(width/3));ys=[y0];y=y0
 while y<y1-1e-6:y=min(y+3,y1);ys.append(y)
 for j,(ya,yb) in enumerate(zip(ys,ys[1:])):
  for k in range(columns):
   u0,u1=k/columns,(k+1)/columns
   if skip and skip(u0,u1,ya,yb):continue
   du=min(.06/width,(u1-u0)/4);dy=min(.06,(yb-ya)/4);prefix=name+'_H%02d_C%02d'%(j,k)
   patch(prefix+'_VJoint',point,u0,u0+du,ya,yb,'metal');patch(prefix+'_HJoint',point,u0+du,u1,ya,ya+dy,'metal');patch(prefix+'_Glazing',point,u0+du,u1,ya+dy,yb,'glass')
   patch(prefix+'_ReceiverV',point,u0,u0+du,ya,yb,'metal',.18,.40,'solid_frame');patch(prefix+'_ReceiverH',point,u0+du,u1,ya,ya+dy,'metal',.18,.40,'solid_frame')
 # Exact continuous top receiver for roof/next-source seams.
 patch(name+'_TopReceiver',point,0,1,y1-.22,y1,'metal',.18,.40,'solid_frame')
def side_half(z):
 # Piecewise calibrated maximum hull halfbeam, used only at terminal stations.
 hits=[]
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if a.y==b.y:
   if abs(z-a.y)<1e-6:hits.extend([abs(a.x),abs(b.x)])
  elif min(a.y,b.y)<=z<=max(a.y,b.y):hits.append(abs(a.x+(b.x-a.x)*(z-a.y)/(b.y-a.y)))
 return max(hits)
for term in PLAN['terms']:
 bpy.ops.wm.read_factory_settings(use_empty=True);materials={};parts=[];geometry=[];markers=[];doors=[];sgn=term['sign_z'];name=term['id']
 for r,t,c in [('shell','staff/staff_bluegrey_paint.png',(.32,.40,.44)),('metal','staff/staff_zinc.png',(.48,.51,.52)),('roof','ivory_enamel.png',(.70,.72,.70)),('dark','warm_stone.png',(.24,.28,.31)),('lens','ivory_enamel.png',(.9,.82,.62))]:material(r,t,c)
 material('glass',None,(.50,.70,.75),.24)
 # New lower seal/receiver rails sit on the first-delivery frame atY61.
 r0,r40=inset(0),inset(.4)
 for edge in term['outer_edges']:
  a,b=ring[edge],ring[(edge+1)%len(ring)];prism(name+'_LowerSeam_E%02d'%edge,[(r0[edge].x,r0[edge].y),(r0[(edge+1)%len(ring)].x,r0[(edge+1)%len(ring)].y),(r40[(edge+1)%len(ring)].x,r40[(edge+1)%len(ring)].y),(r40[edge].x,r40[edge].y)],61,61.08,'metal','solid_frame')
  def point(u,y,a=a,b=b):q=a.lerp(b,u);scale=1-.015*(y-61)/8.5;return(q.x*scale,y,q.y)
  patch(name+'_LowerSill_E%02d'%edge,point,0,1,61.08,61.9,'shell');field_grid(name+'_OuterFacet_E%02d'%edge,point,(b-a).length,61.9,69.5)
 # A simple polygon with a deliberate open route notch, not a full-plan slab.
 prism(name+'_SteppedRoof',term['roof_boundary_xz'],69.2,69.5,'roof','solid_roof')
 for i,zabs in enumerate([538,533,526,519,512]):
  z=sgn*zabs;half=side_half(z)*.985-.55
  intervals=[(-half,half)] if zabs>=531.5 else [(-half,-6),(6,half)]
  for j,(x0,x1) in enumerate(intervals):rect(name+'_RoofRib_%02d_%02d'%(i,j),x0,x1,z-.07,z+.07,68.70,69.2,'metal','solid_frame')
 # Receiver beam follows the protected route notch and holds neck-wall feet.
 for side in [-1,1]:
  xs=sorted([side*6,side*7.08]);za,zb=sorted([sgn*530.7,sgn*509.2]);rect(name+'_NeckReceiver_'+str(side),*xs,za,zb,68.80,69.2,'metal','solid_frame')
 za,zb=sorted([sgn*531.7,sgn*530.7]);rect(name+'_EndReceiver',-7.08,7.08,za,zb,68.80,69.2,'metal','solid_frame')
 # Four explicit planar headwall fields per terminal preserve the route opening.
 for side in [-1,1]:
  def hp(u,y,side=side):half=term['headwall_halfwidth_at_y69_5']+(term['headwall_halfwidth_at_y106_5']-term['headwall_halfwidth_at_y69_5'])*(y-69.5)/37;return(side*(6.8+(half-6.8)*u),y,sgn*510)
  field_grid(name+'_Headwall_'+str(side),hp,term['headwall_halfwidth_at_y69_5']-6.8,69.5,106.5)
  # Neck is a real thin corridor enclosure around existing±4m routes.
  # Native staff threshold occupies a cut only in this newly owned side face.
  zknots=[510,516.12,518.88,531.5];yknots=[69.5,72.32,78,84,88.5,93,97.5,102,106.5]
  for k,(za,zb) in enumerate(zip(zknots,zknots[1:])):
   for j,(ya,yb) in enumerate(zip(yknots,yknots[1:])):
    if k==1 and j==0:continue
    def np(u,y,za=za,zb=zb,side=side):return(side*6.8,y,sgn*(za+(zb-za)*u))
    field_grid(name+'_Neck_'+str(side)+'_%02d_%02d'%(k,j),np,zb-za,ya,yb)
  poly=term['bridge_polygons_xz'][0 if side==1 else 1];prism(name+'_MaintenanceBridge_'+str(side),poly,69.28,69.5,'dark','solid_roof')
  z=sgn*517.5
  for edgez in [z-1.44,z+1.44]:
   beam(name+'_BridgeGuard_'+str(side)+'_'+str(edgez),(side*4.12,70.6,edgez),(side*5.90,70.6,edgez),.035)
   for x in [side*4.15,side*5.8]:beam(name+'_BridgeGuardPost_'+str(x)+'_'+str(edgez),(x,69.5,edgez),(x,70.6,edgez),.035)
  # Bounded roof maintenance receiver: guarded working bay outside public route.
  for i,(a,b) in enumerate([((side*7.08,69.5,z-3.5),(side*11.5,69.5,z-3.5)),((side*11.5,69.5,z-3.5),(side*11.5,69.5,z+3.5)),((side*11.5,69.5,z+3.5),(side*7.08,69.5,z+3.5))]):
   aa,bb=Vector(a),Vector(b);beam(name+'_ServiceGuard_'+str(side)+'_'+str(i),aa+Vector((0,1.1,0)),bb+Vector((0,1.1,0)),.04)
   steps=max(1,math.ceil((bb-aa).length/2))
   for k in range(steps+1):q=aa.lerp(bb,k/steps);beam(name+'_ServiceGuardPost_'+str(side)+'_%d_%d'%(i,k),q,q+Vector((0,1.1,0)),.04)
  # Exact retained source family, visible closed source only; controller later.
  before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(P/'dependencies/BlenderCatalogue/assets/staff_threshold/exports/AST-STF-008.glb'));imported=list(set(bpy.data.objects)-before);root=bpy.data.objects.new(name+'_DoorPrefab_'+str(side),None);bpy.context.collection.objects.link(root);root.location=(side*6.8,-z,69.5);root.rotation_euler.z=-side*math.pi/2
  for o in imported:
   original=o.name
   if o.parent is None:o.parent=root
   o['contact_category']='family_door_preview';o['retained_family']='AST-STF-008';o['retained_family_node']=original
  door={'id':name+'_MaintenanceDoor_'+str(side),'family':'AST-STF-008','origin_world_xyz':[side*6.8,69.5,z],'rotation_y':-side*math.pi/2,'scale':[1,1,1],'controller':'Retain Game/scripts/service_door.gd; root instantiates original family, drops preview meshes and adopts stable IDs. No controller/permission change or operating door claimed.','clear_aperture_m':[2.4,2.54],'clear_between_handles_m':2.168,'root_route_contact_edge_xyz':[side*4,69.5,z],'bridge_width_m':3,'root_receiver_collar':'Existing route edge belongs to root; proposal abuts atX±4 with no retained slab overwrite','preview_objects':[o.name for o in imported]};doors.append(door)
  # Attached downlight hardware; actual emitting point is below its lens.
  lx=side*7.15;ly=72.32;lz=z
  rect(name+'_SourceBracket_'+str(side),min(side*6.78,lx),max(side*6.78,lx),lz-.06,lz+.06,ly-.05,ly+.05,'metal','solid_frame');rect(name+'_SourceHousing_'+str(side),lx-.13,lx+.13,lz-.16,lz+.16,ly-.01,ly+.13,'metal','solid_frame');rect(name+'_SourceLens_'+str(side),lx-.10,lx+.10,lz-.13,lz+.13,ly-.03,ly-.01,'lens','visual_lens')
  datum=bpy.data.objects.new('DATUM_'+name+'_ServiceSource_'+str(side),None);bpy.context.collection.objects.link(datum);datum.location=(lx,-lz,ly-.04);light=bpy.data.lights.new(name+'_ServiceSource_'+str(side),'SPOT');light.energy=100;light.color=(.91,.96,1);light.use_custom_distance=True;light.cutoff_distance=3.5;light.spot_size=math.radians(50);o=bpy.data.objects.new(light.name,light);bpy.context.collection.objects.link(o);o.location=datum.location;markers.append({'id':light.name,'position_world_xyz':[lx,ly-.04,lz],'direction_xyz':[0,-1,0],'range_m':3.5,'spot_angle_deg':25,'color_rgb':[.91,.96,1],'energy_proposal':.8,'controller':'Root existing light budget; not exported as running light'})
 def ep(u,y):return(-6.8+13.6*u,y,sgn*531.5)
 field_grid(name+'_NeckEnd',ep,13.6,69.5,106.5)
 scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.context.view_layer.update()
 # Record exact transformed retained preview vertices for fit/source checks.
 for door in doors:
  for oname in door['preview_objects']:
   o=bpy.data.objects[oname]
   if o.type!='MESH':continue
   me=o.data;me.calc_loop_triangles();world=[o.matrix_world@v.co for v in me.vertices];geometry.append({'object':o.name,'vertices_world_xyz':[(q.x,q.z,-q.y) for q in world],'triangles':len(me.loop_triangles),'role':'family_door','contact_category':'family_door_preview'})
 native=P/'source/natives'/(name+'_Terminal_r002.blend');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native))
 # Keep semantic native untouched; assemble compact runtime export in own scene.
 exportscene=bpy.data.scenes.new(name+'_CompactExport');bpy.context.window.scene=exportscene
 for role in materials:
  for category in ['solid_skin','solid_frame','solid_roof','solid_guard','visual_lens']:
   selected=[g for g in geometry if g['role']==role and g['contact_category']==category];v=[];faces=[]
   for g in selected:
    o=bpy.data.objects[g['object']];i=len(v);v.extend(tuple(o.matrix_world@p.co) for p in o.data.vertices);faces.extend(tuple(i+k for k in f.vertices) for f in o.data.polygons)
   if not v:continue
   me=bpy.data.meshes.new(name+'_'+role+'_'+category);me.from_pydata(v,[],faces);me.update();o=bpy.data.objects.new(me.name,me);exportscene.collection.objects.link(o);me.materials.append(materials[role]);o['contact_category']=category;uv=me.uv_layers.new(name='MetreScaled')
   for f in me.polygons:
    n=f.normal;u=Vector((0,1,0)) if abs(n.x)>.8 else Vector((1,0,0));w=n.cross(u)
    for k in f.loop_indices:q=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(q.dot(u),q.dot(w))
 for o in exportscene.objects:o.select_set(True)
 glb=P/'exports/terminal'/(name+'_Architecture_r002.glb');bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_yup=True,export_extras=True,use_selection=True,use_active_scene=True,export_lights=False,export_cameras=False)
 bpy.context.window.scene=scene
 for door in doors:
  bpy.ops.object.select_all(action='DESELECT')
  for n in door['preview_objects']:bpy.data.objects[n].select_set(True)
  f=P/'exports/terminal'/(door['id']+'_Preview_r002.glb');bpy.ops.export_scene.gltf(filepath=str(f),export_format='GLB',export_yup=True,export_extras=True,use_selection=True,use_active_scene=True,export_lights=False,export_cameras=False);door['preview_export']=f.relative_to(P).as_posix();door['preview_sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
 (P/'qa'/(name+'_geometry.json')).write_text(json.dumps(geometry,indent=2)+'\n');rows.append({'id':name,'native':native.relative_to(P).as_posix(),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'export':glb.relative_to(P).as_posix(),'export_sha256':hashlib.sha256(glb.read_bytes()).hexdigest(),'source_geometry':('qa/'+name+'_geometry.json'),'editable_mesh_parts':len(geometry),'architectural_triangles':sum(g['triangles'] for g in geometry if g['role']!='family_door'),'door_preview_triangles':sum(g['triangles'] for g in geometry if g['role']=='family_door'),'origin_world_xyz':[0,0,0],'rotation_y':0,'scale':[1,1,1],'doors':doors,'lights':markers,'no_top_cap_over_D18_route':True,'remaining':'Root route collars, operating service controllers and exact upper route roof/headroom; adjacent general-body seams atZ±510; pressure/load and final acceptance remain open'})
(P/'docs/TERMINAL_DELIVERY_R002.json').write_text(json.dumps({'assemblies':rows,'status':'Constructed isolated terminal architecture; checks and source views required before adoption','first_delivery_untouched':True,'root_floor_rule':PLAN['source_floor_policy'],'runtime_model_effort':'Not exposed'},indent=2)+'\n');print('TERMINAL_SLICE_CONSTRUCTED',[(r['id'],r['editable_mesh_parts'],r['architectural_triangles']) for r in rows])
