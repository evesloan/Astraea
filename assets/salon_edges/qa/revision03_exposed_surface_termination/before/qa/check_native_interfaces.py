"""Native-file marker, bounds and deliberately blocked-control collision screen.
Static component proposal evidence only. Not a host route or engine physics test.
"""
import json,hashlib,importlib.util
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
from scipy.optimize import linprog
BASE=Path(__file__).resolve().parents[1];CAT=BASE.parents[1]
s=importlib.util.spec_from_file_location('salon_glb_reader',BASE/'qa/validate_glb.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r)
def nodes(doc):
 out={}
 def walk(i,parent):
  n=doc['nodes'][i];m=parent@r.matrix(n);out[n['name']]=(n,m)
  for c in n.get('children',[]):walk(c,m)
 for i in doc['scenes'][doc.get('scene',0)]['nodes']:walk(i,np.eye(4))
 return out
def overlap(lo,hi,sh):
 if sh['type']=='box':return bool(np.all(np.maximum(lo,sh['min_source_m'])<np.minimum(hi,sh['max_source_m'])))
 h=ConvexHull(sh['points_source_m']);return bool(linprog([0,0,0],A_ub=h.equations[:,:3],b_ub=-h.equations[:,3],bounds=list(zip(lo,hi)),method='highs').success)
coll=json.loads((BASE/'collision_proposals.json').read_text());records=[]
for mp in sorted(BASE.glob('AST-SAL-*.manifest.json')):
 rec=json.loads(mp.read_text());path=BASE/rec['export'];d,b=r.read(path);ns=nodes(d);markers=[];voids=[]
 for m in rec['physical_and_proposal_markers']:
  n,t=ns[m['name']];delta=float(np.linalg.norm(t[:3,3]-m['gltf_m']));wrong=float(np.linalg.norm(t[:3,3]-m['source_m']));markers.append({'name':m['name'],'kind':m['kind'],'native_gltf_m':t[:3,3].tolist(),'expected_gltf_m':m['gltf_m'],'position_error_m':delta,'wrong_unconverted_source_error_m':wrong,'passes':delta<1e-6})
 for v in rec['receiver_voids']:
  lo=np.array(v['min_source_m'])+1e-5;hi=np.array(v['max_source_m'])-1e-5;hits=[sh['name']for sh in coll[rec['catalogue_id']]['shapes']if overlap(lo,hi,sh)]
  # A deliberately wrong box fills this exact declared void. The algorithm must reject it.
  blocker={'type':'box','min_source_m':(lo-1e-4).tolist(),'max_source_m':(hi+1e-4).tolist()}
  control=overlap(lo,hi,blocker)
  voids.append({'name':v['name'],'compound_shape_intersections':hits,'clear_passes':not hits,'deliberately_filled_receiver_control_detected':control,'passes':not hits and control})
 shapes=coll[rec['catalogue_id']]['shapes'];first=next(sh for sh in shapes if sh['type']=='box');lo=np.array(first['min_source_m']);hi=np.array(first['max_source_m']);centre=(lo+hi)/2
 physical=overlap(centre-1e-4,centre+1e-4,first)
 native=r.validate(path);sb=rec['bounds_blender_z_up'];elo=np.array([sb['min_m'][0],sb['min_m'][2],-sb['max_m'][1]]);ehi=np.array([sb['max_m'][0],sb['max_m'][2],-sb['min_m'][1]])
 err=max(float(np.abs(np.array(native['bounds_gltf_y_up']['min'])-elo).max()),float(np.abs(np.array(native['bounds_gltf_y_up']['max'])-ehi).max()))
 comparison={'bounds_max_error_m':err,'triangle_count_equal':native['triangle_count']==rec['evaluated_triangles'],'roles_equal':sorted(x.replace('ASTRAEA_','')for x in native['material_roles'])==rec['material_roles'],'passes':err<1e-5 and native['triangle_count']==rec['evaluated_triangles']}
 row={'catalogue_id':rec['catalogue_id'],'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'native_marker_checks':markers,'collision_void_checks':voids,'source_export_comparison':comparison,'actual_occupied_shape_control':{'shape':first['name'],'probe_source_m':centre.tolist(),'blocked_detected':physical},'wrong_axis_negative_control_detected':any(m['wrong_unconverted_source_error_m']>.05 for m in markers),'passes':all(x['passes']for x in markers+voids)and comparison['passes']and physical}
 records.append(row)
report={'scope':'Actual native GLB hierarchy and compound collision-proposal checks, with filled-void and occupied-geometry controls; no real actor/cart or host acceptance','assets':records,'all_passed':all(r['passes']for r in records)}
(BASE/'qa/native_interfaces_and_voids.json').write_text(json.dumps(report,indent=2)+'\n');print('NATIVE_CHECKS',report['all_passed']);assert report['all_passed']
