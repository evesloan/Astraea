#!/usr/bin/env python3
"""Original editable aquatic rest-cradle. Blender 4.3+, no downloads or dependencies.
Run blender -b --python build_aquatic_cradle.py -- [--no-render].
Design coordinates are Godot/glTF metres, right +X, up +Y, front -Z.
Only this new asset family is written. No catalogue registration or Game changes.
"""
import bpy,bmesh,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
FAMILY='aquatic_rest_cradle_20261009';ID='AST-RST-AQ-001'
assert OUT.name==FAMILY
CAT=OUT.parents[1]/'catalogue_manifest.json'
manifest=json.loads(CAT.read_text())
def exact_ids(v):
 if isinstance(v,dict):
  for k,x in v.items():
   if isinstance(x,str) and x==ID:yield k
   yield from exact_ids(x)
 elif isinstance(v,list):
  for x in v:yield from exact_ids(x)
existing_id_occurrences=list(exact_ids(manifest))
if existing_id_occurrences:
 own=[a for a in manifest.get('assets',[]) if a.get('catalogue_id',a.get('id'))==ID]
 assert len(own)==1 and own[0].get('family')==FAMILY, 'Exact catalogue ID belongs to another/unknown family; review before regenerating'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials):bpy.data.materials.remove(m)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
bpy.context.preferences.filepaths.save_version=0
col=bpy.data.collections.new(ID+' | editable fixture');scene.collection.children.link(col)
root=bpy.data.objects.new(ID,None);col.objects.link(root)
for k,v in {'asset_id':ID,'front_gltf':'negative Z','source_front':'positive Y','species_assignment':'unassigned','component_status':'proposed construction component','water_function':'visual surface only; no physics','biological_fit':'NOT_VERIFIED'}.items():root[k]=v
parts=[]
def B(p):return (p[0],-p[2],p[1])
def G(p):return (p[0],p[2],-p[1])
def mat(name,c,rough=.6,metal=0,alpha=1):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,alpha);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,alpha);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;p.inputs['Alpha'].default_value=alpha
 if alpha<1:m.surface_render_method='DITHERED';m.use_transparency_overlap=False
 return m
ivory=mat('01 | warm ivory vitreous shell',(.79,.73,.61),.28)
lagoon=mat('02 | deep lagoon shell base',(.025,.19,.18),.46)
seafoam=mat('03 | seafoam basin interior',(.30,.59,.52),.3)
foam=mat('04 | pale aqua immersed rest liner',(.54,.74,.65),.5)
foam2=mat('05 | rest liner quiet alternating panels',(.40,.65,.56),.52)
wood=mat('06 | warm honey ash trim',(.39,.20,.08),.53)
endwood=mat('07 | amber nonslip transfer slats',(.60,.35,.16),.64)
dark=mat('08 | charcoal resilient base and seams',(.026,.069,.068),.82)
bronze=mat('09 | satin bronze service fittings',(.49,.29,.10),.4,.52)
watermat=mat('10 | lagoon water visual alpha',(.08,.52,.60),.13,.13,.34)
# No refractive/export extension dependency. Transparent shaded water is an authored placeholder.
ripplemat=mat('11 | original pale water ripple highlights',(.60,.86,.82),.3,0,.70)
coral=mat('12 | terracotta service indicator',(.57,.18,.09),.58)
def mesh(name,verts,faces,material,role,closed=True,policy='static_concave_candidate'):
 me=bpy.data.meshes.new(name+' geometry');me.from_pydata([B(p) for p in verts],[],faces);me.materials.append(material);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if not closed:
  for f in bm.faces:
   if f.normal.z<0:f.normal_flip()
 bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);col.objects.link(ob);ob.parent=root
 for k,v in {'asset_id':ID,'component_role':role,'collision_policy':policy,'closed_solid_expected':closed}.items():ob[k]=v
 parts.append(ob);return ob

def box(name,c,s,m,role,policy='simplified_box_candidate'):
 x,y,z=c;a,b,d=[v/2 for v in s]
 vs=[(x+sx*a,y+sy*b,z+sz*d) for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 return mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m,role,policy=policy)
