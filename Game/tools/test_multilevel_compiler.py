"""Verify mezzanines cannot silently erase their lower floor and slab clashes fail."""
from pathlib import Path
import tempfile,json,subprocess,shutil,os
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='astraea-layer-test-') as temp:
 t=Path(temp)
 for folder in ['tools','data/generated','docs']:(t/folder).mkdir(parents=True,exist_ok=True)
 shutil.copy2(root/'tools/compile_layout.py',t/'tools/compile_layout.py')
 (t/'data/design_contract.json').write_text(json.dumps({'deck_datums':[{'deck_id':'D08','floor_elevation_m':44}]}))
 square=[[0,0],[10,0],[10,10],[0,10]]
 regions=[{'id':'lower','deck':'D08','boundary':square,'status':'test','thickness':.4},{'id':'mezzanine','deck':'D08','boundary':square,'status':'test','priority':20,'offset_y':4.25,'thickness':.4}]
 p=t/'data/spatial_layout.json';p.write_text(json.dumps({'regions':regions,'voids':[]}))
 subprocess.run(['python3',str(t/'tools/compile_layout.py')],env=os.environ,check=True,capture_output=True,text=True)
 result=json.loads((t/'data/generated/structural_meshes.json').read_text())
 assert [r['structural_area_m2'] for r in result['regions']]==[100,100]
 regions[1]['offset_y']=.2;p.write_text(json.dumps({'regions':regions,'voids':[]}))
 bad=subprocess.run(['python3',str(t/'tools/compile_layout.py')],env=os.environ,capture_output=True,text=True)
 assert bad.returncode!=0 and 'intersecting structural slabs' in bad.stderr
print('PASS: mezzanine retains lower floor; intersecting slab volumes rejected')
