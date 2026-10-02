"""Actual native GLB wheel, grip and sampled sweep with wrong-axis controls."""
from pathlib import Path
import json,hashlib
import numpy as np
from independent_geometry import Native,C,rotate_axis
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch06'
path=ROOT/'assets/utility_pipework/exports/AST-ENG-006.glb';n=Native(path)
wi=next(i for i,x in enumerate(n.g.doc['nodes']) if x.get('name')=='VALVE_CONTROL_WHEEL')
wn=n.g.doc['nodes'][wi];e=wn['extras'];p=n.world[wi][:3,3];axis=np.asarray(e['wheel_axis_gltf_yup'])
grips=json.loads(e['grip_records_json']);gr=[]
for g in grips:
    q=np.asarray(g['position_gltf_yup_m']);got=n.nearest(q,role='staff_rubber',node='VALVE_CONTROL_WHEEL')
    wrong=n.nearest(g['position_blender_source_m'],role='staff_rubber',node='VALVE_CONTROL_WHEEL')
    gr.append({'name':g['name'],'native_point_m':q.tolist(),'source_basis_error_m':float(np.linalg.norm(C@g['position_blender_source_m']-q)),
               'surface_witness':got,'centreline_to_faceted_tube_surface_acceptance_m':[.014,.0151],
               'pass':.014<=got['distance_m']<=.0151,'wrong_axis_distance_m':wrong['distance_m'],
               'wrong_axis_detected':not .014<=wrong['distance_m']<=.0151})
vs=np.concatenate([n.node_vertices[c] for c in wn['children']]);vs=np.unique(np.round(vs,7),axis=0)
rad=vs-p;rad-=np.outer(rad@axis,axis);radius=np.linalg.norm(rad,axis=1)
# Axle/hub coupling is intentionally excluded; retain deterministic actual mesh
# vertices from every radius band and all six principal grip directions.
candidates=vs[radius>.046];take=np.linspace(0,len(candidates)-1,96).astype(int);sample=candidates[take]
st=object.__new__(Native);mask=np.array(['VALVE_CONTROL_WHEEL' not in x for x in n.nodes]);st.tris=n.tris[mask];st.materials=n.materials[mask];st.nodes=n.nodes[mask]
def posed(v,a,angle):return p+rotate_axis(v-p,a,angle)
def sweep(a):
    hits=[];minimum=float('inf');previous=sample.copy()
    for angle in np.arange(15,361,15):
        current=np.asarray([posed(v,a,np.radians(angle)) for v in sample])
        for ix,(q0,q1) in enumerate(zip(previous,current)):
            hh=st.segment_hits(q0,q1)
            if hh:hits.append({'angle_deg':int(angle),'sample_index':ix,'first_hit':hh[0]})
        previous=current
    return hits
correct=sweep(axis);wrong=sweep(np.array([0.,0,1.]))
# Actual first child vertex, expressed through both coordinate bases.
v=sample[-1];source=C.T@v;sp=np.array(e['pivot_blender_source_m']);angle=np.radians(37)
native_pose=posed(v,axis,angle);source_pose=sp+rotate_axis(source-sp,e['wheel_axis_blender_source'],angle)
out={'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'actual_wheel_pivot_native_m':p.tolist(),
     'pivot_metadata_error_m':float(np.linalg.norm(p-e['pivot_gltf_yup_m'])),
     'actual_wheel_bounds_blender_source':{'min_m':(vs@C).min(axis=0).tolist(),'max_m':(vs@C).max(axis=0).tolist()},
     'metadata':e,'grip_checks':gr,'same_signed_37deg_basis_pose_error_m':float(np.linalg.norm(native_pose-C@source_pose)),
     'wrong_native_Z_37deg_pose_error_m':float(np.linalg.norm(posed(v,[0,0,1],angle)-native_pose)),
     'sampled_surface_sweep':{'actual_vertices_sampled':len(sample),'pose_step_deg':15,'turn_degrees':360,'excluded_axis_coupling_radius_m':.046,
       'correct_axis_fixed_geometry_hit_count':len(correct),'correct_axis_hits':correct[:10],
       'wrong_axis_fixed_geometry_hit_count':len(wrong),'wrong_axis_hits':wrong[:10],
       'correct_axis_clear':not correct,'wrong_axis_blocked_control_detected':bool(wrong)},
     'limitations':['Finite actual-mesh vertex trajectories are a bounded geometric screen, not continuous collision proof or hand/actor usability.','Central axle coupling is deliberately excluded; it is a designed contact, not an obstruction.','No controller, opening-state mapping, fluid regulation or engineering rating is established.']}
out['pass']=bool(out['pivot_metadata_error_m']<1e-6 and out['same_signed_37deg_basis_pose_error_m']<1e-6 and all(g['pass'] and g['wrong_axis_detected'] for g in gr) and not correct and wrong)
(OUT/'independent_wheel_report.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['actual_wheel_bounds_blender_source','pivot_metadata_error_m','same_signed_37deg_basis_pose_error_m','wrong_native_Z_37deg_pose_error_m','sampled_surface_sweep','pass']},indent=2))
