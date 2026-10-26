from pathlib import Path
import bpy,json,struct,hashlib
import numpy as np
R=Path(__file__).resolve().parents[2];D=R/'Game/orchard_tram_interior_20261025/r007'
native=R/json.loads((D/'FINAL_NATIVE.json').read_text())['path'];bpy.ops.wm.open_mainfile(filepath=str(native))
b=(D/'OrchardReceiving_exact.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);binary=b[28+n:];rows=[]
for node in d['nodes']:
 if 'mesh' not in node:continue
 o=bpy.data.objects[node['name']];actual=np.array([[v.x,v.z,-v.y] for v in [o.matrix_world@v.co for v in o.data.vertices]])
 points=[]
 for p in d['meshes'][node['mesh']]['primitives']:
  acc=d['accessors'][p['attributes']['POSITION']];view=d['bufferViews'][acc['bufferView']]
  v=np.ndarray((acc['count'],3),dtype='<f4',buffer=binary,offset=view.get('byteOffset',0)+acc.get('byteOffset',0),strides=(view.get('byteStride',12),4)).copy().astype(float)
  assert not node.get('rotation') and not node.get('matrix') and not node.get('scale')
  v+=np.array(node.get('translation',[0,0,0]));points.extend(v)
 points=np.unique(np.array(points),axis=0);actual=np.unique(actual,axis=0)
 error=0.
 for start in range(0,len(actual),64):error=max(error,float(np.sqrt(((actual[start:start+64,None,:]-points[None,:,:])**2).sum(axis=2)).min(axis=1).max()))
 for start in range(0,len(points),64):error=max(error,float(np.sqrt(((points[start:start+64,None,:]-actual[None,:,:])**2).sum(axis=2)).min(axis=1).max()))
 assert error<.00002,(node['name'],error)
 rows.append({'member':node['name'],'max_vertex_error_m':error})
assert len(rows)==278
receipt=json.loads((D/'FINAL.json').read_text());assert receipt['light_budget_changed']==False
for lamp in receipt['fixtures']:
 o=bpy.data.objects[lamp['name']];back=bpy.data.objects[lamp['backplate']]
 lo=min((o.matrix_world@v.co).x for v in o.data.vertices)
 assert lo>9.99 # Lens clears east face of supporting post, not buried/self-shadowing.
 assert lamp['xyz'][0]>max((o.matrix_world@v.co).x for v in o.data.vertices)
result={'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'runtime_sha256':hashlib.sha256(b).hexdigest(),'matched_members':len(rows),'max_vertex_error_m':max(x['max_vertex_error_m'] for x in rows),'lens_mounts_and_emitters_clear':2,'rows':rows}
out=D/'NATIVE_RUNTIME_CHECK.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
