"""Batch B original fitted source proposals. Blender 4.3.2; metres.
Each rebuild is independent. Root owns structural adoption, floors, doors and runtime.
Run via heavy_job.py so all heavy work holds the shared Windows mutex.
"""
import bpy,math,json,sys,hashlib,random
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parent
USED_SOURCE=Path(__file__).read_bytes()
CONFIG=json.loads((BASE/'section_profiles.json').read_text())
section=sys.argv[sys.argv.index('--')+1];mode=sys.argv[sys.argv.index('--')+2];C=CONFIG[section];P=BASE/section
for n in ['source','exports','qa/views','docs']: (P/n).mkdir(parents=True,exist_ok=True)
M={};A=[];LIGHTS=[];POLY=[];COL=None
if not mode.startswith('render'):(P/'source/build_used.py').write_bytes(USED_SOURCE)
else:(P/'qa/render_used.py').write_bytes(USED_SOURCE)

def xyz(u,h,v):return (C['sign']*u,-v,h)
def uv(o):
 if o.type!='MESH':return
 o.data.update();layer=o.data.uv_layers.active or o.data.uv_layers.new(name='UV0')
 for f in o.data.polygons:
  drop=max(range(3),key=lambda i:abs(f.normal[i]));axes=[i for i in range(3) if i!=drop]
  for li in f.loop_indices:
   co=o.data.vertices[o.data.loops[li].vertex_index].co;layer.data[li].uv=(co[axes[0]]*.8,co[axes[1]]*.8)

def finish(o,n,mat,support='ROOT_FLOOR',role='fitted',bev=.025):
 o.name=n
 for c in list(o.users_collection):c.objects.unlink(o)
 COL.objects.link(o)
 if o.type=='MESH':
  if bev:
   bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Manufactured radius','BEVEL');mod.width=bev;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
  bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
  uv(o)
 o.data.materials.append(M[mat]);o['programme_key']=C['key'];o['support']=support;o['role']=role;A.append(o);return o

def box(n,u,h,v,w,ht,d,mat='wood',support='ROOT_FLOOR',role='fitted',bev=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(u,h,v));o=bpy.context.object;o.dimensions=(w,d,ht);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,mat,support,role,min(bev,min(w,ht,d)*.3))
def prism(n,poly,h,ht,mat,sup='ROOT_FLOOR',role='fitted',bev=.025):
 vs=[xyz(u,h,v) for u,v in poly]+[xyz(u,h+ht,v) for u,v in poly];count=len(poly);faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],faces);me.update();o=bpy.data.objects.new(n,me);COL.objects.link(o);return finish(o,n,mat,sup,role,bev)
def rod(n,a,b,r,mat='brass',sup='ROOT_FLOOR',role='support',vertices=12):
 pa=Vector(xyz(*a));pb=Vector(xyz(*b));delta=pb-pa;bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=delta.length,location=(pa+pb)/2);o=bpy.context.object;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,mat,sup,role,.007)
def disc(n,u,h,v,r,ht,mat,sup='ROOT_FLOOR',role='fitted'):
 return rod(n,(u,h,v),(u,h+ht,v),r,mat,sup,role,24)
def edge(n,a,b,h,ht,width,mat,sup='ROOT_FLOOR',role='enclosure'):
 du,dv=b[0]-a[0],b[1]-a[1];ln=math.hypot(du,dv);nu,nv=-dv/ln*width/2,du/ln*width/2
 return prism(n,[(a[0]+nu,a[1]+nv),(b[0]+nu,b[1]+nv),(b[0]-nu,b[1]-nv),(a[0]-nu,a[1]-nv)],h,ht,mat,sup,role)
def arc(n,u,v,r,a0,a1,h,ht,width,mat,sup='ROOT_FLOOR',role='fitted',steps=16):
 outer=[(u+(r+width/2)*math.cos(a0+(a1-a0)*i/steps),v+(r+width/2)*math.sin(a0+(a1-a0)*i/steps)) for i in range(steps+1)];inner=[(u+(r-width/2)*math.cos(a0+(a1-a0)*i/steps),v+(r-width/2)*math.sin(a0+(a1-a0)*i/steps)) for i in reversed(range(steps+1))];return prism(n,outer+inner,h,ht,mat,sup,role,.018)