def tube(name,points,r,m,role,sides=8,loop=False,policy='no_collision_detail'):
 ps=[Vector(p) for p in points];vs=[];fs=[]
 for i,p in enumerate(ps):
  t=(ps[(i+1)%len(ps)]-ps[(i-1)%len(ps)]).normalized() if loop else (ps[min(i+1,len(ps)-1)]-ps[max(i-1,0)]).normalized()
  guide=Vector((0,1,0)) if abs(t.y)<.94 else Vector((0,0,1));u=t.cross(guide).normalized();v=t.cross(u).normalized()
  for j in range(sides):a=2*math.pi*j/sides;vs.append(tuple(p+r*(math.cos(a)*u+math.sin(a)*v)))
 for i in range(len(ps) if loop else len(ps)-1):
  j=(i+1)%len(ps)
  for k in range(sides):fs.append((i*sides+k,i*sides+(k+1)%sides,j*sides+(k+1)%sides,j*sides+k))
 if not loop:fs += [tuple(reversed(range(sides))),tuple((len(ps)-1)*sides+j for j in range(sides))]
 return mesh(name,vs,fs,m,role,policy=policy)
def mark(name,p,role):
 ob=bpy.data.objects.new(name,None);col.objects.link(ob);ob.parent=root;ob.location=B(p);ob.empty_display_type='PLAIN_AXES';ob.empty_display_size=.08;ob['datum_kind']=role;return ob
# Pinched rear and broad front shoulders make a distinct generous aquatic rest basin.
def spow(v,p):return math.copysign(abs(v)**p,v)
def ring(a,b,y,n=64):
 vs=[]
 for i in range(n):
  t=2*math.pi*i/n;s=spow(math.sin(t),.78);x=a*spow(math.cos(t),.72)*(1-.08*(s+1)/2);z=b*s
  h=y(s,t) if callable(y) else y;vs.append((x,h,z))
 return vs
def rim_y(s,t):return .635+.48*((s+1)/2)**2+.04*math.cos(t)**2
N=64
rings=[ring(1.27,1.68,.025),ring(1.38,1.77,.24),ring(1.47,1.88,lambda s,t:rim_y(s,t)-.045),ring(1.46,1.87,rim_y),ring(1.23,1.63,lambda s,t:rim_y(s,t)-.012),ring(1.08,1.45,.16)]
vs=sum(rings,[]);fs=[]
for r in range(len(rings)-1):
 for i in range(N):j=(i+1)%N;fs.append((r*N+i,r*N+j,(r+1)*N+j,(r+1)*N+i))
# Interior floor and underside are real capped geometry: open water cavity, closed material shell.
vs += [(0,.16,0),(0,.025,0)];flooridx=len(vs)-2;underidx=len(vs)-1
for i in range(N):j=(i+1)%N;fs.append((5*N+i,5*N+j,flooridx));fs.append((j,i,underidx))
basin=mesh('Hollow continuous basin shell with interior floor',vs,fs,ivory,'watertight-looking material shell with open cavity')
basin.data.materials.append(lagoon);basin.data.materials.append(seafoam)
for p in basin.data.polygons:
 if p.index<N:p.material_index=1
 elif p.index>=4*N:p.material_index=2
# Readable thick rim and slim warm wrap. No single closed top lid.
tube('Continuous ash rim outer reveal',ring(1.476,1.886,lambda s,t:rim_y(s,t)-.072),.021,wood,'rim detailing',sides=6,loop=True)
tube('Inner pale rim bead',ring(1.229,1.63,lambda s,t:rim_y(s,t)-.004),.014,ivory,'rim detailing',sides=6,loop=True)
# Ground contact: broad crescent feet and base strap; no shell hovering above the floor.
for sign,tag in [(-1,'L'),(1,'R')]:
 for z in [-1.05,.95]:box(tag+f' resilient floor foot {z:+.2f}',(sign*.81,.025,z),(.40,.05,.52),dark,'floor contact')
# Longitudinal coved support with flared shoulders, a deep middle and elevated rear.
ZMIN=-1.37;ZMAX=1.35
zs=[ZMIN+(ZMAX-ZMIN)*j/28 for j in range(29)];us=[-1+2*i/20 for i in range(21)]
def sw(z):
 t=(z-ZMIN)/(ZMAX-ZMIN)
 return .76+.25*math.sin(math.pi*t)-.12*t*t

