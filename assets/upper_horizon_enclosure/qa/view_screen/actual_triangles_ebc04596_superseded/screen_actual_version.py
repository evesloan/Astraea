#!/usr/bin/env python3
"""Read-only actual Blender oriented-triangle optical screen for revised005+006.
Run after screen.py. Writes only sibling actual_triangles/ evidence.
"""
from pathlib import Path
import hashlib,itertools,json
import numpy as np
from screen import CAT,continuous_candidates,native,triangle_hits

ROOT=Path(__file__).resolve().parent
QA=CAT/'assets/upper_horizon_enclosure/qa'
OUT=ROOT/'actual_triangles';OUT.mkdir(exist_ok=True)
inputs=[QA/'actual_AST-CMD-005_triangles.json',QA/'actual_AST-CMD-006_triangles.json']
docs=[json.loads(p.read_text())for p in inputs]
sources=[CAT/'assets/aft_crown_platform/source/AST-CMD-005.blend',CAT/'assets/upper_horizon_enclosure/source/AST-CMD-006.blend']
exports=[CAT/'assets/aft_crown_platform/exports/AST-CMD-005.glb',CAT/'assets/upper_horizon_enclosure/exports/AST-CMD-006.glb']
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in inputs+sources+exports}
for d,p in zip(docs,sources):assert d['source_sha256']==hashes[str(p)],('Actual triangle/source hash mismatch',p)
assert hashes[str(sources[1])]=='ebc04596d9edc69a1ccc45d31fb76a37e42a0294a1c4b04f63963202c7b0f8e9'
assert hashes[str(exports[1])]=='64a0b8b22e2d0f61b64ac27f9f4b0bd1e9dd4e3b0af093319a0550e8803a9fef'
parts=[]
for d in docs:
    for p in d['parts']:
        v=np.array(p['vertices_world']);lo=v.min(axis=0);hi=v.max(axis=0)
        parts.append({**p,'world_aabb':[lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]],'actual_triangles':v[np.array(p['triangles'])]})
opaque=[p for p in parts if p['group']!='glass'];glass=[p for p in parts if p['group']=='glass']
tri=np.concatenate([p['actual_triangles']for p in parts]);owners=[p['name']for p in parts for _ in p['triangles']]
base=json.loads((ROOT/'revised005/results.json').read_text());rays=np.load(ROOT/'revised005/rays.npz')
result={'status':'PASS: actual source triangle/envelope optical screen for specified targets and eyes only; runtime/visual/route and final-stage acceptance remain pending','input_sha256':hashes,'actual_source_part_counts':[len(d['parts'])for d in docs],'actual_triangle_count':len(tri),'opaque_part_count':len(opaque),'glass_part_count':len(glass),'baseline_result_sha256':hashlib.sha256((ROOT/'revised005/results.json').read_bytes()).hexdigest(),'method':'AABBs computed directly from actual Blender world vertices cull against continuous complete target cones over eye boxes. Any surviving opaque candidate is tested by oriented double-sided Moller-Trumbore triangle intersections. Every sampled target ray is also tested against actual protective glass triangles and must traverse its two physical faces. Whole-box zero-candidate proof covers all intermediate rays and eyes, beyond samples. Glass is expected optically transmitting; no collision-layer exemption is asserted.','screens':[],'witness_rays':[],'failures':[]}
saved_eyes={}

def many_hits(eye,ds,ts):
    first=np.full(len(ds),np.inf);last=np.full(len(ds),-np.inf);count=np.zeros(len(ds),dtype=int)
    for t in ts:
        e1=t[1]-t[0];e2=t[2]-t[0];h=np.cross(ds,e2);a=h@e1
        valid=np.abs(a)>1e-12;f=np.zeros(len(ds));f[valid]=1/a[valid];s=eye-t[0];u=f*(h@s);q=np.cross(s,e1);v=f*(ds@q);distance=f*np.dot(e2,q)
        hit=valid&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(distance>1e-8)
        count[hit]+=1;first[hit]=np.minimum(first[hit],distance[hit]);last[hit]=np.maximum(last[hit],distance[hit])
    return first,last,count

