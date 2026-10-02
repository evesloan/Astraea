"""Verify the bounded arrangement against native GLB nodes and current bytes."""
from pathlib import Path
import json,hashlib
import numpy as np
from independent_geometry import Native,C
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch06'
e=json.loads((OUT/'arrangement/evidence.json').read_text());instances={};files=[]
for r in e['imports']:
    path=ROOT/r['file'];n=Native(path);shift=np.asarray(r['source_position_m']);ports={}
    for i,node in enumerate(n.g.doc['nodes']):
        if not node.get('name','').startswith('PORT_'):continue
        x=node['extras'];p=n.world[i][:3,3]+C@shift
        ports[x['name']]={'native_position':p,'native_normal':np.array(x['normal_gltf_yup']),'extra':x}
    vs=n.tris.reshape(-1,3)@C+shift
    instances[r['name']]={'native':n,'source_position':shift,'ports':ports,'source_vertices':vs}
    files.append({'instance':r['name'],'path':r['file'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'arrangement_import_hash_current':hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256']})
seams=[]
for row in e['actual_mating_seams']:
    a,an=row['a'];b,bn=row['b'];A=instances[a]['ports'][an];B=instances[b]['ports'][bn]
    gap=np.linalg.norm(A['native_position']-B['native_position']);dot=A['native_normal']@B['native_normal'];ac=np.array(json.loads(A['extra']['bolt_centres_gltf_yup_m_json']))+C@instances[a]['source_position'];bc=np.array(json.loads(B['extra']['bolt_centres_gltf_yup_m_json']))+C@instances[b]['source_position'];phase=np.linalg.norm(ac[:,None,:]-bc[None,:,:],axis=2).min(axis=1).max()
    seams.append({'a':row['a'],'b':row['b'],'native_position_gap_m':float(gap),'native_normal_dot':float(dot),'native_six_bolt_phase_error_m':float(phase),'pass':bool(gap<1e-6 and abs(dot+1)<1e-6 and phase<1e-6)})
clear=[]
for r in e['maintenance_prisms']:
    lo=np.asarray(r['min_world_m']);hi=np.asarray(r['max_world_m']);hits=[]
    for name,data in instances.items():
        if name==r['owner']:continue
        v=data['source_vertices'];a=v.min(axis=0);b=v.max(axis=0)
        if np.all(np.minimum(b,hi)-np.maximum(a,lo)>0):hits.append(name)
    clear.append({'owner':r['owner'],'reservation':r['name'],'other_asset_aabb_overlaps':hits,'pass':not hits})
# Additional bounded service-space screens for the wheel and wall console.
for owner,lo,hi in [('valve',[.105,-.25,.25],[.545,.25,.75]),('console',[-.41,-1.048,-.45],[.41,-.25,.34])]:
    shift=instances[owner]['source_position'];lo=np.asarray(lo)+shift;hi=np.asarray(hi)+shift;hits=[]
    for name,data in instances.items():
        if name==owner:continue
        v=data['source_vertices'];a=v.min(axis=0);b=v.max(axis=0)
        if np.all(np.minimum(b,hi)-np.maximum(a,lo)>0):hits.append(name)
    clear.append({'owner':owner,'reservation':'proposed_control_approach','other_asset_aabb_overlaps':hits,'pass':not hits})
out={'files':files,'seams':seams,'service_reservations':clear,'numeric_pass':all(r['arrangement_import_hash_current'] for r in files) and all(r['pass'] for r in seams+clear),
     'method':'Independently resolve actual native GLB node transforms, then apply the documented arrangement translations in the GLB basis. Compare mating origins/normals/bolt phases. Separately screen other-asset bounds against proposed work reservations.',
     'scope':'Neutral component inspection assembly only. Not a ship room, real load/clearance certification, completed service network, fluid circuit, game scene or target-GPU acceptance.'}
(OUT/'independent_assembly_report.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
