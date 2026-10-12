from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[3]
native=R/'BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002/Group4_Port_Successor_002.blend'
h=hashlib.sha256(native.read_bytes()).hexdigest();P=json.loads((W/'SAFETY_PLAN.json').read_text());targets={q['mesh'] for q in P['vehicle_cuts']}
bpy.ops.wm.open_mainfile(filepath=str(native));rows=[]
for ob in bpy.data.collections['TRAM_EDITABLE_COMPONENT'].objects:
 if ob.name not in targets:continue
 points=[list(ob.matrix_world@v.co) for v in ob.data.vertices];faces=[]
 for p in ob.data.polygons:
  faces.append({'indices':list(p.vertices),'normal':list(p.normal),'uv':[list(ob.data.uv_layers.active.data[i].uv) for i in p.loop_indices]})
 rows.append({'name':ob.name,'points_blender_xyz':points,'faces':faces,'uv_name':ob.data.uv_layers.active.name})
assert len(rows)==8 and hashlib.sha256(native.read_bytes()).hexdigest()==h
(W/'SOURCE_PRISM_INPUTS.json').write_text(json.dumps({'source_native_sha256':h,'meshes':rows,'read_only':True},indent=2)+'\n')
print('READ_ONLY_PRISM_INPUTS',len(rows),'exact source meshes; originals unchanged')
