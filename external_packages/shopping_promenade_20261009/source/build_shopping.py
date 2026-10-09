"""Editable D09 footprint chunks, ten fitted typologies and bounded court architecture.
Blender5.1.2. Source XYZ Z-up, each chunk origin world(X,-Z,0); GLB Y-up.
Detailed source parts stay editable. Exports batch only one chunk/layer/material.
"""
from pathlib import Path
import bpy,bmesh,json,math,sys,importlib.util,hashlib
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];D=P/'dependencies';CAT=D/'BlenderCatalogue'
PLAN=json.loads((P/'docs/PLACEMENT_AND_CONNECTORS.json').read_text());FLOORS=PLAN['floor_proposals']
for n in ['source/natives','exports','qa','preview']:(P/n).mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('palette',CAT/'standards/retail_materials.py');pal=importlib.util.module_from_spec(spec);spec.loader.exec_module(pal);M=pal.materials()
for role,col,rough,metal in [('shop_glass',(0.17,.30,.31,.20),.18,0),('fixture_lens',(1,.91,.72,1),.45,0),('quiet_teal',(.14,.35,.33,1),.85,0)]:
 mat=bpy.data.materials.new(role);mat.use_nodes=True;b=mat.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=col;b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;mat['meters_per_tile_uv']=[1,1]
 if role=='shop_glass':mat.surface_render_method='DITHERED';b.inputs['Alpha'].default_value=.20;b.inputs['Transmission Weight'].default_value=.20
 if role=='fixture_lens':b.inputs['Emission Color'].default_value=col;b.inputs['Emission Strength'].default_value=1.4
 M[role]=mat
