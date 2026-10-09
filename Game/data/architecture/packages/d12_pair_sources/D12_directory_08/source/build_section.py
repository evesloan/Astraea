"""Batch D source authoring. Blender4.3.2; metres. Authored local (u,height,v) maps to world XYZ then Blender(X,-Z,Y). Native/export omit floors and QA context. No registry IDs created."""
import bpy,math,json,hashlib,importlib.util,sys
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1]; C=P/'dependencies/Catalogue';CONFIG=json.loads((P/'docs/design.json').read_text());SIDE=CONFIG['side'];Z=CONFIG['z'];KEY=CONFIG['key']; A=[];LIGHTS=[];M={};seq=0

def world(p):u,y,v=p;return (SIDE*(8+u),78+y,Z+v)
def xyz(p):x,y,z=world(p);return Vector((x,-z,y))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def uv(o):
 if o.type!='MESH':return
 me=o.data;me.update();layer=me.uv_layers.get('UV0') or me.uv_layers.new(name='UV0')
 for f in me.polygons:
  drop=max(range(3),key=lambda a:abs(f.normal[a]));ax=[a for a in range(3) if a!=drop]
  for li in f.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;layer.data[li].uv=(v[ax[0]],v[ax[1]])

def finish(o,n,mat='ivory_enamel',support='root_floor_proposal',zone='architecture',bev=.03):
 o.name=KEY+'__'+n
 if o.type=='MESH':
  bpy.context.view_layer.objects.active=o
  if bev:
   b=o.modifiers.new('Edge craft','BEVEL');b.width=bev;b.segments=2;bpy.ops.object.modifier_apply(modifier=b.name)
  o.data.materials.clear();o.data.materials.append(M[mat]);uv(o)
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT')
 o['section']=KEY;o['support']=support if support.startswith(('root_',KEY)) else KEY+'__'+support;o['zone']=zone;A.append(o);return o

def box(n,p,d,mat='ivory_enamel',sup='root_floor_proposal',zone='architecture',bev=.03):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(p));o=bpy.context.object;o.dimensions=(d[0],d[2],d[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,mat,sup,zone,min(bev,min(d)*.3))

def rod(n,a,b,r=.06,mat='champagne_metal',sup='root_floor_proposal',zone='architecture',verts=12):
 va,vb=xyz(a),xyz(b);delta=vb-va;bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=delta.length,location=(va+vb)/2);o=bpy.context.object;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,mat,sup,zone,.008)

def prism(n,poly,y,h,mat='warm_walnut',sup='root_floor_proposal',zone='architecture'):
 vs=[xyz((u,y,v)) for u,v in poly]+[xyz((u,y+h,v)) for u,v in poly];k=len(poly);faces=[tuple(range(k-1,-1,-1)),tuple(range(k,2*k))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)];me=bpy.data.meshes.new(n);me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);return finish(o,n,mat,sup,zone,.025)

def cyl(n,p,r,h,mat='champagne_metal',sup='root_floor_proposal',zone='programme'):
 return rod(n,p,(p[0],p[1]+h,p[2]),r,mat,sup,zone,32)

def wall(n,a,b,h=4.9,w=.36,mat='ivory_enamel',y=0,sup='root_floor_proposal',zone='architecture'):
 u,v=a;du,dv=b[0]-u,b[1]-v;l=math.hypot(du,dv);o=box(n,((u+b[0])/2,y+h/2,(v+b[1])/2),(l,w,h) if False else (l,h,w),mat,sup,zone,.045)
 # Long box local BlenderX must align actual converted wall vector.
 vec=xyz((b[0],y,b[1]))-xyz((a[0],y,a[1]));o.rotation_euler[2]=math.atan2(vec.y,vec.x);return o

def sign(n,body,u,v,y=1.7,sup='root_floor_proposal'):
 back=box(n+'_plate',(u,y,v),(.10,.50,2.0),'warm_walnut',sup,zone='wayfinding');cu=bpy.data.curves.new(n,'FONT');cu.body=body;cu.align_x='CENTER';cu.align_y='CENTER';cu.size=.16;cu.extrude=.001;o=bpy.data.objects.new(n,cu);bpy.context.collection.objects.link(o);o.location=xyz((u-.06,y,v));o.rotation_euler=(math.pi/2,0, math.pi/2 if SIDE<0 else -math.pi/2);o.data.materials.append(M['ivory_enamel']);finish(o,n+'_text',support=back.name,zone='wayfinding',bev=0)