def text(n,body,u,h,v,size=.18,sup='ROOT_FLOOR',face='entry'):
 cu=bpy.data.curves.new(n,'FONT');cu.body=body;cu.size=size;cu.align_x='CENTER';cu.extrude=.001;o=bpy.data.objects.new(n,cu);COL.objects.link(o);o.location=xyz(u,h,v);o.rotation_euler=(math.pi/2,0,-C['sign']*math.pi/2) if face=='entry' else (math.pi/2,0,0);o.data.materials.append(M['ivory']);o['support']=sup;o['role']='editable_sign';o['programme_key']=C['key'];A.append(o)
def lamp(n,u,v,h=3.2,sup='ROOT_FLOOR',cool=False):
 disc(n+'_foot',u,0,v,.22,.08,'brass');rod(n+'_stem',(u,.08,v),(u,h,v),.045,'brass',n+'_foot');disc(n+'_shade',u,h-.15,v,.33,.28,'cool' if cool else 'orange',n+'_stem');disc(n+'_lens',u,h-.18,v,.27,.04,'light',n+'_shade');LIGHTS.append(dict(name=n,pos=(u,h-.23,v),power=130 if cool else 180,color=(.72,.86,1) if cool else (1,.72,.40),size=1.0))
def ceiling_light(n,u,v,h,sup,power=350):
 rod(n+'_suspension',(u,h+.02,v),(u,C['ceiling']+.04,v),.04,'brass',sup);box(n+'_housing',u,h,v,1.7,.12,.85,'brass',n+'_suspension');box(n+'_lens',u,h-.075,v,1.55,.04,.7,'light',n+'_housing');LIGHTS.append(dict(name=n,pos=(u,h-.11,v),power=power,color=(1,.80,.58),size=2.5))
def counter(n,poly,mat='orange',top='stone',height=1.02):
 prism(n+'_base',poly,0,height-.1,mat,role='floor_contact');prism(n+'_top',poly,height-.1,.1,top,n+'_base',role='work_surface',bev=.045);return n+'_top'
def table(n,u,v,w=1.8,d=1.4,game=False):
 box(n+'_foot',u,.045,v,w*.58,.09,d*.65,'brass',role='floor_contact');box(n+'_stem',u,.42,v,.22,.68,.22,'brass',n+'_foot');box(n+'_top',u,.80,v,w,.12,d,'wood',n+'_stem','activity_surface',.055)
 if game:
  box(n+'_board',u,.876,v,w*.62,.035,d*.64,'teal',n+'_top','inert_tabletop_display',.015)
  for i in range(5):
   disc(n+'_piece'+str(i),u-.42+i*.21,.895,v-.18+(i%2)*.34,.065,.08,'ivory' if i%2 else 'orange',n+'_board','inert_tabletop_piece')
 return n+'_top'
def chair(n,u,v,angle=0):
 disc(n+'_foot',u,0,v,.35,.07,'brass',role='floor_contact');disc(n+'_stem',u,.07,v,.08,.33,'brass',n+'_foot');box(n+'_seat',u,.46,v,.78,.12,.78,'cloth',n+'_stem','supported_rest',.05)
 du,dv=math.cos(angle)*.33,math.sin(angle)*.33;back=box(n+'_back',u+du,.87,v+dv,.16,.79,.72,'cloth',n+'_seat','supported_rest',.05)
 if C['kind']=='games':back.rotation_euler[2]=-C['sign']*angle
def bench(n,u,v,length=3.8,back='north'):
 box(n+'_plinth',u,.19,v,length,.38,.92,'wood',role='floor_contact');box(n+'_cushion',u,.46,v,length-.12,.16,.88,'cloth',n+'_plinth','supported_rest',.065);box(n+'_back',u,.92,v+.41 if back=='north' else v-.41,length,1.00,.18,'cloth',n+'_plinth','supported_rest',.055)
