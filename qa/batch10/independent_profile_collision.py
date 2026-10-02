"""Finite actual crown/rising-profile clearance measurements beyond rectangular voids."""
from pathlib import Path
import json,hashlib,sys,numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'qa/batch10'
sys.path.insert(0,str(ROOT/'qa/batch07'));from independent_geometry import Native,C
sys.path.insert(0,str(ROOT/'qa/batch08'));from independent_collision_geometry import Hull
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();base=ROOT/'assets/salon_threshold';cp=base/'collision_proposals.json';cr=json.loads(cp.read_text())['assets'];rows=[]
for ident in ['AST-SAL-001','AST-SAL-002']:
 gp=base/'exports'/(ident+'.glb');n=Native(gp);hs=[Hull(h['points_m'])for h in cr[ident]['hulls']];measurements=[];rays=[]
 xs=np.r_[-2.195,-2.19,-2.18,-2.16,-2.14,-2.12,-2.10,-2.08,-2.06,-1.,0,1.,2.06,2.08,2.10,2.12,2.14,2.16,2.18,2.19,2.195]if ident.endswith('001')else np.linspace(.015,2.385,65)
 ys=[.05,.64,1.23]if ident.endswith('001')else[.08,.64,1.2]
 for x in xs:
  for y in ys:
   a=np.array([x,y,2.7]);b=np.array([x,y,3.9]);hits=n.segment_hits(C@a,C@b);assert hits
   visual=min(h['fraction']for h in hits);compound=min((h.segment(a,b)[0]for h in hs if h.segment(a,b)is not None),default=None);assert compound is not None
   vz=a[2]+visual*(b[2]-a[2]);cz=a[2]+compound*(b[2]-a[2]);delta=vz-cz
   measurements.append({'source_xy_m':[float(x),float(y)],'actual_native_underside_z_m':float(vz),'compound_underside_z_m':float(cz),'clear_space_intrusion_m':float(delta),'inside_intentionally_filled_finish_channel':bool(ident.endswith('002')and .18<y<1.10)})
   # A bounded vertical segment strictly below the nearest measured profile and a crossing segment.
   for label,p,q,expected in [('clear_profile_offset',[x,y,min(vz,cz)-.045],[x,y,min(vz,cz)-.020],False),('blocked_profile_crossing',[x,y,min(vz,cz)-.020],[x,y,max(vz,cz)+.020],True)]:
    v=bool(n.segment_hits(C@p,C@q));h=any(s.segment(p,q)is not None for s in hs);rays.append({'name':label,'source_segment_m':[p,q],'visual_blocked':v,'compound_blocked':h,'expected_blocked':expected,'passed':v==expected and h==expected})
 row={'catalogue_id':ident,'native_glb_sha256':sha(gp),'collision_sha256':sha(cp),'profile_measurements':measurements,'finite_clear_and_blocked_controls':rays,'all_offset_clear_and_crossing_controls_pass':all(x['passed']for x in rays),'maximum_outside_finish_channel_intrusion_m':max(x['clear_space_intrusion_m']for x in measurements if not x['inside_intentionally_filled_finish_channel']),'maximum_intentional_channel_fill_m':max([x['clear_space_intrusion_m']for x in measurements if x['inside_intentionally_filled_finish_channel']]+[0])};rows.append(row)
res={'passed':all(x['all_offset_clear_and_crossing_controls_pass']for x in rows),'scope':'Finite native crown and variable cove underside probes, in addition to rectangular clear volumes. Intrusions are measured; intentional finish-channel filling is kept distinct.','assets':rows,'limits':['Profile-offset controls use20mm clearance outside measured occupied profiles, not boundary-perfect collision equivalence.','Curved primitive approximations and filled fixture channels are not actor/door sweep approval.']}
(OUT/'independent_profile_collision.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps([{k:v for k,v in x.items()if k not in ['profile_measurements','finite_clear_and_blocked_controls']}for x in rows],indent=2))