def asset(n,file,u,v,y=0,yaw=None,sup=None):
 with bpy.data.libraries.load(str(C/file),link=False) as (data,to):to.objects=data.objects
 os=[o for o in to.objects if o and o.type=='MESH']
 for ob in os:bpy.context.collection.objects.link(ob)
 bpy.context.view_layer.update()
 original_world={o:o.matrix_world.copy() for o in os}
 for ob in os:ob.parent=None
 rot=Matrix.Rotation((SIDE*math.pi/2 if yaw is None else yaw),4,'Z');trans=Matrix.Translation(xyz((u,y,v)))
 for o in os:
  o.hide_render=False;o.hide_viewport=False;o.hide_select=False;o.hide_set(False);o.parent=None;o.matrix_world=trans@rot@original_world[o];o.name=KEY+'__'+n+'__'+o.name;o['section']=KEY;o['zone']='catalogue_'+n;o['support']='catalogue_contact_graph';o['shelf_support']=sup or '';A.append(o)
  for im in bpy.data.images:
   if im.source=='FILE' and not im.packed_file:
    try:im.pack()
    except:pass
 return os

def seat(n,u,v,length=5,face=1,cloth='teal_weave',zone='rest'):
 b=box(n+'_plinth',(u,.17,v),(1.3,.34,length),'warm_walnut',zone=zone,bev=.08)
 box(n+'_pad',(u,.45,v),(1.4,.22,length-.15),cloth,b.name,zone,.075)
 back=box(n+'_back',(u-.56*face,.86,v),(.24,1.10,length),cloth,b.name,zone,.08)
 for k in [-1,1]:box(n+'_arm'+str(k),(u,.52,v+k*(length/2-.12)),(1.42,.40,.24),'warm_walnut',b.name,zone,.06)
 return b.name

def arcseat(n,u,v,r,start,end,cloth='oatmeal_weave'):
 # Faceted continuous fitted seating with radial depth; generous gap in arrival sector.
 count=max(3,int(abs(end-start)/18));poly=[]
 for j in range(count+1):a=math.radians(start+(end-start)*j/count);poly.append((u+(r+.55)*math.cos(a),v+(r+.55)*math.sin(a)))
 for j in range(count,-1,-1):a=math.radians(start+(end-start)*j/count);poly.append((u+(r-.55)*math.cos(a),v+(r-.55)*math.sin(a)))
 b=prism(n+'_base',poly,0,.33,'warm_walnut',zone='gathering');prism(n+'_cushion',poly,.33,.20,cloth,b.name,'gathering')
 for j in range(count):
  a0=math.radians(start+(end-start)*j/count);a1=math.radians(start+(end-start)*(j+1)/count)
  pa=(u+(r+.54)*math.cos(a0),v+(r+.54)*math.sin(a0));pb=(u+(r+.54)*math.cos(a1),v+(r+.54)*math.sin(a1));wall(n+'_back'+str(j),pa,pb,.78,.20,cloth,.33,b.name,'gathering')

def table(n,u,v,r=.85):
 f=cyl(n+'_foot',(u,0,v),r*.60,.08,'dark_rubber');p=cyl(n+'_stem',(u,.08,v),.11,.61,'champagne_metal',f.name);t=cyl(n+'_top',(u,.69,v),r,.10,'warm_walnut',p.name)
 cyl(n+'_cup',(u+.20,.79,v),.09,.13,'ivory_enamel',t.name);box(n+'_folio',(u-.20,.815,v-.10),(.34,.05,.45),'clay_weave',t.name,'rest',.008);return t.name

def fixture(n,u,v,y=4.4,power=900):
 # Floor-supported blade pendant: roof frame and visible diffuser.
 post=box(n+'_post',(u,y/2,v),(.16,y,.16),'champagne_metal',zone='light_support')
 box(n+'_arm',(u+.5,y-.12,v),(1.14,.16,.18),'warm_walnut',post.name,'fixture')
 box(n+'_shade',(u+.86,y-.24,v),(.60,.32,.90),'ivory_enamel',n+'_arm','fixture',.09)
 box(n+'_lens',(u+.86,y-.42,v),(.48,.04,.74),'oatmeal_weave',n+'_shade','fixture',.01)
 LIGHTS.append((n,(u+.86,y-.47,v),power,.65,.85))

