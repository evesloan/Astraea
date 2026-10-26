from pathlib import Path
import importlib.util,json,math,sys
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2]
s=importlib.util.spec_from_file_location('retained',R/'recovery/tram_section_successor_20261023/author_section_r002.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a)
base=json.loads((R/'Game/orchard_tram_interior_20261025/r003/PLAN.json').read_text(encoding='utf-8'));old=np.array(base['route_points_xz']);variants=[]
for radius in [4.5,5.0,5.1]:
 north=a.screen.fillet([[-5.6,-315],[-5.6,-290],[17.3,-290],[17.3,-233.5]])
 theta=math.acos(1-3.2/(2*radius));start=np.array([17.3,-233.5]);curve=[]
 for t in np.linspace(0,theta,33)[1:]:curve.append(start+np.array([radius*(1-math.cos(t)),radius*math.sin(t)]))
 half=start+np.array([radius*(1-math.cos(theta)),radius*math.sin(theta)])
 for t in np.linspace(0,theta,33)[1:]:curve.append(half+np.array([radius*(math.cos(theta-t)-math.cos(theta)),radius*(math.sin(theta)-math.sin(theta-t))]))
 end=np.array(curve[-1]);assert -222-end[1]>=4
 south=a.screen.fillet([end.tolist(),[20.5,-222],[-5.6,-222],[-5.6,-205]])
 route=np.vstack([old[old[:,1]<-315],north,np.array(curve),south[1:],old[old[:,1]>-205]])
 fit=a.PathFit(route);lo=fit.nearest(np.array([-5.6,-315]));hi=fit.nearest(np.array([-5.6,-205]))
 poses=[fit.fit(float(at)) for at in np.arange(lo,hi,.1)]
 variants.append({'crossing_z':radius,'meaning_of_label':'departure curve radius, north crossing stays -290','route_points_xz':route.tolist(),'poses':poses})
p=R.parent/'Astraea-resume-20261025/orchard-departure-alignments-001.json';assert not p.exists();p.write_text(json.dumps({'variants':variants},separators=(',',':'))+'\n',encoding='utf-8')
print('Prepared three complete approach/departure alignments')