def sh(u,z):
 t=(z-ZMIN)/(ZMAX-ZMIN)
 return .22+.135*u*u+.05*(1-t)**3+.48*t**5
sv=[]
for off in [0,-.065]:
 for z in zs:
  for u in us:sv.append((u*sw(z),sh(u,z)+off,z))
V=len(zs)*len(us);sf=[]
for j in range(len(zs)-1):
 for i in range(len(us)-1):
  a=j*len(us)+i;b=a+1;c=b+len(us);d=a+len(us);sf += [(a,d,c,b),(V+a,V+b,V+c,V+d)]
for j in [0,len(zs)-1]:
 for i in range(len(us)-1):
  a=j*len(us)+i;b=a+1;sf.append((a,b,V+b,V+a))
for i in [0,len(us)-1]:
 for j in range(len(zs)-1):
  a=j*len(us)+i;b=a+len(us);sf.append((a,b,V+b,V+a))
support=mesh('Contoured broad immersed rest support',sv,sf,foam,'actual contoured rest contact surface')
support.data.materials.append(foam2)
for p in support.data.polygons:
 if p.index<28*20*2 and (p.index//40)%5==0:p.material_index=1
# Small continuous ribs attach support to the floor; rear wedge makes supported slope legible.
for z in [-1.05,-.5,.10,.70,1.23]:
 h=sh(0,z)-.065;box(f'Underliner pedestal {z:+.2f}',(0,(h+.155)/2,z),(sw(z)*1.50,max(.018,h-.155),.12),seafoam,'support bearing',policy='no_collision_detail')
# Removable pad seams describe broad concavity under water; surface-contact ribs are deliberately subtle.
for j in [4,9,14,19,24,27]:
 z=zs[j];tube(f'Liner seam {j:02}',[(u*sw(z),sh(u,z)+.004,z) for u in us],.006,foam2,'liner seam',sides=6)
# Side rest rails follow the surface. Their volume remains on the support perimeter, not across approach.
for sign,tag in [(-1,'L'),(1,'R')]:
 tube(tag+' waterborne lateral cradle bolster',[(sign*.95*sw(z),sh(.95,z)+.025,z) for z in zs[2:-1]],.045,foam2,'raised lateral rest contour',sides=10,policy='static_concave_candidate')
# Water plane with an actual clipped rear hole where the support rises through the design waterline.
WATER=.57
# Inner-wall cavity radius interpolated at water elevation along the sloped inner shell.
def cavity_boundary(theta):
 s=spow(math.sin(theta),.78);outerh=rim_y(s,theta)-.012
 q=(WATER-.16)/(outerh-.16)
 a=1.08+(1.23-1.08)*q;b=1.45+(1.63-1.45)*q
 return (a*spow(math.cos(theta),.72)*(1-.08*(s+1)/2),b*s)
waterverts=[];waterfaces=[]
# 64 rays x 14 rings tessellation. Clip each triangle to the submerged side of support contour.
water_boundary=[cavity_boundary(2*math.pi*i/64) for i in range(64)]
radial=[(0,WATER,0)]
for j in range(1,15):
 for x,z in water_boundary:radial.append((x*j/14,WATER,z*j/14))
tri=[]
for i in range(64):tri.append((0,1+i,1+(i+1)%64))
for j in range(1,14):
 a0=1+(j-1)*64;b0=1+j*64
 for i in range(64):k=(i+1)%64;tri.extend([(a0+i,b0+i,b0+k),(a0+i,b0+k,a0+k)])
# Subtract the projected raised contact triangles, rather than clipping a discontinuous
# analytic mask. Every remaining patch is convex and exactly tessellated.
dry=[]
def area(poly):return sum(a[0]*b[2]-b[0]*a[2] for a,b in zip(poly,poly[1:]+poly[:1]))/2
for contact_object in [support]+[o for o in parts if 'lateral cradle bolster' in o.name]:
 contact_object.data.calc_loop_triangles()
 for tr in contact_object.data.loop_triangles:
  if contact_object==support and (tr.polygon_index>=28*20*2 or tr.polygon_index%2):continue
  pp=[G(contact_object.data.vertices[i].co) for i in tr.vertices];cut=[]
  for a,b in zip(pp,pp[1:]+pp[:1]):
   fa=a[1]-(WATER-.003);fb=b[1]-(WATER-.003)
   if fa>=0:cut.append((a[0],WATER,a[2]))
   if (fa>=0)!=(fb>=0):
    t=fa/(fa-fb);cut.append((a[0]+t*(b[0]-a[0]),WATER,a[2]+t*(b[2]-a[2])))
  if len(cut)>=3 and abs(area(cut))>1e-10:
   if area(cut)<0:cut.reverse()
   dry.append(cut)
def cross(a,b,p):return (b[0]-a[0])*(p[2]-a[2])-(b[2]-a[2])*(p[0]-a[0])
def split(poly,a,b):
 inside=[];outside=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  fp=cross(a,b,p);fq=cross(a,b,q)
  (inside if fp>=0 else outside).append(p)
  if (fp>=0)!=(fq>=0):
   t=fp/(fp-fq);k=tuple(p[i]+t*(q[i]-p[i]) for i in range(3));inside.append(k);outside.append(k)
 return inside,outside
def bbox(poly):return [min(p[0] for p in poly),max(p[0] for p in poly),min(p[2] for p in poly),max(p[2] for p in poly)]
def overlap(a,b):return not(a[1]<b[0]-1e-9 or a[0]>b[1]+1e-9 or a[3]<b[2]-1e-9 or a[2]>b[3]+1e-9)
dry=[(p,bbox(p)) for p in dry]
lookup={}
def wi(p):
 k=tuple(round(v,8) for v in p)
 if k not in lookup:lookup[k]=len(waterverts);waterverts.append(k)
 return lookup[k]
for inds in tri:
 patches=[[radial[i] for i in inds]]
 for poly,db in dry:
  new=[]
  for patch in patches:
   if not overlap(bbox(patch),db):new.append(patch);continue
   inner=patch
   for a,b in zip(poly,poly[1:]+poly[:1]):
    if len(inner)<3:break
    inner,outer=split(inner,a,b)
    if len(outer)>=3 and abs(area(outer))>1e-10:new.append(outer)
  patches=new
  if not patches:break
 for pp in patches:
  ids=[wi(p) for p in pp]
  for j in range(1,len(ids)-1):
   if len({ids[0],ids[j],ids[j+1]})==3 and abs(area([waterverts[ids[0]],waterverts[ids[j]],waterverts[ids[j+1]]]))>1e-8:waterfaces.append((ids[0],ids[j+1],ids[j]))
used=sorted({i for f in waterfaces for i in f});remap={old:new for new,old in enumerate(used)}
waterverts=[waterverts[i] for i in used];waterfaces=[tuple(remap[i] for i in f) for f in waterfaces]
water=mesh('WaterSurface_VisualOnly',waterverts,waterfaces,watermat,'original flat clipped water visual',False,'NO_SOLID_COLLISION')
water['surface_level_gltf_y_m']=WATER;water['physics_state']='not implemented';water['optional_future_sensor']='separate non-solid volume, not supplied'
# Authored thin ribbons, not stock texture. Never become collision surfaces.
for k,(cx,cz,rx,rz,start,span) in enumerate([(-.69,-.84,.28,.09,.10,2.5),(.59,-1.1,.32,.11,2.8,2.3),(-.67,.18,.31,.11,.3,2.2),(.70,.57,.28,.075,2.5,2.4),(.07,-.42,.25,.10,.2,2.0),(-.03,-1.25,.23,.09,3.2,2.2)]):
 pts=[(cx+rx*math.cos(start+span*j/16),WATER+.0028,cz+rz*math.sin(start+span*j/16)) for j in range(17)]
 rv=[]
 for x,y,z in pts:rv.extend([(x,y,z-.005),(x,y,z+.005)])
 rf=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(16)]
 mesh(f'Water ripple ribbon {k+1:02}',rv,rf,ripplemat,'nonphysical original water highlight',False,'NO_SOLID_COLLISION')