def books(n,u,v,length=5):
 b=box(n+'_back',(u,1.5,v),(.18,3,length),'warm_walnut',zone='collection')
 for h in [.20,.91,1.62,2.33,2.95]:
  shelf=box(n+'_shelf'+str(h),(u-.44,h,v),(1.0,.08,length),'warm_walnut',b.name,'collection')
  if h<2.9:
   # One detailed existing stock group anchors each shelf; fitted bound volumes fill the remaining bays economically.
   q=v-length/2+.45
   asset(n+'_books'+str(h)+'_catalogue','assets/library_contents/AST-LIB-006_upright_book_group.blend',u-.40,q,h+.04,yaw=SIDE*math.pi/2,sup=shelf.name)
   for j in range(1,int(length/.48)):
    q=min(v-length/2+.45+j*.48,v+length/2-.21)
    for k in range(2):
     ht=.32+.07*((j+k)%3);z=q+k*.13;name=n+'_volume'+str(h)+'_'+str(j)+'_'+str(k)
     pages=box(name+'_pages',(u-.43,h+.04+ht/2,z),(.36,ht,.11),'ivory_enamel',shelf.name,'collection',.009)
     box(name+'_spine',(u-.61,h+.04+(ht+.02)/2,z),(.045,ht+.02,.14),'teal_weave' if (j+k)%2 else 'clay_weave',shelf.name,'collection',.008)
 return b.name

def cupboard(n,u,v):
 b=box(n+'_body',(u,1.1,v),(1.20,2.2,4.0),'warm_walnut',zone='service')
 for q in [-1,1]:box(n+'_door'+str(q),(u-.62,1.20,v+q*.98),(.08,1.85,1.84),'ivory_enamel',b.name,'service')
 for q in [-1,1]:box(n+'_handle'+str(q),(u-.70,1.30,v+q*.35),(.09,.30,.09),'champagne_metal',n+'_door'+str(q),'service')
 sign(n,'CARE / STOCK',u-.67,v,2.02,n+'_door-1')

def shell():
 poly=CONFIG['footprint'];
 # Entry edge split around broad root connection hold. Other walls faceted to primary form.
 for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
  if abs(a[0]-.7)<.01 and abs(b[0]-.7)<.01:
   wall('entry_left',a,(.7,4),4.96);wall('entry_right',(.7,-4),b,4.96)
  else:wall('enclosure_'+str(i),a,b,5.05)
 # Deep open threshold: no invented working door; root supplies existing controller/receiving approach.
 for v in [-4,4]:box('portal_jamb'+str(v),(2.0,1.95,v),(3.1,3.9,.45),'warm_walnut',zone='arrival',bev=.09)
 box('portal_crown',(2,4.04,0),(3.1,.30,8.4),'warm_walnut','portal_jamb-4','arrival',.07)
 sign('arrival',CONFIG['title'].upper(),2,-4.20,1.75,'portal_jamb-4')
 cupboard('care',6,-24)
 # Side walls have a tactile dado and pronounced pilaster joints, rather than huge blank fields.
 for side in [-1,1]:
  for j,u in enumerate([12,20,28,36]):
   foot=box('pilaster_foot'+str(side)+'_'+str(j),(u,.16,side*29.8),(.85,.32,.55),'warm_stone')
   box('pilaster'+str(side)+'_'+str(j),(u,2.45,side*29.8),(.36,4.58,.36),'warm_walnut',foot.name)
   wall('dado'+str(side)+'_'+str(j),(u-3.7,side*30),(u+3.7,side*30),1.12,.30,'warm_walnut')
 for side in [-1,1]:
  # Benches support threshold returns in section; keep the 8m entrance open.
  seat('threshold_rest'+str(side),5,side*10,5,1,'oatmeal_weave')
  table('threshold_table'+str(side),7,side*10,.7)

 # Faceted rising ceiling: each wedge meets its perimeter wall; central crown remains below D13.
 for j,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
  centre=(21,5.25,0);pts=[xyz((a[0],4.92,a[1])),xyz((b[0],4.92,b[1])),xyz(centre)];vs=pts+[p+Vector((0,0,.18)) for p in pts];me=bpy.data.meshes.new('crown_wedge');me.from_pydata(vs,[],[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]);me.update();ob=bpy.data.objects.new('crown_wedge',me);bpy.context.collection.objects.link(ob);finish(ob,'crown_wedge'+str(j),'ivory_enamel','entry_left' if abs(a[0]-.7)<.01 and abs(b[0]-.7)<.01 else 'enclosure_'+str(j),'ceiling',.015)
 # Quiet ceiling fields share load-bearing side piers, never a claimed D13 slab.
 for q in [-1,1]:
  for i,u in enumerate([9,19,29,39]):fixture('edge_light'+str(q)+'_'+str(i),u,q*23,4.5,1300)


