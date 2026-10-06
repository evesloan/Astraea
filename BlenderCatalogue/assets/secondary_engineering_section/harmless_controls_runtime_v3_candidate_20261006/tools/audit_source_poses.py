#!/usr/bin/env python3
"""Exact frozen-GLB approach/camera screen, NOT a replacement for Godot physics.
Only the new cell model is present; whole-ship original-player acceptance is pending.
"""
from pathlib import Path
import json, math, numpy as np
from glb_geometry import glb, Query
ROOT=Path(__file__).resolve().parents[1]
MODEL=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/secondary_engineering_section/workbay_section_gate_v2_candidate_20261006/exports/AST-ENG-008_workbay_section_gate_v2.glb')

def closest_point_triangle(p,a,b,c):
    ab=b-a; ac=c-a; ap=p-a; d1=np.dot(ab,ap); d2=np.dot(ac,ap)
    if d1<=0 and d2<=0:return a
    bp=p-b; d3=np.dot(ab,bp);d4=np.dot(ac,bp)
    if d3>=0 and d4<=d3:return b
    vc=d1*d4-d3*d2
    if vc<=0 and d1>=0 and d3<=0:return a+ab*(d1/(d1-d3))
    cp=p-c;d5=np.dot(ab,cp);d6=np.dot(ac,cp)
    if d6>=0 and d5<=d6:return c
    vb=d5*d2-d1*d6
    if vb<=0 and d2>=0 and d6<=0:return a+ac*(d2/(d2-d6))
    va=d3*d6-d5*d4
    if va<=0 and d4-d3>=0 and d5-d6>=0:return b+(c-b)*((d4-d3)/((d4-d3)+(d5-d6)))
    den=va+vb+vc
    if abs(den)<1e-20:return min((a,b,c),key=lambda q:np.linalg.norm(p-q))
    return a+ab*(vb/den)+ac*(vc/den)

def segments_distance(p1,q1,p2,q2):
    d1=q1-p1;d2=q2-p2;r=p1-p2;a=np.dot(d1,d1);e=np.dot(d2,d2);f=np.dot(d2,r)
    if a<=1e-20 and e<=1e-20:return np.linalg.norm(p1-p2)
    if a<=1e-20:s=0;t=np.clip(f/e,0,1)
    else:
        c=np.dot(d1,r)
        if e<=1e-20:t=0;s=np.clip(-c/a,0,1)
        else:
            b=np.dot(d1,d2);den=a*e-b*b;s=np.clip((b*f-c*e)/den,0,1) if den>1e-20 else 0
            t=(b*s+f)/e
            if t<0:t=0;s=np.clip(-c/a,0,1)
            elif t>1:t=1;s=np.clip((b-c)/a,0,1)
    return np.linalg.norm((p1+s*d1)-(p2+t*d2))

def segment_triangle_distance(p,q,tri):
    a,b,c=tri;d=q-p;e1=b-a;e2=c-a;h=np.cross(d,e2);det=np.dot(e1,h)
    if abs(det)>1e-12:
        inv=1/det;s=p-a;u=np.dot(s,h)*inv;qq=np.cross(s,e1);v=np.dot(d,qq)*inv;t=np.dot(e2,qq)*inv
        if 0<=u<=1 and 0<=v and u+v<=1 and 0<=t<=1:return 0.
    return min(np.linalg.norm(p-closest_point_triangle(p,a,b,c)),np.linalg.norm(q-closest_point_triangle(q,a,b,c)),
               *(segments_distance(p,q,x,y) for x,y in ((a,b),(b,c),(c,a))))

def capsule_query(tri, owners, foot):
    p=foot+np.array([0,.3,0]);q=foot+np.array([0,1.5,0]);radius=.3
    lo=p-radius;hi=q+radius
    candidates=np.flatnonzero(np.all(tri.max(1)>=lo-1e-9,axis=1)&np.all(tri.min(1)<=hi+1e-9,axis=1))
    hits=[];minimum=math.inf
    for i in candidates:
        d=segment_triangle_distance(p,q,tri[i]);minimum=min(minimum,d)
        if d<radius-.001:hits.append({'mesh':owners[i],'distance_to_capsule_axis_m':float(d),'triangle_index':int(i)})
    return hits, None if math.isinf(minimum) else minimum