# Front transfer nose: thick warm flat surface blends into low continuous water-retaining rim.
box('Low front transfer nose',(0,.615,-1.852),(1.24,.075,.285),wood,'low transfer edge')
for i in range(8):box(f'Transfer nonslip slat {i+1:02}',(-.535+i*.153,.661,-1.868),(.136,.022,.265),endwood,'transfer surface',policy='simplified_box_candidate')
# Under-nose foot ledge gives a visually readable change of level without claiming ramp accessibility.
box('Front grounded transfer foot ledge',(0,.10,-1.857),(1.16,.20,.43),lagoon,'grounded foot ledge')
for i in range(7):box(f'Foot ledge nonslip inlay {i+1:02}',(-.48+i*.16,.204,-1.97),(.14,.008,.17),endwood,'nonslip visual detail',policy='no_collision_detail')
# Low side handles stay away from center transfer aperture.
for sign,tag in [(-1,'L'),(1,'R')]:
 tube(tag+' short transfer assist rail',[(sign*.79,.655,-1.69),(sign*.82,.91,-1.61),(sign*.93,.96,-1.26),(sign*1.03,.80,-1.13)],.033,wood,'side transfer grip',sides=8,policy='static_concave_candidate')
# Reachable front-right service furniture: visible dock, supply spout and removal panel, not simulated plumbing.
box('Right service dock body',(1.35,.50,-.47),(.35,.71,.70),ivory,'reachable service mounting')
box('Right removable service panel',(1.53,.52,-.47),(.025,.40,.48),wood,'service access panel')
for z in [-.65,-.52,-.39,-.26]:box('Service panel vent '+str(z),(1.545,.52,z),(.007,.24,.018),dark,'service panel groove',policy='no_collision_detail')
box('Service control mounting pad',(1.355,.882,-.50),(.28,.055,.41),lagoon,'reachable control mounting surface')
box('Nonfunctional service control face',(1.355,.914,-.50),(.23,.012,.31),bronze,'nonfunctional control face',policy='no_collision_detail')
for k,z in enumerate([-.58,-.45]):box('Service status inset '+str(k),(1.355,.923,z),(.13,.009,.042),coral if k==0 else seafoam,'nonfunctional status inset',policy='no_collision_detail')
tube('Return supply spout proposed',[(1.38,.87,-.18),(1.38,1.18,-.18),(1.16,1.20,-.18),(1.10,1.15,-.18)],.036,bronze,'proposed supply interface',sides=8,policy='no_collision_detail')
# Service face view: quick-release fasteners and reachable hose mount.
for y in [.37,.67]:
 for z in [-.65,-.29]:box(f'Panel fastener {y} {z}',(1.551,y,z),(.018,.025,.025),bronze,'service fastener',policy='no_collision_detail')