def horizon():
 # Fan ribs terminate at supported rear crown; the walking axis stays separate from seated ring.
 for j,v in enumerate([-24,-16,-8,0,8,16,24]):
  wall('fan_rear_pier'+str(j),(42.4,v-.25),(42.4,v+.25),5.1,.30,'warm_walnut')
  rod('fan_rib'+str(j),(7,4.60,v*.82),(42.4,4.95,v),.14,'warm_walnut','fan_rear_pier'+str(j))
 # Observation connection remains a substantial opaque receiving boundary, not sky graphics.
 box('exterior_connection_hold',(42.6,2.4,0),(.30,4.8,14),'teal_weave',zone='root_connection_hold',bev=.07)
 arcseat('seated_view_axis',32,0,6.0,-65,65)
 arcseat('conversation_arc',25,-14,4.3,40,220,'clay_weave')
 # Central viewing instrument: sculptural optical frame on an accessible fitted console.
 b=cyl('optical_plinth',(33,0,0),1.1,.30,'warm_stone');p=cyl('optical_column',(33,.30,0),.34,1.62,'champagne_metal',b.name)
 rod('optical_frame_support',(33,1.6,0),(33,1.9,1.0),.09,'champagne_metal',p.name)
 for i in range(16):
  a=math.tau*i/16;b0=math.tau*(i+1)/16
  rod('optical_ring'+str(i),(33,1.9+1.0*math.sin(a),1.0*math.cos(a)),(33,1.9+1.0*math.sin(b0),1.0*math.cos(b0)),.045,'champagne_metal','optical_frame_support' if i==0 else 'optical_ring'+str(i-1))
 rod('optical_tube',(32.5,1.70,0),(33.5,2.15,0),.12,'dark_rubber',p.name)
 for i,v in enumerate([-16,16]):
  seat('view_bench'+str(i),37,v,8,1,'oatmeal_weave');table('view_table'+str(i),39,v)
 for i,v in enumerate([-12,12]):
  asset('arrival_chair'+str(i),'assets/furniture/AST-FUR-002_day_reading_chair.blend',13,v)
  table('arrival_table'+str(i),15,v)
 fixture('focus_light',31,3,3.65,700)
 # Two inhabited, sheltered view-facing branches flank the walking axis.
 for side in [-1,1]:
  for j,u in enumerate([20,29,38]):
   seat('side_social'+str(side)+'_'+str(j),u,side*23,4.5,1,'teal_weave' if side>0 else 'clay_weave')
   table('side_social_table'+str(side)+'_'+str(j),u+2.5,side*23,.85)
  # Deep framed alcove closes the quiet wing at useful human scale.
  for q in [17,29]:wall('wing_return'+str(side)+'_'+str(q),(17,side*q),(24,side*q),3.20,.26,'warm_walnut')
  lid=prism('wing_leaf_lid'+str(side),[(17,side*17),(24,side*17),(25,side*23),(24,side*29),(17,side*29)],3.2,.18,'ivory_enamel','wing_return'+str(side)+'_17','sheltered_rest')
  box('wing_recordledge'+str(side),(22,1.0,side*28.6),(4,.14,.50),'warm_walnut','wing_return'+str(side)+'_29','sheltered_rest')
 # A fitted broad optical working edge increases the focal hierarchy without implying a mini-game.
 podium=prism('view_console_body',[(31,-4),(33,-4),(34,-2),(34,2),(33,4),(31,4)],0,.92,'warm_walnut',zone='observation')
 top=prism('view_console_top',[(30.9,-4.1),(33.1,-4.1),(34.1,-2),(34.1,2),(33.1,4.1),(30.9,4.1)],.92,.10,'warm_stone',podium.name,'observation')
 for j,v in enumerate([-2.5,2.5]):
  stem=cyl('optic_aux_stem'+str(j),(32,1.02,v),.14,.40,'champagne_metal',top.name)
  rod('optic_aux_tube'+str(j),(31.65,1.32,v),(32.45,1.55,v),.11,'dark_rubber',stem.name,'observation')



 # Optical frame seats on the final console; no hidden overlap with its surrounding bench.
 for ob in A:
  if '__optical_' in ob.name:ob.location.z+=1.02
  if ob.name.endswith('__optical_plinth'):ob['support']=top.name


