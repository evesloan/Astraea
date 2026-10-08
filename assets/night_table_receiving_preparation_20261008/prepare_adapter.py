from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parent;C=R/'runtime_candidate';S=R.parent/'remaining_amenity_review_20261007/packages/WP12_D10_directory_07';Q=C/'data/architecture/night_table';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(rel,text):
 p=C/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
mat=json.load(open(S/'dependencies/materials/material_manifest.json'))['materials'];staff=json.load(open(S/'dependencies/materials/staff/manifest.json'))['materials']['staff_zinc'];mat['staff_zinc']={**staff,'base_color_file':'staff/'+staff['file']}
textures=[]
for role in ['warm_stone','warm_walnut','teal_weave','clay_weave','staff_zinc']:
 spec=mat[role];p=S/'dependencies/materials'/spec['base_color_file'];assert sha(p)==spec['sha256'];dest=C/'assets/material_textures/night_table'/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);textures.append({'role':role,'file':'res://'+dest.relative_to(C).as_posix(),'sha256':sha(p),'tile_uv_m':spec['meters_per_tile_uv'],'roughness':spec['roughness'],'metallic':spec['metallic']})
map=json.load(open(Q/'NODE_NAME_MAP.json'));lights=[]
for n in map:
 if n['light_index']is None:continue
 name=n['source_name'];up='uplight'in name;cool='clean_work'in name or 'dirty_work'in name
 lights.append({'runtime_name':n['runtime_name'],'source_name':name,'light_index':n['light_index'],'energy':.28 if up else .7,'range_m':3.5 if 'lantern'in name else 6.0,'color':[.82,.90,1.0]if cool else [1.0,.92,.82],'requested_shadow':True})
manifest={'programme':'D10_directory_07','historical_alias':'D10_dining6','root_name':'D10_NightTable_Receiving_WIP','model_file':'WP12_night_table_runtime_names001.glb','runtime_sha256':sha(C/'assets/models/WP12_night_table_runtime_names001.glb'),'source_sha256':'6830a683917b7c1f98009dbf489f77673557250901f6913a562c4ec5022f1f47','placement':[-31,61,216],'source_node_count':11983,'source_mesh_count':2977,'source_light_count':146,'capacity':240,'canonical_dining_total':2200,'floor_owners':['D10_night_table_floor','D10_night_table_entry'],'textures':textures,'lights':lights,'scope':'Whole original source candidate receiving. Runtime light-unit/range adaptation only; source geometry/materials preserved. Food service, seating interaction, stock interaction, loaded cart, final art and target hardware unverified.'}
put('data/architecture/night_table/runtime_manifest.json',json.dumps(manifest,indent=2)+'\n')
shader='''shader_type spatial;
render_mode diffuse_burley,specular_schlick_ggx;
varying vec2 ship_xz;
void vertex(){ship_xz=(MODEL_MATRIX*vec4(VERTEX,1.0)).xz;}
'''
for role in [t['role']for t in textures]:shader+=f'uniform sampler2D {role}: source_color,filter_nearest_mipmap,repeat_enable;\n'
shader+='''void fragment(){
 float u=ship_xz.x+54.0;float v=ship_xz.y-182.0;
 vec2 uv=vec2(ship_xz.x+31.0,216.0-ship_xz.y);
'''
conds={'warm_stone':'true','teal_weave':'u>=2.0&&u<44.0&&v>=2.0&&v<29.0','clay_weave':'u>=2.0&&u<44.0&&v>=39.0&&v<66.0','warm_walnut':'u>=22.0&&u<25.0&&((v>=2.0&&v<29.0)||(v>=39.0&&v<66.0))','staff_zinc':'u<26.0&&v>=30.0&&v<38.0'}
for role in ['warm_stone','teal_weave','clay_weave','warm_walnut','staff_zinc']:
 t=next(t for t in textures if t['role']==role);a,b=t['tile_uv_m'];shader+=f' if({conds[role]}){{ALBEDO=texture({role},uv/vec2({float(a)},{float(b)})).rgb;ROUGHNESS={float(t["roughness"])};METALLIC={float(t["metallic"])};}}\n'
shader+='}\n';put('shaders/night_table_receiving_finish.gdshader',shader)
put('scripts/night_table_receiving.gd','''extends RefCounted
static func build(ship:Node3D)->Node3D:
 var data:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/architecture/night_table/runtime_manifest.json"))
 var path:String="res://assets/models/"+str(data.model_file)
 assert(FileAccess.get_sha256(path)==str(data.runtime_sha256))
 var space:Node3D=ship.get_node("ShipSpace")
 assert(space.get_node_or_null(str(data.root_name))==null)
 var root:=Node3D.new();root.name=str(data.root_name);space.add_child(root)
 root.set_meta("programme_key",str(data.programme));root.set_meta("historical_alias",str(data.historical_alias));root.set_meta("source_dining_places",240);root.set_meta("operational_acceptance",false)
 var model:Node3D=ship.model(root,str(data.model_file),"NightTableSource",Vector3(-31,61,216))
 for spec in data.lights:
  var light:Light3D=model.find_child(str(spec.runtime_name),true,false)as Light3D
  assert(light!=null)
  light.set_meta("source_light_name",str(spec.source_name));light.set_meta("source_import_energy",light.light_energy)
  light.light_energy=float(spec.energy);light.light_color=Color(spec.color[0],spec.color[1],spec.color[2]);light.shadow_enabled=true
  if light is SpotLight3D:light.spot_range=float(spec.range_m)
  elif light is OmniLight3D:light.omni_range=float(spec.range_m)
  else:assert(false,"Unexpected source light class")
 var material:=ShaderMaterial.new();material.shader=load("res://shaders/night_table_receiving_finish.gdshader")
 for t in data.textures:
  assert(FileAccess.get_sha256(str(t.file))==str(t.sha256));material.set_shader_parameter(str(t.role),load(str(t.file)))
 for id in data.floor_owners:
  var floor:Node3D=space.get_node("CompiledStructuralFloors_NotFinishedRooms/"+str(id))
  for mesh in floor.find_children("*","MeshInstance3D",true,false):
   if str(mesh.name)!="StructuralSidesAndUnderside":mesh.material_override=material
 return root
''')
print('Prepared whole source adapter and exact source floor-finish regions;146bounded lights,240places; no live changes')