def shelf(n,u,v,length=4.0,height=2.6,items='books',mat='wood',reverse=False):
 box(n+'_back',u+(-.5 if reverse else .5),height/2,v,.16,height,length,mat,role='floor_contact');box(n+'_plinth',u,.08,v,1.15,.16,length,mat,role='floor_contact')
 for j in range(4):
  h=.32+j*.64;box(n+'_shelf'+str(j),u,h,v,1.1,.08,length,mat,n+'_back','stock_surface')
  for i in range(int(length/.45)-1):
   vv=v-length/2+.4+i*.45;hh=.36 if items=='books' else .30
   if items=='bread':
    disc(n+'_tray'+str(j)+'_'+str(i),u,h+.04,vv,.20,.035,'brass',n+'_shelf'+str(j));box(n+'_loaf'+str(j)+'_'+str(i),u,h+.04+.035+hh/2,vv,.42,hh,.27,'oatmeal',n+'_tray'+str(j)+'_'+str(i),'display_bakery_food',.09)
   else:
    box(n+'_stock'+str(j)+'_'+str(i),u,h+.04+hh/2,vv,.50,hh,.22 if items=='books' else .36,['teal','orange','ivory'][i%3],n+'_shelf'+str(j),'book_stock' if items=='books' else 'parcel_stock',.015)
 for vv in [v-length/2+.06,v+length/2-.06]:box(n+'_end'+str(vv),u,height/2,vv,1.1,height,.12,mat,n+'_plinth')
def plant(n,u,v):
 disc(n+'_pot',u,0,v,.55,.65,'orange',role='floor_contact');rod(n+'_stem',(u,.65,v),(u,1.75,v),.065,'wood',n+'_pot')
 for i in range(6):
  a=i*math.tau/6;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.7,location=xyz(u+.32*math.cos(a),1.4+.20*(i%2),v+.32*math.sin(a)));o=bpy.context.object;o.scale=(.7,.5,1.0);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,n+'_leaf'+str(i),'green',n+'_stem','plant',0)
def catalogue(n,id,u,v,angle=0):
 cat=json.loads((BASE/'dependencies/catalogue_manifest.json').read_text());rec=next(a for a in cat['assets'] if a['catalogue_id']==id);path=BASE/'dependencies/catalogue'/rec['source'];loaded=[]
 with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.objects=[o for o in src.objects]
 objs=[o for o in dst.objects if o and o.type=='MESH']; pts=[o.matrix_world@Vector(c) for o in objs for c in o.bound_box];minz=min(p.z for p in pts);cx=(min(p.x for p in pts)+max(p.x for p in pts))/2;cy=(min(p.y for p in pts)+max(p.y for p in pts))/2
 for i,o in enumerate(objs):
  COL.objects.link(o);o.hide_viewport=False;o.hide_render=False;o.hide_select=False;o.hide_set(False);world=o.matrix_world.copy();o.parent=None;me=o.data.copy();o.data=me
  for vert in me.vertices:
   q=world@vert.co;xx=q.x-cx;yy=q.y-cy;uu=u+xx*math.cos(angle)-yy*math.sin(angle);vv=v-xx*math.sin(angle)-yy*math.cos(angle);vert.co=xyz(uu,q.z-minz,vv)
  o.matrix_world.identity();
  if world.to_3x3().determinant()*C['sign']<0:me.flip_normals()
  me.update();o.name=n+'_'+str(i);o['support']='ROOT_FLOOR' if min((o.matrix_world@Vector(c)).z for c in o.bound_box)<.02 else n+'_0';o['role']='catalogue_'+id;o['programme_key']=C['key'];uv(o);A.append(o)
 for im in bpy.data.images:
  if im.source=='FILE' and not im.packed_file:
   try:im.pack()
   except Exception:pass

