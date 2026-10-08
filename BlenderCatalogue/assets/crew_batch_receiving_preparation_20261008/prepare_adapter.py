from pathlib import Path
import json,struct,hashlib,numpy as np
R=Path(__file__).resolve().parent;C=R/'runtime_candidate';sections=[]
for item in json.loads((R/'INTAKE.json').read_text()):
 key=item['programme'];i=key[-2:];raw=Path(item['glb']['path']).read_bytes();ln=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+ln]);maps=json.loads((C/key/'NODE_NAME_MAP.json').read_text());lights=[]
 def matrix(n):
  if 'matrix'in n:return np.array(n['matrix']).reshape(4,4).T
  x,y,z,w=n.get('rotation',[0,0,0,1]);m=np.eye(4);m[:3,:3]=np.array([[1-2*y*y-2*z*z,2*x*y-2*z*w,2*x*z+2*y*w],[2*x*y+2*z*w,1-2*x*x-2*z*z,2*y*z-2*x*w],[2*x*z-2*y*w,2*y*z+2*x*w,1-2*x*x-2*y*y]])@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
 def visit(idx,parent):
  n=d['nodes'][idx];m=parent@matrix(n);name=n.get('name','')
  if 'light'in name.lower() and name.lower().endswith('lens'):
   assert 'mesh'in n;vs=[]
   for primitive in d['meshes'][n['mesh']]['primitives']:
    a=d['accessors'][primitive['attributes']['POSITION']];vs.extend([a['min'],a['max']])
   center=(np.min(vs,axis=0)+np.max(vs,axis=0))/2;center=(m@np.r_[center,1])[:3]
   lights.append({'fixture_runtime_name':maps[idx]['runtime_name'],'fixture_source_name':name,'fixture_center':center.tolist(),'position':(center-np.array([0,.045,0])).tolist(),'energy':.9,'range_m':8,'color':[.78,.88,1.0],'shadow':True})
  for child in n.get('children',[]):visit(child,m)
 for n in d['scenes'][d.get('scene',0)]['nodes']:visit(n,np.eye(4))
 assert lights
 model=C/key/(key+'_runtime_names001.glb');sections.append({'programme':key,'root_name':key+'_Source_Receiving_WIP','model_file':model.name,'runtime_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'source_sha256':item['glb']['sha256'],'placement':[0,0,0],'floor_owners':[f'D03_crew_{i}_floor',f'D03_crew_{i}_entry'],'source_import_light_count':0,'mounted_receiving_lights':lights,'receiving_hold':'Dedicated D03 aft-core aperture required' if i=='10' else 'Actual installed traversal and visual review pending'})
p=C/'data/architecture/crew_batch';p.mkdir(parents=True,exist_ok=True);(p/'runtime_manifest.json').write_text(json.dumps({'schema':1,'root_name':'D03_CrewBatch_Receiving_WIP','sections':sections,'scope':'Scratch adapter preparation. Exact source models with separately mounted receiving lights. Existing global light budget unchanged. No operating programme, loaded cart, final art or installed acceptance.'},indent=2)+'\n')
p=C/'scripts';p.mkdir(exist_ok=True);(p/'crew_batch_receiving.gd').write_text('''extends RefCounted
static func build(ship:Node3D)->Node3D:
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/crew_batch/runtime_manifest.json"))
 var space:Node3D=ship.get_node("ShipSpace")
 assert(space.get_node_or_null(str(data.root_name))==null)
 var root:=Node3D.new();root.name=str(data.root_name);space.add_child(root)
 root.set_meta("operational_acceptance",false)
 for section in data.sections:
  var path:String="res://assets/models/"+str(section.model_file)
  assert(FileAccess.get_sha256(path)==str(section.runtime_sha256))
  var room:=Node3D.new();room.name=str(section.root_name);root.add_child(room)
  room.set_meta("programme_key",str(section.programme));room.set_meta("receiving_hold",str(section.receiving_hold))
  var model:Node3D=ship.model(room,str(section.model_file),"Source",Vector3.ZERO)
  var index:int=0
  for spec in section.mounted_receiving_lights:
   var fixture:MeshInstance3D=model.find_child(str(spec.fixture_runtime_name),true,false)as MeshInstance3D
   assert(fixture!=null)
   var light:=OmniLight3D.new();light.name="MountedSourceFixture_%02d"%index;room.add_child(light)
   light.position=Vector3(spec.position[0],spec.position[1],spec.position[2])
   light.light_energy=float(spec.energy);light.omni_range=float(spec.range_m)
   light.light_color=Color(spec.color[0],spec.color[1],spec.color[2]);light.shadow_enabled=true
   light.set_meta("source_fixture",str(spec.fixture_source_name));index+=1
 return root
''')
print([(s['programme'],len(s['mounted_receiving_lights']))for s in sections]);print('Scratch-only adapter prepared; source models and live project untouched')
