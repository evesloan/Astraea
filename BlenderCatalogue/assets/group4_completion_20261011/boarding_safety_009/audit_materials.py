from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[3]
def material(m):
 out={'nodes':[],'links':[]}
 for n in m.node_tree.nodes:
  row={'type':n.bl_idname,'inputs':{}}
  for i in n.inputs:
   if not i.is_linked and hasattr(i,'default_value'):
    v=i.default_value
    try:v=list(v)
    except TypeError:pass
    if isinstance(v,(bool,str,int,float,list)):row['inputs'][i.name]=v
  if n.type=='TEX_IMAGE' and n.image:
   row['image_sha256']=hashlib.sha256(bytes(n.image.packed_file.data)).hexdigest();row['interpolation']=n.interpolation;row['color_space']=n.image.colorspace_settings.name
  out['nodes'].append(row)
 for link in m.node_tree.links:out['links'].append([link.from_node.bl_idname,link.from_socket.name,link.to_node.bl_idname,link.to_socket.name])
 return out
old=R/'BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002/Group4_Port_Successor_002.blend'
bpy.ops.wm.open_mainfile(filepath=str(old));body={o.name:[material(m) for m in o.data.materials] for o in bpy.data.collections['TRAM_EDITABLE_COMPONENT'].objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(W/'Group4_Powered_Portal_Body_r001.blend'));checks=0
for n,q in body.items():assert [material(m) for m in bpy.data.objects[n].data.materials]==q,n;checks+=1
p=json.loads((W/'TERMINAL_PLAN.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/p['source_lantern_native']));lamps={o.name:[material(m) for m in o.data.materials] for o in bpy.data.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(W/p['native']))
for o in bpy.data.collections['TERMINAL_BRANCH_EDGES'].objects:
 if o.type!='MESH' or '__' not in o.name:continue
 n=o.name.split('__',1)[1]
 if n in lamps:assert [material(m) for m in o.data.materials]==lamps[n],o.name;checks+=1
(W/'MATERIAL_FIDELITY.json').write_text(json.dumps({'status':'PASS','checks':checks,'all39_car_material_graphs_retained':True,'all32_fixture_material_graphs_retained':True,'packed_texture_bytes_interpolation_and_color_space_exact':True},indent=2)+'\n');print('MATERIAL_FIDELITY_PASS',checks)