def materials():
 specs={'wood':'warm_walnut','brass':'champagne_metal','cloth':'clay_weave','oatmeal':'oatmeal_weave','ivory':'ivory_enamel','rubber':'dark_rubber','stone':'warm_stone','teal':'teal_weave','cool':'staff_bluegrey_paint','zinc':'staff_zinc','white':'staff_white_paint','light':'staff_opal','orange':'ivory_enamel','green':'teal_weave'}
 for key,fn in specs.items():
  ma=bpy.data.materials.new('B_'+key);ma.use_nodes=True;bs=ma.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.78;bs.inputs['Metallic'].default_value=.45 if key in ['brass','zinc'] else 0;im=bpy.data.images.load(str(BASE/'dependencies/materials'/(fn+'.png')),check_existing=True);im.pack();tx=ma.node_tree.nodes.new('ShaderNodeTexImage');tx.image=im;tx.interpolation='Closest'
  if key in ['orange','green']:
   mix=ma.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.85,.24,.045,1) if key=='orange' else (.22,.55,.25,1);ma.node_tree.links.new(tx.outputs['Color'],mix.inputs[1]);ma.node_tree.links.new(mix.outputs['Color'],bs.inputs['Base Color'])
  else:ma.node_tree.links.new(tx.outputs['Color'],bs.inputs['Base Color'])
  if key=='light':bs.inputs['Emission Color'].default_value=(1,.7,.35,1);bs.inputs['Emission Strength'].default_value=2
  M[key]=ma


def fan_roof(poly,edgeh,peak,centre):
 for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
  coords=[(a[0],edgeh,a[1]),(b[0],edgeh,b[1]),(centre[0],peak,centre[1])];vs=[xyz(*q) for q in coords]+[xyz(q[0],q[1]+.20,q[2]) for q in coords]
  me=bpy.data.meshes.new('Folded_roof_'+str(i));me.from_pydata(vs,[],[(2,1,0),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]);me.update();o=bpy.data.objects.new('Folded_roof_'+str(i),me);COL.objects.link(o);finish(o,'Folded_roof_'+str(i),'ivory','Perimeter_'+str(min(i,len(poly)-2)),'folded_ceiling',0)
def fan_height(u,v):
 c=(26,34)
 for a,b in zip(POLY,POLY[1:]+POLY[:1]):
  den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
  if abs(den)<1e-8:continue
  wa=((b[1]-c[1])*(u-c[0])+(c[0]-b[0])*(v-c[1]))/den;wb=((c[1]-a[1])*(u-c[0])+(a[0]-c[0])*(v-c[1]))/den;wc=1-wa-wb
  if min(wa,wb,wc)>=-.0001:return 4.8+(C['ceiling']-4.8)*wc
 return C['ceiling']
def clip_u(poly,limit,left):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[0]<=limit if left else a[0]>=limit;ib=b[0]<=limit if left else b[0]>=limit
  if ia:out.append(a)
  if ia!=ib:
   t=(limit-a[0])/(b[0]-a[0]);out.append((limit,a[1]+t*(b[1]-a[1])))
 return out


def architecture():
 global POLY
 kind=C['kind']
 if kind=='archive':POLY=[(0,31.6),(6,31.6),(6,10),(13,5),(39,5),(43,10),(43,58),(38,63),(13,63),(6,58),(6,36.4),(0,36.4)]
 elif kind=='inspection':POLY=[(0,31.6),(6,31.6),(6,24),(12,20),(12,7),(40,7),(43,12),(43,56),(40,61),(12,61),(12,48),(6,44),(6,36.4),(0,36.4)]
 else:POLY=[(0,31.6),(6,31.6),(6,12),(12,8),(40,8),(43,12),(43,56),(38,61),(12,61),(6,56),(6,36.4),(0,36.4)]
 for i,(a,b) in enumerate(zip(POLY,POLY[1:]+POLY[:1])):
  if a[0]==b[0]==0:continue
  edge('Enclosure_'+str(i),a,b,0,4.35,.20,'cool',role='floor_contact')
 # A shallow solid folded lid carried by actual walls, with a raised longitudinal work spine.
 fan_roof(POLY,4.35,5.15,(26,34))
 for vv in [31.2,36.8]:box('Portal_cheek'+str(vv),4,1.45,vv,4,2.9,.25,'cool',role='floor_contact')
 box('Portal_head',4,2.98,34,4,.16,5.9,'cool','Portal_cheek31.2')
 box('Identity_panel',5.9,2.0,31.2,.15,.45,2.7,'white','Portal_cheek31.2');text('Identity',C['name'].upper(),5.80,2.0,31.2,.11,'Identity_panel')
 for j,(u,v) in enumerate([(16,15),(34,15),(16,51),(34,51),(26,34)]):ceiling_light('Work_light'+str(j),u,v,4.1,'Folded_roof_2',800)
 (P/'docs/floor_proposal.json').write_text(json.dumps({'status':'Root receiving proposal only; absent from native/export','programme_key':C['key'],'local_xz':[[C['sign']*u,v]for u,v in POLY],'translation_xyz':[C['sign']*C['x'],C['floor'],C['z']],'entry_proposal_xyz':[C['sign']*C['x'],C['floor'],C['z']+34],'clear_width_m':3.6,'clear_height_m':2.65,'portal_keep_clear_world_xz':[[C['sign']*C['x']-2,C['z']+32],[C['sign']*C['x']+2,C['z']+32],[C['sign']*C['x']+2,C['z']+36],[C['sign']*C['x']-2,C['z']+36]],'holds':'Root slab support, connections, shared portals, installed collision/navigation and operation'},indent=2))

