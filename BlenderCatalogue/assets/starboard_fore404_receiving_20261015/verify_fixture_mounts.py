from pathlib import Path
import json
D=Path(__file__).parent;p=json.loads((D/'NATIVE_VERIFICATION.json').read_text());walls=[r for r in p['bounds']if r['name'].startswith('SFR_Edge')and r['name'].endswith('_Cove')];mounts=[]
for r in p['bounds']:
 if not r['name'].endswith('_WallBracket'):continue
 hits=[]
 for w in walls:
  lo=[max(r['min'][i],w['min'][i])for i in range(3)];hi=[min(r['max'][i],w['max'][i])for i in range(3)];dims=[hi[i]-lo[i]for i in range(3)]
  if min(dims)>1e-5:hits.append((w,lo,hi,dims))
 assert hits,r['name'];w,lo,hi,dims=max(hits,key=lambda h:h[3][0]*h[3][1]*h[3][2]);axis=min([0,2],key=lambda i:w['max'][i]-w['min'][i]);mounts.append({'fixture':r['name'],'wall':w['name'],'positive_overlap_xyz_m':dims,'all_positive_wall_pieces':[{'wall':h[0]['name'],'overlap_xyz_m':h[3]}for h in hits],'at':[(lo[i]+hi[i])/2 for i in range(3)],'query_axis':axis,'wall_bounds':[w['min'],w['max']]})
assert len(mounts)==3;(D/'FIXTURE_MOUNT_VERIFICATION.json').write_text(json.dumps({'status':'PASS_THREE_POSITIVE_WALL_MOUNTS','first_probe_single_panel_assumption_corrected':'First bracket spans two touching native wall panels. Both positive supports retained; no geometry change.','mounts':mounts},indent=2)+'\n');print('PASS_THREE_POSITIVE_WALL_MOUNTS')
