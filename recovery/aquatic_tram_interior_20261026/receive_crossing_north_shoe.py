"""Receive the single remaining shoe on the existing north arrival hanger."""
from pathlib import Path
import json,importlib.util,sys
import numpy as np
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[2];D=R/'Game/aquatic_tram_interior_20261026/r004'
spec=importlib.util.spec_from_file_location('author',R/'recovery/tram_section_successor_20261023/author_section_r002.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
r=json.loads((D/'ROUTE_SUPPORTS.json').read_text());assert len(r['unresolved'])==1
missing=r['unresolved'][0];assert missing['side']==1
fit=a.PathFit(np.array(json.loads((D/'PLAN.json').read_text())['route_points_xz']));q,t=fit.sample(missing['cursor']);assert 184<q[1]<186 and abs(q[0]-18.5)<1e-6
pad=np.array([21.1,188.25]);shoe=q+np.array([t[1],-t[0]])*1.48
a.beam('StationSharedNorthApproachShoe',[shoe[0],55.60,shoe[1]],[pad[0],55.60,pad[1]],.38,.19)
r['parts']+=a.parts;r['receivers'].append({'cursor':missing['cursor'],'leg':pad.tolist(),'pad':pad.tolist(),'owner':{'authored_member':'ArrivalHanger_0','receipt':'r002/RECEIVERS.json','shared_existing_source_bearing':True}});r['unresolved']=[]
out=D/'ROUTE_SUPPORTS_r002.json';assert not out.exists();out.write_bytes((json.dumps(r,separators=(',',':'))+'\n').encode());print('Received north shoe; source and unresolved first revision preserved')
