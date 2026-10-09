"""Shared authored construction utilities, Blender 4.3.2; Godot world to Blender (X,-Z,Y)."""
import bpy,bmesh,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
F=106.5;P=None;SEC=None;M={};PARTS=[];LIGHTS=[]
def xyz(p):return (p[0],-p[2],F+p[1])
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def init(path,key):
 global P,SEC,M,PARTS,LIGHTS
 P=Path(path).resolve().parents[1];SEC=key;PARTS=[];LIGHTS=[]
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC';bpy.context.preferences.filepaths.save_version=0
 spec={'blue':('staff_bluegrey_paint',.78,0),'white':('staff_white_paint',.76,0),'zinc':('staff_zinc',.61,.65),'rubber':('staff_rubber',.91,0),'opal':('staff_opal',.45,0),'cloth':('teal_weave',.9,0),'oat':('oatmeal_weave',.9,0),'wood':('warm_walnut',.68,0),'ivory':('ivory_enamel',.66,0),'brass':('champagne_metal',.48,.55),'floor':('staff_floor',.85,0)}
 for k,(fn,rough,metal) in spec.items():
  m=bpy.data.materials.new('A_'+k);m.use_nodes=True;m.use_fake_user=True;n=m.node_tree.nodes;b=n.get('Principled BSDF');b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
  t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(P/'materials'/(fn+'.png')));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color'])
  if k=='opal':m.node_tree.links.new(t.outputs['Color'],b.inputs['Emission Color']);b.inputs['Emission Strength'].default_value=.5
  M[k]=m
def finish(o,n,mat,support,zone,role='fitted_component',bevel=.025):
 o.name='A_'+n;o['section_key']=SEC;o['support']=support if support.startswith(('A_','shared_')) else 'A_'+support;o['zone']=zone;o['role']=role
 if o.type=='MESH':
  bpy.context.view_layer.objects.active=o
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  if bevel:
   mod=o.modifiers.new('Manufactured radius','BEVEL');mod.width=bevel;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
  o.data.update();uv=o.data.uv_layers.new(name='MetreUV')
  for face in o.data.polygons:
   drop=max(range(3),key=lambda j:abs(face.normal[j]));axes=[j for j in range(3) if j!=drop]
   for li in face.loop_indices:
    v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]],v[axes[1]])
 o.data.materials.append(M[mat]);PARTS.append(o);return o
def box(n,p,d,mat,sup,zone,bev=.025,role='fitted_component'):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(p));o=bpy.context.object;o.dimensions=(d[0],d[2],d[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 return finish(o,n,mat,sup,zone,role,min(bev,min(d)*.3))
def mesh(n,verts,faces,mat,sup,zone,bev=.015,role='fitted_profile'):
 me=bpy.data.meshes.new(n);me.from_pydata([xyz(v) for v in verts],[],faces);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);return finish(o,n,mat,sup,zone,role,bev)
def prism(n,poly,y,h,mat,sup,zone,bev=.025,role='fitted_profile'):
 count=len(poly);vs=[(x,v,z) for v in [y,y+h] for x,z in poly];fs=[tuple(reversed(range(count))),tuple(range(count,count*2))]+[(j,(j+1)%count,(j+1)%count+count,j+count) for j in range(count)];return mesh(n,vs,fs,mat,sup,zone,bev,role)
def rod(n,a,b,r,mat,sup,zone,sides=12):
 pa,pb=Vector(xyz(a)),Vector(xyz(b));d=pb-pa;bpy.ops.mesh.primitive_cylinder_add(vertices=sides,radius=r,depth=d.length,location=(pa+pb)/2);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,n,mat,sup,zone,'support_or_hardware',.005)
def disc(n,x,z,y,r,h,mat,sup,zone):return rod(n,(x,y,z),(x,y+h,z),r,mat,sup,zone,24)
def profile(n,points,z0,z1,mat,sup,zone,bev=.025):
 # XY cross-section extruded in world Z.
 count=len(points);vs=[(x,y,z) for z in [z0,z1] for x,y in points];fs=[tuple(reversed(range(count))),tuple(range(count,count*2))]+[(j,(j+1)%count,(j+1)%count+count,j+count) for j in range(count)];return mesh(n,vs,fs,mat,sup,zone,bev)
def chamfer(x0,x1,z0,z1,c=.3):return [(x0+c,z0),(x1-c,z0),(x1,z0+c),(x1,z1-c),(x1-c,z1),(x0+c,z1),(x0,z1-c),(x0,z0+c)]
def ellipse(cx,cz,rx,rz,segments=32):return [(cx+rx*math.cos(i*math.tau/segments),cz+rz*math.sin(i*math.tau/segments)) for i in range(segments)]
def arcwall(n,cx,cz,r,thick,a0,a1,y,h,mat,sup,zone,steps=20):
 out=[]
 for j in range(steps):
  t0=a0+(a1-a0)*j/steps;t1=a0+(a1-a0)*(j+1)/steps
  poly=[(cx+rad*math.cos(t),cz+rad*math.sin(t)) for rad,t in [(r-thick/2,t0),(r+thick/2,t0),(r+thick/2,t1),(r-thick/2,t1)]]
  out.append(prism(n+'_'+str(j),poly,y,h,mat,sup,zone,.01))
 return out
