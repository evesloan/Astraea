"""Original four approved gallery compositions. No shared or retained source writes."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];D=P/'dependencies/canonical_9d6f85'
for directory in ['source/natives','exports/gallery','qa/gallery_views']:(P/directory).mkdir(parents=True,exist_ok=True)
M={};parts=[];footprints=[];lights=[];rows=[]
def mat(role,texture,color,emission=0):
 m=bpy.data.materials.new('G7_'+role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=.78
 path=D/'BlenderCatalogue/materials'/texture
 if path.exists():
  t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(path),check_existing=True);t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color'])
 if emission:b.inputs['Emission Color'].default_value=(*color,1);b.inputs['Emission Strength'].default_value=emission
 M[role]=m
def mesh(name,vertices,faces,role,contact='solid',foot=None):
 v=[(x,-z,y) for x,y,z in vertices];me=bpy.data.meshes.new(name);me.from_pydata(v,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name;assert bm.calc_volume()>1e-9,name;bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);me.materials.append(M[role]);uv=me.uv_layers.new(name='MetreScaled')
 for f in me.polygons:
  n=f.normal;u=Vector((0,1,0)) if abs(n.x)>.9 else Vector((1,0,0));w=n.cross(u)
  for i in f.loop_indices:q=me.vertices[me.loops[i].vertex_index].co;uv.data[i].uv=(q.dot(u),q.dot(w))
 o['contact_category']=contact;o['material_role']=role;parts.append(o)
 if foot:footprints.append({'object':name,'boundary':foot,'contact_y':0})
 return o
def prism(name,poly,y0,y1,role,contact='solid'):
 n=len(poly);v=[(x,y,z) for y in [y0,y1] for x,z in poly];f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,v,f,role,contact,poly if abs(y0)<1e-7 else None)
def rect(name,x0,x1,z0,z1,y0,y1,role,contact='solid'):
 return prism(name,[(x0,z0),(x1,z0),(x1,z1),(x0,z1)],y0,y1,role,contact)
def cylinder(name,x,z,r,y0,y1,role,n=12,contact='solid'):
 return prism(name,[(x+r*math.cos(i*math.tau/n),z+r*math.sin(i*math.tau/n)) for i in range(n)],y0,y1,role,contact)
def band(name,cx,cz,rx,rz,width,a0,a1,y0,y1,role,steps=12):
 outer=[(cx+(rx+width/2)*math.cos(a0+(a1-a0)*i/steps),cz+(rz+width/2)*math.sin(a0+(a1-a0)*i/steps)) for i in range(steps+1)]
 inner=[(cx+(rx-width/2)*math.cos(a0+(a1-a0)*i/steps),cz+(rz-width/2)*math.sin(a0+(a1-a0)*i/steps)) for i in reversed(range(steps+1))]
 return prism(name,outer+inner,y0,y1,role)
def stem(name,a,b,r,role):
 a=Vector(a);b=Vector(b);t=(b-a).normalized();u=t.cross(Vector((0,1,0)))
 if u.length<.1:u=t.cross(Vector((1,0,0)))
 u.normalize();w=t.cross(u);v=[tuple(p+r*(u*math.cos(i*math.tau/8)+w*math.sin(i*math.tau/8))) for p in [a,b] for i in range(8)]
 return mesh(name,v,[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)],role)
def leaf(name,a,b,width):
 a=Vector(a);b=Vector(b);middle=a.lerp(b,.55);cross=Vector((b.z-a.z,0,a.x-b.x)).normalized()*width;v=[a,middle+cross,b,middle-cross]
 return mesh(name,[tuple(q) for q in v]+[tuple(q+Vector((0,.018,0))) for q in v],[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)],'leaf','visual_plant')
def planting(name,x,z,y=.54,scale=1):
 for i in range(6):
  a=i*math.tau/6+.25;start=(x,y,z);tip=(x+scale*.32*math.cos(a),y+scale*(.40+.09*(i%3)),z+scale*.32*math.sin(a));stem(name+'_stem_'+str(i),start,tip,.014,'metal');leaf(name+'_leaf_'+str(i),start,tip,.11*scale)
def lantern(name,x,z):
 # Exact source/down-cone bounds stay inside approved X43..46.5 footprint.
 cylinder(name+'_base',x,z,.12,0,.035,'metal');cylinder(name+'_stem',x,z,.025,.035,1.74,'metal',8)
 cylinder(name+'_cup',x,z,.16,1.72,1.81,'metal');cylinder(name+'_opal',x,z,.13,1.81,1.94,'lens',12,'visual_lens');cylinder(name+'_cap',x,z,.16,1.94,1.97,'ivory')
 cylinder(name+'_down_lens',x,z,.115,1.695,1.72,'lens',12,'visual_lens')
 q=(x+.085,1.688,z);o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=(q[0],-q[2],q[1])
 l=bpy.data.lights.new(name+'_Source','SPOT');l.energy=65;l.color=(1,.92,.77);l.use_custom_distance=True;l.cutoff_distance=1.9;l.spot_size=math.radians(48);l.spot_blend=.35;o=bpy.data.objects.new(l.name,l);bpy.context.collection.objects.link(o);o.location=(q[0],-q[2],q[1])
 lights.append({'id':name,'datum':'DATUM_'+name,'position_local_xyz':q,'direction_xyz':[0,-1,0],'type':'SpotLight3D','range_m':1.9,'spot_angle_deg':24,'energy_proposal':.8,'color_rgb':[1,.92,.77],'collision':False,'cone_horizontal_bound_m':1.9*math.tan(math.radians(24)),'scope':'Downward source footprint only; no light reaches the X42..43 protected margin. Root registers through existing light budget.'})
def screen(name,x,z,width,height,y):
 rect(name+'_frame',x,x+.12,z-width/2,z+width/2,y,y+height,'metal')
 rect(name+'_face',x-.015,x,z-width/2+.08,z+width/2-.08,y+.08,y+height-.08,'teal')
 for j in range(4):rect(name+'_tactile_'+str(j),x-.03,x-.015,z-width*.30+j*width*.16,z-width*.26+j*width*.16,y+.18,y+.40,'ivory','visual_mark')
def bench_supports(name,x,z0,z1):
 for i,z in enumerate([z0,z1]):rect(name+'_foot_'+str(i),x-.12,x+.12,z-.16,z+.16,0,.40,'ivory')
def build(deck,y,kind):
 global M,parts,footprints,lights
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);M={};parts=[];footprints=[];lights=[]
 for role,tex,col in [('ivory','ivory_enamel.png',(.86,.82,.71)),('stone','warm_stone.png',(.54,.49,.40)),('metal','champagne_metal.png',(.58,.46,.26)),('wood','warm_walnut.png',(.24,.12,.055)),('teal','teal_weave.png',(.16,.31,.32)),('leaf','botanical/botanical_leaf_jade.png',(.15,.39,.23)),('soil','botanical/botanical_soil.png',(.09,.065,.04))]:mat(role,tex,col)
 mat('lens','ivory_enamel.png',(1,.78,.40),.65)
 # Rear architectural spine is a shaped low enclosure on the outer side,
 # leaving inward standing/approach space; no repeated room box or new floor.
 if kind=='botanical':
  band('Botanical_soil_receiver',2.7,3.1,.43,1.55,.28,-math.pi/2,math.pi/2,0,.54,'stone')
  band('Botanical_soil',2.7,3.1,.40,1.49,.21,-math.pi/2,math.pi/2,.54,.57,'soil')
  band('Botanical_curved_rest',2.05,3.1,.65,1.8,.42,-math.pi/2,math.pi/2,.40,.49,'wood')
  bench_supports('Botanical_rest',2.32,1.46,4.74)
  for i,z in enumerate([2.0,2.8,3.6,4.25]):planting('Specimen_'+str(i),2.99,z,.57,.62)
  screen('Botanical_field_guide',2.60,1.2,.75,.70,.78);cylinder('Botanical_guide_receiver',2.66,1.2,.035,0,.79,'metal',8)
 elif kind=='craft':
  poly=[(2.2,.85),(2.90,.85),(3.1,1.2),(3.1,4.8),(2.8,5.1),(2.15,5.1),(1.95,4.8),(1.95,3.8),(2.45,3.65),(2.45,2.05),(1.9,1.8),(1.9,1.15)]
  prism('Craft_swept_counter',poly,.77,.87,'wood');rect('Craft_accessible_worktop',1.3,2.5,2.35,3.25,.72,.79,'stone')
  for i,z in enumerate([1.30,4.55]):rect('Craft_receiver_'+str(i),2.35,2.75,z-.20,z+.20,0,.77,'ivory')
  for i,z in enumerate([1.4,4.45]):cylinder('Craft_stool_'+str(i),1.30,z,.28,.39,.48,'teal');cylinder('Craft_stool_post_'+str(i),1.3,z,.10,0,.39,'metal')
  for i in range(5):cylinder('Tactile_material_sample_'+str(i),2.55,1.10+i*.18,.055,.87,.94,['stone','metal','teal','wood','ivory'][i],8,'visual_sample')
  screen('Craft_guide',3.08,3.05,1.12,.66,1.02);cylinder('Craft_guide_receiver',3.14,3.05,.035,0,1.03,'metal',8)
 elif kind=='sky_reading':
  for i,z in enumerate([1.65,4.15]):
   band('Sky_reading_crescent_'+str(i),2.85,z,.87,.73,.45,math.pi*.65,math.pi*1.35,.40,.49,'teal',10)
   bench_supports('Sky_reading_receiver_'+str(i),2.15,z-.4,z+.4)
   band('Sky_reading_back_'+str(i),2.97,z,.92,.78,.11,math.pi*.65,math.pi*1.35,.49,.96,'wood',10)
  rect('Sky_reading_table',1.75,2.8,2.66,3.25,.67,.74,'stone');rect('Sky_table_receiver',2.15,2.35,2.83,3.05,0,.67,'metal')
  screen('Sky_orientation',3.04,3.0,.94,.76,1.02);cylinder('Sky_orientation_receiver',3.10,3.0,.035,0,1.03,'metal',8)
  for i in range(8):cylinder('Sky_map_star_'+str(i),2.4+.14*math.cos(i*2.4),2.94+.18*math.sin(i*2.4),.017,.74,.76,'metal',6,'visual_mark')
 else:
  poly=[(2.55,.75),(3.32,1.2),(3.32,4.8),(2.55,5.25),(2.12,4.85),(2.12,1.15)]
  prism('Refuge_shaped_rest_base',poly,0,.37,'ivory');prism('Refuge_cushion',[(x-.035,z) for x,z in poly],.37,.46,'teal')
  for i,z in enumerate([1.2,4.8]):
   stem('Refuge_canopy_receiver_'+str(i),(3.15,0,z),(3.15,1.75,z),.065,'wood');stem('Refuge_canopy_arm_'+str(i),(3.15,1.75,z),(1.95,1.92,z),.045,'metal')
  poly=[(1.92,.98),(2.6,.8),(3.3,1.22),(3.3,4.78),(2.6,5.2),(1.92,5.02)]
  prism('Refuge_folded_canopy',poly,1.94,2.04,'ivory');screen('Refuge_orientation',3.05,3.0,.90,.76,.74);cylinder('Refuge_orientation_receiver',3.11,3.0,.035,.46,.75,'metal',8)
 # Light sources are placed within footprint, not across the protected margin.
 for i,z in enumerate([1.05,4.95]):lantern('Gallery_source_'+str(i),1.75,z)
 for i,z in enumerate([.48,5.52]):
  cylinder('Edge_specimen_receiver_'+str(i),2.85,z,.22,0,.36,'stone');cylinder('Edge_specimen_soil_'+str(i),2.85,z,.17,.36,.38,'soil');planting('Edge_specimen_'+str(i),2.85,z,.38,.48)
 scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
 geometry=[]
 for o in parts:
  me=o.data;me.calc_loop_triangles();pts=[(v.co.x,v.co.z,-v.co.y) for v in me.vertices]
  assert all(.02<=q[0]<=3.48 and .02<=q[2]<=5.98 and -.00001<=q[1]<=2.10 for q in pts),(o.name,min(q[0] for q in pts),max(q[0] for q in pts))
  geometry.append({'object':o.name,'contact':o['contact_category'],'role':o['material_role'],'vertices_local_xyz':pts,'triangles':len(me.loop_triangles)})
 for l in lights:
  x,h,z=l['position_local_xyz'];r=l['cone_horizontal_bound_m'];assert x-r>=0 and x+r<=3.5 and z-r>=0 and z+r<=6,'Light cone leaves footprint'
 native=P/f'source/natives/G7_Gallery_{deck}_r001.blend';bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native))
 # The native retains semantic editability; export is batched by material and
 # contact category so root can create appropriate static contacts cheaply.
 for role in M:
  for contact in ['solid','visual_plant','visual_lens','visual_mark','visual_sample']:
   selected=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('material_role')==role and o.get('contact_category')==contact]
   if not selected:continue
   bpy.ops.object.select_all(action='DESELECT')
   for o in selected:o.select_set(True)
   bpy.context.view_layer.objects.active=selected[0]
   if len(selected)>1:bpy.ops.object.join()
   bpy.context.object.name='G7_'+deck+'_'+role+'_'+contact;bpy.context.object['contact_category']=contact
 out=P/f'exports/gallery/G7_Gallery_{deck}_r001.glb';bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
 row={'id':'G7_Gallery_'+deck+'_r001','deck':deck,'purpose':kind,'origin_world_xyz':[43,y,-25],'rotation_y':0,'scale':[1,1,1],'bounds_world_xyz':[[43,y,-25],[46.5,y+2.1,-19]],'source':native.relative_to(P).as_posix(),'export':out.relative_to(P).as_posix(),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'semantic_parts':len(geometry),'triangles':sum(o['triangles'] for o in geometry),'foot_contacts':footprints,'lights':lights,'new_floor_area_m2':0,'retained_floor_owner':deck+'_authored_atrium_terrace','collision_rule':'solid contact-category meshes only; foliage/lens/marks/samples excluded. Root adopts static contact cache, existing light budget and residency.','status':'Constructed first source batch, uninstalled; no operational display/audio/species-fit/final-art acceptance'}
 (P/f'qa/gallery_geometry_{deck}.json').write_text(json.dumps(geometry,indent=2)+'\n');rows.append(row)
for deck,y,kind in [('D06',27,'botanical'),('D09',52.5,'craft'),('D12',78,'sky_reading'),('D16',97.5,'refuge')]:build(deck,y,kind)
(P/'docs/GALLERY_PLACEMENT_AND_INTERFACES.json').write_text(json.dumps({'canonical_ownership_baseline':'9d6f8518f9ddbe5892711ca4eb4849a46fbd32be','approved_central_bypass':[[0,-72],[0,-56],[40,-52],[40,52],[0,56],[0,72]],'protected_strip_x':[38,42],'preserved_margin_x':[42,43],'rooms':rows,'root_integration':'Add four models at exact origins; no new floor/cap/guard or global shared files here. Catalogue identities are pending root registration.'},indent=2)+'\n');print('GALLERY_BATCH_CONSTRUCTED',len(rows))