def vesper():
 # Layered diagonal shelters create successive social rooms, with a continuous level loop.
 for i,(u,v,ln,h) in enumerate([(12,-12,14,2.6),(22,12,16,3.5),(32,-11,16,3.1)]):
  wall('shelter_'+str(i),(u,v-ln/2),(u+3,v+ln/2),h,.40,'warm_walnut',zone='sheltered_social')
  seat('booth'+str(i),u+2,v,ln-3,1,'clay_weave');
  for j,q in enumerate([v-4,v+4]):table('booth_table'+str(i)+'_'+str(j),u+4,q)
  fixture('booth_light'+str(i),u+1,v+ln/2-1,h+.20,850)
 # Evening gathering edge is a broad crescent, separated from a tactile drink-service counter.
 arcseat('evening_crescent',34,13,6.2,-80,100,'teal_weave')
 for j,ang in enumerate([-50,0,50]):
  a0=math.radians(ang);table('crescent_table'+str(j),34+4.6*math.cos(a0),13+4.6*math.sin(a0),.85)
 for j,(u,v) in enumerate([(16.5,-22),(20,-20)]):asset('refreshment_chair'+str(j),'assets/furniture/AST-FUR-002_day_reading_chair.blend',u,v)
 table('refreshment_social_table',18,-21,.85)
 box('opaque_view_hold',(42.6,2.35,5),(.30,4.7,18),'clay_weave',zone='root_connection_hold')
 b=prism('refreshment_body',[(6,-19),(9,-19),(12,-16),(12,-10),(9,-10),(6,-13)],0,1.02,'warm_walnut',zone='refreshment')
 t=prism('refreshment_top',[(5.9,-19.1),(9.1,-19.1),(12.1,-16.1),(12.1,-9.9),(8.9,-9.9),(5.9,-12.9)],1.02,.10,'warm_stone',b.name,'refreshment')
 for i in range(5):cyl('carafe'+str(i),(8,1.12,-17+i),.16,.42,'ivory_enamel',t.name,'refreshment')
 for i,u in enumerate([10,20,30,40]):
  wall('sail_support'+str(i),(u,-25.2),(u,-24.8),5.10,.32,'warm_walnut');rod('evening_sail'+str(i),(u,4.8,-25),(u+1.2,5.10,25),.18,'warm_walnut','sail_support'+str(i))


