exec(open('/workspace/astraea-integration-cutoff-20261013/arrivals_staff_receiving_20261015/verify_outside_geometry.py').read().split('a,ab=load')[0])
j,b=load(G/'assets/models/AST-STF-009_pool_market_home_equipment.glb');out=[]
for n in j['nodes']:
 if 'mesh'not in n:continue
 ps=np.concatenate([accessor(j,b,p['attributes']['POSITION'])for p in j['meshes'][n['mesh']]['primitives']]);T=np.array(n.get('translation',[0,0,0]));ps=ps+T;lo=ps.min(0);hi=ps.max(0)
 if np.all(hi>[-55.6,-.24,-444.3])and np.all(lo<[-53.7,3.5,-439.7]):
  ix=(ps[:,0]>-55.7)&(ps[:,0]<-53.6)&(ps[:,1]>-.3)&(ps[:,1]<3.6)&(ps[:,2]>-444.4)&(ps[:,2]<-439.6);q=ps[ix];out.append({'name':n['name'],'bounds':[lo.tolist(),hi.tolist()],'nearby_vertex_bounds':[q.min(0).tolist(),q.max(0).tolist()]if len(q)else[], 'translation':T.tolist()})
(D/'STAFF_ENCLOSURE_NEARBY_SOURCE_BOUNDS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
