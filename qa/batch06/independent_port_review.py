"""Actual exported flange, bore, node-frame and mating-profile measurements."""
from pathlib import Path
import json,hashlib,itertools,sys
import numpy as np
from independent_geometry import Native,C
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch06'
paths=[Path(x).resolve() for x in sys.argv[1:]] if len(sys.argv)>1 else sorted((ROOT/'assets').glob('utility*/**/*.glb'))
rows=[];profiles=[];cache={}
for path in paths:
    n=Native(path);cache[path.stem]=n
    for i,node in enumerate(n.g.doc['nodes']):
        e=node.get('extras',{})
        if not node.get('name','').startswith('PORT_'):continue
        p=np.array(e['position_gltf_yup_m']);axis=np.array(e['normal_gltf_yup']);u=np.array(e['radial_zero_gltf_yup']);v=np.cross(axis,u)
        t=n.tris; local=t-p; s=local@axis;radial=np.linalg.norm(local-s[:,:,None]*axis,axis=2)
        front=(np.max(np.abs(s),axis=1)<1e-6)&(np.max(radial,axis=1)<.161)
        ft=t[front];fp=np.unique(np.round(np.column_stack([(ft-p).reshape(-1,3)@u,(ft-p).reshape(-1,3)@v]),6),axis=0)
        normals=np.cross(ft[:,1]-ft[:,0],ft[:,2]-ft[:,0]);normals/=np.linalg.norm(normals,axis=1)[:,None]
        bore=[]
        for r in [0,.04,.078]:
            for a in ([0] if r==0 else np.arange(12)*2*np.pi/12):
                q=p+r*(u*np.cos(a)+v*np.sin(a)); hits=n.segment_hits(q+axis*.02,q-axis*.115)
                bore.append({'radial_offset_m':float(r),'angle_rad':float(a),'hit_count':len(hits),'first_hit':hits[0] if hits else None})
        centres=np.asarray(json.loads(e['bolt_centres_gltf_yup_m_json']))
        holes=[len(n.segment_hits(q+axis*.002,q-axis*.004)) for q in centres]
        # Known occupied annular material and centreline are opposing controls.
        surface=p+u*.11;surface_test=n.nearest(surface);wrong=n.nearest(C.T@surface)
        annulus_hits=n.segment_hits(surface+axis*.002,surface-axis*.004)
        allnear=(radial<.161)&(s>-.058)&(s<.04);forward_max=float(s[allnear].max())
        row={'asset':path.stem,'node':node['name'],'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
             'native_marker_origin_m':n.world[i][:3,3].tolist(),'position_record_gltf_m':p.tolist(),
             'marker_position_error_m':float(np.linalg.norm(n.world[i][:3,3]-p)),
             'metadata_point_basis_error_m':float(np.linalg.norm(C@e['position_blender_source_m']-p)),
             'metadata_normal_basis_error':float(np.linalg.norm(C@e['normal_blender_source']-axis)),
             'metadata_radial_basis_error':float(np.linalg.norm(C@e['radial_zero_blender_source']-u)),
             'front_face_triangle_count':len(ft),'front_face_minimum_normal_dot_outward':float((normals@axis).min()),
             'front_face_radius_range_m':[float(radial[front].min()),float(radial[front].max())],
             'front_profile_vertex_count':len(fp),'front_profile_uv_points_m':fp.tolist(),
             'six_bolt_mouth_open_hit_counts':holes,'bore_samples':bore,
             'maximum_geometry_forward_of_face_m_in_flange_zone':forward_max,
             'annular_surface_witness':surface_test,'occupied_annulus_blocked_control_hit_count':len(annulus_hits),
             'wrong_axis_surface_control':{'wrong_point_native_m':(C.T@surface).tolist(),'distance_m':wrong['distance_m'],'detected':wrong['distance_m']>1e-4},
             'wrong_axis_note':'A port at the origin on X can be rotationally symmetric; only nondegenerate wrong-axis controls prove frame sensitivity.'}
        row['pass']=bool(row['marker_position_error_m']<1e-6 and row['metadata_point_basis_error_m']<1e-6 and row['metadata_normal_basis_error']<1e-6 and row['metadata_radial_basis_error']<1e-6 and np.all(np.array(holes)==0) and all(x['hit_count']==0 for x in bore) and len(annulus_hits)>0 and forward_max<1e-6 and row['front_face_minimum_normal_dot_outward']>.999 and surface_test['distance_m']<1e-6)
        rows.append(row);profiles.append((row,n,p,axis,u,v,fp,centres))
mates=[]
for a,b in zip(profiles,profiles[1:]):
    ar,an,ap,aa,au,av,af,ac=a;br,bn,bp,ba,bu,bv,bf,bc=b
    # Proper rigid mating transform: preserve radial zero and reverse normal.
    A=np.column_stack([au,av,aa]);B=np.column_stack([bu,bv,ba]);R=A@np.diag([1,-1,-1])@B.T;trans=ap-R@bp
    transformed=bc@R.T+trans
    hole_error=float(np.max(np.min(np.linalg.norm(ac[:,None,:]-transformed[None,:,:],axis=2),axis=1)))
    # Compare actual boundary samples with Hausdorff distance in mating plane.
    flipped=bf*np.array([1,-1]);d=np.linalg.norm(af[:,None,:]-flipped[None,:,:],axis=2)
    profile_error=float(max(d.min(axis=0).max(),d.min(axis=1).max()))
    mates.append({'a':ar['asset']+'/'+ar['node'],'b':br['asset']+'/'+br['node'],
                  'b_to_a_native_rotation':R.tolist(),'b_to_a_native_translation_m':trans.tolist(),
                  'rotation_determinant':float(np.linalg.det(R)),'opposed_normal_dot':float(aa@(R@ba)),
                  'actual_front_boundary_hausdorff_error_m':profile_error,'six_hole_phase_max_error_m':hole_error,
                  'pass':profile_error<2e-6 and hole_error<1e-6})
out={'method':'Read native actual GLB scene hierarchy and triangles; test 25 bore-path rays per port, six bolt-mouth rays, actual annular surface, and occupied-material negative control. Mating compares actual exported front boundary vertices after proper rigid transform.','ports':rows,'pairwise_mating_chain':mates,'all_port_checks_pass':all(r['pass'] for r in rows),'all_profile_mates_pass':all(r['pass'] for r in mates),'nondegenerate_wrong_axis_controls_detected':sum(r['wrong_axis_surface_control']['detected'] for r in rows),'limitations':['Bore rays prove sampled geometric opening through the flange/neck, not flow, pressure, valve actuation or engineering certification.','Mating compares artist-proposed component interfaces and no real hardware tolerance.','X-normal origin ports are symmetric under some wrong-axis tests; non-origin/turned-port controls supply axis sensitivity.']}
(OUT/'independent_port_report.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'ports':[{'asset':r['asset'],'node':r['node'],'pass':r['pass'],'bore_hits':sum(x['hit_count'] for x in r['bore_samples']),'front_forward_m':r['maximum_geometry_forward_of_face_m_in_flange_zone']} for r in rows],'mates':mates,'all_pass':out['all_port_checks_pass'] and out['all_profile_mates_pass']},indent=2))
