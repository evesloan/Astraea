"""Scratch-only additive AST-ENG-008 furnishings. Requires parent serial Blender slot."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,sys
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
assert str(R)=='/workspace/scratch/375c2e438292/engineering-essentials'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((C/'catalogue_manifest.json').read_text());registry={a['catalogue_id']:a for a in manifest['assets']}
assert registry['AST-ENG-008']['family']=='secondary_engineering_section'
inputs={}
for ID in ['AST-ENG-008','AST-ENG-003','AST-STF-007']:
 for k in ['source','export']:
  p=C/registry[ID][k];h=sha(p);assert h==registry[ID][k+'_sha256'];inputs[str(p)]=h
for p in [C/'standards/staff_materials.py',C/'materials/staff/manifest.json']+list((C/'materials/staff').glob('*.png')):inputs[str(p)]=sha(p)
(R/'qa/input_hashes.json').write_text(json.dumps(inputs,indent=2)+'\n')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sys.path.insert(0,str(C/'standards'));import staff_materials
M=staff_materials.materials();parts=[];contacts=[];instances=[]
def cv(p):return(p[0],-p[2],p[1])
def uv(mesh,mat):
 layer=mesh.uv_layers.new(name='MetreScaled');tile=mat.get('meters_per_tile_uv',[1,1])
 for f in mesh.polygons:
  n=f.normal;u=Vector((1,0,0)) if abs(n.x)<.7 else Vector((0,1,0));u=(u-n*u.dot(n)).normalized();v=n.cross(u)
  for li in f.loop_indices:
   q=mesh.vertices[mesh.loops[li].vertex_index].co;layer.data[li].uv=(q.dot(u)/tile[0],q.dot(v)/tile[1])
def mesh(n,verts,faces,role='staff_zinc',bevel=0):
 me=bpy.data.meshes.new(n);me.from_pydata([cv(v) for v in verts],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(ob);me.materials.append(M[role]);uv(me,M[role]);ob['material_role']=role;ob['catalogue_derivative']='AST-ENG-008_essentials';ob['collision_contract']='static_surface';parts.append(ob)
 if bevel:
  m=ob.modifiers.new('Editable edge easing','BEVEL');m.width=bevel;m.segments=2;m.limit_method='ANGLE';m=ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL');m.keep_sharp=True
 return ob
def box(n,b,role='staff_zinc',bevel=0):
 x,y,z,X,Y,Z=b;return mesh(n,[(x,y,z),(X,y,z),(X,y,Z),(x,y,Z),(x,Y,z),(X,Y,z),(X,Y,Z),(x,Y,Z)],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role,bevel)
def plate(n,x,y,z,w,h,d,role='staff_zinc',ch=.025):
 # A chamfered profile in the XY plane, with actual thickness along Z.
 a=[(-w/2+ch,-h/2),(w/2-ch,-h/2),(w/2,-h/2+ch),(w/2,h/2-ch),(w/2-ch,h/2),(-w/2+ch,h/2),(-w/2,h/2-ch),(-w/2,-h/2+ch)]
 return mesh(n,[(x+u,y+v,z+s*d/2) for s in [-1,1] for u,v in a],[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)],role)
def cylinder(n,c,r,depth,role='staff_zinc',axis='y',segments=16):
 x,y,z=c;verts=[]
 for side in [-1,1]:
  for i in range(segments):
   a=2*math.pi*i/segments
   verts.append((x+r*math.cos(a),y+side*depth/2,z+r*math.sin(a)) if axis=='y' else (x+r*math.cos(a),y+r*math.sin(a),z+side*depth/2))
 return mesh(n,verts,[tuple(reversed(range(segments))),tuple(range(segments,segments*2))]+[(i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)],role)
def append_instance(ID,p,yaw=0,scale=1,prefix=''):
 source=C/registry[ID]['source']
 with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=src.objects
 objs=[o for o in dst.objects if o and o.type in ('MESH','EMPTY')]
 for o in objs:bpy.context.collection.objects.link(o)
 bpy.context.view_layer.update();T=Matrix.Translation(Vector(cv(p)))@Matrix.Rotation(yaw,4,'Z')@Matrix.Diagonal((scale,scale,scale,1))
 for o in objs:
  if o.parent not in objs:o.matrix_world=T@o.matrix_world
 for o in objs:
  o.name=prefix+o.name;o['retained_source_id']=ID;o['retained_source_sha256']=registry[ID]['source_sha256'];o['catalogue_derivative']='AST-ENG-008_essentials'
  if o.type=='MESH':parts.append(o);o['collision_contract']='static_surface'
 # Only local material copies get the new static engineering print; no source bytes change.
 if ID=='AST-ENG-003':
  for o in objs:
   if o.type!='MESH':continue
   for s in o.material_slots:
    m=s.material
    if m and m.get('astraea_material_role')=='utility_console_original_print':
     local=m.copy();local.name=prefix+'EngineeringStaticPrint';local['astraea_material_role']='engineering_static_print'
     for node in local.node_tree.nodes:
      if node.type=='TEX_IMAGE':node.image=bpy.data.images.load(str(R/'textures/console_graphics.png'),check_existing=True);node.image.pack()
     s.material=local
 instances.append({'id':ID,'prefix':prefix,'position_xyz':p,'yaw':yaw,'uniform_scale':scale})
 return objs
# Retained proper cabinet: source rear edge touches the south wall, feet touch compiler Y6.
append_instance('AST-STF-007',(31,6,-400.49),math.pi,prefix='WorkbenchStorage_')
contacts.append({'part':'WorkbenchStorage','target':'workbay_south_wall0','type':'rear_splashboard_wall','plane_z':-400.18})
contacts.append({'part':'WorkbenchStorage','target':'compiler floor','type':'feet','plane_y':6})
# Three source-derived tactile control faces. Backing extensions are seated on existing display fronts.
for x in [23,26,29]:
 plate(f'ConsoleBacking_{x}',x,7.47,-462.925,.98,.84,.05,'staff_bluegrey_paint',.06)
 append_instance('AST-ENG-003',(x,7.5,-462.90),prefix=f'Control_{x}_')
 contacts.append({'part':f'ConsoleBacking_{x}','target':f'control_display_{x}','type':'rear_face_contact','plane_z':-462.95})
# Isolation control is mounted to its existing north-facing solid support.
append_instance('AST-ENG-003',(36,7.3,-441.4),math.pi,prefix='Isolation_')
contacts.append({'part':'Isolation','target':'isolation_face','type':'wall_pads','plane_z':-441.4})
# The existing instrument casing remains; the small real controls give it purpose.
append_instance('AST-ENG-003',(22.5,7.15,-401.8),math.pi,.55,prefix='BenchInstrument_')
contacts.append({'part':'BenchInstrument','target':'bench_supported_instrument','type':'wall_pads','plane_z':-401.8})
# Worktop returns rest on the retained bench, avoiding the instrument's occupied rectangle.
for i,(lo,hi) in enumerate([(21.02,21.97),(23.03,26.98)]):box('BenchWorktop_'+str(i),(lo,6.9,-401.97,hi,6.936,-400.73),'staff_white_paint',.012)
box('BenchFrontFold',(21.015,6.76,-402.03,26.985,6.9,-402),'staff_zinc',.005)
for x in [21.22,23.5,26.78]:box('BenchLegibleDrawerPull_'+str(x),(x-.12,6.53,-402.07,x+.12,6.57,-402),'staff_rubber',.009)
contacts.append({'part':'BenchWorktop','target':'maintenance_bench','type':'top_contact','plane_y':6.9})
# Supported recessed toolboard on the existing south wall; no route intrusion.
plate('ToolboardFoldedBack',24,7.73,-400.23,5.5,1.42,.06,'staff_bluegrey_paint',.12)
plate('ToolboardInset',24,7.73,-400.275,5.24,1.17,.03,'staff_rubber',.08)
for x in [21.45,26.55]:
 for y in [7.12,8.34]:cylinder('ToolboardWallStandoff_'+str((x,y)),(x,y,-400.19),.028,.02,'staff_zinc','z')
# Each tool is a readable silhouette held by a separate bracket.
for i,x in enumerate([21.85,22.5,23.15]):
 y=7.70;plate('SpannerHandle_'+str(i),x,y,-400.34,.095,.57,.028,'staff_zinc',.035)
 # Open jaw: two prongs, neck and shoulder; no flat icon used as a tool.
 plate('SpannerShoulder_'+str(i),x,y+.31,-400.34,.22,.14,.028,'staff_zinc',.035)
 for sx in [-1,1]:plate('SpannerJaw_'+str((i,sx)),x+sx*.085,y+.41,-400.34,.055,.17,.028,'staff_zinc',.013)
 cylinder('SpannerHandleEnd_'+str(i),(x,y-.30,-400.34),.066,.028,'staff_zinc','z')
 box('SpannerHook_'+str(i),(x-.035,y-.04,-400.35,x+.035,y+.01,-400.29),'staff_cable_blue',.004)
for i,x in enumerate([24,24.5]):
 plate('DriverGrip_'+str(i),x,7.53,-400.35,.12,.29,.065,'staff_cable_red',.04)
 cylinder('DriverShaft_'+str(i),(x,7.87,-400.35),.016,.42,'staff_zinc','y',12)
 box('DriverClip_'+str(i),(x-.08,7.61,-400.4,x+.08,7.68,-400.29),'staff_zinc',.007)
# Sized socket rail: distinct nested openings and a supporting lip.
box('SocketRail',(25.0,7.13,-400.48,26.35,7.19,-400.29),'staff_zinc',.01)
for i,x in enumerate([25.15,25.43,25.74,26.08]):
 r=.065+i*.012;N=16;v=[]
 for y,rad in [(7.19,r),(7.41,r),(7.41,r*.58),(7.25,r*.58)]:
  v += [(x+rad*math.cos(2*math.pi*j/N),y,-400.36+rad*math.sin(2*math.pi*j/N)) for j in range(N)]
 f=[]
 for k in range(3):
  f += [(k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j) for j in range(N)]
 f += [tuple(reversed(range(N))),tuple(range(3*N,4*N))]
 mesh('HollowSocket_'+str(i),v,f,'staff_zinc')
contacts.append({'part':'ToolboardWallStandoff','target':'workbay_south_wall0','type':'wall_contact','plane_z':-400.18})
# Closed cabinets gain purposeful framed access, handles and ventilated lower panels.
for n,x,z,front in [('spares',36,-462.5,1),('quarantine',44,-462.5,1),('consumables',36,-401.5,-1),('bagged_returns',44,-401.5,-1)]:
 plane=z+front*.65
 plate(n+'_DoorFront',x,7.13,plane+front*.012,1.12,2.08,.024,'staff_bluegrey_paint',.075)
 for sy in [-1,1]:plate(n+'_Hinge_'+str(sy),x-.48,7.12+sy*.63,plane+front*.037,.05,.15,.026,'staff_zinc',.008)
 plate(n+'_Pull',x+.39,7.16,plane+front*.057,.06,.28,.066,'staff_zinc',.018)
 for i in range(5):box(n+'_Louvre_'+str(i),(x-.34,6.27+i*.055,min(plane+front*.026,plane+front*.045),x+.34,6.291+i*.055,max(plane+front*.026,plane+front*.045)),'staff_zinc')
 contacts.append({'part':n+'_DoorFront','target':n+'_closed_cabinet','type':'front_surface_contact','plane_z':plane})
# Modest pigment signage with source-framed mounts. No fake screens or light sources.
def image_mat(name,path):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.86;tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(path),check_existing=True);tex.image.pack();tex.interpolation='Linear';m.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color']);return m
signmat=image_mat('EngineeringOriginalSignPigment',R/'textures/engineering_signs.png')
def sign(n,c,w,h,row,normal='north'):
 x,y,z=c;front=-1 if normal=='north' else 1
 plate(n+'_Mount',x,y,z,w+.08,h+.08,.05,'staff_zinc',.025)
 ob=mesh(n+'_PrintedFace',[(x-w/2,y-h/2,z+front*.027),(x+w/2,y-h/2,z+front*.027),(x+w/2,y+h/2,z+front*.027),(x-w/2,y+h/2,z+front*.027)],[(0,1,2,3)])
 ob.data.materials.clear();ob.data.materials.append(signmat);ob['collision_contract']='none';uvl=ob.data.uv_layers.active
 for li,(u,v) in zip(ob.data.polygons[0].loop_indices,[(0,0),(1,0),(1,1),(0,1)]):uvl.data[li].uv=((1-u if front<0 else u),1-(row+1-v)/10)
 # Correct normals for selected viewing face.
 if front>0:
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
 return ob
sign('WorkbayIdentity',(24,8.68,-400.205),4.9,.60,1)
sign('ToolReturnLegend',(24,8.33,-400.335),2.05,.16,2)
# Instrument carries its retained-derived printed legend; no floating plaque.
for i,x in enumerate([23,26,29]):sign('ControlLegend_'+str(i),(x,7.97,-462.926),1.2,.15,7,'south')
for n,x,z,front,row in [('spares',36,-462.5,1,3),('quarantine',44,-462.5,1,8),('consumables',36,-401.5,-1,9),('bagged_returns',44,-401.5,-1,4)]:sign(n+'_Label',(x,7.83,z+front*.699),1.04,.13,row,'north' if front<0 else 'south')
# Visitor plaque lives on opaque south wall, not across the plant glass.
sign('VisitorInterpretation',(12.8,7.53,-417.205),3.3,.415,0)
# Supported cable rail under the three consoles, kept behind the operating zone.
for x in [23,26,29]:
 box('ConsoleCableTray_'+str(x),(x-.21,7.05,-462.62,x+.21,7.095,-462.56),'staff_zinc',.009)
 box('ConsoleCableBracket_'+str(x),(x-.045,7.01,-462.95,x+.045,7.075,-462.56),'staff_zinc',.009)
# Reuse exact semantic material graphs across appended copies, avoiding per-instance duplicates.
local_print=None
for ob in parts:
 for slot in ob.material_slots:
  mat=slot.material
  if not mat:continue
  role=mat.get('astraea_material_role')
  if role in M:slot.material=M[role]
  elif role=='engineering_static_print':
   if local_print is None:local_print=mat
   slot.material=local_print
# Classify materials and save editable source before evaluating static export copies.
for ob in parts:
 if 'material_role' not in ob:ob['material_role']='retained_staff_component'
 ob['static_furnishing_only']=True
bpy.context.view_layer.update();bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene['scope']='Additive candidate only; no runtime or first-pass art acceptance'
# Bounds from actual evaluated source, not planned cuboids.
def bounds(obs):
 dg=bpy.context.evaluated_depsgraph_get();vs=[];tri=0
 for ob in obs:
  eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();tri+=len(me.loop_triangles);vs += [ob.matrix_world@v.co for v in me.vertices];eo.to_mesh_clear()
 vv=[(v.x,v.z,-v.y) for v in vs];return [min(v[i] for v in vv) for i in range(3)]+[max(v[i] for v in vv) for i in range(3)],tri
rows=[]
for ob in parts:
 b,t=bounds([ob]);rows.append({'name':ob.name,'bounds_xyz':b,'triangles':t,'collision':ob.get('collision_contract','static_surface')})
prisms={'north_cart_strip':[20,6,-454.6,53.7,8.7,-451],'south_cart_strip':[20,6,-413,53.7,8.7,-409.4],'east_cart_strip':[48.3,6,-465.7,53.7,9.6,-398.3],'control_turn':[28.2,6,-460.8,31.8,8.7,-457.2],'workbay_turn':[28.2,6,-406.8,31.8,8.7,-403.2],'control_operating_face':[21.9,6,-462.4,30.1,8.4,-460.9]}
def overlap(a,b):return all(min(a[i+3],b[i+3])-max(a[i],b[i])>1e-5 for i in range(3))
clear={n:[r['name'] for r in rows if overlap(r['bounds_xyz'],b)] for n,b in prisms.items()};assert not any(clear.values()),clear
for p,h in inputs.items():assert sha(Path(p))==h
bpy.ops.file.pack_all();blend=R/'source/AST-ENG-008_essentials.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
# Static role batching retains all real openings in evaluated triangle geometry.
dg=bpy.context.evaluated_depsgraph_get();groups={};exportobs=[]
for src in parts:
 me=bpy.data.meshes.new_from_object(src.evaluated_get(dg));bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();active=me.uv_layers.active
 if active:
  for l in list(me.uv_layers):
   if l!=active:me.uv_layers.remove(l)
  active.name='MetreScaled';active.active_render=True
  # Evaluated bevel side faces need genuine nonzero metric UVs as well.
  me.calc_loop_triangles();repair=set()
  for tr in me.loop_triangles:
   a,b,c=[active.data[k].uv for k in tr.loops]
   if abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))<1e-9:repair.add(tr.polygon_index)
  for pi in repair:
   f=me.polygons[pi];axis=max(range(3),key=lambda k:abs(f.normal[k]));axes=[k for k in range(3) if k!=axis]
   for li in f.loop_indices:
    q=me.vertices[me.loops[li].vertex_index].co;active.data[li].uv=(q[axes[0]],q[axes[1]])
 ob=bpy.data.objects.new('EXPORT_'+src.name,me);bpy.context.collection.objects.link(ob);ob.matrix_world=src.matrix_world.copy()
 key=(tuple(m.name for m in me.materials),src.get('collision_contract','static_surface'));groups.setdefault(key,[]).append(ob)
for i,(key,obs) in enumerate(groups.items()):
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
 if len(obs)>1:bpy.ops.object.join()
 ob=obs[0];ob.name='EssentialsRole_'+str(i);ob['collision_contract']=key[1];ob['catalogue_derivative']='AST-ENG-008_essentials';exportobs.append(ob)
bpy.ops.object.select_all(action='DESELECT')
for ob in exportobs:ob.select_set(True)
bpy.context.view_layer.objects.active=exportobs[0];glb=R/'exports/AST-ENG-008_essentials.glb'
bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_apply=True,export_cameras=False,export_lights=False)
record={'scope':'Scratch additive furniture; no production adoption or visual acceptance','source':str(blend),'source_sha256':sha(blend),'export':str(glb),'export_sha256':sha(glb),'retained_inputs_unchanged':True,'instances':instances,'contacts':contacts,'actual_evaluated_parts':rows,'actual_clearance_prisms':prisms,'clearance_intrusions':clear,'input_hashes':inputs,'no_new_light_sources':True,'no_new_floor_mesh':True,'static_control_artwork':True,'not_tested':['Godot integration','actual physical cart handling','normal player-height in-game visual acceptance','target hardware performance']}
(R/'qa/source_build.json').write_text(json.dumps(record,indent=2)+'\n');print('ESSENTIALS_BUILD_OK',len(rows),sum(r['triangles'] for r in rows),len(exportobs))