def cabinet(n,u,v,w=1.8,d=1.2,h=2.6):
 box(n+'_body',u,h/2,v,w,h,d,'cool',role='floor_contact');box(n+'_front',u-w/2-.02,h/2,v,.06,h-.16,d-.12,'white',n+'_body');box(n+'_grip',u-w/2-.08,h*.55,v,.06,.34,.07,'zinc',n+'_front')

def worktop(n,u,v,w,d,h=.92):
 return counter(n,[(u-w/2,v-d/2),(u+w/2,v-d/2),(u+w/2,v+d/2),(u-w/2,v+d/2)],'cool','zinc',h)

def archive():
 # Four archive streets terminate on a central consultation court, leaving a separate service aisle.
 for j,u in enumerate([20,33]):
  for i,v in enumerate([14,23,46,55]):
   for k in range(3):cabinet('Archive_bank_'+str(j)+'_'+str(i)+'_'+str(k),u,v-2.8+k*2.8,1.5,2.5,2.7)
 counter('Consultation_core',[(14,31),(24,31),(27,34),(24,37),(14,37)],'cool','zinc',.92)
 for i,u in enumerate([17,21]):box('Archive_document'+str(i),u,.965,34,1.3,.09,1.8,'ivory','Consultation_core_top','inert_document_case')
 worktop('Intake_sorting',38,34,3,8)
 for v in [31,37]:box('Transfer_case'+str(v),38,1.17,v,1.8,.50,1.1,'white','Intake_sorting_top')
 for i,v in enumerate([17,52]):bench('Staff_consultation'+str(i),11,v,4);table('Consultation_table'+str(i),11,v-1.7,2.5,1.1)
 catalogue('Care_cabinet','AST-STF-007',38,58)
 for v in [12,25,44,57]:box('Archive_aisle_end'+str(v),27,1.55,v,.25,3.1,.4,'zinc',role='floor_contact');rod('Archive_aisle_header'+str(v),(20,3.05,v),(34,3.05,v),.08,'zinc','Archive_aisle_end'+str(v))

def inspection():
 # Long inspection lane remains floor-free and unoccupied; fitted inspection edges remain on both sides.
 for j,v in enumerate([17,31,47]):
  for u in [18,35]:
   worktop('Inspection_station'+str(j)+'_'+str(u),u,v,2.5,5)
   box('Inspection_console'+str(j)+'_'+str(u),u,1.17,v,1.7,.50,.8,'white','Inspection_station'+str(j)+'_'+str(u)+'_top')
  for u in [20,33]:box('Inspection_frame'+str(j)+'_'+str(u),u,1.65,v,.30,3.3,.30,'zinc',role='floor_contact')
  edge('Inspection_gantry'+str(j),(20,v),(33,v),3.2,.20,.35,'cool','Inspection_frame'+str(j)+'_20')
 for v in [15,54]:cabinet('Inspection_stow'+str(v),40,v,2,4,2.7)
 catalogue('Care_cabinet','AST-STF-007',39,58)
 worktop('Intake_desk',11,28,3,3);bench('Inspection_wait',9,42,4)