def main():
    # Unit witnesses for exact distance implementation.
    tri=np.array([[0,0,0],[1,0,0],[0,0,1.]])
    assert abs(segment_triangle_distance(np.array([.2,1,.2]),np.array([.2,2,.2]),tri)-1)<1e-9
    assert segment_triangle_distance(np.array([.2,-1,.2]),np.array([.2,1,.2]),tri)==0
    data=json.loads((ROOT/'data/ENGINEERING_CALIBRATION_DRAFT.json').read_text());g=glb(MODEL)
    assert g['sha256']==data['model_sha256']
    contacts=[m for m in g['meshes'] if m['extras'].get('collision_contract') in ('static_surface','contact_only_glass_26mm','stair_flight_contact','moving_door_leaf')]
    query=Query(contacts); triangles=query.tri;owners=np.array([query.meshes[int(i)]['node'] for i in query.owner])
    records=[]
    for r in data['controls']:
        eye=np.array(r['proposed_eye_xyz']);foot=np.array(r['proposed_approach_xyz']);target=np.array(r['target_center_xyz']);distance=np.linalg.norm(target-eye)
        direction=(target-eye)/distance;sphere_first=float(distance-r['target_radius_m'])
        hits=query.rays(eye,target);occluders=[h for h in hits if h['distance_m']<sphere_first-1e-5]
        body_hits,min_dist=capsule_query(triangles,owners,foot)
        # Original pose is used literally: feet at source-proposed XYZ, 1.8 m
        # capsule with center y=.9 and 1.65 m camera. No fly camera correction.
        pitch=math.atan2(direction[1],math.hypot(direction[0],direction[2]));yaw=math.atan2(-direction[0],-direction[2])
        records.append({'id':r['id'],'feet_xyz':foot.tolist(),'eye_xyz':eye.tolist(),'target_xyz':target.tolist(),
            'yaw_rad':yaw,'pitch_rad':pitch,'source_floor_owner':r['floor_owner'], 'eye_to_target_m':float(distance),
            'first_target_sphere_m':sphere_first,'within_original_2_5m_ray':sphere_first<2.5,'within_original_pitch_limit':abs(pitch)<=1.35,
            'source_fixed_contact_occluders':occluders,'source_capsule_penetrations':body_hits,
            'source_nearby_triangle_minimum_axis_distance_m':min_dist,
            'floor_support_and_walked_reachability':'UNRUN_REQUIRES_ORIGINAL_FULL_RUNTIME'})
    failures=[r['id'] for r in records if r['source_fixed_contact_occluders'] or r['source_capsule_penetrations'] or not r['within_original_2_5m_ray'] or not r['within_original_pitch_limit']]
    report={'status':'SOURCE_POSE_SCREEN_PASS' if not failures else 'SOURCE_POSE_SCREEN_BLOCKED','model_sha256':g['sha256'],
            'controls':120,'failed_ids':failures,'scope':'Only frozen new-cell GLB fixed contacts plus its closed leaf. No full-ship floors, old machinery, carts or physical walk executed. This is not engine QA.',
            'godot_executed':False,'original_player_loaded':False,'actual_engine_accepted':False,'poses':records}
    (ROOT/'reports/source_pose_screen.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'], len(failures),'failed of',len(records))
    for r in records:
        if r['id'] in failures:print(r['id'],'occluders',[(x['node'],x['distance_m']) for x in r['source_fixed_contact_occluders'][:3]],'capsule',[(x['mesh'],x['distance_to_capsule_axis_m']) for x in r['source_capsule_penetrations'][:3]])
if __name__=='__main__':main()
