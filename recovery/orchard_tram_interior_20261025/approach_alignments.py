"""Bounded route choices against an installed collision snapshot; no admission."""
from pathlib import Path
import importlib.util,json,sys
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2]
s=importlib.util.spec_from_file_location('retained',R/'recovery/tram_section_successor_20261023/author_section_r002.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
base=json.loads((R/'Game/orchard_tram_interior_20261025/r003/PLAN.json').read_text())
old=np.array(base['route_points_xz']);variants=[]
for crossing in [-290.,-294.,-298.,-302.,-306.]:
 north=a.screen.fillet([[-5.6,-315],[-5.6,crossing],[17.3,crossing],[17.3,-233.5]])
 route=np.vstack([old[old[:,1]<-315],north,old[old[:,1]>-233.5]])
 fit=a.PathFit(route);start=fit.nearest(np.array([-5.6,-315]));end=fit.nearest(np.array([-5.6,-205]))
 poses=[fit.fit(float(at)) for at in np.arange(start,end+.01,.25)]
 variants.append({'crossing_z':crossing,'route_points_xz':route.tolist(),'poses':poses,'interval':[start,end],'maximum_cross_slide_m':max(abs(p[i]) for p in poses for i in [4,7])})
out=R.parent/'Astraea-resume-20261025/orchard-approach-alignments-001.json';assert not out.exists()
out.write_text(json.dumps({'status':'unselected geometry queries only','variants':variants},separators=(',',':'))+'\n',encoding='utf-8')
print(json.dumps({'variants':len(variants),'queries':[len(v['poses']) for v in variants]}))