def workshop():
 # A broad cruciform work aisle separates fabrication, repair and clean bench pockets.
 for j,(u,v) in enumerate([(17,18),(34,18),(17,50),(34,50)]):
  worktop('Repair_bench'+str(j),u,v,5,5)
  for k in range(3):box('Tool_case'+str(j)+'_'+str(k),u-1.5+k*1.5,1.08,v,.9,.32,1.1,'white','Repair_bench'+str(j)+'_top')
  cabinet('Workshop_stock'+str(j),u,v+5,2,4,2.6)
 worktop('Shared_assembly',26,34,6,8)
 for v in [11,57]:box('Workshop_rackpost'+str(v),41,1.7,v,.5,3.4,.5,'zinc',role='floor_contact');rod('Workshop_angled_service'+str(v),(41,3.3,v),(15,4.0,v+2),.10,'zinc','Workshop_rackpost'+str(v))
 catalogue('Care_cabinet','AST-STF-007',39,55)

VIEWS={
 'archive':[('arrival',(2,34),(23,34)),('consultation',(11,34),(23,34)),('collection',(15,18),(22,23)),('service',(32,34),(39,34)),('care',(35,61),(38,58))],
 'inspection':[('arrival',(2,34),(25,34)),('inspection',(25,26),(25,47)),('station',(29,31),(35,31)),('intake',(7,29),(12,28)),('care',(34,58),(39,58))],
 'workshop':[('arrival',(2,34),(26,34)),('assembly',(20,34),(27,34)),('repair',(11,18),(17,18)),('storage',(30,24),(34,23)),('care',(33,55),(39,55))]}
