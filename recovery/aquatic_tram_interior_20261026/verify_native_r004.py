from pathlib import Path
import bpy,json,hashlib,importlib.util,sys
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2];D=R/'Game/aquatic_tram_interior_20261026/r004'
native=R/'BlenderCatalogue/assets/aquatic_tram_interior_20261026/r004/AquaticIntegratedReceiving_r004.blend'
bpy.ops.wm.open_mainfile(filepath=str(native))
spec=importlib.util.spec_from_file_location('screen',R/'recovery/tram_section_successor_20261023/screen_section.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
groups={}
for name,points in s.glb_vertices(str((D/'AquaticIntegratedReceiving.glb').resolve())):groups.setdefault(name,[]).append(points)
rows=[]
for name,clouds in groups.items():
 o=bpy.data.objects[name];actual=np.unique(np.array([[v.x,v.z,-v.y] for v in [o.matrix_world@v.co for v in o.data.vertices]]),axis=0);points=np.unique(np.vstack(clouds),axis=0);error=0.
 for start in range(0,len(actual),64):error=max(error,float(np.sqrt(((actual[start:start+64,None,:]-points[None,:,:])**2).sum(axis=2)).min(axis=1).max()))
 for start in range(0,len(points),64):error=max(error,float(np.sqrt(((points[start:start+64,None,:]-actual[None,:,:])**2).sum(axis=2)).min(axis=1).max()))
 assert error<.00003,(name,error)
 rows.append({'member':name,'max_vertex_error_m':error})
assert len(rows)==json.loads((D/"BUILD.json").read_text())["total_meshes"]
result={'matched_members':len(rows),'max_vertex_error_m':max(r['max_vertex_error_m'] for r in rows),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'runtime_sha256':hashlib.sha256((D/'AquaticIntegratedReceiving.glb').read_bytes()).hexdigest(),'rows':rows}
out=D/'NATIVE_RUNTIME_CHECK.json';assert not out.exists();out.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