W='ivory_enamel';O='warm_walnut';T='retail_terracotta_enamel';K='dark_rubber';S='warm_stone';C='champagne_metal';E='fixture_lens'
templates={};retained_inspection={}
for aid,family in [('AST-RTL-001','retail_display'),('AST-RTL-002','retail_display'),('AST-RTL-003','retail_work'),('AST-RTL-008','retail_textile_display')]:
 path=CAT/'assets'/family/'source'/(aid+'.blend')
 with bpy.data.libraries.load(str(path),link=False) as (available,dst):dst.objects=available.objects
 objs=[o for o in dst.objects if o and o.type=='MESH'];templates[aid]=[]
 for o in objs:
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=bpy.data.meshes.new_from_object(ev);mat=o.data.materials[0] if o.data.materials else M[W];role=o.get('material_role',mat.get('astraea_material_role',mat.name.replace('ASTRAEA_','').split('.')[0]));role=role if role in M else W
  # Imported source object matrices include only component-local parenting.
  me.transform(o.matrix_world);templates[aid].append((o.name,me,role))
 retained_inspection[aid]={'native':str(path.relative_to(P)),'meshes':len(objs),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scope':'Read-only native inspection/evaluated reuse; no retained file save'}
 for o in dst.objects:
  if o:bpy.data.objects.remove(o,do_unlink=True)
# R070 retained native inspection is separate from reuse; never copied into a new room.
path=CAT/'assets/retail_curios_room/source/AST-RTL-005.blend'
with bpy.data.libraries.load(str(path),link=False) as (a,d):d.objects=a.objects
retained_inspection['R070']={'native_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'meshes':sum(o is not None and o.type=='MESH' for o in d.objects),'maximum_source_height_m':max(v.co.z for o in d.objects if o and o.type=='MESH' for v in o.data.vertices),'reused':False}
for o in d.objects:
 if o:bpy.data.objects.remove(o,do_unlink=True)
(P/'qa/retained_native_inspection.json').write_text(json.dumps(retained_inspection,indent=2)+'\n')
bpy.context.preferences.filepaths.save_version=1
PARTS=[];ROWS=[];LIGHTS=[];OCC=[];GEOMETRY={};CONTACTS=[];SUPPORTS=[];ROOT=None;COL=None;CURRENT=None
def reset(bank):
 global PARTS,ROOT,COL
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for c in list(bpy.data.collections):
  if c.users==0:bpy.data.collections.remove(c)
 PARTS=[];bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene['scope']='Bounded construction source; root integration and final art/gameplay pending';bpy.context.scene['bank']=bank
def chunk(row):
 global ROOT,COL,CURRENT
 CURRENT=row;ident=row['chunk_id'];COL=bpy.data.collections.new(ident);bpy.context.scene.collection.children.link(COL);ROOT=bpy.data.objects.new(ident,None);COL.objects.link(ROOT);ROOT.location=(row['position'][0],-row['position'][2],0);ROOT['chunk_id']=ident;ROOT['room_id']=row.get('stable_room_id') or '';ROOT['proposed_room_id']=row.get('proposed_room_id') or '';ROOT['identity_status']=row.get('identity_status','architectural_circulation');ROOT['datum_world_y']=52.5;ROOT['source_frame']='Blender XYZ m Z up; GLB native Y up';ROOT['render_scope']='This bounded chunk only'
def mesh(name,verts,faces,role,layer='fitout',opaque=False):
 name=CURRENT['chunk_id']+'__'+name;me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me)
 if layer=='floor':bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update();me.materials.append(M[role]);uv=me.uv_layers.new(name='metric_material_uv');sc=M[role].get('meters_per_tile_uv',[1,1])
 for f in me.polygons:
  axis=max(range(3),key=lambda a:abs(f.normal[a]));axes=[a for a in range(3) if a!=axis]
  for li in f.loop_indices:
   q=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(q[axes[0]]/sc[0],q[axes[1]]/sc[1])
 ob=bpy.data.objects.new(name,me);COL.objects.link(ob);ob.parent=ROOT;ob['chunk_id']=CURRENT['chunk_id'];ob['layer']=layer;ob['material_role']=role;ob['opaque_surface_candidate']=opaque;PARTS.append(ob)
 return ob
def coord(u,v,h):
 # Width u is ship Z; depth v points away from the public street.
 return (-CURRENT.get('front_sign_x',1)*v,-u,h)
FACES=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def cube(n,lo,hi,r=W,layer='fitout',opaque=False):
 verts=[coord(lo[0] if i==0 else hi[0],lo[1] if j==0 else hi[1],lo[2] if k==0 else hi[2]) for i,j,k in [(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1)]]
 return mesh(n,verts,FACES,r,layer,opaque)
def prism(n,poly,z0,z1,r=W,layer='fitout',opaque=False):
 N=len(poly);return mesh(n,[coord(u,v,z) for z in [z0,z1] for u,v in poly],[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],r,layer,opaque)
def disk(n,u,v,r,z0,z1,role=W,segments=16,layer='fitout'):
 return prism(n,[(u+math.cos(i*math.tau/segments)*r,v+math.sin(i*math.tau/segments)*r) for i in range(segments)],z0,z1,role,layer)
def sweep(n,points,width,z0,z1,r=W,layer='fitout'):
 # Analytic open-path ribbon with semicircular ends; no external geometry wheel.
 tangents=[Vector((b[0]-a[0],b[1]-a[1])).normalized() for a,b in zip(points,points[1:])];left=[];right=[];rad=width/2
 for i,p in enumerate(points):
  t=tangents[0] if i==0 else tangents[-1] if i==len(points)-1 else (tangents[i-1]+tangents[i]).normalized();normal=Vector((-t.y,t.x));ref=tangents[max(0,i-1)];rn=Vector((-ref.y,ref.x));scale=rad/max(.3,normal.dot(rn));q=Vector(p);left.append(tuple(q+normal*scale));right.append(tuple(q-normal*scale))
 end_angle=math.atan2(tangents[-1].y,tangents[-1].x);start_angle=math.atan2(tangents[0].y,tangents[0].x)
 poly=left+[(points[-1][0]+rad*math.cos(end_angle+math.pi/2-j*math.pi/8),points[-1][1]+rad*math.sin(end_angle+math.pi/2-j*math.pi/8)) for j in range(1,8)]+list(reversed(right))+[(points[0][0]+rad*math.cos(start_angle-math.pi/2-j*math.pi/8),points[0][1]+rad*math.sin(start_angle-math.pi/2-j*math.pi/8)) for j in range(1,8)]
 return prism(n,poly,z0,z1,r,layer)
def mark(n,u,v,h,kind):
 o=bpy.data.objects.new(CURRENT['chunk_id']+'__DATUM_'+n,None);COL.objects.link(o);o.parent=ROOT;o.location=coord(u,v,h);o.empty_display_size=.1;o['kind']=kind;return o
def contact(ob):
 lo=min(v.co.z for v in ob.data.vertices);CONTACTS.append({'chunk':CURRENT['chunk_id'],'part':ob.name,'bottom_height_m':lo,'floor_y':52.5,'expected_floor_y':52.5+lo})
def fixture(n,u,v,h=4.5,layer='shell'):
 cube(n+'_ceiling_rod',(u-.025,v-.025,h+.14),(u+.025,v+.025,6.0),C,layer)
 disk(n+'_shade',u,v,.32,h,h+.14,W,16,layer);disk(n+'_lens',u,v,.23,h-.016,h,E,16,layer);mark(n,u,v,h-.02,'reserved_downlight')
 p=coord(u,v,h-.02);LIGHTS.append({'chunk_id':CURRENT['chunk_id'],'id':CURRENT['chunk_id']+'_'+n,'local_xyz':[p[0],p[2],-p[1]],'position_world':[p[0]+CURRENT['position'][0],52.5+p[2],-p[1]+CURRENT['position'][2]],'kind':'SpotLight3D','direction':[0,-1,0],'range_m':7,'angle_deg':70,'energy':.9,'colour':[1,.95,.86],'root_budget':'Enable only active room/court fixture budget; no whole-promenade all-lights-on acceptance'})
def textface(n,text,u,v,h,size=.25,layer='shell'):
 font=bpy.data.curves.new(n,'FONT');font.body=text;font.size=size;font.align_x='CENTER';font.extrude=.003;font.resolution_u=2;o=bpy.data.objects.new(n,font);COL.objects.link(o);bpy.context.view_layer.update();me=bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()));verts=[coord(u+(-p.co.x if layer=='shell' and CURRENT.get('front_sign_x',1)==1 else p.co.x),v-p.co.z,h+p.co.y) for p in me.vertices];faces=[tuple(reversed(f.vertices)) if layer=='shell' and CURRENT.get('front_sign_x',1)==1 else tuple(f.vertices) for f in me.polygons];bpy.data.objects.remove(o,do_unlink=True);return mesh(n,verts,faces,C,layer)
