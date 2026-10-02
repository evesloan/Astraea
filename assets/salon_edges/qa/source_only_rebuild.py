"""Rebuild in a fresh directory from production source inputs only, then compare actual exports."""
from pathlib import Path
import tempfile,shutil,subprocess,json,hashlib,importlib.util
import numpy as np
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
s=importlib.util.spec_from_file_location('reader',BASE/'qa/validate_glb.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inputs():
 files=['standards/materials.py','standards/botanical_materials.py','materials/material_manifest.json','materials/botanical/manifest.json']
 files+=['materials/'+v['base_color_file']for v in json.loads((CAT/'materials/material_manifest.json').read_text())['materials'].values()]
 files+=['materials/botanical/'+v['file']for v in json.loads((CAT/'materials/botanical/manifest.json').read_text())['materials'].values()]
 files+=['assets/salon_edges/source/build_salon_edges.py'];return sorted(set(files))
def geometry(path):
 d,b=r.read(path);rows=[]
 def walk(i,parent):
  n=d['nodes'][i];m=parent@r.matrix(n)
  if 'mesh'in n:
   for p in d['meshes'][n['mesh']]['primitives']:
    v=r.accessor(d,b,p['attributes']['POSITION']);v=(m@np.c_[v,np.ones(len(v))].T).T[:,:3];ix=r.accessor(d,b,p['indices']).reshape(-1,3)
    rows.append({'role':d['materials'][p['material']]['name'],'triangles':len(ix),'xyz_digest':hashlib.sha256(np.round(v[ix],6).astype('<f8').tobytes()).hexdigest(),'uv_digest':hashlib.sha256(np.round(r.accessor(d,b,p['attributes']['TEXCOORD_0']),6).astype('<f8').tobytes()).hexdigest()})
  for c in n.get('children',[]):walk(c,m)
 for i in d['scenes'][d.get('scene',0)]['nodes']:walk(i,np.eye(4))
 return sorted(rows,key=lambda r:r['role'])
rows=[];files=inputs();report={'scope':'Fresh source-only rebuild with no QA, existing assets, output folders or scene inputs; generator creates all output parents. Actual native geometry/UVs compared at1 micrometre rounding, not source timestamps.','input_files':[{'path_from_catalogue_root':f,'sha256':sha(CAT/f)}for f in files]}
with tempfile.TemporaryDirectory(prefix='source_only_',dir=BASE/'qa')as tmp:
 root=Path(tmp)/'catalogue'
 for f in files:
  dst=root/f;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(CAT/f,dst)
 before=sorted(str(p.relative_to(root))for p in root.rglob('*')if p.is_file());report['pre_run_files']=before
 command=['blender','--background','--threads','1','--python-exit-code','1','--python',str(root/'assets/salon_edges/source/build_salon_edges.py')]
 p=subprocess.run(command,cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(BASE/'qa/source_only_rebuild.log').write_text(p.stdout);report['process_exit_code']=p.returncode
 if p.returncode:raise RuntimeError('Source-only rebuild failed')
 for ident in('AST-SAL-004','AST-SAL-005','AST-SAL-006'):
  orig=BASE/'exports'/f'{ident}.glb';new=root/'assets/salon_edges/exports'/f'{ident}.glb';a,b=geometry(orig),geometry(new);row={'catalogue_id':ident,'source_only_rebuilt_export_exists':new.exists(),'original_glb_sha256':sha(orig),'rebuilt_glb_sha256':sha(new),'geometry_and_uv_equal':a==b,'geometry_digest_rows':b};rows.append(row)
report['assets']=rows;report['all_passed']=report['process_exit_code']==0 and all(x['geometry_and_uv_equal']for x in rows);(BASE/'qa/source_only_rebuild.json').write_text(json.dumps(report,indent=2)+'\n');print('SOURCE_ONLY_REBUILD',report['all_passed']);assert report['all_passed']
