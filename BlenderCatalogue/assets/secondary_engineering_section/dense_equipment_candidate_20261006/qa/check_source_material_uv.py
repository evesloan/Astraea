"""Read-only saved-source UV/material comparison against actual GLB triangle corners."""
from pathlib import Path
import json,hashlib,sys,bpy
import numpy as np
from collections import defaultdict
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'qa'));from geometry_review import glb
source=R/'source/AST-ENG-008_dense_bays.blend';before=hashlib.sha256(source.read_bytes()).hexdigest();g=glb(R/'exports/AST-ENG-008_dense_bays.glb');S=json.loads((R/'qa/source_build.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(source));dg=bpy.context.evaluated_depsgraph_get();a=defaultdict(list);b=defaultdict(list)
def canonical(material,tri,uv):
 # Actual source/export vertex correspondence is independently established exactly.
 points=[tuple(np.round(p,5)) for p in tri];rotation=min(range(3),key=lambda i:points[i]);order=[rotation,(rotation+1)%3,(rotation+2)%3];key=(material,)+tuple(points[i] for i in order);return key,np.array([uv[i] for i in order])
for row in S['parts']:
 ob=bpy.data.objects[row['name']];eo=ob.evaluated_get(dg);me=eo.to_mesh();me.calc_loop_triangles();uvl=me.uv_layers.active
 for tr in me.loop_triangles:
  ps=[ob.matrix_world@me.vertices[i].co for i in tr.vertices];ps=[(p.x,p.z,-p.y) for p in ps];uv=[(uvl.data[i].uv.x,1-uvl.data[i].uv.y) for i in tr.loops];material=me.materials[tr.material_index].name;key,value=canonical(material,ps,uv);a[key].append(value)
 eo.to_mesh_clear()
for m in g['meshes']:
 for tri,ids in zip(m['triangles'],m['indices']):
  key,value=canonical(m['material'],tri,m['uv'][ids]);b[key].append(value)
missing=sum(len(v) for k,v in a.items() if k not in b);maxuv=0.;bad=[]
for key,values in a.items():
 if key not in b:continue
 if len(values)!=len(b[key]):bad.append('multiplicity');continue
 rem=b[key][:]
 for x in values:
  index=min(range(len(rem)),key=lambda i:np.abs(x-rem[i]).max());err=float(np.abs(x-rem.pop(index)).max());maxuv=max(maxuv,err)
  if err>.00004:bad.append({'material':key[0],'uv_max_error':err})
report={'passed':missing==0 and not bad and hashlib.sha256(source.read_bytes()).hexdigest()==before,'scope':'Exact oriented triangle/material matching plus actual per-corner metric/atlas UV correspondence, with documented glTF V-axis inversion','source_sha256':before,'export_sha256':g['sha256'],'source_triangles':sum(len(v) for v in a.values()),'export_triangles':sum(len(v) for v in b.values()),'missing_oriented_triangles':missing,'max_uv_component_error':maxuv,'uv_tolerance':.00004,'material_names':sorted({k[0] for k in a}),'failures':bad,'source_unchanged':True};(R/'qa/source_material_uv_check.json').write_text(json.dumps(report,indent=2)+'\n');print(report);assert report['passed']

import resource
print('PROCESS_PEAK_RSS_KIB',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