def celestial():
 # Intimate lobed salon: central interpretation sculpture surrounded by three distinct conversation bays.
 for i,(u,v,r,a,b) in enumerate([(29,0,4.2,-70,70),(23,-15,3.0,30,220),(23,15,3.0,140,330)]):
  arcseat('conversation_lobe'+str(i),u,v,r,a,b,['teal_weave','clay_weave','oatmeal_weave'][i]);table('lobe_table'+str(i),u,v)
  # Usable low tables follow each seating arc at a reachable front-edge distance.
  for j,ang in enumerate(([ -40,40 ] if i==0 else [90,170] if i==1 else [190,270])):
   a0=math.radians(ang);rr=2.6 if i==0 else 1.5;table('near_lobe_table'+str(i)+'_'+str(j),u+rr*math.cos(a0),v+rr*math.sin(a0),.75)
  # Knee-high plinth and floor-supported curved screen embrace each side bay.
  if i:
   wall('lobe_screen'+str(i),(u+4,v-5),(u+5,v+5),3.0,.30,'warm_walnut')
   fixture('lobe_lamp'+str(i),u+4,v+4,3.35,800)
 # Celestial interpretation is a tangible multi-plane armillary, no fictional map office or capacity.
 p=cyl('interpretation_base',(24,0,0),1.45,.40,'warm_stone');q=cyl('interpretation_stem',(24,.40,0),.28,.92,'champagne_metal',p.name)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.55,location=xyz((24,1.85,0)));finish(bpy.context.object,'interpretation_world','teal_weave',q.name,'interpretation',0)
 for j in range(3):
  rod('orbit_support'+str(j),(24,1.32,0),(25.1+j*.2,1.85,0),.06,'champagne_metal',q.name,zone='interpretation')
  for i in range(20):
   a=math.tau*i/20;b=math.tau*(i+1)/20;r=1.1+j*.2
   def pt(t):return (24+r*math.cos(t),1.85+r*math.sin(t)*math.sin(.5+j*.7),r*math.sin(t)*math.cos(.5+j*.7))
   rod('orbit_'+str(j)+'_'+str(i),pt(a),pt(b),.035,'champagne_metal','orbit_support'+str(j) if i==0 else 'orbit_'+str(j)+'_'+str(i-1),zone='interpretation')
 # Branching ceiling with low conversation edges and taller central crown, supported entirely at room floor.
 for j,v in enumerate([-20,-10,0,10,20]):
  wall('crown_pier'+str(j),(40,v-.20),(40,v+.20),5.05,.3,'warm_walnut')
  rod('crown_branch'+str(j),(18,4.2,v*.45),(40,4.90,v),.13,'warm_walnut','crown_pier'+str(j))
 fixture('interpretation_lamp',24,4,3.4,850)
 for i,v in enumerate([-9,9]):asset('entrance_chair'+str(i),'assets/furniture/AST-FUR-002_day_reading_chair.blend',10,v)


def gallery():
 # Three different exhibit groups along a branching loop with sightline pauses and service backs.
 for i,(u,v,w,h) in enumerate([(12,-13,12,3.0),(23,12,16,3.7),(34,-11,13,3.2)]):
  wall('exhibit_spine'+str(i),(u,v-w/2),(u,v+w/2),h,.40,'warm_walnut',zone='exhibition')
  for j in range(3):
   q=v-w/2+2+j*(w-4)/2;b=box('specimen_plinth'+str(i)+'_'+str(j),(u-2,.45,q),(1.65,.90,1.65),'warm_stone',zone='exhibition')
   if i==0:
    for k in range(3):
     bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.38+k*.08,location=xyz((u-2,.90+.35+k*.15,q)));o=bpy.context.object;o.scale=(1,.65,1.3);finish(o,'geological_'+str(j)+'_'+str(k),'clay_weave',b.name if k==0 else 'geological_'+str(j)+'_'+str(k-1),'exhibition',0)
   elif i==1:
    rod('branch_stem'+str(j),(u-2,.9,q),(u-2,2.5,q),.06,'champagne_metal',b.name,'exhibition')
    for k in [-1,1]:rod('branch_arm'+str(j)+'_'+str(k),(u-2,1.5,q),(u-2+k*.55,2.2,q),.045,'champagne_metal','branch_stem'+str(j),'exhibition')
    cyl('specimen_crown'+str(j),(u-2,2.3,q),.55,.18,'teal_weave','branch_stem'+str(j),'exhibition')
   else:
    for k in range(4):box('art_layer'+str(j)+'_'+str(k),(u-2,.98+k*.20,q),(1.2-k*.17,.20,.80),'ivory_enamel',b.name if k==0 else 'art_layer'+str(j)+'_'+str(k-1),'exhibition',.06)
   # Fitted plaque avoids floating billboard.
   box('label_'+str(i)+'_'+str(j),(u-2,.93,q-.62),(.95,.04,.30),'champagne_metal',b.name,'exhibition',.008)
  fixture('exhibit_lamp'+str(i),u-.5,v-w/2+1,3.6,1000)
 # Pause wall makes a framed relief rather than another plinth row.
 back=box('relief_back',(40,1.9,15),(.32,3.8,12),'teal_weave',zone='exhibition')
 for j in range(5):box('relief_stratum'+str(j),(39.72,1.0+j*.45,15),(.25,.20,10-j),'champagne_metal',back.name,'exhibition',.03)
 seat('pause_bench',32,20,8,1,'oatmeal_weave');seat('entry_pause',8,13,5,1,'clay_weave')
 for i,u in enumerate([12,23,34]):
  wall('blade_support'+str(i),(u,-25.2),(u,-24.8),4.8,.32,'warm_walnut');rod('exhibit_ceiling_blade'+str(i),(u,4.5,-25),(u,5.05,25),.15,'warm_walnut','blade_support'+str(i))


