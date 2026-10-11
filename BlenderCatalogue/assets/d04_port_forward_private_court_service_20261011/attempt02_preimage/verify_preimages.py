from pathlib import Path
import json,hashlib,numpy as np
W=Path(__file__).resolve().parent;R=W.parents[2];P=json.load(open(W/'PLAN.json'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reader=R/'BlenderCatalogue/assets/forward_staff_shaft_interfaces_20261010/source_geometry.py';ns={'__file__':str(reader)};exec(reader.read_text(),ns);T=ns['triangles'];cache={};rows=[]
for f,h in P['source_pins'].items():assert sha(R/f)==h,f
for r in P['preimages']:
 if r['model_file']not in cache:cache[r['model_file']]={n:t for n,t in T(r['model_file'])}
 q=r['preimage'];v=np.array(q['verts']);t=cache[r['model_file']][q['name']].reshape(-1,3)
 assert np.max(abs(t.min(0)-v.min(0)))<.00004 and np.max(abs(t.max(0)-v.max(0)))<.00004,q['name']
 successors=[p for p in P['successor_parts']if p['name'].startswith('D04PCS_'+q['name']+'_')]
 volume=0
 for s in successors:
  a=np.array(s['verts']);assert np.all(a.min(0)>=v.min(0)-1e-9)and np.all(a.max(0)<=v.max(0)+1e-9);volume+=np.prod(a.max(0)-a.min(0))
 x,X=r['opening_x'];y,Y=r['opening_y'];lo=v.min(0);hi=v.max(0);cut=(X-x)*(min(Y,hi[1])-max(y,lo[1]))*(hi[2]-lo[2]);assert abs(volume+cut-np.prod(hi-lo))<1e-7
 rows.append({'name':q['name'],'model_file':r['model_file'],'bounds_max_difference_m':float(np.max(abs(t.min(0)-v.min(0)))),'contained_successors':len(successors),'preimage_volume_m3':float(np.prod(hi-lo)),'opening_volume_m3':float(cut),'preserved_volume_m3':float(volume)})
units=P['all_twenty_allocations_unchanged'];assert len(units)==20 and sum(u['proposed_rest_place_count']for u in units)==25
from shapely.geometry import box
for b in P['bridges']:
 lo,hi=b['bounds'];foot=box(lo[0],lo[2],hi[0],hi[2])
 for u in units:assert foot.intersection(box(*[u['allocation_x'][0],u['allocation_z'][0],u['allocation_x'][1],u['allocation_z'][1]])).area<1e-9
report={'status':'PASS','preimages':rows,'protected_pin_count':len(P['source_pins']),'allocations':20,'reserved_rests':25,'new_floor_m2':P['new_floor_m2'],'home_allocation_overlap_m2':0,'production_active':False,'engineering_accepted':False,'court_audit':P['court_audit']}
(W/'PREIMAGE_SUPPORT.json').write_text(json.dumps(report,indent=2)+'\n');print('PRIVATE_COURT_PREIMAGES_PASS',len(rows))