def opaque_quad(n,verts):
 ps=[coord(*p) for p in verts];OCC.append({'chunk_id':CURRENT['chunk_id'],'surface':n,'local_vertices_godot':[[p[0],p[2],-p[1]] for p in ps],'triangles':[0,1,2,0,2,3],'scope':'Literal solid wall face. Portal/window/service aperture regions omitted.'})
def wall(n,u0,u1,v0,v1,h0,h1,r=W):
 ob=cube(n,(u0,v0,h0),(u1,v1,h1),r,'shell',True)
 # Both long faces describe the actual wall solid, not a full-room hull.
 if abs(v1-v0)<abs(u1-u0):
  for v in [v0,v1]:opaque_quad(n+'_'+str(v),[(u0,v,h0),(u1,v,h0),(u1,v,h1),(u0,v,h1)])
 else:
  for u in [u0,u1]:opaque_quad(n+'_'+str(u),[(u,v0,h0),(u,v1,h0),(u,v1,h1),(u,v0,h1)])
 return ob
def native_asset(aid,u,v,h=0,angle=0,tag=''):
 out=[];co=math.cos(angle);si=math.sin(angle)
 for i,(name,me,role) in enumerate(templates[aid]):
  verts=[]
  for p in me.vertices:
   x,y,z=p.co;verts.append(coord(u+co*x-si*y,v+si*x+co*y,h+z))
  ob=mesh(aid+'_'+tag+'_'+str(i),verts,[tuple(f.vertices) for f in me.polygons],role);out.append(ob)
 if aid=='AST-RTL-001':
  # Real grounded backing meets the source rear pads exactly; no floating wall mount.
  corners=[(x,y) for x,y in [(-1.70,.45),(1.70,.45),(1.70,.56),(-1.70,.56)]]
  poly=[(u+co*x-si*y,v+si*x+co*y) for x,y in corners]
  backing=prism(aid+'_'+tag+'_grounded_backing',poly,h,h+3.0,W)
  if h==0:contact(backing)
 SUPPORTS.append({'chunk':CURRENT['chunk_id'],'asset':aid,'instance':tag,'origin_uvh':[u,v,h],'angle_z':angle,'kind':'Static fitted source component; future detached/owned stock excluded from static batch'})
 return out
def shelving(n,u,v,width=2.8,depth=.55,height=2.5,layer='fitout'):
 ob=cube(n+'_sole',(u-width/2,v-depth/2,0),(u+width/2,v+depth/2,.06),K,layer);contact(ob)
 for du in [-width/2,width/2-.08]:cube(n+'_side_'+str(du),(u+du,v-depth/2,.06),(u+du+.08,v+depth/2,height),W,layer)
 cube(n+'_back',(u-width/2,v+depth/2-.04,.06),(u+width/2,v+depth/2,height),T,layer)
 for z in [.4,1.05,1.7,2.35]:
  if z<height:cube(n+'_shelf_'+str(z),(u-width/2+.08,v-depth/2,z),(u+width/2-.08,v+depth/2-.04,z+.05),O,layer)
def bench(n,points,role='oatmeal_weave',layer='fitout'):
 ob=sweep(n+'_floor_shoe',points,.65,0,.07,K,layer);contact(ob);sweep(n+'_shaped_base',points,.73,.07,.43,W,layer);sweep(n+'_seat',points,.82,.43,.50,role,layer)
def planter(n,u,v,r=.5,height=0):
 ob=disk(n+'_foot',u,v,r,height,height+.06,K)
 if height==0:contact(ob)
 else:SUPPORTS.append({'chunk':CURRENT['chunk_id'],'instance':n,'bottom_height_m':height,'kind':'Potted sample seated on actual raised display terrace'})
 disk(n+'_basin',u,v,r+.035,height+.06,height+.59,W);disk(n+'_soil',u,v,r-.05,height+.56,height+.60,'botanical_soil' if 'botanical_soil' in M else K)
 for i in range(8):
  a=i*math.tau/8;du,dv=math.cos(a)*.38,math.sin(a)*.38;pts=[coord(u,v,height+.60),coord(u+du,v+dv,height+1.55+(i%3)*.15),coord(u+du*.8-dv*.22,v+dv*.8+du*.22,height+1.28),coord(u+du*.4+dv*.22,v+dv*.4-du*.22,height+1.05)]
  mesh(n+'_leaf_'+str(i),pts,[(0,1,2),(0,3,1)],'quiet_teal')
def display_goods(n,u,v,h,style=0):
 # Decorative immutable first-pass samples, not inventory-bearing objects.
 for j in range(4):
  x=u+(j-1.5)*.26
  if style%3==0:disk(n+'_'+str(j),x,v,.095,h,h+.12+(j%2)*.08,T,12)
  elif style%3==1:cube(n+'_'+str(j),(x-.08,v-.10,h),(x+.08,v+.10,h+.04+(j%2)*.03),'clay_weave')
  else:prism(n+'_'+str(j),[(x-.10,v-.08),(x+.10,v-.08),(x+.075,v+.075),(x-.075,v+.075)],h,h+.18,W)
