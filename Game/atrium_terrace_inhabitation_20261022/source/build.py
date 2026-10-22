"""Forty purposeful terrace compositions from verified native catalogue assets."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];G=P.parent;R=G.parent;N=R/'BlenderCatalogue/assets/atrium_terrace_inhabitation_20261022'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pre=json.loads((P/'evidence/PREREQUISITES.json').read_text())
for f,h in pre['source_pins'].items():assert sha(G/f)==h,f
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
kit={};kit_objects=[]
for key,row in pre['assets'].items():
 path=R/'BlenderCatalogue'/row['source'];assert sha(path)==row['source_sha256']
 with bpy.data.libraries.load(str(path),link=False)as(a,b):b.objects=list(a.objects)
 loaded=[o for o in b.objects if o is not None]
 for o in loaded:bpy.context.collection.objects.link(o)
 bpy.context.view_layer.update();meshes=[o for o in loaded if o.type=='MESH']
 pts=[o.matrix_world@Vector(v)for o in meshes for v in o.bound_box]
 lo=Vector([min(v[k]for v in pts)for k in range(3)]);hi=Vector([max(v[k]for v in pts)for k in range(3)])
 center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
 kit[key]=[(o,o.matrix_world.copy(),center)for o in meshes];kit_objects+=loaded
 for o in loaded:
  for c in list(o.users_collection):c.objects.unlink(o)
old=json.loads((G/'night_garden_court_completion_20261022/evidence/BUILD_R003.json').read_text());assert sha(R/old['native'])==old['native_sha256']
names=['NGRC_PorcelainStructure','NGRC_HoneyWalnut','NGRC_BrushedChampagne','NGRC_OpalFixture']
with bpy.data.libraries.load(str(R/old['native']),link=False)as(a,b):b.materials=list(names)
cream,wood,metal,glow=[bpy.data.materials[n]for n in names]
objects=[];instances=[];lights=[];counts={}
def place(key,row,u,v,h=0,yaw=0):
 # u increases toward the outer edge on each bank; local front is Godot+Z.
 pos=Vector((row['x']+row['side']*u,-(row['z']+v),row['y']+h))
 t=Matrix.Translation(pos)@Matrix.Rotation(-yaw,4,'Z');index=counts.get(row['name'],0);counts[row['name']]=index+1
 for source,pose,center in kit[key]:
  o=source.copy();o.parent=None;o.matrix_world=t@Matrix.Translation(-center)@pose;o.name=f'{row["name"]}_{index:02}_{key}_{source.name}';bpy.context.collection.objects.link(o)
  name=source.name.lower();plant=key in ['AST-BOT-001','AST-BOT-002','AST-BOT-003'];solid=not plant or any(s in name for s in ['trunk','stem','branch'])
  if any(s in name for s in ['soil','leaf','flower','foliage','lens']):solid=False
  o['physical_contact']=solid;o['terrace_group']=row['name'];o['catalogue_source']=key;objects.append(o)
 instances.append({'group':row['name'],'catalogue_id':key,'position_godot':[pos.x,pos.z,-pos.y],'yaw':yaw})
def mesh(n,vs,fs,m,row,solid=True):
 data=bpy.data.meshes.new(n);data.from_pydata([(row['x']+row['side']*x,-(row['z']+z),row['y']+y)for x,y,z in vs],[],fs);data.update()
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(data);bm.free()
 o=bpy.data.objects.new(n,data);bpy.context.collection.objects.link(o);data.materials.append(m);o['physical_contact']=solid;o['terrace_group']=row['name'];objects.append(o);return o
def cylinder(n,u,v,low,high,radius,m,row,solid=True):
 vs=[]
 for y in [low,high]:
  vs.extend([(u+radius*math.cos(i*math.tau/16),y,v+radius*math.sin(i*math.tau/16))for i in range(16)])
 fs=[tuple(reversed(range(16))),tuple(range(16,32))]+[(i,(i+1)%16,(i+1)%16+16,i+16)for i in range(16)]
 return mesh(n,vs,fs,m,row,solid)
def bar(n,a,b,radius,m,row):
 axis=(Vector(b)-Vector(a)).normalized();cross=axis.cross(Vector((0,1,0)))
 if cross.length<.1:cross=axis.cross(Vector((1,0,0)))
 cross.normalize();other=axis.cross(cross);vs=[]
 for p in [Vector(a),Vector(b)]:
  for i in range(12):vs.append(p+radius*(cross*math.cos(i*math.tau/12)+other*math.sin(i*math.tau/12)))
 fs=[tuple(reversed(range(12))),tuple(range(12,24))]+[(i,(i+1)%12,(i+1)%12+12,i+12)for i in range(12)]
 return mesh(n,vs,fs,m,row)
for row in pre['groups']:
 side=row['side'];view=-side*math.pi/2;deck=row['deck'];name=row['name']
 # Sculpted catalogue planting edges frame the outlook without closing the public aisle.
 place('AST-BOT-005',row,1.70,-1.45,0,view)
 place('AST-BOT-001',row,1.70,-1.45,.47,view+(math.pi/6 if row['variant']else -math.pi/6))
 place('AST-BOT-004',row,1.70,1.35,0,view)
 place('AST-BOT-002',row,2.00,.85,.47,view)
 place('AST-BOT-003',row,2.00,1.85,.47,view)
 if deck==13:
  place('AST-FUR-001',row,-.5,1.4,0,view);place('AST-FUR-002',row,-.5,-1.35,0,view)
  for v in [-1.35,1.4]:place('AST-FUR-003',row,-1.85,v,0,view)
 elif deck==14:
  for v,yaw in [(-1.35,0),(1.35,math.pi)]:place('AST-FUR-002',row,-1.5,v,0,yaw)
  place('AST-FUR-003',row,-1.5,0,0,0)
  place('AST-FUR-002',row,.05,1.45,0,view+side*.45)
 elif deck==15:
  place('AST-FUR-001',row,-.35,1.4,0,view);place('AST-FUR-002',row,-.35,-1.4,0,view)
  place('AST-FUR-003',row,-1.7,1.4,0,view)
  cylinder(name+'_OrientationPlinth',-1.65,-1.4,0,.84,.38,wood,row)
  cylinder(name+'_TactileReliefRim',-1.65,-1.4,.84,.9,.42,metal,row)
  for k in range(3):cylinder(name+'_ReliefContour_'+str(k),-1.65,-1.4,.90+k*.025,.925+k*.025,.31-k*.08,cream,row)
 elif deck==16:
  for v,yaw in [(-1.5,0),(1.5,math.pi)]:place('AST-FUR-001',row,-.65,v,0,yaw)
  place('AST-FUR-003',row,-.65,0,0,0)
 else:
  for v in [-1.5,0,1.5]:place('AST-FUR-002',row,-.3,v,0,view+side*(.12 if v<0 else -.12))
  for v in [-.75,.75]:place('AST-FUR-003',row,-1.7,v,0,view)
 # Twin lanterns share a supported floor standard; no floating or ambient rescue light.
 cylinder(name+'_LampFoot',.85,0,0,.10,.22,wood,row)
 cylinder(name+'_LampStem',.85,0,.10,2.38,.045,metal,row)
 for i,v in enumerate([-.62,.62]):
  bar(name+'_LampArm_'+str(i),(.85,2.38,0),(-.35,2.38-i*.14,v),.045,metal,row)
  y=2.22-i*.14;cylinder(name+'_LampShade_'+str(i),-.35,v,y,y+.14,.24,cream,row)
  cylinder(name+'_LampOpal_'+str(i),-.35,v,y-.015,y+.005,.19,glow,row,False)
  lights.append({'name':name+'_Source_'+str(i),'position':[row['x']-side*.35,row['y']+y-.035,row['z']+v],'target':[row['x']-side*1.4,row['y']+.45,row['z']+v],'energy':1.25,'range':7.5,'angle':68,'group':name})
bpy.context.view_layer.update();records=[]
for row in pre['groups']:
 group=[o for o in objects if o['terrace_group']==row['name']];pts=[o.matrix_world@Vector(c)for o in group for c in o.bound_box];pts=[(v.x,v.z,-v.y)for v in pts]
 records.append({'name':row['name'],'bounds':[[min(v[k]for v in pts)for k in range(3)],[max(v[k]for v in pts)for k in range(3)]],'native_parts':len(group),'purpose':row['purpose'],'owner':row['owner']})
native=N/'UpperAtriumInhabitation_r001.blend';out=P/'runtime/UpperAtriumInhabitation_r001.glb';assert not native.exists()and not out.exists()
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
# Export only from the immutable saved scene using bounded direct-data batching.
exec(compile(Path(__file__).with_name("export_saved.py").read_text(),str(Path(__file__).with_name("export_saved.py")),"exec"))
