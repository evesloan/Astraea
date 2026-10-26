"""Add unselected inherited-world entry and exact construction-time receivers."""
import json,hashlib,pathlib
R=pathlib.Path(__file__).resolve().parents[2];D=R/'Game/grand_arrivals_tram_20261026/integration_r001'
P='res://grand_arrivals_tram_20261026/integration_r001/'
A=R/'Game/aquatic_tram_interior_20261026/integration'
assert not (D/'ship.gd').exists()
def write(name,text):(D/name).write_text(text,encoding='utf-8',newline='\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
changes=[]
for name in ['r002/CORE_RECEIVING.json','r005/CORE_RECEIVING.json']:
 d=json.loads((D.parent/name).read_text());changes.append({'before':d['original_region'],'after':d['replacement_region']})
for d in json.loads((D.parent/'r004/RECEIVING.json').read_text())['receivers']:
 changes.append({'before':d['original_region'],'after':d['replacement_region']})
assert len({x['before']['id'] for x in changes})==6
models={}
for receipt,output in [('r003/BUILD.json','r003/ForeMidCoreEnclosure.glb'),('r005/ENCLOSURE_BUILD.json','r005/PrimaryCoreEnclosure.glb'),('r007/ENCLOSURE_BUILD.json','r007/ForwardGroundEnclosure.glb'),('r006/HALL_BUILD.json','r006/ArrivalsHallExit.glb')]:
 d=json.loads((D.parent/receipt).read_text());filename=pathlib.Path(d['source']).name
 models[filename]={'original_sha256':d['source_sha256'],'successor':'res://grand_arrivals_tram_20261026/'+output,'successor_sha256':sha(D.parent/output)}
supports={}
for name in ['r002/ForeMidCoreReceiving.glb','r004/LinkedForeReceiving.glb','r005/PrimaryCoreReceiving.glb','r007/LowerDeparture.glb']:
 supports['res://grand_arrivals_tram_20261026/'+name]=sha(D.parent/name)
proof={'selected':False,'compiled_source_sha256':sha(R/'Game/data/generated/structural_meshes.json'),'floor_changes':changes,'models':models,'supports':supports,'holds':['Complete graded rolling guideway and all under-rail supports are not yet integrated','Full inherited-world contacts, doors, rider and capacity acceptance pending','Old upper guideway and end buffers retained pending explicit supersession; motion admission stays false']}
write('WORLD_RECEIVING.json',json.dumps(proof,indent=2)+'\n')
write('floors.gd','''extends RefCounted
static func build(parent:Node3D,top:Material,side:Material,materials:Dictionary={})->Node3D:
 var proof:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("PREFIXWORLD_RECEIVING.json"))
 assert(FileAccess.get_sha256("res://data/generated/structural_meshes.json")==proof.compiled_source_sha256)
 var source:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/generated/structural_meshes.json"))
 var count:=0
 for i in source.regions.size():
  for change:Dictionary in proof.floor_changes:
   if source.regions[i].id==change.before.id:
    assert(source.regions[i]==change.before,"Exact original floor receiver required")
    source.regions[i]=change.after;count+=1
 assert(count==6)
 var group:Node3D=load("res://scripts/structural_floor_builder.gd").build_regions(parent,top,side,source.regions,materials)
 group.set_meta("lower_arrivals_exact_floor_changes",count)
 return group
'''.replace('PREFIX',P))
write('receiving.gd','''extends RefCounted
static func add_supports(ship:Node3D)->void:
 var owner:=Node3D.new();owner.name="LowerArrivalsSourceReceiving_UNSELECTED"
 var districts:Node3D=ship.get_node("ShipSpace/Districts")
 assert(not districts.has_node(owner.name));districts.add_child(owner)
 var proof:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("PREFIXWORLD_RECEIVING.json"))
 for path:String in proof.supports:
  assert(FileAccess.get_sha256(path)==str(proof.supports[path]))
  var visual:Node3D=load("PREFIXassembly.gd").raw_model(path)
  assert(visual!=null);owner.add_child(visual)
  load("res://scripts/static_contact_cache.gd").attach_group(visual,visual.find_children("*","MeshInstance3D",true,false))
 owner.set_meta("operation_holds",proof.holds)
'''.replace('PREFIX',P))
ship=(A/'ship.gd').read_text()
assert ship.count('load("res://scripts/structural_floor_builder.gd").build(')==1
ship=ship.replace('load("res://scripts/structural_floor_builder.gd").build(',f'load("{P}floors.gd").build(')
assert ship.count('res://aquatic_tram_interior_20261026/integration/adapter.gd')==2
ship=ship.replace('res://aquatic_tram_interior_20261026/integration/adapter.gd',P+'adapter.gd')
ship+='''
# Construction-only source routing: the old model is never first installed and
# removed, and no lift/stair/persistent owner is swapped or recreated.
func model(parent:Node3D,file:String,label:String,location:Vector3,yaw:float=0.0)->Node3D:
 var proof:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("PREFIXWORLD_RECEIVING.json"))
 if not proof.models.has(file):return super.model(parent,file,label,location,yaw)
 var row:Dictionary=proof.models[file]
 assert(FileAccess.get_sha256("res://assets/models/"+file)==row.original_sha256)
 assert(FileAccess.get_sha256(row.successor)==row.successor_sha256)
 var wrapper:=Node3D.new();wrapper.name=label;wrapper.set_meta("catalogue_file",file)
 wrapper.set_meta("lower_arrivals_source_successor",row.successor)
 parent.add_child(wrapper);wrapper.position=location;wrapper.rotation.y=yaw
 var visual:Node3D=load("PREFIXassembly.gd").raw_model(row.successor)
 assert(visual!=null);wrapper.add_child(visual);_static_contacts(visual)
 return wrapper
'''.replace('PREFIX',P)
ship='\n'.join(('\t'*(len(x)-len(x.lstrip(' ')))+x.lstrip(' ')) if x.startswith(' ') else x for x in ship.split('\n'))
write('ship.gd',ship)
write('ship.tscn',(A/'ship.tscn').read_text().replace('res://aquatic_tram_interior_20261026/integration/ship.gd',P+'ship.gd'))
adapter=(A/'adapter.gd').read_text().replace('res://aquatic_tram_interior_20261026/integration/assembly.gd',P+'assembly.gd')
old='.create(districts,"AFT_MIDSHIP" if "--aquatic-review-spawn" in OS.get_cmdline_user_args() else "CENTRAL")'
assert adapter.count(old)==1;adapter=adapter.replace(old,'.create(districts,"FORWARD")')
needle='\tvar assembly: Node3D = load("'+P+'assembly.gd").create'
assert adapter.count(needle)==1
adapter=adapter.replace(needle,'\tload("'+P+'receiving.gd").add_supports(ship)\n'+needle)
adapter=adapter.replace('assembly.set_meta("integrated_empty_startup_station", "CENTRAL")','assembly.set_meta("integrated_empty_startup_station", "FORWARD")')
write('adapter.gd',adapter)
print(json.dumps({'floor_receivers':len(changes),'source_models':list(models),'support_sources':list(supports),'entry':P+'ship.tscn','selected':False}))