def text(n,body,p,size,sup,zone,face='north',mat='opal'):
 cu=bpy.data.curves.new(n,'FONT');cu.body=body;cu.size=size;cu.extrude=.001;cu.align_x='CENTER';o=bpy.data.objects.new(n,cu);bpy.context.collection.objects.link(o);o.location=xyz(p)
 o.rotation_euler={'east':(math.pi/2,0,math.pi/2),'west':(math.pi/2,0,-math.pi/2),'north':(math.pi/2,0,0),'south':(math.pi/2,0,math.pi)}[face];finish(o,n,mat,sup,zone,'small_editable_sign',0)
def light(n,x,z,y,w,l,sup,zone,watts=350):
 box(n+'_body',(x,y,z),(w,.14,l),'zinc',sup,zone)
 box(n+'_lens',(x,y-.08,z),(w-.10,.035,l-.10),'opal',n+'_body',zone,.006);LIGHTS.append([n,[x,y-.12,z],w-.1,l-.1,watts])
def swivel(n,x,z,zone,facing=0,cloth='cloth'):
 start=len(PARTS)
 disc(n+'_foot',x,z,0,.43,.06,'rubber','shared_floor',zone)
 disc(n+'_post',x,z,.06,.11,.37,'zinc',n+'_foot',zone)
 prism(n+'_seat',chamfer(x-.42,x+.42,z-.43,z+.43,.12),.43,.14,cloth,n+'_post',zone,.045)
 box(n+'_stem',(x,.80,z+.35),(.1,.7,.08),'zinc',n+'_seat',zone,.015)
 box(n+'_back',(x,1.03,z+.38),(.83,.67,.16),cloth,n+'_stem',zone,.055)
 for side in [-1,1]:
  rod(n+'_arm'+str(side),(x+side*.4,.48,z+.22),(x+side*.4,.77,z+.22),.03,'zinc',n+'_seat',zone)
  box(n+'_pad'+str(side),(x+side*.4,.78,z),(.10,.055,.48),'rubber',n+'_arm'+str(side),zone,.02)
 rotate_group(PARTS[start:],x,z,facing)
def rotate_group(parts,x,z,angle):
 from mathutils import Matrix
 center=Vector(xyz((x,0,z)));mat=Matrix.Translation(center)@Matrix.Rotation(-angle,4,'Z')@Matrix.Translation(-center)
 for o in parts:o.matrix_world=mat@o.matrix_world
def seat(n,x,z,w,zone,facing=0,cloth='cloth'):
 start=len(PARTS);pl=chamfer(x-w/2,x+w/2,z-.5,z+.5,.18)
 prism(n+'_base',pl,0,.32,'blue','shared_floor',zone,.06)
 prism(n+'_cushion',chamfer(x-w/2+.04,x+w/2-.04,z-.49,z+.43,.15),.32,.16,cloth,n+'_base',zone,.055)
 box(n+'_backframe',(x,.67,z+.39),(w,.76,.19),'blue',n+'_base',zone,.06)
 box(n+'_backpad',(x,.76,z+.275),(w-.12,.58,.12),cloth,n+'_backframe',zone,.05)
 for side in [-1,1]:box(n+'_arm'+str(side),(x+side*(w/2-.07),.54,z),(.14,.42,.92),'ivory',n+'_base',zone,.05)
 rotate_group(PARTS[start:],x,z,facing)
def table(n,x,z,w,d,zone,y=.78,mat='white',oval=False):
 poly=ellipse(x,z,w/2,d/2) if oval else chamfer(x-w/2,x+w/2,z-d/2,z+d/2,.3)
 prism(n+'_shoe',chamfer(x-w*.3,x+w*.3,z-d*.3,z+d*.3,.12),0,.10,'rubber','shared_floor',zone,.035)
 box(n+'_pedestal',(x,(y+.1)/2,z),(max(.4,w*.33),y-.1,max(.35,d*.33)),'blue',n+'_shoe',zone,.05)
 prism(n+'_top',poly,y,.09,mat,n+'_pedestal',zone,.035);return n+'_top'