def bbox(o):
 pts=[o.matrix_world@Vector(c) for c in o.bound_box];return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def export():
 bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');temp=[]
 for o in A:
  if o.type=='FONT':
   copy=o.copy();copy.data=o.data.copy();COL.objects.link(copy);copy.name=o.name+'_export';bpy.context.view_layer.objects.active=copy;copy.select_set(True);bpy.ops.object.convert(target='MESH');temp.append(bpy.context.object);o.select_set(False)
  else:o.select_set(True)
 (P/'qa/export_selection.json').write_text(json.dumps([{'name':o.name,'selected':o.select_get(),'hide':o.hide_get(),'hide_viewport':o.hide_viewport,'hide_render':o.hide_render,'visible':o.visible_get()} for o in A],indent=2))
 bpy.ops.export_scene.gltf(filepath=str(P/'exports'/('section.glb')),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
 for o in temp:bpy.data.objects.remove(o,do_unlink=True)

def validation():
 errors=[];rows=[]
 for o in A:
  bb=bbox(o);ok=bb[0][0]>=(-46 if C['sign']==-1 else 0)-.002 and bb[0][1]<=(0 if C['sign']==-1 else 46)+.002 and bb[1][0]>=-68-.002 and bb[1][1]<=.002 and bb[2][0]>=-.002 and bb[2][1]<=C['roof']-C['floor']+.002
  if not ok:errors.append({'name':o.name,'containment':bb})
  if o.type=='MESH':
   if not o.data.uv_layers:errors.append({'name':o.name,'error':'UV missing'})
   if any(not math.isfinite(float(x)) for v in o.data.vertices for x in v.co):errors.append({'name':o.name,'error':'nonfinite'})
   if any(p.normal.length<.9 for p in o.data.polygons):errors.append({'name':o.name,'error':'degenerate normal'})
  rows.append({'name':o.name,'type':o.type,'bounds_blender':bb,'support':o.get('support'),'role':o.get('role')})
 imgs=[{'name':im.name,'packed':bool(im.packed_file)} for im in bpy.data.images if im.source=='FILE'];
 if any(not i['packed'] for i in imgs):errors.append({'error':'unpacked image'})
 report={'scope':'source containment/UV/normal/resource screen; not installed Godot acceptance','programme_key':C['key'],'errors':errors,'objects':len(A),'images':imgs,'source_sha256':digest(P/'source/native.blend'),'export_sha256':digest(P/'exports/section.glb'),'no_preview_floor_in_saved_native':not any(o.name.startswith('QA_') for o in bpy.context.scene.objects)}
 (P/'qa/validation.json').write_text(json.dumps(report,indent=2));(P/'qa/objects.json').write_text(json.dumps(rows,indent=2));print('SOURCE VALIDATION',len(errors),'errors',flush=True)
 if errors:raise RuntimeError('Source checks failed; evidence retained')

def render():
 sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.render.resolution_x=960;sc.render.resolution_y=540;sc.render.resolution_percentage=100;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.render.image_settings.file_format='PNG';sc.world=sc.world or bpy.data.worlds.new('QA low ambient');sc.world.color=(.075,.075,.075);sc.view_settings.view_transform='AgX';sc.render.film_transparent=False
 # Preview slab is made after final native/export and is never saved into final source.
 preview=prism('QA_RECEIVING_SLAB',POLY,-.1,.1,'stone',role='qa_only_preview_floor',bev=0);A.remove(preview)
 for l in LIGHTS:
  ld=bpy.data.lights.new('QA_'+l['name'],'AREA');ld.energy=l['power'];ld.color=l['color'];ld.shape='DISK';ld.size=l['size'];o=bpy.data.objects.new('QA_'+l['name'],ld);sc.collection.objects.link(o);o.location=xyz(*l['pos'])
 camd=bpy.data.cameras.new('QA_Eye');cam=bpy.data.objects.new('QA_Eye',camd);sc.collection.objects.link(cam);sc.camera=cam;camd.lens=21;camd.clip_end=180
 views=[]
 for n,(u,v),(tu,tv) in VIEWS[C['kind']]:
  if '_' in mode and mode.startswith('render') and n!=mode.split('_',1)[1]:continue
  cam.location=xyz(u,1.65,v);target=Vector(xyz(tu,1.65,tv));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(P/'qa/views'/(n+'.png'));bpy.ops.render.render(write_still=True);views.append({'name':n,'eye_local_xyz':[C['sign']*u,1.65,v],'target_local_xyz':[C['sign']*tu,1.65,tv],'image_sha256':digest(sc.render.filepath)})
 if mode.startswith('render') and '_' in mode:
  old=json.loads((P/'qa/view_receipt.json').read_text());merged={x['name']:x for x in old['views']};merged.update({x['name']:x for x in views});views=list(merged.values())
 (P/'qa/view_receipt.json').write_text(json.dumps({'source_sha256':digest(P/'source/native.blend'),'export_sha256':digest(P/'exports/section.glb'),'views':views,'render_scope':'source preview with proposed receiving slab; not installed Godot acceptance'},indent=2))

def run():
 global COL
 if mode.startswith('render'):
  bpy.ops.wm.open_mainfile(filepath=str(P/'source/native.blend'));COL=bpy.data.collections.get('Batch B '+C['name']);A.extend(o for o in COL.objects);materials() # materials reused for QA slab only
  meta=json.loads((P/'source/build_metadata.json').read_text());POLY.extend(meta['polygon']);LIGHTS.extend(meta['lights']);render();return
 bpy.ops.wm.read_factory_settings(use_empty=True);COL=bpy.data.collections.new('Batch B '+C['name']);bpy.context.scene.collection.children.link(COL);bpy.context.scene.unit_settings.system='METRIC';materials();architecture();globals()[C['kind']]()
 bpy.context.scene['programme_key']=C['key'];bpy.context.scene['placement_xyz']=[C['sign']*C['x'],C['floor'],C['z']];bpy.context.scene['status']='Independent fitted source proposal; root adoption and Godot acceptance pending'
 meta={'section':C,'polygon':POLY,'lights':LIGHTS,'builder_sha256':hashlib.sha256(USED_SOURCE).hexdigest(),'profiles_sha256':digest(BASE/'section_profiles.json'),'rebuild':'Python deterministic geometry; Catalogue native appends pinned in dependencies'};(P/'source/build_metadata.json').write_text(json.dumps(meta,indent=2))
 bpy.ops.wm.save_as_mainfile(filepath=str(P/'source/native.blend'));export();validation();render()
run()
