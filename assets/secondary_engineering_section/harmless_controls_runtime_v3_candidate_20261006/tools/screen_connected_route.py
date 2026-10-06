#!/usr/bin/env python3
"""New-GLB-only capsule screen of every proposed walk edge. Not full-world QA."""
from pathlib import Path
import json,math,numpy as np
from audit_source_poses import capsule_query,MODEL
from glb_geometry import glb,Query
R=Path(__file__).resolve().parents[1]
def main():
    data=json.loads((R/'data/ENGINEERING_CALIBRATION_DRAFT.json').read_text());route=json.loads((R/'data/ENGINEERING_CONTROLS_WALK_ROUTE_V3.json').read_text())
    g=glb(MODEL);assert g['sha256']==data['model_sha256']
    query=Query([m for m in g['meshes'] if m['extras'].get('collision_contract') in ('static_surface','contact_only_glass_26mm','stair_flight_contact','moving_door_leaf')])
    owners=np.array([query.meshes[int(i)]['node'] for i in query.owner]);prior=np.array(route['initial_supported_arrival_xyz']);rows=[];failed=[];samples=0;distance=0.
    for segment in route['segments']:
        stops=list(segment['waypoints_xyz'])+[x['proposed_approach_xyz'] for x in data['controls'] if x['panel']==segment['panel']]
        for target in stops:
            target=np.array(target);length=float(np.linalg.norm(target-prior));steps=max(1,math.ceil(length/.15));distance+=length
            for step in range(steps+1):
                point=prior+(target-prior)*step/steps;hits,_=capsule_query(query.tri,owners,point);samples+=1
                if hits:
                    failed.append({'panel':segment['panel'],'point_xyz':point.tolist(),'hits':hits[:5]});break
            rows.append({'panel':segment['panel'],'from_xyz':prior.tolist(),'to_xyz':target.tolist(),'sample_count':steps+1})
            prior=target
    result={'status':'NEW_GLB_ROUTE_SCREEN_PASS' if not failed else 'NEW_GLB_ROUTE_SCREEN_BLOCKED','failed':failed,'edges':len(rows),'capsule_samples':samples,'planned_path_length_m':distance,'segments':rows,
        'actual_main_scene_walking':'UNRUN','scope':'Only the new source GLB contacts; excludes old models, compiled floors and live actors. This cannot certify connected full-scene access.'}
    (R/'reports/source_connected_route_screen.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],'edges',len(rows),'samples',samples,'length_m',round(distance,3),'failures',len(failed))
    for fail in failed[:8]: print(fail)
if __name__=='__main__':main()
