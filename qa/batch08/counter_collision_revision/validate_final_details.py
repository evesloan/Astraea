"""Focused original toe recess, floor, seam and version consistency checks."""
from pathlib import Path
import ast,json,hashlib,sys
import numpy as np
from scipy.spatial import ConvexHull
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'qa/batch07'))
from independent_geometry import Native,C
mod=ast.parse((OUT/'validate_collision_revision.py').read_text());selected=[n for n in mod.body if isinstance(n,ast.FunctionDef) and n.name in ['hulls','segment_hull','point_tri_distance','segment_tri_distance','shape_hits']];exec(compile(ast.Module(body=selected,type_ignores=[]),'geometry_helpers','exec'))
base=ROOT/'assets/hospitality_counters';cur=json.loads((base/'collision_proposals.json').read_text());old=json.loads((OUT/'original_inputs/assets/hospitality_counters/collision_proposals.json').read_text());tests=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for ident in cur:
 n=Native(base/'exports'/f'{ident}.glb');tri=n.tris@C;hs=hulls(cur[ident]);oh=hulls(old[ident]);m=json.loads((base/f'{ident}.manifest.json').read_text())
 points=([[.014,.324,.09],[2.386,.324,.09]] if ident.endswith('001') else [[.007,.324,.09],[.296,.613,.09]])
 for j,p in enumerate(points):
  a=np.array(p)-[0,0,.005];b=np.array(p)+[0,0,.005];radius=.010
  hits=shape_hits(hs,a,b,radius);old_hits=shape_hits(oh,a,b);d=segment_tri_distance(a,b,tri)
  tests.append({'name':ident+'_toe_recess_'+str(j),'source_segment_m':[a.tolist(),b.tolist()],'sphere_radius_m':radius,'actual_GLB_clearance_m':d,'new_hits':hits,'old_positive_control_hits':old_hits,'pass':not hits and d>radius and bool(old_hits)})
 for p in m['physical_contacts']:
  source=np.array(p['source_m']);hits=shape_hits(hs,source,source,radius=1e-7)
  tests.append({'name':ident+'_physical_contact_'+p['name'],'contact_numeric_tolerance_m':1e-7,'hits':hits,'pass':bool(hits)})
 pp=np.concatenate([h['v'] for h in hs]);tests.append({'name':ident+'_floor_and_top_datums','min_source_z_m':float(pp[:,2].min()),'max_source_z_m':float(pp[:,2].max()),'pass':abs(pp[:,2].min())<1e-7 and abs(pp[:,2].max()-.9)<1e-7})
 tests.append({'name':ident+'_manifest_shapes','pass':m['collision_proposal']['shape_count']==len(hs),'shapes':len(hs)})
 tests.append({'name':ident+'_original_visual_hashes','pass':m['source_sha256']==sha(base/'source'/f'{ident}.blend') and m['export_sha256']==sha(base/'exports'/f'{ident}.glb')})
a=np.concatenate([np.array(p['source_points_m']) for p in cur['AST-HSP-001']['proposals']]);b=np.concatenate([np.array(p['source_points_m']) for p in cur['AST-HSP-002']['proposals']]);gap=b[:,0].min()+2.4-a[:,0].max();tests.append({'name':'joined_counter_collision_seam','source_x_gap_m':float(gap),'pass':abs(gap-.002)<1e-6})
d=json.loads((base/'dependency_manifest.json').read_text())['collision_only_reproduction'];tests.append({'name':'dependency_receipt','pass':all(sha(ROOT/p['catalogue_relative_path'])==p['sha256'] for p in d['required_existing_inputs']) and sha(base/'collision_proposals.json')==d['output']['sha256']})
for t in tests:t['pass']=bool(t['pass'])
report={'pass':all(t['pass'] for t in tests),'checks':tests,'collision_sha256':sha(base/'collision_proposals.json')}
(OUT/'final_detail_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