def reading():
 # Four individually formed pockets, linked by the quiet central route; varying privacy, scale and activity.
 # Crescent shared reading bay.
 arcseat('shared_crescent',30,-15,2.5,25,245,'oatmeal_weave');table('shared_reading_table',30,-15,1.35)
 wall('shared_quiet_back',(27,-22),(35,-22),2.4,.28,'warm_walnut',zone='sheltered_reading')
 wall('shared_quiet_wing',(35,-22),(37,-15),2.4,.28,'warm_walnut',zone='sheltered_reading')
 # Deep single study cell with bilateral timber returns and proper task shelf.
 for i,v in enumerate([9,18]):
  b=box('study_back'+str(i),(36,1.55,v),(.30,3.1,6.4),'warm_walnut',zone='sheltered_reading')
  for k in [-1,1]:wall('study_return'+str(i)+'_'+str(k),(28,v+k*3.2),(36,v+k*3.2),3.1,.28,'warm_walnut',zone='sheltered_reading')
  box('study_lid'+str(i),(32,3.16,v),(8.25,.22,6.7),'ivory_enamel',b.name,'sheltered_reading',.065)
  seat('study_bench'+str(i),34.8,v,4.8,-1,'teal_weave' if i==0 else 'clay_weave')
  table('study_table'+str(i),33.0,v,.9);fixture('study_light'+str(i),35,v+2.6,2.8,650)
 # Lower open family leaf with generous level access and adjacent bound collection.
 seat('family_leaf_back',15,-15,8,1,'clay_weave');seat('family_leaf_return',19,-19,3,1,'oatmeal_weave');table('family_leaf_table',17,-15,1.1);table('family_return_table',21,-19,.8)
 wall('family_leaf_screen',(13,-21),(22,-21),2.6,.35,'warm_walnut',zone='sheltered_reading')
 prism('family_sheltering_leaf',[(13,-21),(22,-21),(24,-12),(18,-10.5),(13,-12)],2.6,.18,'ivory_enamel','family_leaf_screen','sheltered_reading')
 fixture('family_leaf_light',14,-20,2.65,650)
 # Individual writing edge sheltered by stepped library spine; no extra elevated accessible levels invented.
 books('collection_a',40,-12,12);books('collection_b',22,21,10);books('quiet_route_collection',18,-6,8)
 box('writing_support',(15,.38,13),(1.2,.76,5),'warm_walnut',zone='writing')
 box('writing_top',(14.8,.80,13),(1.8,.12,5.3),'warm_stone','writing_support','writing')
 for j,v in enumerate([11.5,13,14.5]):asset('writing_chair'+str(j),'assets/furniture/AST-FUR-002_day_reading_chair.blend',13.2,v)
 box('writing_folio',(14.4,.89,13),(.50,.06,.65),'clay_weave','writing_top','writing',.008)
 wall('writing_screen',(17,9),(17,17),2.5,.30,'warm_walnut',zone='writing')
 fixture('writing_lamp',16.5,16,2.7,650)
 for j,u in enumerate([11,22,33]):
  wall('quiet_support'+str(j),(u,-24.2),(u,-23.8),4.9,.3,'warm_walnut');rod('quiet_ceiling_spine'+str(j),(u,4.70,-24),(u,4.9,24),.12,'warm_walnut','quiet_support'+str(j))


