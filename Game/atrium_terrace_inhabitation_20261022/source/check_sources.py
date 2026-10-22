"""Focused retained-footprint, source-byte and headroom checks."""
import json,hashlib
from pathlib import Path
from shapely.geometry import Polygon,box
P=Path(__file__).resolve().parents[1];G=P.parent;R=G.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pre=json.loads((P/'evidence/PREREQUISITES.json').read_text());build=json.loads((P/'evidence/BUILD.json').read_text());ceiling=json.loads((P/'evidence/CEILING_BUILD.json').read_text());occupation=json.loads((P/'evidence/OCCUPANCY_REVIEW.json').read_text());regions=json.loads((G/'data/generated/structural_meshes.json').read_text())['regions'];checks=[]
def check(ok,label):checks.append({'pass':bool(ok),'label':label})
check(all(sha(G/f)==h for f,h in pre['source_pins'].items()),'Exact retained prerequisite hashes unchanged')
check(all(sha(R/'BlenderCatalogue'/a['source'])==a['source_sha256']for a in pre['assets'].values()),'All nine eligible original catalogue natives remain exact')
for b in [build,ceiling]:
 check(sha(R/b['native'])==b['native_sha256'],'Native saved bytes: '+b['native'])
 check(sha(G/b['runtime'])==b['runtime_sha256'],'Runtime export bytes: '+b['runtime'])
check(len(build['groups'])==40 and len(build['lights'])==80,'Forty composed groups and eighty attached fixture sources')
for group in build['groups']:
 plan=next(x for x in pre['groups']if x['name']==group['name']);lo,hi=group['bounds'];foot=box(lo[0],lo[2],hi[0],hi[2]);row=next(x for x in regions if x['id']==group['owner']);poly=Polygon(row['rings'][0],row['rings'][1:])
 check(poly.covers(foot),'All geometry supported by actual retained footprint: '+group['name'])
 check(lo[1]>=plan['y']-.001 and hi[1]<plan['y']+3.4,'Native baseline and overhead clearance: '+group['name'])
 clear=True
 for ob in occupation['obstacles'][str(plan['deck'])]:
  a,b=ob['bounds'];obstacle=box(a[0]-.1,a[2]-.1,b[0]+.1,b[2]+.1)
  if foot.intersects(obstacle):clear=False
 check(clear,'No intersection with recorded existing owner envelopes: '+group['name'])
 check(min(abs(lo[0]),abs(hi[0]))>=37.5 and max(abs(lo[0]),abs(hi[0]))<=45 and (hi[2]<-2.5 or lo[2]>2.5) and (hi[2]<40 or lo[2]>44)and(hi[2]<-44 or lo[2]>-40),'Preserved longitudinal aisles and transverse portals: '+group['name'])
check(ceiling['minimum_added_clearance_after']>3.96 and ceiling['minimum_added_clearance_after']>ceiling['minimum_added_clearance_before'],'Only added geometry raised; minimum D17 clearance improved beyond3.96m')
check(all(p['bounds'][0][0]>=-48.001 and p['bounds'][1][0]<=48.001 and p['bounds'][0][2]>=-64.001 and p['bounds'][1][2]<=64.001 and p['bounds'][1][1]<=106.26 for p in ceiling['parts']),'Ceiling stays within original cap footprint and underside')
check(not ceiling['protected_cap_changed'] and build['new_rooms_or_rests']==0 and build['new_catalogue_ids']==0,'Protected cap, IDs, capacity and original sources retained')
out={'checks':checks,'failures':sum(not x['pass']for x in checks),'scope':'Conservative source support/occupancy/route envelopes. No whole-ship or seating animation acceptance.'};(P/'evidence/SOURCE_CHECK.json').write_text(json.dumps(out,indent=2)+'\n');print('SOURCE_CHECK',len(checks),'failures',out['failures']);assert out['failures']==0