def room_shell(r):
 # Floor is independent from shells and fittings. All walls inside12x12 allocation.
 for u,t in [(-5.8,'left'),(5.56,'right')]:wall(t+'_bearing_wall',u,u+.24,-5.8,5.8,0,6)
 # Rear stock door at width u=-3.5 has an actual2.2x3m opening.
 for a,b in [(-5.56,-4.6),(-2.4,5.56)]:wall('rear_'+str(a),a,b,5.56,5.8,0,6)
 wall('rear_service_transom',-4.6,-2.4,5.56,5.8,3,6)
 # Stock/work bay is3m deep, screened from the public room with same real door.
 for a,b in [(-5.56,-4.6),(-2.4,5.56)]:wall('stock_privacy_'+str(a),a,b,2.65,2.8,0,6)
 wall('stock_service_head',-4.6,-2.4,2.65,2.8,3,6)
 # Front glazing apertures are structural openings with glass, sills and separate returns.
 for a,b in [(-5.56,-5.3),(-2.6,-1.8),(1.8,2.6),(5.3,5.56)]:wall('front_pier_'+str(a),a,b,-5.8,-5.56,0,6)
 for a,b in [(-5.3,-2.6),(2.6,5.3)]:
  wall('window_sill_'+str(a),a,b,-5.8,-5.56,0,.95,S);wall('window_head_'+str(a),a,b,-5.8,-5.56,3.6,6)
  cube('true_window_glass_'+str(a),(a,-5.70,.95),(b,-5.68,3.6),'shop_glass','shell')
  for z in [.95,3.55]:cube('window_metal_rail_'+str(a)+'_'+str(z),(a,-5.82,z),(b,-5.78,z+.05),C,'shell')
 wall('public_door_header',-1.8,1.8,-5.8,-5.56,3.8,6)
 # Gable surfaces close the raised public-room volume above the wall line.
 prof=[(-5.8,6),(-4.4,6.35),(-2.5,7.10),(0,7.35),(2.5,7.10),(4.4,6.35),(5.8,6)]
 for i in range(len(prof)-1):
  a,ha=prof[i];b,hb=prof[i+1]
  for v,n in [(-5.8,'front'),(2.65,'stock')]:
   mesh(n+'_gable_'+str(i),[coord(a,v,6),coord(b,v,6),coord(b,v,hb),coord(a,v,ha),coord(a,v+.15,6),coord(b,v+.15,6),coord(b,v+.15,hb),coord(a,v+.15,ha)],FACES,W,'shell',True)
  verts=[coord(a,v,ha+dz) for dz in [0,.15] for v in [-5.8,2.8]]+[coord(b,v,hb+dz) for dz in [0,.15] for v in [-5.8,2.8]]
  # Explicit roof wedge, vertex order front-left/rear-left/rear-right/front-right.
  mesh('vault_ceiling_'+str(i),[coord(a,-5.8,ha),coord(b,-5.8,hb),coord(b,2.8,hb),coord(a,2.8,ha),coord(a,-5.8,ha+.15),coord(b,-5.8,hb+.15),coord(b,2.8,hb+.15),coord(a,2.8,ha+.15)],FACES,W,'shell')
 cube('stock_ceiling',(-5.8,2.8,6),(5.8,5.8,6.15),W,'shell')
 # Nested orange entry surround sits entirely outside the3.6x3.8 clear passage.
 for sign in [-1,1]:cube('entry_nested_jamb_'+str(sign),(1.82*sign if sign>0 else -2.04,-5.95,0),(2.04 if sign>0 else -1.82,-5.82,4.05),T,'shell')
 sweep('entry_shaped_crown',[(-1.95,-5.88),(-1.4,-5.96),(0,-6),(1.4,-5.96),(1.95,-5.88)],.12,3.85,4.07,T,'shell')
 # Facade address is a reviewable proposal for unlabelled joins, never persistence truth.
 textface('front_address',r['proposed_room_id'],0,-5.99,4.35,.38)
 textface('brand_front',r['name'].split(' / ')[0],0,-5.99,4.96,.28)
 cube('inset_front_canopy',(-5.3,-6.0,5.7),(5.3,-5.15,5.84),W,'shell')
 for u in [-4.8,4.8]:
  ob=disk('interior_column_foot_'+str(u),u,-3.8,.28,0,.10,S,12,'shell');contact(ob);disk('interior_column_'+str(u),u,-3.8,.19,.10,5.95,W,12,'shell')
 for n,u,v in [('public_light',0,-2.8),('rear_public_light',1,1.5),('work_light',0,4.1)]:fixture(n,u,v,4.6 if 'work' not in n else 4.3)
 mark('public_threshold',0,-6,0,'entry_floor_contact');mark('public_turn',0,-3.2,0,'clear_turn_proposal');mark('service_threshold',-3.5,5.8,0,'service_floor_contact');mark('stock_entry',-3.5,2.7,0,'service_passage')
 for n,poly in [('public_clear',[[-1.8,-5.8],[1.8,-5.8],[1.8,-1.4],[-1.8,-1.4]]),('service_clear',[[-4.6,2.6],[-2.4,2.6],[-2.4,5.8],[-4.6,5.8]])]:
  r.setdefault('reserved_clear_zones_uv',{})[n]=poly
