"""Prove actual appended source components retain the intended asset transforms."""
from pathlib import Path
import bpy,json,runpy,math,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1];BATCH=ROOT;CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
decode=runpy.run_path(str('/workspace/scratch/375c2e438292/residential-batch-neighborhood-20261006/qa/independent_review/geometry_decode.py'))['decode'];cache={};rows=[]
for source in sorted((BATCH/'outputs/production_r011').glob('*/assembly.blend')):
    before=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));deps=bpy.context.evaluated_depsgraph_get();actual={}
    for ob in bpy.context.scene.objects:
        member=ob.get('assembly_member','')
        if not member or ob.type not in ['MESH','CURVE']:continue
        ev=ob.evaluated_get(deps);me=ev.to_mesh();actual.setdefault(member,[]).extend(tuple(ob.matrix_world@v.co)for v in me.vertices);ev.to_mesh_clear()
    receipt=json.loads((source.parent/'SOURCE_RECEIPT.json').read_text())
    for placement in receipt['placements']:
        if placement.get('candidate_export'):path=BATCH/placement['candidate_export']
        else:
            p=Path(placement['catalogue_source']);path=CAT/p.parent.parent/'exports'/(p.stem+'.glb') if 'source'in p.parts else CAT/p.with_suffix('.glb')
        if path not in cache:
            _,tri,_,_=decode(path);cache[path]=tri.reshape(-1,3)[:,[0,2,1]]*np.array([1,-1,1])
        a=placement['source_yaw'];M=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
        expected=cache[path]@M.T+np.array(placement['source_xyz']);got=np.array(actual[placement['label']]);err=max(float(np.abs(got.min(0)-expected.min(0)).max()),float(np.abs(got.max(0)-expected.max(0)).max()))
        rows.append({'room':source.parent.name,'component':placement['label'],'bounds_error_m':err,'pass':err<.0001})
    assert hashlib.sha256(source.read_bytes()).hexdigest()==before
report={'status':'PASS_ACTUAL_SOURCE_COMPONENT_TRANSFORMS' if all(x['pass']for x in rows)else'FAIL_ACTUAL_SOURCE_COMPONENT_TRANSFORMS','rooms':len(list((BATCH/'outputs/production_r011').glob('*/assembly.blend'))),'components':rows,'scope':'Actual evaluated .blend component bounds versus decoded retained GLB at declared transform; catches link-before-evaluation origin collapse. Not runtime collision or visual acceptance.'}
(ROOT/'qa/ASSEMBLY_COMPONENT_TRANSFORMS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));assert report['status'].startswith('PASS')
