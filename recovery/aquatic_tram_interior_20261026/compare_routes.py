"""Decision-only alignments against the retained actual aquatic snapshot."""
from pathlib import Path
import json,sys,importlib.util
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('source',R/'recovery/tram_section_successor_20261023/author_section_r002.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base=json.loads((R/'Game/orchard_tram_interior_20261025/r006/PLAN.json').read_text());old=np.array(base['route_points_xz']);variants=[]
for x,entry,departure in [(18.5,160,248),(18.5,174,248),(18.5,160,288),(18.5,174,288),(17.3,174,248),(17.3,174,288)]:
 corners=[[-5.6,140],[-5.6,entry],[x,entry],[x,departure],[-5.6,departure],[-5.6,300]]
 segment=m.screen.fillet(corners,4.5);route=np.vstack([old[old[:,1]<140],segment,old[old[:,1]>300]])
 fit=m.PathFit(route);start=fit.nearest(np.array([-5.6,140]));end=fit.nearest(np.array([-5.6,300]))
 poses=[fit.fit(float(at))+[.25] for at in np.arange(start,end+.001,.1)]
 assert max(abs(p[i]) for p in poses for i in [4,7])<.2
 variants.append({'crossing_z':f'x{x}_in{entry}_out{departure}','route_points_xz':route.tolist(),'interval':[start,end],'poses':poses,'intended_station':'AFT_MIDSHIP','provisional_dock_xyz':[x,56.1,192]})
out=R.parent/'Astraea-resume-20261025/aquatic-route-options-001.json';assert not out.exists();out.write_text(json.dumps({'scope':'Unselected geometric comparison, no new station or source adoption','variants':variants})+'\n',encoding='utf-8');print(json.dumps({'variants':len(variants),'poses':sum(len(v['poses']) for v in variants)}))