def room_fitout(r):
 f=r['family_index'];variant=r['variation'];shift=(variant%3-1)*.18
 # Grounded common stock/work infrastructure, with rear access kept clear on the left.
 shelving('rear_stock_rack',1.8,5.1,5.0,.50,2.6);native_asset('AST-RTL-003',1.4,3.75,0,0,'staff_wrapping');display_goods('static_stock_sample',1.8,5.02,.45,f)
 # Original reusable display bays backed into the right side of the public room.
 native_asset('AST-RTL-001',3.35,2.05,0,0,'rear_display');display_goods('rear_sample',3.0,1.9,.95,f)
 # Ten plan types differ in both use and furnishing topology; variants adjust bays,
 # profiles, asymmetry and stock-facing craft without changing the approved allocation.
 if f==0:
  for u,v in [(-3.4,-1.9),(3.2,-.6)]:
   native_asset('AST-RTL-002',u,v,0,variant*.12,'orbit_'+str(u));display_goods('orbit_sample_'+str(u),u,v-.30,.69,f)
  bench('orbit_rest',[(-1.7,.5),(-1.2,1.6),(0,2.0)]);disk('orbit_display_ring',-3.7,.9,.62,.50,.59,C);planter('orbit_green',4.6,.3,.4)
 elif f==1:
  for u in [-3.6,3.4]:
   shelving('textile_sample_wall_'+str(u),u,.5,1.2,.7,2.25)
   for j in range(3):native_asset('AST-RTL-008',u+(j-1)*.30,.05,2.12,0,'swatch_'+str(u)+'_'+str(j))
  sweep('textile_privacy_return',[(2.4,.8),(2.3,1.9),(3.2,2.2),(4.9,2.2)],.14,0,2.45,W);bench('fitting_rest',[(3.4,1.15),(4.5,1.15)],'clay_weave');native_asset('AST-RTL-002',-3.4,-2.0,0,.18,'folded_display')
 elif f==2:
  for u,v,z in [(-3.4,-2.0,.5),(-3.6,.2,.85),(3.6,-.2,.7)]:
   ob=disk('garden_step_foot_'+str(u)+'_'+str(v),u,v,.82,0,.10,K);contact(ob);disk('garden_step_'+str(u)+'_'+str(v),u,v,.90,.10,z,W);planter('garden_sample_'+str(v),u,v,.52,z)
  shelving('garden_care_niche',-3.6,1.7,2.4,.6,2.1);display_goods('care_trays',-3.6,1.55,1.10,2);bench('garden_pause',[(2.7,-3.7),(4.7,-3.5)])
 elif f==3:
  for u in [-3.4,3.1]:native_asset('AST-RTL-003',u,-.1,0,-.1 if u<0 else .1,'parcel_public_'+str(u))
  shelving('parcel_cubbies',0,1.7,3.3,.8,2.4);native_asset('AST-RTL-002',3.3,-2.5,0,0,'parcel_landing');display_goods('parcel_samples',3.2,-2.8,.69,2)
 elif f==4:
  bench('soft_curve',[(-4.3,-2.5),(-3.1,-2.3),(-2.6,-1.4),(-2.7,.4),(-3.5,1.0)],'oatmeal_weave');bench('soft_wall',[(3.6,-2.5),(4.6,-.2)],'teal_weave');native_asset('AST-RTL-002',2.8,.5,0,.25,'soft_samples');native_asset('AST-RTL-008',-4.9,1.8,2.2,0,'soft_hanging_sample');planter('soft_green',-3.3,-4.5,.4)
 elif f==5:
  for u in [-3.5,3.5]:
   native_asset('AST-RTL-001',u,.65,0,-.2 if u<0 else .2,'paper_library_'+str(u));display_goods('paper_stack_'+str(u),u,.4,.95,1)
  native_asset('AST-RTL-003',2.8,-2.65,0,0,'writing_surface');bench('writing_pause',[(-4.5,-2.6),(-2.9,-2.6)],'clay_weave')
 elif f==6:
  native_asset('AST-RTL-002',-3.2,-1.6,0,.30,'reed_low');native_asset('AST-RTL-002',2.7,.2,0,-.25,'reed_high')
  for j in range(7):cube('reed_screen_'+str(j),(-4.9+j*.20,1.7,0),(-4.83+j*.20,1.83,2.1+math.sin(j*.4)*.3),O)
  bench('reed_contour',[(3.4,-2.9),(4.7,-2.2),(4.9,-1.0)],'teal_weave');display_goods('reed_forms',-3.2,-1.9,.69,0);planter('reed_green',-4.5,.2,.45)
 elif f==7:
  sweep('tide_display_sole',[(-4.5,-2.2),(-3.3,-1.4),(-3.3,.4)],.76,0,.08,K);sweep('tide_display_base',[(-4.5,-2.2),(-3.3,-1.4),(-3.3,.4)],.90,.08,.72,W);sweep('tide_display_top',[(-4.5,-2.2),(-3.3,-1.4),(-3.3,.4)],1.0,.72,.80,S);display_goods('tide_vessels',-3.8,-1.7,.80,2);native_asset('AST-RTL-002',3.2,-2.1,0,0,'tide_island');bench('tide_pause',[(3.2,.4),(4.6,.8)],'teal_weave')
 elif f==8:
  native_asset('AST-RTL-003',-3.4,-1.0,0,.2,'buttons_craft');native_asset('AST-RTL-002',3.1,-1.9,0,-.18,'buttons_tray');display_goods('button_trays',3.1,-2.15,.69,0);shelving('button_samples',-3.4,1.3,3.2,.5,2.3)
  for j in range(10):disk('button_sample_'+str(j),-4.6+j*.24,1.2,.062,1.1,1.13,C if j%2 else T,12)
 elif f==9:
  for u,v in [(-3.4,-2.1),(3.3,-.4)]:native_asset('AST-RTL-002',u,v,0,(variant%3)*.18,'curio_'+str(u));display_goods('curio_sample_'+str(u),u,v-.25,.69,0)
  native_asset('AST-RTL-003',0,1.7,0,0,'curio_care');planter('curio_green',3.4,-4.5,.4)
 # Low paired surface gives an inclusive resting/reach alternative without claiming species fit.
 cube('low_contact_surface_foot',(-4.9,-4.8,0),(-4.5,-4.2,.43),W);cube('low_contact_surface',(-5.0,-4.9,.43),(-4.35,-4.1,.50),O)
 mark('accessible_low_surface',-4.65,-4.5,.50,'reserved_low_support');mark('work_surface',1.68,3.75,.95,'wrapping_support');mark('persistent_goods_socket',3.0,1.9,1.0,'future_owned_merchandise_anchor')
 r['fitout_programme']=['Public display/selection/rest zone','Screened rear stock and wrapping/repair bay','Real source fixtures, static supported samples and source-driven lights','Reserved low support and future owned-goods sockets'];r['typology']=r['name'].split(' / ')[0]
