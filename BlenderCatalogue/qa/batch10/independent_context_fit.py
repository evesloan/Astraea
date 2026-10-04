"""Actual native context roots/stock fit within named new component surfaces."""
from pathlib import Path
import json,hashlib,sys,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch10';ap=OUT/'assembly/render_evidence_v2.json';r=json.loads(ap.read_text())
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import nearest_distances
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bind=lambda p:{'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
rows=[];sources={}
for ident in ['AST-SAL-003','AST-SAL-004']:
 sr=json.loads((OUT/f'independent_source_{ident}.json').read_text());assert sha(ROOT/sr['path'])==sr['sha256'];a=np.load(ROOT/sr['geometry_cache']);sources[ident]=(a['triangles'],a['object_names'],sr)
for c in r['context']:
 p=ROOT/c['path'];assert sha(p)==c['sha256'];n=Native(p);v=np.unique(np.round((n.tris@C+np.asarray(c['local_source_translation_m'])).reshape(-1,3),9),axis=0);lo=v.min(axis=0);hi=v.max(axis=0);bottom=v[np.abs(v[:,2]-lo[2])<1e-6]
 if c['parent_component']=='quiet':
  side=-1 if 'left'in c['key']else 1;tris,names,sr=sources['AST-SAL-003'];part='quiet_book_'+str(side)+'_shelf_2';support=tris[names==part];distance=float(nearest_distances(bottom,support).max());xa,xb=(-2.91,-2.64)if side<0 else(2.64,2.91);margins=[float(lo[0]-xa),float(xb-hi[0]),float(1.336-hi[2])];wrong_shift_rejected=bool(hi[0]+.10>xb);passed=distance<.0002 and min(margins)>0 and wrong_shift_rejected;extra={'side_cheek_clearances_and_above_m':margins,'shifted_100mm_negative_control_rejected':wrong_shift_rejected}
 else:
  tris,names,sr=sources['AST-SAL-004'];part='actual_soil_contact_surface';support=tris[names==part];distance=float(nearest_distances(bottom,support).max());clear=bool(lo[1]>.70);passed=distance<.0002 and clear;extra={'all_native_foliage_bounds_behind_seat_space_Y_0p70':clear}
 rows.append({'context_key':c['key'],'actual_native_context':bind(p),'placement_source_m':c['local_source_translation_m'],'parent_source':{'path':sr['path'],'sha256':sr['sha256']},'named_physical_support':part,'base_vertices_checked':len(bottom),'maximum_support_distance_m':distance,'native_local_bounds_m':[lo.tolist(),hi.tolist()],'new_design_count':0,'passed':bool(passed),**extra})
res={'passed':all(x['passed']for x in rows),'scope':'Disclosed old-book subsets and botanical QA context, measured against actual new named component source surfaces; no host or actor fit.','evidence_at_check':bind(ap),'contexts':rows,'limits':'Finite root/base and bounded shelf/cheek screens, not handling/reach/load or horticultural certification.'}
(OUT/'independent_context_fit.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