def chart(n,x,z,w,d,sup,zone,y=.875):
 # Static physical, inset ruled chart surface without simulated live data.
 box(n+'_field',(x,y,z),(w,.015,d),'blue',sup,zone,.005)
 for j in range(1,6):box(n+'_rule'+str(j),(x-w/2+j*w/6,y+.010,z),(.012,.005,d-.06),'zinc',n+'_field',zone,.001)
 for j in range(1,4):box(n+'_cross'+str(j),(x,y+.010,z-d/2+j*d/4),(w-.06,.005,.012),'zinc',n+'_field',zone,.001)
 for j in range(3):disc(n+'_pin'+str(j),x-w*.26+j*w*.24,z+(j%2-.5)*d*.35,y+.013,.042,.015,'brass',n+'_field',zone)
def cabinet(n,x,z,w,d,zone,height=2.3,mat='blue',face='east'):
 box(n+'_carcass',(x,height/2,z),(w,height,d),mat,'shared_floor',zone,.055)
 # Fitted cabinet face with broad inset panels/real handles.
 for j in range(2):
  dz=z+(-.25 if j==0 else .25)*d
  box(n+'_door'+str(j),(x+w/2+.014,height/2,dz),(.045,height-.14,d/2-.06),'white',n+'_carcass',zone,.025)
  rod(n+'_handle'+str(j),(x+w/2+.056,.8,dz+.10),(x+w/2+.056,1.08,dz+.10),.018,'zinc',n+'_door'+str(j),zone)
 return n+'_carcass'
def shelf(n,x,z,w,d,zone,height=2.7,mat='blue'):
 box(n+'_back',(x,height/2,z),(w,height,.13),mat,'shared_floor',zone,.03)
 for side in [-1,1]:box(n+'_end'+str(side),(x+side*(w/2-.06),height/2,z-d/2),(.12,height,d),mat,n+'_back',zone,.015)
 for j,y in enumerate([.25,.88,1.50,2.12]):
  box(n+'_shelf'+str(j),(x,y,z-d/2),(w,.08,d),'white',n+'_back',zone,.01)
  if j in [1,2]:
   for k in range(3):
    xx=x-w*.30+k*w*.3
    box(n+'_folio'+str(j)+'_'+str(k),(xx,y+.26,z-d*.55),(.24,.44,d*.65),'blue' if k%2 else 'rubber',n+'_shelf'+str(j),zone,.03)
 light(n+'_shelf_task',x,z-d+.02,2.05,min(w-.2,2.0),.4,n+'_shelf3',zone,70)
def care(n,x,z,zone):
 cab=cabinet(n,x,z,1.0,3.2,zone,2.2)
 box(n+'_wash',(x+.9,.84,z-.7),(.85,.12,1.15),'ivory',cab,zone,.06)
 rod(n+'_tap',(x+.65,.90,z-.65),(x+.65,1.21,z-.65),.04,'zinc',n+'_wash',zone)
 rod(n+'_spout',(x+.65,1.21,z-.65),(x+1.0,1.21,z-.65),.04,'zinc',n+'_tap',zone)
 box(n+'_return',(x+.68,.31,z+.8),(.35,.62,.80),'rubber',cab,zone,.055)
 light(n+'_care_task',x+.8,z,2.10,.75,2.5,cab,zone,160)
def terminal(n,x,z,sup,zone,y=.9,facing=0):
 start=len(PARTS)
 disc(n+'_foot',x,z,y,.21,.03,'rubber',sup,zone)
 rod(n+'_stem',(x,y+.03,z),(x,y+.35,z),.06,'zinc',n+'_foot',zone)
 box(n+'_case',(x,y+.52,z),(.86,.6,.24),'blue',n+'_stem',zone,.05)
 box(n+'_face',(x,y+.53,z-.135),(.69,.44,.022),'rubber',n+'_case',zone,.01)
 for j in range(3):box(n+'_indicator'+str(j),(x-.12,y+.63-j*.09,z-.153),(.27-j*.04,.023,.010),'zinc',n+'_face',zone,.001)
 box(n+'_keyboard',(x,y+.036,z-.45),(.69,.062,.30),'rubber',sup,zone,.025)
 rotate_group(PARTS[start:],x,z,facing)
def cup(n,x,z,y,sup,zone):
 disc(n+'_body',x,z,y,.075,.13,'ivory',sup,zone)
 rod(n+'_handle',(x+.07,y+.04,z),(x+.13,y+.08,z),.02,'ivory',n+'_body',zone)
def save(contract):
 contract['authored_fixture_preview']=LIGHTS;contract['coordinate_mapping']='Blender=(GodotX,-GodotZ,GodotY); world origin identity placement';contract['runtime_acceptance']='Not integrated; source evidence only'
 (P/'contract.json').write_text(json.dumps(contract,indent=2))
 bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(P/'source/native.blend'))
 fonts=[o for o in PARTS if o.type=='FONT']
 for o in fonts:
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
  uv=o.data.uv_layers.new(name='TextUV')
  for j,v in enumerate(uv.data):v.uv=(0,0)
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:
  if o.get('section_key')==SEC:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(P/'exports'/(''+SEC+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_extras=True)
 print('DELIVERED',SEC,'parts',len(PARTS))

