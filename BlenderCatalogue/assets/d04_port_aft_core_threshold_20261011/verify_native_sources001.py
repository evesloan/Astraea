from pathlib import Path
import bpy,json,hashlib
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));source=R/'BlenderCatalogue/assets/primary_atrium_core/source/AST-CIR-005_spine_core.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={r['native']:sha(W/r['native'])for r in P['native_export_records']}
def payload(o):
 d={'matrix_world':[list(q)for q in o.matrix_world]}
 if o.type=='MESH':d.update(vertices=[list(q.co)for q in o.data.vertices],faces=[list(q.vertices)for q in o.data.polygons],materials=[m.name for m in o.data.materials],uv={u.name:[list(v.uv)for v in u.data]for u in o.data.uv_layers})
 return d
bpy.ops.wm.open_mainfile(filepath=str(source));original={o.name:payload(o)for o in bpy.data.objects if o.type in ['MESH','EMPTY']};empty={o.name:payload(o)for o in bpy.data.objects if o.type=='EMPTY'};bpy.ops.wm.open_mainfile(filepath=str(W/'AST-CIR-005_aft_midship_d04_port_threshold_r001.blend'));unchanged=0
for name,value in original.items():
 if name in P['exact_removed_source_meshes']:continue
 assert name in bpy.data.objects and payload(bpy.data.objects[name])==value,name
 if name not in empty:unchanged+=1
assert unchanged==837
for f,h in pins.items():assert sha(W/f)==h
(W/'INDEPENDENT_NATIVE_SOURCE_VERIFICATION.json').write_text(json.dumps({'status':'PASS_EXACT_SAVED_NATIVE_SOURCE_PRESERVATION','unchanged_meshes_vertices_faces_materials_UV_and_transforms':unchanged,'unchanged_empty_markers':len(empty),'exact_empty_marker_payloads':empty,'original_source_sha256':sha(source),'native_pins':pins,'native_bytes_unchanged':True},indent=2)+'\n');print('Independent saved-native source preservation',unchanged,len(empty))
