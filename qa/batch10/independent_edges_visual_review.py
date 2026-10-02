"""Bind already manually inspected final native edge images; no rendering."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch10';BASE=ROOT/'assets/salon_edges';qa=BASE/'qa'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
meta=json.loads((qa/'render_evidence.json').read_text());views=[]
for name,row in meta['views'].items():
 ident=row['camera']['id'];mp=BASE/(ident+'.manifest.json');m=json.loads(mp.read_text());sp=BASE/m['source'];gp=BASE/m['export'];assert sha(sp)==row['source_sha256_at_capture'] and sha(gp)==row['glb_sha256']
 for c in row['context']:assert sha(ROOT/c['path_from_catalogue_root'])==c['sha256']
 views.append({'name':name,'image':bind(qa/(name+'.png')),'source':bind(sp),'export':bind(gp),'camera':row['camera'],'camera_canonical_sha256':hashlib.sha256(json.dumps(row['camera'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),'context':row['context'],'manually_pixels_inspected':True,'image_frame_role':'normal-height component' if row['camera']['res']==[640,360] else 'intentional detail crop'})
res={'passed':True,'scope':'Component visual gate for SAL004–006 only; final connected assembly review remains separate.','render_evidence':bind(qa/'render_evidence.json'),'render_script':bind(qa/'render_imported.py'),'views':views,'reference_receipt':bind(OUT/'independent_initial_reference_receipt.json'),'findings':[
 {'catalogue_id':'AST-SAL-004','readout':'Low open planting edge has a continuous tactile timber seat, three visible under-seat bearings, quieter teal recess and a shaped end perch. Final perch bearing now reaches floor. The useful seat surface and soil separation are legible at640×360. Original botanical002/003 reuse is disclosed; no new plant counted.','pass':True},
 {'catalogue_id':'AST-SAL-005','readout':'Three substantial supported posts carry a continuous tactile cap with restrained inset/arris, real empty receiver fields and visible fixing feet. It is a restrained terminal component. Its usefulness and avoidance of a detached decorative rail depend on the separately reviewed physical portal join in the combined arrangement. No glass/infill or completed safety barrier supplied.','component_pass':True,'assembly_gate_separate':True},
 {'catalogue_id':'AST-SAL-006','readout':'Guest-facing ivory frame, three vertical teal recessed fields and timber ledge distinguish this from the open shelf/service side. The real corner work surface and low return provide a coherent useful transition. The normal-height rear view retains some Eevee shadow grain, but shelf positions, open mouths and bearing sides remain readable. All shelves/returns are fixed.','pass':True}],
 'limits':['Neutral Blender imported-GLB inspection, no CRT/shader or game performance proof.','Materials and authored geometry are assessed against actual supplied references; architectural allocation, final guest polygon and host moving-door reservations remain unavailable.','Component views do not complete a room. The terminal relationship is accepted only if the final normal-height assembly shows the intended real join.']}
(OUT/'independent_edges_visual_review.json').write_text(json.dumps(res,indent=2)+'\n');print('Bound',len(views),'manually inspected final edge views')
