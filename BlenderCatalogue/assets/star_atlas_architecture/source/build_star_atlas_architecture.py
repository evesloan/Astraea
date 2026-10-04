"""Original layered Star Atlas library architecture, fitted to reviewed production volumes."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={};parts=[];material_contract=json.loads((CAT/'materials/material_manifest.json').read_text())['materials']
for role in ['ivory_enamel','warm_walnut','warm_stone','champagne_metal','teal_weave','botanical_soil','oatmeal_weave','clay_weave']:
 m=bpy.data.materials.new(role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=material_contract.get(role,{}).get('roughness',.82);b.inputs['Metallic'].default_value=material_contract.get(role,{}).get('metallic',0);m['meters_per_tile_uv']=material_contract.get(role,{}).get('meters_per_tile_uv',[1,1])
 path=CAT/'materials'/('botanical/'+role+'.png' if role.startswith('botanical') else role+'.png')
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(path));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
m=bpy.data.materials.new('GardenOpalLens');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(1,.95,.84,1);b.inputs['Emission Color'].default_value=(1,.91,.75,1);b.inputs['Emission Strength'].default_value=.7;mats['lens']=m

def mesh(name,vertices,faces,role):
 d=bpy.data.meshes.new(name);d.from_pydata(vertices,[],faces);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='MetreScaled')
 for p in d.polygons:
  n=p.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized() if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u).normalized();scale=mats[role].get('meters_per_tile_uv',[1,1])
  for li in p.loop_indices:
   q=d.vertices[d.loops[li].vertex_index].co
   uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
 return o

def extrusion(name,outline,bottom,top,role):
 n=len(outline);v=[(x,y,z)for z in [bottom,top]for x,y in outline];f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];return mesh(name,v,f,role)

def beam(name,points,width,depth,role):
 v=[]
 for i,p in enumerate(points):
  p=Vector(p);t=(Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])).normalized();side=Vector((0,1,0)) if abs(t.y)<.95 else Vector((1,0,0));side=(side-t*t.dot(side)).normalized();up=t.cross(side).normalized()
  for w,h in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]:v.append(tuple(p+side*w+up*h))
 f=[(3,2,1,0),tuple(range(len(v)-4,len(v)))]+[(i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j)for i in range(len(points)-1)for j in range(4)];return mesh(name,v,f,role)

def datum(name,p):
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=p


D=json.loads((ROOT/'source/section_contract.json').read_text());AID='AST-LIB-011'
for a in json.loads((CAT/'catalogue_manifest.json').read_text())['assets']:
 if a['catalogue_id']==AID:assert a['source']=='assets/star_atlas_architecture/source/'+AID+'.blend'
def xy(p):return(p[0]+80,-p[1])
def xyz(x,y,z):return(x+80,-z,y-78)
def wall(name,a,b,z0,z1,width,role):
 a=Vector(xy(a));b=Vector(xy(b));v=(b-a).normalized();n=Vector((-v.y,v.x))*width/2
 return extrusion(name,[tuple(a+n),tuple(b+n),tuple(b-n),tuple(a-n)],z0-78,z1-78,role)
def plane_box(name,x0,x1,z0,z1,y0,y1,role):return extrusion(name,[xy(v)for v in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]],y0-78,y1-78,role)
m=bpy.data.materials.new('StarAtlasArchitecturalGlass');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.23,.39,.42,.28);p.inputs['Alpha'].default_value=.28;mats['glass']=m
# Lower envelope follows the room's oblique corners. Inset every opaque wall
# within the actual allocation; the east face has genuine atrium glazing.
outer=D['lower_outline_xz']
for i,(a,b)in enumerate(zip(outer,outer[1:]+outer[:1])):
 if abs(a[0]+52)<.01 and abs(b[0]+52)<.01:continue
 aa=Vector(a);bb=Vector(b);t=(bb-aa).normalized();inside=Vector((t.y,-t.x))*.16;aa+=inside;bb+=inside
 wall('LIB_LowerPlinth_'+str(i),aa,bb,78,79.15,.24,'warm_walnut')
 wall('LIB_LowerWall_'+str(i),aa,bb,79.15,83.76,.20,'ivory_enamel')
 wall('LIB_LowerCrown_'+str(i),aa,bb,83.35,83.76,.30,'warm_walnut')
for z0,z1 in [(-29.8,-3.3),(3.3,27.8)]:
 wall('LIB_AtriumWindowBase_'+str(z0),(-52.16,z0),(-52.16,z1),78,78.72,.24,'warm_walnut')
 wall('LIB_AtriumGlass_'+str(z0),(-52.16,z0),(-52.16,z1),78.72,83.20,.028,'glass')
 wall('LIB_AtriumWindowHeader_'+str(z0),(-52.16,z0),(-52.16,z1),83.20,83.76,.26,'ivory_enamel')
 count=math.ceil((z1-z0)/4.5)
 for j in range(count+1):
  z=z0+(z1-z0)*j/count;wall('LIB_WindowMullion_%s_%s'%(z0,j),(-52.28,z),(-52.04,z),78.7,83.25,.12,'champagne_metal')
# Existing commons remain separate programmes, with actual floor-specific rooms.
for deck,y,ceiling in [('D13',84,88.26),('D14',88.5,92.76)]:
 for i,(a,b)in enumerate([((-96.85,-13.85),(-96.85,13.85)),((-96.85,-13.85),(-63.15,-13.85)),((-96.85,13.85),(-63.15,13.85))]):
  wall('LIB_'+deck+'_PerimeterBase_'+str(i),a,b,y,y+1.10,.22,'warm_walnut')
  wall('LIB_'+deck+'_PerimeterWall_'+str(i),a,b,y+1.10,ceiling,.18,'ivory_enamel')
 for z0,z1 in [(-13.85,-3.3),(3.3,13.85)]:
  wall('LIB_'+deck+'_ViewBase_'+str(z0),(-63.15,z0),(-63.15,z1),y,y+.72,.22,'warm_walnut')
  wall('LIB_'+deck+'_ViewGlass_'+str(z0),(-63.15,z0),(-63.15,z1),y+.72,ceiling-.40,.025,'glass')
  wall('LIB_'+deck+'_ViewHeader_'+str(z0),(-63.15,z0),(-63.15,z1),ceiling-.40,ceiling,.24,'ivory_enamel')
# Deep gently crowned portals leave the full6m clear route untouched.
for name,x,y,top in [('lower',-52.7,78,83.6),('middle',-63.7,84,88.1),('upper',-63.7,88.5,92.6)]:
 for side in [-1,1]:
  wall('LIB_PortalJamb_'+name+str(side),(x-.3,side*3.38),(x+.3,side*3.38),y,top,.22,'warm_stone')
 points=[xyz(x,top-.40+.20*math.sin(math.pi*i/16),-3.38+6.76*i/16)for i in range(17)]
 beam('LIB_ProfiledPortal_'+name,points,.30,.35,'warm_walnut')
# Four reserved bearing profiles, with every ring within the reviewed radius.
for i,pier in enumerate(D['support_reservations']):
 cx,cy=xy(pier['center_xz']);n=16;rings=[(0,.55),(.16,.58),(.42,.40),(5.55,.40),(5.76,.58),(6,.58),(6.24,.40),(9.90,.40),(10.26,.58),(10.5,.58),(10.74,.40),(14.20,.40),(14.48,.58),(14.76,.58)]
 v=[(cx+rr*math.cos(2*math.pi*j/n),cy+rr*math.sin(2*math.pi*j/n),h)for h,rr in rings for j in range(n)];f=[tuple(reversed(range(n))),tuple(range(len(v)-n,len(v)))]+[(k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j)for k in range(len(rings)-1)for j in range(n)];mesh('LIB_ReservedPier_'+str(i),v,f,'warm_stone')
# Coordinated floor-edge guards use the already-unioned openings. Split ONLY
# the actual upper-flight mouth, not the full width of a U-stair opening.
def guard_segments(a,b,deck):
 mouth=D['first_stair']if deck=='D13'else D['second_stair'];z=mouth['start_z'];lo,hi=mouth['upper_flight_x'];lo-=.04;hi+=.04
 if abs(a[1]-z)<.015 and abs(b[1]-z)<.015:
  x0,x1=sorted([a[0],b[0]]);parts=[]
  if x0<lo:parts.append(((x0,z),(min(lo,x1),z)))
  if x1>hi:parts.append(((max(hi,x0),z),(x1,z)))
  return [(aa,bb)for aa,bb in parts if Vector(aa).lerp(Vector(bb),.5)!=Vector(aa)]
 return[(a,b)]
lift=D['lift'];shaft=lift['floor_hole_xz']
for region in D['floor_regions']:
 if '_gallery_'not in region['id']:continue
 deck=region['deck'];y=D['floor_y'][deck]
 for ri,ring in enumerate([region['boundary']]+region['holes']):
  for j,(a,b)in enumerate(zip(ring,ring[1:]+ring[:1])):
   mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
   if abs(mid[0]+48)<.01:continue
   if shaft['x'][0]-.02<=mid[0]<=shaft['x'][1]+.02 and shaft['z'][0]-.02<=mid[1]<=shaft['z'][1]+.02:continue
   for si,(aa,bb)in enumerate(guard_segments(a,b,deck)):
    name='%s_%s_%s_%s'%(deck,ri,j,si)
    wall('LIB_Fascia_'+name,aa,bb,y-.44,y+.04,.18,'ivory_enamel')
    wall('LIB_GuardBase_'+name,aa,bb,y+.04,y+.23,.12,'warm_walnut')
    wall('LIB_GuardGlass_'+name,aa,bb,y+.23,y+1.07,.023,'glass')
    wall('LIB_GuardCap_'+name,aa,bb,y+1.07,y+1.16,.10,'champagne_metal')
# Deliberate guard attachment at the tangent pier; stays within its0.6m envelope.
wall('LIB_PierGuardJoint',(-79,10),(-79,10.22),85.07,85.16,.10,'champagne_metal')
# Source-authored treads and closed supports; runtime uses matching smooth ramps.
for label,st in [('first',D['first_stair']),('second',D['second_stair'])]:
 sign=1 if st['turn_z']>st['start_z']else -1
 for flight,(bounds,a,b,y0,y1)in enumerate([(st['lower_flight_x'],st['start_z'],st['turn_z'],st['bottom_y'],st['landing_y']),(st['upper_flight_x'],st['turn_z'],st['start_z'],st['landing_y'],st['top_y'])]):
  x0,x1=bounds
  for i in range(st['steps_per_flight']):
   za=a+(b-a)*i/st['steps_per_flight'];zb=a+(b-a)*(i+1)/st['steps_per_flight'];lo,hi=sorted([za,zb]);h0=y0+(y1-y0)*i/st['steps_per_flight'];h1=y0+(y1-y0)*(i+1)/st['steps_per_flight']
   plane_box('LIB_Step_%s_%d_%02d'%(label,flight,i),x0,x1,lo,hi,h0,h1,'warm_stone')
  # Solid wedge below each smooth flight is not an under-stair circulation route.
  v=[xyz(x,yy,z)for x in [x0,x1]for yy,z in [(st['bottom_y'],a),(st['bottom_y'],b),(y1,b),(y0,a)]]
  mesh('LIB_ClosedFlight_'+label+str(flight),v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'warm_walnut')
  for x in [x0-.04,x1+.04]:
   points=[xyz(x,y0+1.1,a),xyz(x,y1+1.1,b)];beam('LIB_StairCap_'+label+str(flight)+str(x),points,.08,.08,'champagne_metal')
   # Continuous glass keeps loose objects out of the inter-flight well.
   vv=[xyz(xx,yy,zz)for xx in [x-.012,x+.012]for yy,zz in [(y0+.13,a),(y1+.13,b),(y1+1.03,b),(y0+1.03,a)]]
   mesh('LIB_StairGlass_'+label+str(flight)+str(x),vv,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'glass')
 # Seal the narrow inter-flight gap under the upper slope; no loose-prop trap.
 gx0=st['lower_flight_x'][1];gx1=st['upper_flight_x'][0];a=st['turn_z'];b=st['start_z'];y0=st['landing_y'];y1=st['top_y']
 vv=[xyz(x,yy,z)for x in [gx0,gx1]for yy,z in [(st['bottom_y'],a),(st['bottom_y'],b),(y1,b),(y0,a)]]
 mesh('LIB_ClosedInterflightSpine_'+label,vv,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'warm_walnut')
 lx0=st['lower_flight_x'][0];lx1=st['upper_flight_x'][1];za,zb=st['landing_z']
 plane_box('LIB_Landing_'+label,lx0,lx1,za,zb,st['landing_y']-.24,st['landing_y'],'warm_stone')
 plane_box('LIB_LandingClosedBase_'+label,lx0,lx1,za,zb,st['bottom_y'],st['landing_y']-.24,'warm_walnut')
 back=zb if sign>0 else za
 for aa,bb in [((lx0,za),(lx0,zb)),((lx1,za),(lx1,zb)),((lx0,back),(lx1,back))]:
  wall('LIB_LandingGlass_'+label+str(aa),aa,bb,st['landing_y']+.13,st['landing_y']+1.07,.024,'glass');wall('LIB_LandingCap_'+label+str(aa),aa,bb,st['landing_y']+1.07,st['landing_y']+1.16,.10,'champagne_metal')
for reservation in D['non_public_reservations']:
 if 'backing' in reservation['id']:
  plane_box('LIB_NonPublicBacking_'+reservation['id'],*reservation['x'],*reservation['z'],reservation['bottom_y'],reservation['top_y'],'warm_walnut')
# Fitted shaft, with three actual landing apertures and an opaque pan that stays
# within the D12 slab instead of opening the performers' commons below.
ox,cz=lift['origin_xz'];top=lift['shaft_top_y']
for side in [-1,1]:wall('LIB_LiftShaftSide_'+str(side),(ox-.18,cz+side*2.10),(ox+3.76,cz+side*2.10),77.76,top,.12,'ivory_enamel')
wall('LIB_LiftShaftRear',(ox+3.76,cz-2.10),(ox+3.76,cz+2.10),77.76,top,.12,'ivory_enamel')
for lo,hi in [(80.86,84),(86.86,88.5),(91.36,top)]:wall('LIB_LiftFrontBand_'+str(lo),(ox-.10,cz-2.04),(ox-.10,cz+2.04),lo,hi,.12,'ivory_enamel')
plane_box('LIB_LiftPitPan',*lift['floor_hole_xz']['x'],*lift['floor_hole_xz']['z'],*lift['pit_pan_y'],'warm_stone')
# Warm ceiling structure belongs to the same tapered library section. No false
# exterior skylight is cut through the protected D15 commons.
for i,z in enumerate([-11.5,-4,4,11.5]):
 points=[xyz(-96.7+33.4*j/16,92.24+.30*math.sin(math.pi*j/16),z)for j in range(17)];beam('LIB_CeilingRib_'+str(i),points,.26,.20,'ivory_enamel')
 for x in [-92.5,-80,-66.5]:beam('LIB_RibRoofMating_%s_%s'%(i,x),[xyz(x,92.48,z),xyz(x,92.76,z)],.08,.08,'champagne_metal')
# Distinct low canopies mark the lower peripheral reading bays.
for i,(x0,x1,z0,z1,h)in enumerate([(-91,-76,-31,-21,81.45),(-91,-76,21,31,81.70),(-62,-53,-26,-10,82.40),(-62,-53,10,25,82.15)]):
 plane_box('LIB_ReadingCanopy_'+str(i),x0,x1,z0,z1,h,h+.18,'warm_walnut')
 for x in [x0+.2,x1-.2]:beam('LIB_CanopyReturn_%s_%s'%(i,x),[xyz(x,h+.18,z0+.2),xyz(x,83.76,z0+.2)],.10,.10,'ivory_enamel')
# Source-mounted local fixtures, with explicit below-lens exit markers.
lights=[(-59,0,83.25),(-83,-25,81.18),(-83,25,81.43),(-57,-17,82.13),(-57,17,81.88),(-80,0,91.9),(-90,-11.5,87.5),(-72.2,0,87.55),(-82,12.5,91.95),(-72.2,0,91.95)]
for i,(x,z,h)in enumerate(lights):
 cx,cy=xy((x,z));q=[(cx+.28*math.cos(j*math.pi/8),cy+.28*math.sin(j*math.pi/8))for j in range(16)];extrusion('LIB_LightHousing_'+str(i),q,h-78,h-78+.10,'champagne_metal');extrusion('LIB_OpalLens_'+str(i),[(cx+(a-cx)*.88,cy+(b-cy)*.88)for a,b in q],h-78-.025,h-78,'lens');datum('light_'+str(i),(cx,cy,h-78-.04))
 mount=83.76 if i==0 else [0,81.45,81.70,82.40,82.15][i]if i<5 else 92.76 if i==5 or i>=8 else 88.26
 beam('LIB_LightMount_'+str(i),[(cx,cy,h-78+.10),(cx,cy,mount-78)],.045,.045,'champagne_metal')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source));tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
# Retain editable semantic source parts, but export local material/contact groups.
for o in parts:o['contact_group']='steps'if o.name.startswith('LIB_Step')else'static'
for group in ['static','steps']:
 for role,material in mats.items():
  selected=[o for o in list(scene.objects)if o.type=='MESH'and o.get('contact_group')==group and o.data.materials and o.data.materials[0]==material]
  if not selected:continue
  bpy.ops.object.select_all(action='DESELECT')
  for o in selected:o.select_set(True)
  bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.join();bpy.context.object.name='LIB_'+group+'_'+role
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Star Atlas layered library and port commons architecture','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Editable production section; runtime stairs, three-stop lift, guard, furnishings, lighting and visual acceptance pending'};(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
