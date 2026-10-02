"""Independent evaluated-source support termination and exported receiver checks."""
from pathlib import Path
import json,hashlib
import numpy as np
from independent_geometry import Native,C
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch06'
def source_asset(ident):
    data=np.load(OUT/('independent_source_geometry_'+ident+'.npz'))
    n=object.__new__(Native);n.tris=data['triangles'];n.nodes=data['object_names'];n.materials=n.nodes
    return n
def part(n,name):
    out=object.__new__(Native);mask=n.nodes==name;out.tris=n.tris[mask];out.nodes=n.nodes[mask];out.materials=n.materials[mask]
    assert len(out.tris),name
    return out
def cap_check(ident,support,finish,direction,high=True):
    s=source_asset(ident);v=np.unique(part(s,support).tris.reshape(-1,3),axis=0);d=np.asarray(direction,float);d/=np.linalg.norm(d)
    vdot=v@d;target=vdot.max() if high else vdot.min();v=v[np.abs(vdot-target)<1e-6];body=part(s,finish);rows=[]
    for p in v:
        r=body.nearest(p);signed=float(np.dot(p-r['point_gltf_m'],r['normal_gltf']));rows.append({'source_point_m':p.tolist(),'distance_to_finished_surface_m':r['distance_m'],'signed_nearest_surface_m':signed,'inside_finished_solid':signed<=1e-6})
    return {'asset':ident,'support':support,'finished_solid':finish,'terminal_cap_vertex_count':len(v),'checks':rows,'pass':len(v)>0 and all(r['inside_finished_solid'] for r in rows),'method':'Actual evaluated source cap vertices against oriented nearest triangles of the named finished solid; negative signed distance is inside material, including hollow-shell inner boundaries.'}
supports=[]
for x in [-.145,.145]:supports.append(cap_check('AST-ENG-001','pump_cast_mount_web_'+str(x),'cast_pump_chamber_with_open_X_bore',[0,0,1]))
for y in [.55,.87]:
    for x in [-.16,.16]:supports.append(cap_check('AST-ENG-001','motor_saddle_web_'+str((x,y)),'drive_motor_cast_housing',[0,0,1]))
for x in [-.134,.134]:supports.append(cap_check('AST-ENG-001','coupling_guard_standoff_'+str(x),'coupling_guard_skirt_'+str(x),[0,0,1]))
for x in [-.134,.134]:supports.append(cap_check('AST-ENG-001','coupling_guard_standoff_'+str(x),'load_crossmember_0.354',[0,0,1],False))
filter_manifest=json.loads((ROOT/'assets/utility_machines/AST-ENG-002.manifest.json').read_text())
for i,contact in enumerate(filter_manifest['floor_contacts']):
    p=contact['position_blender_source_m'];a=np.arctan2(p[1],p[0])
    direction=[(.267-.37)*np.cos(a),(.267-.37)*np.sin(a),.480-.055]
    supports.append(cap_check('AST-ENG-002','filter_splayed_closed_leg_'+str(i),'filter_hollow_formed_shell',direction))
for y in [-.115,.115]:
    for x in [-.075,.075]:supports.append(cap_check('AST-ENG-002','lid_handle_post_'+str((x,y)),'filter_removable_domed_lid',[0,0,1],False))
for side in [-1,1]:
    supports.append(cap_check('AST-ENG-006','closed_tapered_yoke_cheek_'+str(side),'bonnet_bolted_service_cover',[0,0,1],False))
    supports.append(cap_check('AST-ENG-006','closed_tapered_yoke_cheek_'+str(side),'yoke_upper_bridge',[0,0,1]))