for side,f in base['features'].items():
    s=1 if side=='starboard'else-1;eye=f['eye_box'];positive=rays[side+'_positive_directions']
    eye_groups=[('standing',eye)]+[(f'seated_{h:.2f}',{**eye,'y':[h,h]})for h in [107.55,107.65,107.75]]
    target_specs=[('complete_above_horizon',positive,f['positive_target_p'],f['positive_target_q'])]
    if side=='port':
        ex=f['full_support_extrema'];target_specs.append(('complete_local_port_footprint',rays[side+'_full_directions'],[ex['p_min']['value'],ex['p_max']['value']],[ex['q_min']['value'],ex['q_max']['value']]))
    glasspart=[p for p in glass if side.title() in p['name'] and '_LowBay_Glass' in p['name']];assert len(glasspart)==1
    for group,eb in eye_groups:
        eyes=np.array([[s*x,y,z]for x,y,z in itertools.product(*[np.unique(np.linspace(*eb[k],3))for k in ['abs_x','y','z']])]);saved_eyes[side+'_'+group]=eyes
        for target,ds,pp,qq in target_specs:
            oc=continuous_candidates(opaque,eb,s,pp,qq);gc=continuous_candidates(glass,eb,s,pp,qq)
            assert {p['name']for p in gc}=={glasspart[0]['name']},('Unexpected extra glazing in target cone',side,group,target,gc)
            row={'side':side,'eye_group':group,'target':target,'eye_box':eb,'opaque_continuous_candidates':[p['name']for p in oc],'glass_continuous_candidates':[p['name']for p in gc],'eye_count':len(eyes),'direction_count':len(ds),'tested_eye_ray_pairs':len(eyes)*len(ds),'sample_opaque_hit_count':0,'glass_missed_rays':0,'glass_two_face_failures':0,'first_hit_distance_range':[float('inf'),0],'glass_ray_path_length_range':[float('inf'),0]}
            for eye in eyes:
                for cp in oc:
                    part=next(p for p in opaque if p['name']==cp['name']);_,_,hits=many_hits(eye,ds,part['actual_triangles']);count=int((hits>0).sum());row['sample_opaque_hit_count']+=count
                    if count and len(result['failures'])<20:
                        i=int(np.flatnonzero(hits>0)[0]);result['failures'].append({'side':side,'group':group,'target':target,'eye':eye,'direction':ds[i],'part':part['name'],'hits':triangle_hits(eye,ds[i],part['actual_triangles'],[part['name']]*len(part['triangles']))})
                a,b,n=many_hits(eye,ds,glasspart[0]['actual_triangles']);miss=n==0;two=(n<2)|((b-a)<.059)
                row['glass_missed_rays']+=int(miss.sum());row['glass_two_face_failures']+=int(two.sum())
                if np.any(~miss):
                    row['first_hit_distance_range'][0]=min(row['first_hit_distance_range'][0],float(a[~miss].min()));row['first_hit_distance_range'][1]=max(row['first_hit_distance_range'][1],float(a[~miss].max()))
                    paths=b[~miss]-a[~miss];row['glass_ray_path_length_range'][0]=min(row['glass_ray_path_length_range'][0],float(paths.min()));row['glass_ray_path_length_range'][1]=max(row['glass_ray_path_length_range'][1],float(paths.max()))
            row['pass']=not oc and row['sample_opaque_hit_count']==0 and row['glass_missed_rays']==0 and row['glass_two_face_failures']==0
            if not row['pass']:result['failures'].append({'screen':row})
            result['screens'].append(row)
for w in base['witness_rays']:
    e=np.array(w['eye']);d=np.array(w['direction']);hits=triangle_hits(e,d,tri,owners)
    result['witness_rays'].append({'name':w['name'],'eye':e,'direction':d,'actual005_006_hits':hits,'expected_outcome':'Optically ignore hits on exactly named Glass source parts; remaining hits are genuine framing/opaque limitations. Some witnesses are intentionally out of the accepted target or eye boxes.'})
result['input_unchanged_during_check']=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items())
result['total_tested_eye_ray_pairs']=sum(x['tested_eye_ray_pairs']for x in result['screens'])
result['all_pass']=not result['failures'] and result['input_unchanged_during_check']
result['limits']=['Glass is counted as an intended transparent passage. Material readability, optical response and collision barrier behavior need runtime evidence.','Future massing/roof results are the separate unchanged envelope assumptions in revised005/results.json; actual006 pass does not establish installed final-hull geometry.','Full above-horizon starboard cap/halo and port crescent pass; a full primary planet and all negative rays do not.','Standing and seated eye boxes are optical stations, not furniture/body-fit or route acceptance.','This is no Godot/rendering or full-suite validation; the root owns those gates.']
np.savez_compressed(OUT/'eyes.npz',**saved_eyes)
(OUT/'results.json').write_text(json.dumps(result,indent=2,default=native)+'\n')
print(json.dumps({'all_pass':result['all_pass'],'screens':len(result['screens']),'eye_ray_pairs':result['total_tested_eye_ray_pairs'],'opaque_hits':sum(x['sample_opaque_hit_count']for x in result['screens']),'glass_misses':sum(x['glass_missed_rays']for x in result['screens']),'glass_two_face_failures':sum(x['glass_two_face_failures']for x in result['screens']),'results':str(OUT/'results.json')},indent=2))
assert result['all_pass'],result['failures'][:5]