def native_export():
 bpy.context.view_layer.update()
 # All bitmap resources embedded in actual editable source.
 for im in bpy.data.images:
  if im.source=='FILE' and not im.packed_file:im.pack()
 bpy.context.scene['deterministic_source_sha256']=sha(__file__)
 bpy.ops.wm.save_as_mainfile(filepath=str(P/'source/section.blend'))
 # Export evaluated production copies into a clean scene: no inherited collection selection/visibility state.
 dg=bpy.context.evaluated_depsgraph_get();prepared=[]
 for i,o in enumerate(A):
  name=o.name;eo=o.evaluated_get(dg);me=bpy.data.meshes.new_from_object(eo,preserve_all_data_layers=True,depsgraph=dg);prepared.append((name,me,o.matrix_world.copy(),dict(o.items())))
 for i,o in enumerate(A):o.name='NATIVE_HOLD_'+str(i)
 ex=bpy.data.scenes.new('Production exchange only');bpy.context.window.scene=ex
 for name,me,matrix,extra in prepared:
  clone=bpy.data.objects.new(name,me);ex.collection.objects.link(clone);clone.matrix_world=matrix
  for k,v in extra.items():clone[k]=v
  if not me.uv_layers:uv(clone)
 bpy.ops.export_scene.gltf(filepath=str(P/'exports'/(KEY+'.glb')),export_format='GLB',use_selection=False,use_active_scene=True,export_yup=True,export_extras=True,export_apply=True,export_texcoords=True,export_materials='EXPORT')
 (P/'qa/fixtures.json').write_text(json.dumps(LIGHTS,indent=2))


def preview():
 # Reload actual exported GLB for all reviewed pixels; retain native independently.
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(P/'exports'/(KEY+'.glb')))
 # QA floor from the separate proposal; never saved/exported with section.
 poly=CONFIG['footprint'];me=bpy.data.meshes.new('QA_FLOOR');me.from_pydata([xyz((u,0,v)) for u,v in poly],[],[tuple(range(len(poly)))]);me.update();o=bpy.data.objects.new('QA_ONLY_FLOOR_PROPOSAL',me);bpy.context.collection.objects.link(o);o.data.materials.append(next(m for m in bpy.data.materials if 'warm_stone' in m.name));uv(o)
 for n,p,power,w,l in LIGHTS:
  da=bpy.data.lights.new(n,'AREA');da.energy=power;da.color=(1,.82,.60);da.shape='RECTANGLE';da.size=w;da.size_y=l;ob=bpy.data.objects.new(n,da);bpy.context.collection.objects.link(ob);ob.location=xyz(p)
 sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.render.resolution_x=1024;sc.render.resolution_y=576;sc.render.resolution_percentage=100
 sc.world=bpy.data.worlds.new('Dim QA neutral');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.20,.23,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.17;sc.view_settings.view_transform='AgX';sc.view_settings.exposure=.8
 camd=bpy.data.cameras.new('Eye165');cam=bpy.data.objects.new('Eye165',camd);bpy.context.collection.objects.link(cam);sc.camera=cam;camd.lens=18;camd.clip_start=.05;camd.clip_end=120
 rows=[]
 for n,p,t in CONFIG['views']:
  cam.location=xyz(p);cam.rotation_euler=(xyz(t)-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(P/'qa/views'/(n+'.png'));bpy.ops.render.render(write_still=True);rows.append({'name':n,'eye_world':world(p),'eye_above_proposed_floor':p[1],'target_world':world(t),'file':'qa/views/'+n+'.png','sha256':sha(sc.render.filepath)})
 (P/'qa/view_receipt.json').write_text(json.dumps({'deterministic_source_sha256':sha(__file__),'scope':'Actual exported GLB reimport; source preview floor and fixture preview illumination; no Godot/CRT acceptance','native_sha256':sha(P/'source/section.blend'),'glb_sha256':sha(P/'exports'/(KEY+'.glb')),'views':rows},indent=2))

if __name__=='__main__':
 bpy.ops.wm.read_factory_settings(use_empty=True);s=importlib.util.spec_from_file_location('materials',C/'standards/materials.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);M=m.materials();shell();globals()[CONFIG['kind']]();native_export();preview();print('SECTION_BUILD_COMPLETE',KEY,len(A))
