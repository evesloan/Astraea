"""Console actual-node points, controls, mount and hatch geometric screening."""
from pathlib import Path
import json,hashlib
import numpy as np
from independent_geometry import Native,C,rotate_axis
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch06'
path=ROOT/'assets/utility_console/AST-ENG-003.glb';n=Native(path)
m=json.loads((path.parent/'AST-ENG-003.manifest.json').read_text());byname={x.get('name'):i for i,x in enumerate(n.g.doc['nodes'])}
def descendants(i):
    out=[i]
    for ch in n.g.doc['nodes'][i].get('children',[]):out.extend(descendants(ch))
    return out
def split(i):
    ids=descendants(i);names=[n.g.doc['nodes'][x]['name'] for x in ids]
    mask=np.array([x not in names for x in n.nodes]);fixed=object.__new__(Native)
    fixed.tris=n.tris[mask];fixed.nodes=n.nodes[mask];fixed.materials=n.materials[mask]
    vs=np.concatenate([n.node_vertices[x] for x in ids if x in n.node_vertices]);vs=np.unique(np.round(vs,8),axis=0)
    sample=vs[np.linspace(0,len(vs)-1,min(96,len(vs))).astype(int)]
    return fixed,sample,names
controls=[]
for rec in m['controls']:
    i=byname[rec['node']];e=n.g.doc['nodes'][i]['extras'];p=n.world[i][:3,3];q=np.asarray(rec['interaction_gltf_yup_m']);axis=np.asarray(rec['axis_gltf_yup'])
    touch=n.nearest(q,node=rec['node']);wrong=n.nearest(rec['interaction_blender_source_m'],node=rec['node']);fixed,sample,names=split(i)
    correcthits=[];wronghits=[]
    if rec['kind']=='button':
        steps=[rec['max_travel_proposal_m']]
        for a,label,hits in [(axis,'correct',correcthits),(np.asarray(rec['axis_blender_source']),'wrong',wronghits)]:
            for v in sample:
                hh=fixed.segment_hits(v,v+a*steps[0])
                if hh:hits.append(hh[0])
    else:
        for a,hits in [(axis,correcthits),(np.asarray(rec['axis_blender_source']),wronghits)]:
            for sign in [-1,1]:
                old=sample
                extent=max(abs(x) for x in rec['detent_proposals_deg'])
                for angle in np.arange(10,extent+1,10)*sign:
                    cur=np.asarray([p+rotate_axis(v-p,a,np.radians(angle)) for v in sample])
                    for v0,v1 in zip(old,cur):
                        hh=fixed.segment_hits(v0,v1)
                        if hh:hits.append(hh[0])
                    old=cur
    axiskey='press_axis_gltf_yup' if rec['kind']=='button' else 'rotation_axis_gltf_yup'
    row={'node':rec['node'],'kind':rec['kind'],'actual_pivot_gltf_m':p.tolist(),'pivot_error_m':float(np.linalg.norm(p-rec['pivot_gltf_yup_m'])),
        'actual_node_axis':e[axiskey],'axis_basis_error':float(np.linalg.norm(C@rec['axis_blender_source']-e[axiskey])),
        'interaction_actual_mesh_witness':touch,'wrong_axis_contact_distance_m':wrong['distance_m'],
        'actual_mesh_vertices_sampled':len(sample),'motion':rec.get('max_travel_proposal_m',rec.get('detent_proposals_deg')),
        'correct_axis_fixed_hits':len(correcthits),'wrong_axis_fixed_hits':len(wronghits),'correct_first_hit':correcthits[:1],'wrong_first_hit':wronghits[:1]}
    row['pass']=bool(row['pivot_error_m']<1e-6 and row['axis_basis_error']<1e-6 and touch['distance_m']<1e-5 and wrong['distance_m']>1e-4 and not correcthits and wronghits)
    controls.append(row)
mounts=[]
for r in m['mounts']:
    p=np.array(r['point_gltf_yup_m']);w=n.nearest(p,role='staff_rubber');wrong=n.nearest(r['point_blender_source_m'],role='staff_rubber')
    i=byname[r['name']];mounts.append({'name':r['name'],'marker_error_m':float(np.linalg.norm(n.world[i][:3,3]-p)),'actual_surface':w,'expected_normal_gltf':r['normal_gltf_yup'],'normal_dot':float(np.dot(w['normal_gltf'],r['normal_gltf_yup'])),'wrong_axis_distance_m':wrong['distance_m'],'pass':bool(w['distance_m']<1e-6 and wrong['distance_m']>1e-4 and np.dot(w['normal_gltf'],r['normal_gltf_yup'])>.999)})
i=byname[m['service']['hatch_node']];fixed,sample,names=split(i);axis=np.array(m['service']['front_withdrawal_axis_gltf_yup']);forward=[];backward=[]
for v in sample:
    # Allow separation from the intentional gasket seat before withdrawal proof.
    hh=fixed.segment_hits(v+axis*.004,v+axis*.304)
    if hh:forward.append(hh[0])
    hh=fixed.segment_hits(v-axis*.004,v-axis*.304)
    if hh:backward.append(hh[0])
openray=fixed.segment_hits(C@np.array([0,-.23,-.247]),C@np.array([0,-.14,-.247]))
blocked=fixed.segment_hits(C@np.array([0,-.23,0]),C@np.array([0,-.14,0]))
hatch={'hierarchy_names':names,'all_three_material_groups_children':len(names)==4,'seat_separation_allowance_m':.004,'withdrawal_m':.30,'actual_vertices_sampled':len(sample),'outward_obstructions':len(forward),'wrong_inward_obstructions':len(backward),'first_outward_hit':forward[:1],'wrong_inward_first_hit':backward[:1],'exposed_bay_ray_hit_count':len(openray),'solid_face_negative_control_hit_count':len(blocked),'pass':bool(not forward and backward and not openray and blocked and len(names)==4)}
out={'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'controls':controls,'mounts':mounts,'hatch':hatch,'pass':all(r['pass'] for r in controls+mounts) and hatch['pass'],'limits':['Samples use actual GLB geometry and complete hierarchy; this is component-level finite sweep evidence, not an implemented controller or continuous collision guarantee.','Gasket seating overlap is intentional; hatch clearance starts after 4 mm separation.','Standing installation, species reach, wiring, mounting load and real safety/operating behavior remain proposals.']}
(OUT/'independent_console_report.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