def floor_meshes():
 for r in [x for x in FLOORS if x['chunk_id']==CURRENT['chunk_id']]:
  v=[];f=[];cx,_,cz=CURRENT['position']
  # Polygonal top/bottom triangulation explicitly preserves holes and concavities.
  for pts in r['triangles_xz']:
   for z in [-.24,0]:
    idx=len(v);v.extend((x-cx,-(zz-cz),z) for x,zz in pts);f.append((idx,idx+1,idx+2) if z==0 else (idx+2,idx+1,idx))
  for ring in [r['boundary'],*r.get('holes',[])]:
   points=ring+[ring[0]]
   for a,b in zip(points,points[1:]):
    idx=len(v);v.extend([(a[0]-cx,-(a[1]-cz),-.24),(b[0]-cx,-(b[1]-cz),-.24),(b[0]-cx,-(b[1]-cz),0),(a[0]-cx,-(a[1]-cz),0)]);f.append(tuple(range(idx,idx+4)))
  mesh(r['id']+'_owned_slab',v,f,S,'floor')
def world_box(n,lo,hi,role=W,layer='shell',opaque=False):
 cx,_,cz=CURRENT['position'];verts=[(x-cx,-(z-cz),y-52.5) for x,y,z in [(lo[0],lo[1],lo[2]),(hi[0],lo[1],lo[2]),(hi[0],lo[1],hi[2]),(lo[0],lo[1],hi[2]),(lo[0],hi[1],lo[2]),(hi[0],hi[1],lo[2]),(hi[0],hi[1],hi[2]),(lo[0],hi[1],hi[2])]];return mesh(n,verts,FACES,role,layer,opaque)