# Datum values target actual existing support vertices (avoids invented biological poses).
contacts=[]
for name,j,u in [('RestContact_Front',3,0),('RestContact_Center',14,0),('RestContact_Rear',24,0),('RestContact_Left',14,-.6),('RestContact_Right',14,.6)]:
 z=zs[j];p=(u*sw(z),sh(u,z),z);mark(name,p,'support surface contact');contacts.append({'name':name,'position':p})
mark('Transfer_Lip',(-.076,.672,-1.868),'actual transfer slat top')
mark('Waterline_Center',(0,WATER,0),'visual water surface datum')
mark('Service_Control_Mount',(1.355,.920,-.50),'actual bronze control face upper surface')
mark('Service_Access_Stance',(2.05,0,-.47),'external floor reservation datum')
mark('Approach_Center',(0,0,-2.65),'external floor reservation datum')
mark('Floor_Origin',(0,0,0),'floor origin')
bpy.context.view_layer.update()
allv=[Vector(G(o.matrix_world@v.co)) for o in parts for v in o.data.vertices]
lo=[min(v[i] for v in allv) for i in range(3)];hi=[max(v[i] for v in allv) for i in range(3)]
metadata={'schema':'astraea.single_component.v1','catalogue_id_check':{'complete_manifest_checked':True,'unused_on_initial_authoring':True,'manifest_sha256_at_build':hashlib.sha256(CAT.read_bytes()).hexdigest(),'current_registration':'same family' if existing_id_occurrences else 'not registered'},'asset_id':ID,'family':FAMILY,'name':'Lagoon Immersed Rest Cradle','scope':'One original proposed aquatic rest component. No recovered assignment, occupancy or biological certification.',
'coordinates':{'units':'metres','metadata_frame':'Godot/glTF Y-up','front':[0,0,-1],'blender_front':[0,1,0],'source_to_export':'(x,y,z) -> (x,z,-y)','datum':'floor origin'},
'bounds_gltf':{'min':lo,'max':hi,'size':[hi[i]-lo[i] for i in range(3)]},'target_max_dimensions_xyz_m':[3.6,1.6,4.2],
'basin':{'shell_object':basin.name,'interior_floor_height_m':.16,'interior_floor_extent_approx_xz_m':[2.10,2.9],'wall_horizontal_thickness_at_rim_m':[.23,.24],'minimum_front_rim_height_m':.635,'rear_rim_height_m':1.115,'shell_is_open_cavity_closed_material':True},
'support':{'object':support.name,'type':'wide concave immersed support with rising rear and raised lateral contours','z_extent_m':[ZMIN,ZMAX],'width_range_m':[2*min(sw(z) for z in zs),2*max(sw(z) for z in zs)],'central_height_m':sh(0,zs[14]),'front_center_height_m':sh(0,ZMIN),'rear_center_height_m':sh(0,ZMAX),'top_function':'t=(z+1.37)/2.72; width_half=.76+.25*sin(pi*t)-.12*t*t; x=u*width_half; y=.22+.135*u*u+.05*(1-t)^3+.48*t^5; -1<=u<=1','material_thickness_m':.065,'sample_contacts':contacts,'immersion_note':'Most of the central/lateral support is below proposed waterline; rear slope emerges. This is not a solved body pose.'},
'water':{'object':water.name,'level_y_m':WATER,'surface_bounds_xz_m':[[min(p[0] for p in waterverts),min(p[2] for p in waterverts)],[max(p[0] for p in waterverts),max(p[2] for p in waterverts)]],'level_above_basin_floor_m':WATER-.16,'central_support_submergence_m':WATER-sh(0,zs[14]),'minimum_front_freeboard_m':.635-WATER,'closed_volume':False,'proposed_fluid_broadphase_only_bounds':{'min':[min(p[0] for p in waterverts),.16,min(p[2] for p in waterverts)],'max':[max(p[0] for p in waterverts),WATER,max(p[2] for p in waterverts)],'meaning':'AABB for planning only; actual future fluid must be bounded by cavity and exclude support material. No closed water-volume mesh or physics supplied.'},'collision_policy':'NO_SOLID_COLLISION; exclude WaterSurface_VisualOnly and all ripple ribbons from any static collision generation','surface_construction':'original planar radial mesh with exact convex-polygon subtraction of raised source support triangles; translucent material plus six authored ripple ribbons','simulation':'absent: no buoyancy, water quantity, flow, splash, thermal/chemical/environmental regulation or save state'},
'approach':{'external_clear_prism':{'min':[-.67,.005,-3.15],'max':[.67,1.75,-2.08]},'transfer_width_m':1.24,'transfer_height_m':.672,'foot_ledge_height_m':.20,'transfer_direction':[0,0,1],'no_centre_front_bar':True,'note':'Low transfer edge only, not a walk-through opening, ramp or certified accessible facility.'},
'service':{'control_mount_position':[1.355,.920,-.50],'access_stance_position':[2.05,0,-.47],'external_clear_prism':{'min':[1.59,.005,-.95],'max':[2.49,1.75,.01]},'mounting_status':'nonfunctional visible service/control interfaces; actual UI, plumbing and cleaning interaction pending'},
'collision':{'status':'proposal only; no physics bodies exported','shell':'static concave triangle surface or validated multi-convex decomposition preserving cavity; NEVER one convex hull over entire basin','support':'static concave candidate; exact contoured top is actual contact surface','water_and_ripples':'NO_SOLID_COLLISION','decorative_detail':'exclude no_collision_detail meshes from collision','future_water_detection':'separate nonblocking Area3D volume must be authored/tested during integration','all_nodes_have_explicit_collision_policy':True},
'geometry':{'native_mesh_objects':len(parts),'native_mesh_vertices':sum(len(o.data.vertices) for o in parts),'triangles':sum(len(p.vertices)-2 for o in parts for p in o.data.polygons),'materials':len(bpy.data.materials),'external_textures':0},
'proposed_room_reservation_gltf':{'min':[-1.48,0,-3.15],'max':[2.49,1.75,1.90]},'species_assignment':None,'fixed_species_quota':None,'recovered_room_assignment':None,
'body_fit_and_animation':'pending original actor dimensions, rest transitions, transfers and actual contact tests','reference_inspected':['BlenderCatalogue/references/intimate/image(20261002-000722).png','BlenderCatalogue/references/aquatic/image(20261001-035517).png','BlenderCatalogue/assets/quiet_cocoon_support_20261009/preview_front_threequarter.png'],
'source_read':['Game/docs/master_source/MASTER_CURRENT_APPLICATION.json (complete)','Game/docs/master_source/MASTER_FULL_CONTENT_INDEX.json chapters 6 and 8 (complete)','BlenderCatalogue/standards/COORDINATE_CONTRACT.md'],
'validation_limits':['Component source/export geometry and preview only; no Game import','No species compatibility, live water, body fit, rest animation, accessibility, environmental or structural load certification','No room layout or clearance outside stated reservation verified','No occupancy/berth changes, catalogue registration, backups or publication','Preview studio excluded from GLB; no exported lights'],
'authoring':'Original deterministic Python meshes and simple materials. No downloads, image textures, fees or external asset service.'}
assert all(hi[i]-lo[i]<=metadata['target_max_dimensions_xyz_m'][i]+1e-6 for i in range(3)),metadata['bounds_gltf']
assert lo[1]>=-1e-6
# Full per-mesh proposal table makes collision import choices independent of display names.
collision_rows=[]
for ob in parts:
 pts=[Vector(G(ob.matrix_world@v.co)) for v in ob.data.vertices]
 collision_rows.append({'mesh':ob.name,'role':ob['component_role'],'policy':ob['collision_policy'],'closed_solid':bool(ob['closed_solid_expected']),'bounds_gltf':{'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)]}})
(OUT/'collision_proposal.json').write_text(json.dumps({'asset_id':ID,'frame':'Godot/glTF metres Y-up','status':'proposal; no physics bodies supplied','warning':'Do not create a single convex hull of the entire basin. Exclude NO_SOLID_COLLISION water and no_collision_detail objects. Test actual actor routes and contacts after import.','meshes':collision_rows},indent=2)+'\n')
(OUT/'component_metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
bpy.ops.object.select_all(action='DESELECT')
for o in col.objects:o.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.gltf(filepath=str(OUT/(ID+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
# Studio only. No packed images, external textures or compositor dependencies.
studio=bpy.data.collections.new('Preview only | excluded from GLB');scene.collection.children.link(studio)
def mov(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 studio.objects.link(o)
def look(o,p):o.rotation_euler=(Vector(B(p))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=B((5.3,4.6,-6.4)));cam=bpy.context.object;mov(cam);cam.name='Preview_Camera';cam.data.type='ORTHO';cam.data.ortho_scale=5.55;look(cam,(.05,.52,-.02));scene.camera=cam
for name,p,power,size in [('Key',(-3,6,-4),750,5),('Fill',(4,3,-1),430,3),('Rim',(1,4,4),650,3)]:
 bpy.ops.object.light_add(type='AREA',location=B(p));o=bpy.context.object;mov(o);o.name='Preview_'+name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;look(o,(0,.4,0))
scene.world.color=(.17,.17,.17);scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=False
scene.render.resolution_x=960;scene.render.resolution_y=860;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.view_settings.view_transform='AgX'
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.005));o=bpy.context.object;mov(o);o.name='Preview_Ground';o.data.materials.append(mat('Preview sand studio',(.30,.28,.235),.92))
bpy.ops.object.select_all(action='DESELECT');support.select_set(True);bpy.context.view_layer.objects.active=support
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ID+'.blend')),compress=True)
if '--no-render' not in sys.argv:
 scene.render.filepath=str(OUT/'preview_front_threequarter.png');bpy.ops.render.render(write_still=True)
print('COMPONENT_SUMMARY '+json.dumps(metadata['bounds_gltf'])+' triangles='+str(metadata['geometry']['triangles']))