receivers=[];floor=[];grips=[];service=[];files=[]
for ident in ['AST-ENG-001','AST-ENG-002']:
    path=ROOT/'assets/utility_machines/exports'/f'{ident}.glb';n=Native(path);m=json.loads((path.parents[1]/f'{ident}.manifest.json').read_text());files.append({'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    a,b=[np.array(p['position_gltf_yup_m']) for p in m['ports']];axis=(b-a)/np.linalg.norm(b-a);u=np.array([0,1,0]);v=np.cross(axis,u);rr=[]
    for rad in [0,.04,.075]:
        for ang in ([0] if rad==0 else np.arange(12)*np.pi/6):
            offset=rad*(u*np.cos(ang)+v*np.sin(ang));hits=n.segment_hits(a+offset-axis*.02,b+offset+axis*.02)
            rr.append({'radius_m':float(rad),'angle_rad':float(ang),'hit_count':len(hits),'first_hit':hits[:1]})
    # Same test deliberately in known pipe-wall material must be obstructed.
    blocked=n.segment_hits(a+u*.09-axis*.02,b+u*.09+axis*.02)
    receivers.append({'asset':ident,'sampled_rays':rr,'any_named_internal_obstruction':any(x['hit_count'] for x in rr),'occupied_pipe_wall_negative_control_hits':len(blocked),'pass':all(x['hit_count']==0 for x in rr) and bool(blocked),'interpretation':'These current designs have clear sampled straight sight rays into the receiving cavity. An intentional named impeller or cartridge could validly obstruct sight in a later design; this is not a requirement for an empty operating fluid path.'})
    for p in m['floor_contacts']:
        q=np.array(p['position_gltf_yup_m']);r=n.nearest(q,role='staff_rubber');wrong=n.nearest(p['position_blender_source_m'],role='staff_rubber')
        floor.append({'asset':ident,'name':p['name'],'actual_contact_distance_m':r['distance_m'],'wrong_axis_distance_m':wrong['distance_m'],'pass':r['distance_m']<1e-6 and wrong['distance_m']>1e-4})
    if ident=='AST-ENG-002':
        for p in m['service_and_connection_markers']:
            if p['name'].startswith('lid_handle_grip_point'):
                r=n.nearest(p['position_gltf_yup_m'],node='service_lid',role='staff_rubber');grips.append({'kind':p['kind'],'point':p['position_gltf_yup_m'],'distance_to_actual_grip_surface_m':r['distance_m'],'pass':p['kind']=='grip_centreline_proposal' and .0135<r['distance_m']<.0141})
    group='pump_service_cover' if ident=='AST-ENG-001' else 'service_lid';mask=np.array([group not in x for x in n.nodes]);fixed=object.__new__(Native);fixed.tris=n.tris[mask];fixed.nodes=n.nodes[mask];fixed.materials=n.materials[mask]
    if ident=='AST-ENG-001':
        mouth=fixed.segment_hits(C@np.array([0,-.34,.6]),C@np.array([0,-.03,.6]));blocked=fixed.segment_hits(C@np.array([.18,-.34,.6]),C@np.array([.18,-.03,.6]))
        service.append({'asset':ident,'removed_group':group,'central_exposed_service_aperture_hits':len(mouth),'adjacent_solid_shell_negative_control_hits':len(blocked),'pass':not mouth and bool(blocked)})
    else:
        mouth=fixed.segment_hits(C@np.array([0,0,1.65]),C@np.array([0,0,1.]));blocked=fixed.segment_hits(C@np.array([.27,0,1.65]),C@np.array([.27,0,1.]))
        service.append({'asset':ident,'removed_group':group,'open_top_cavity_hits':len(mouth),'rim_negative_control_hits':len(blocked),'pass':not mouth and bool(blocked)})
out={'support_caps':supports,'source_geometry_audits':[{'asset':ident,'source_sha256':json.loads((OUT/('independent_source_'+ident+'.json')).read_text())['sha256']} for ident in ['AST-ENG-001','AST-ENG-002','AST-ENG-006']],'receiver_geometry':receivers,'floor_contacts':floor,'filter_grips':grips,'opened_service_access':service,'actual_glb_files':files,'pass':all(x['pass'] for x in supports+receivers+floor+grips+service),'limits':['Component geometry only; support intersection/containment is not strength or certification.','Finite sampled receiver and service rays do not prove hydraulic function, operating state, continuous clearances or actor usability.','Fastener-thread/captive release mechanics and gasket compression are not modelled or certified.']}
(OUT/'independent_machine_report.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'support_results':[{'name':x['support'],'pass':x['pass']} for x in supports],'receivers':[{'asset':x['asset'],'pass':x['pass']} for x in receivers],'floor':floor,'grips':grips,'service':service,'pass':out['pass']},indent=2))
