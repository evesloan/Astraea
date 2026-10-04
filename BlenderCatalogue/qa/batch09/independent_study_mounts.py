"""Measure actual task-shoe support against unchanged actual study receiver exports."""
from pathlib import Path
import json,sys,hashlib,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch09'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
mp=ROOT/'assets/library_use/AST-LIB-008.manifest.json';m=json.loads(mp.read_text());gp=mp.parent/m['export'];source=json.loads((OUT/'independent_source_AST-LIB-008.json').read_text());assert sha(mp.parent/m['source'])==source['sha256']
a=np.load(ROOT/source['geometry_cache']);t=a['triangles'][a['object_names']=='LIGHT_mating_shoe'];p=np.unique(t.reshape(-1,3),axis=0);bottom=p[np.abs(p[:,2])<1e-7];assert len(bottom)>3
rows=[]
for fit in m['compatible_mounts']:
 pp=list((ROOT/'assets/library_study').glob(fit['asset']+'*.glb'));assert len(pp)==1;n=Native(pp[0]);translation=np.array(fit['fixture_translation_source_m']);witnesses=[n.nearest(C@(v+translation))for v in bottom];centre=n.nearest(C@fit['receiver_source_m']);passed=all(w['distance_m']<1e-6 and w['material']=='ASTRAEA_champagne_metal' and w['normal_gltf'][1]>.999 for w in witnesses)
 rows.append({'receiver_id':fit['asset'],'receiver_export':str(pp[0].relative_to(ROOT)),'receiver_sha256':sha(pp[0]),'translation_source_m':translation.tolist(),'shoe_bottom_vertices_sampled':len(bottom),'all_actual_shoe_bottom_vertices_on_receiver_top':passed,'maximum_contact_distance_m':max(w['distance_m']for w in witnesses),'receiver_centre_witness':centre,'pass':passed})
r={'passed':all(x['pass']for x in rows),'task_source_sha256':source['sha256'],'task_glb_sha256':sha(gp),'task_manifest_sha256':sha(mp),'placements':rows,'limits':'Geometric support-plane and footprint proof only. No fastener, power, stability, headroom, actor contact or room fit validation.'};(OUT/'independent_study_mounts.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