def court_architecture(r):
 cx,_,cz=r['position'];(x0,x1),(a,b)=r['bounds_xz'];side=1 if cx>0 else -1
 guard=next(x for x in json.loads((D/'Game/data/spatial_layout.json').read_text())['regions'] if x['id']=='D09_R070_and_connected_approach')['boundary']
 def protected(x,z,w,d):
  # Conservative spatial exclusion; source approach stays wholly untouched.
  return cx>0 and x+w>=min(p[0] for p in guard)-.18 and x-w<=max(p[0] for p in guard)+.18 and z+d>=min(p[1] for p in guard)-.18 and z-d<=max(p[1] for p in guard)+.18
 for z in [a+2,b-2]:
  for x in [x0+1.1,x1-1.1]:
   if protected(x,z,.5,.5):continue
   world_box('pale_column_foot_'+str(x)+'_'+str(z),(x-.38,52.5,z-.38),(x+.38,52.68,z+.38),S)
   world_box('profiled_pale_column_'+str(x)+'_'+str(z),(x-.23,52.68,z-.23),(x+.23,58.95,z+.23),W)
   world_box('column_cap_'+str(x)+'_'+str(z),(x-.36,58.95,z-.36),(x+.36,59.1,z+.36),W)
 # Broad sculpted ceiling edges and sparse cross ribs give spatial rhythm.
 for x in [x0+.25,x1-.25]:world_box('long_profile_edge_'+str(x),(x-.20,58.95,a),(x+.20,59.25,b),W)
 for z in [a+1,(a+b)/2,b-1]:
  xs=[x0+.25,x0+3,x0+8,x0+13,x1-.25];hs=[6.5,7.05,7.3,7.05,6.5]
  for j in range(4):
   va=[(xs[j]-cx,-(z+dz-cz),hs[j]+dh) for dh in [0,.12] for dz in [-.35,.35]];vb=[(xs[j+1]-cx,-(z+dz-cz),hs[j+1]+dh) for dh in [0,.12] for dz in [-.35,.35]]
   mesh('curved_coffer_rib_'+str(z)+'_'+str(j),[va[0],vb[0],vb[1],va[1],va[2],vb[2],vb[3],va[3]],FACES,W,'shell')
  # Physical horizontal lens suspended on a bearing rib, reserved budgeted spot.
  world_box('street_lens_'+str(z),(cx-.34,58.75,z-.2),(cx+.34,58.80,z+.2),E)
  LIGHTS.append({'chunk_id':r['chunk_id'],'id':r['chunk_id']+'_'+str(z),'local_xyz':[0,6.22,z-cz],'position_world':[cx,58.72,z],'kind':'SpotLight3D','direction':[0,-1,0],'range_m':9,'angle_deg':75,'energy':1.1,'colour':[1,.95,.86],'root_budget':'Current court only'})
 # Rest pockets occupy row gaps, leaving the8m central street band open.
 centres=[x['position'][2] for x in PLAN['rooms'] if x['chunk_id'] in r['shop_chunks']];gaps=sorted(set((p+q)/2 for p,q in zip(sorted(set(centres)),sorted(set(centres))[1:])))
 for j,z in enumerate(gaps):
  x=x0+1.7 if j%2==0 else x1-1.7
  if protected(x,z,.9,2):continue
  # Generic coord u maps Z and v maps-X, so fitout geometry remains chunk-local.
  u=z-cz;v=-(x-cx)
  bench('court_rest_'+str(j),[(u-1.5,v),(u,v-.25),(u+1.5,v)]);planter('court_green_'+str(j),u+2.6,v,.55)
  textface('court_direction_'+str(j),'D09 / '+r['chunk_id'].split('_')[-2]+' / Atrium',u,v-.42,1.5,.16,'fitout')
def service_architecture(r):
 cx,_,cz=r['position'];(x0,x1),(a,b)=r['bounds_xz'];edge=(x0 if cx>0 else x1) if abs(cx)<80 else (x1 if cx>0 else x0)
 world_box('service_opaque_outer_wall',(edge-.05,52.5,a),(edge+.05,55.7,b),W,'shell',True)
 world_box('service_seated_roof',(x0,55.7,a),(x1,55.82,b),W)
 # Only actual opaque wall surface, door-side wall remains the shop rear with holes.
 OCC.append({'chunk_id':r['chunk_id'],'surface':'service_outer_actual_wall','local_vertices_godot':[[edge-cx,0,a-cz],[edge-cx,0,b-cz],[edge-cx,3.2,b-cz],[edge-cx,3.2,a-cz]],'triangles':[0,1,2,0,2,3],'scope':'Exact outer opaque service wall, no doorway blanket'})
 for z in [a+1,(a+b)/2,b-1]:
  world_box('service_light_lens_'+str(z),(cx-.18,55.57,z-.14),(cx+.18,55.6,z+.14),E)
  LIGHTS.append({'chunk_id':r['chunk_id'],'id':r['chunk_id']+'_'+str(z),'local_xyz':[0,3.06,z-cz],'position_world':[cx,55.56,z],'kind':'SpotLight3D','direction':[0,-1,0],'range_m':6,'angle_deg':80,'energy':.7,'colour':[1,.95,.86],'root_budget':'Current service chunk only'})
def link_architecture(r):
 pts=r['points_xz'];cx,_,cz=r['position'];staff=r['kind']=='service_link'
 # Open branches connect retained systems; source-built light portals do not obstruct them.
 for i,(x,z) in enumerate([pts[0],pts[-1]]):
  # Do not insert a column into a retained axial bypass; branches own only ceiling/lens.
  width=2.0 if staff else 4.4
  world_box('branch_lintel_'+str(i),(x-.10,56.05,z-width/2),(x+.10,56.18,z+width/2),W)
  world_box('branch_lens_'+str(i),(x-.15,56.0,z-.20),(x+.15,56.03,z+.20),E)
  LIGHTS.append({'chunk_id':r['chunk_id'],'id':r['chunk_id']+'_'+str(i),'local_xyz':[x-cx,3.46,z-cz],'position_world':[x,55.96,z],'kind':'SpotLight3D','direction':[0,-1,0],'range_m':6,'angle_deg':80,'energy':.7,'colour':[1,.95,.86]})
