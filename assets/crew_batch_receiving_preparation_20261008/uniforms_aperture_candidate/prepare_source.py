from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parent
BASE=Path('/workspace/shared/Astraea_recovery_20261007_AXWr5x')
SRC=BASE/'BlenderCatalogue/assets/primary_atrium_core/source/AST-CIR-005_spine_core.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC))
def fingerprint(o):
 d={'name':o.name,'type':o.type,'matrix':[list(r) for r in o.matrix_world],'props':{k:str(o[k]) for k in o.keys()}}
 if o.type=='MESH':d.update(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons],uvs=[[list(v.uv) for v in uv.data] for uv in o.data.uv_layers],materials=[m.name for m in o.data.materials])
 return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
before={o.name:fingerprint(o) for o in bpy.context.scene.objects}
targets=['CORE_OuterWall_02_1','CORE_WallDado_02_1'];pieces=[];record=[]
for name in targets:
 old=bpy.data.objects[name];assert len(old.data.vertices)==8 and len(old.data.polygons)==6
 lo=[min(v.co[i] for v in old.data.vertices) for i in range(3)];hi=[max(v.co[i] for v in old.data.vertices) for i in range(3)]
 assert abs(lo[1]+20)<1e-5 and abs(hi[1]-13)<1e-5
 splits=[('Fore',2,hi[1],lo[2],hi[2]),('Aft',lo[1],-2,lo[2],hi[2])]
 if 'OuterWall'in name:
  assert abs(lo[2]-12)<1e-5 and abs(hi[2]-16.26)<1e-5
  splits.append(('Header',-2,2,14.65,hi[2]))
 else:assert abs(lo[2]-12.12)<1e-5 and abs(hi[2]-12.78)<1e-5
 for suffix,y0,y1,z0,z1 in splits:
  o=old.copy();o.data=old.data.copy();o.name=name+'_Uniforms_'+suffix;bpy.context.collection.objects.link(o)
  for v in o.data.vertices:
   v.co[1]=y0 if abs(v.co[1]-lo[1])<1e-5 else y1
   v.co[2]=z0 if abs(v.co[2]-lo[2])<1e-5 else z1
  o.data.update()
  for p in o.data.polygons:
   normal=p.normal.normalized();u=(Vector((1,0,0))-normal*normal.x).normalized() if abs(normal.z)>.7 else Vector((-normal.y,normal.x,0)).normalized();v=normal.cross(u)
   for k in p.loop_indices:
    q=o.data.vertices[o.data.loops[k].vertex_index].co;o.data.uv_layers.active.data[k].uv=(q.dot(u),q.dot(v))
  pieces.append(o)
  record.append({'name':o.name,'material':o.data.materials[0].name,'glb_bounds':[[min(v.co[0] for v in o.data.vertices),min(v.co[2] for v in o.data.vertices),-max(v.co[1] for v in o.data.vertices)],[max(v.co[0] for v in o.data.vertices),max(v.co[2] for v in o.data.vertices),-min(v.co[1] for v in o.data.vertices)]]})
 bpy.data.objects.remove(old,do_unlink=True)
after={o.name:fingerprint(o) for o in bpy.context.scene.objects}
assert all(after[k]==v for k,v in before.items() if k not in targets)
assert set(after)-set(before)=={o.name for o in pieces}
bpy.ops.wm.save_as_mainfile(filepath=str(R/'AST-CIR-005_aft_uniforms_d03.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in pieces:o.select_set(True)
bpy.context.view_layer.objects.active=pieces[0]
bpy.ops.export_scene.gltf(filepath=str(R/'doorway_replacement_pieces.glb'),export_format='GLB',export_yup=True,export_extras=True,use_selection=True)
(R/'SOURCE_PROOF.json').write_text(json.dumps({'original_path':str(SRC),'original_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'successor_sha256':hashlib.sha256((R/'AST-CIR-005_aft_uniforms_d03.blend').read_bytes()).hexdigest(),'original_object_fingerprints':before,'successor_object_fingerprints':after,'removed_objects':targets,'replacement_boxes':record,'unchanged_objects':len(before)-2},indent=2)+'\n')
print('SOURCE_PREPARATION_OK',len(before),len(after))