def save_source(name):
 for im in bpy.data.images:
  if im.source=='FILE':im.pack()
 bpy.ops.wm.save_as_mainfile(filepath=str(P/'source/natives'/name),compress=True)
def finish_chunks():
 bpy.context.view_layer.update()
 roots=[o for o in bpy.context.scene.objects if o.type=='EMPTY' and 'chunk_id' in o]
 for root in roots:
  ident=root['chunk_id'];items=[o for o in PARTS if o.get('chunk_id')==ident];row=next(r for r in PLAN['rooms']+PLAN['chunks'] if r['chunk_id']==ident)
  rowstats={'chunk_id':ident,'parts':len(items),'layers':{},'position_world':row['position'],'source_native':bpy.context.scene['saved_native']}
  old=root.location.copy();root.location=(0,0,0);bpy.context.view_layer.update()
  for layer,path in list(row['exports'].items()):
   selected=[o for o in items if o['layer']==layer];groups={};temp=[]
   for ob in selected:
    groups.setdefault(ob['material_role'],[]).append(ob)
    GEOMETRY.setdefault(ident+'__'+layer,[]).append({'part':ob.name,'vertices_xyz':[[float(v.co.x),float(v.co.z),float(-v.co.y)] for v in ob.data.vertices],'material':ob['material_role']})
   for role,obs in groups.items():
    vs=[];faces=[];uvs=[]
    for ob in obs:
     start=len(vs);vs.extend(tuple(ob.matrix_world@v.co) for v in ob.data.vertices)
     for f in ob.data.polygons:
      faces.append(tuple(start+i for i in f.vertices));uvs.extend(tuple(ob.data.uv_layers.active.data[i].uv) for i in f.loop_indices)
    me=bpy.data.meshes.new(ident+'__'+layer+'__'+role);me.from_pydata(vs,[],faces);me.update();me.materials.append(M[role]);uv=me.uv_layers.new(name='metric_material_uv')
    for i,p in enumerate(uvs):uv.data[i].uv=p
    cp=bpy.data.objects.new(me.name,me);bpy.context.scene.collection.objects.link(cp);cp['chunk_id']=ident;cp['layer']=layer;cp['source_parts_json']=json.dumps([o.name for o in obs]);cp['collision_kind']='precise_floor' if layer=='floor' else 'opaque_shell_and_frame' if layer=='shell' else 'static_fitout';temp.append(cp)
   if temp:
    bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT')
    for o in temp:o.select_set(True)
    bpy.context.view_layer.objects.active=temp[0]
    bpy.ops.export_scene.gltf(filepath=str(P/path),export_format='GLB',use_selection=True,use_active_scene=True,export_yup=True,export_extras=True,export_texcoords=True,export_normals=True,export_cameras=False,export_lights=False)
   else:
    # An empty additive floor is still explicit in metadata; never invent a slab.
    row['exports'].pop(layer,None);continue
   tris=sum(len(o.data.loop_triangles) for o in temp if not o.data.calc_loop_triangles());rowstats['layers'][layer]={'runtime_meshes':len(temp),'source_parts':len(selected),'triangles':tris,'bytes':(P/path).stat().st_size}
   for o in temp:bpy.data.objects.remove(o,do_unlink=True)
  root.location=old;ROWS.append(rowstats)
  print('CHUNK_OK',ident,flush=True)
def main():
 for bank in ['P72','P100','S72','S100']:
  reset(bank)
  for r in PLAN['rooms']:
   if bank not in r['chunk_id'] or r['retained']:continue
   chunk(r);floor_meshes();room_shell(r);room_fitout(r)
  name='D09_shops_'+bank+'.blend';bpy.context.scene['saved_native']='source/natives/'+name;save_source(name);finish_chunks()
 reset('circulation')
 for r in PLAN['chunks']:
  chunk(r);floor_meshes()
  if r['kind']=='court':court_architecture(r)
  elif r['kind']=='service':service_architecture(r)
  else:link_architecture(r)
 bpy.context.scene['saved_native']='source/natives/D09_courts_and_services.blend';save_source('D09_courts_and_services.blend');finish_chunks()
 def dump(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
 dump('docs/PLACEMENT_AND_CONNECTORS.json',PLAN);dump('docs/LIGHT_SOURCES.json',LIGHTS);dump('docs/OPAQUE_SURFACES.json',OCC);dump('qa/source_geometry.json',GEOMETRY);dump('qa/floor_contact_proposals.json',CONTACTS);dump('docs/FITTED_COMPONENT_INTERFACES.json',SUPPORTS);dump('qa/build_receipt.json',{'blender_version':bpy.app.version_string,'rooms_constructed':99,'retained_R070':True,'chunks':ROWS,'runtime_meshes_total':sum(v['runtime_meshes'] for r in ROWS for v in r['layers'].values()),'editable_source_parts_total':sum(r['parts'] for r in ROWS),'batch_scope':'Exactly one bounded footprint/court/service chunk, one layer and one material. Detailed source saved before export batching.','identity_gate':PLAN['identity_gate'],'model_effort':'Not exposed','gameplay':'Reserved interfaces only'})
 print('SHOPPING_BUILD_COMPLETE',len(ROWS),flush=True)
if __name__=='__main__':main()
