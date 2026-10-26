"""Limited fore-spine edge receivers; preserve source and wider public passage."""
import ast,copy,hashlib,json,math,pathlib
R=pathlib.Path(__file__).resolve().parents[2];D=R/'Game/grand_arrivals_tram_20261026/r004'
assert not D.exists()
# Reuse the protected exact polygon operations, without invoking its authoring.
source=R/'recovery/grand_arrivals_embarkation_20261026/author_receiving_r002.py'
tree=ast.parse(source.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['area','clip','subtract']],type_ignores=[]),str(source),'exec'))
fpath=R/'Game/data/generated/structural_meshes.json';floors=json.loads(fpath.read_text())['regions']
planpath=R/'Game/grand_arrivals_tram_20261026/r002/PLAN.json';plan=json.loads(planpath.read_text());parts=[];receivers=[]
def box(name,lo,hi,role,purpose):
 x,y,z=lo;X,Y,Z=hi
 parts.append({'name':name,'vertices':[[x,y,z],[X,y,z],[x,Y,z],[X,Y,z],[x,y,Z],[X,y,Z],[x,Y,Z],[X,Y,Z]],'faces':[[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]],'material':role,'purpose':purpose})
for deck in ['D02','D03','D04','D05']:
 f=next(f for f in floors if f['id']==deck+'_fore_route');y=f['floor_y']
 pts=[p for p in plan['route_xyz'] if abs(p[0]-5.6)<1e-6 and -410<p[2]<-80 and p[1]-.7<=y and p[1]+4.5>=y-f['thickness']]
 rect=[3.6,min(p[2] for p in pts)-3,7.6,max(p[2] for p in pts)+3]
 after=copy.deepcopy(f);out=[];removed=0
 for t in f['triangles']:
  pieces,a=subtract(t,rect);out.extend(pieces);removed+=a
 after['triangles']=out;after['structural_area_m2']=sum(abs(area(t)) for t in out)
 for c in after.get('render_chunks',[]):c['triangles']=[p for t in c['triangles'] for p in subtract(t,rect)[0]]
 rings=[];segments=[]
 for ring in f['rings']:
  xs=[p[0] for p in ring];zs=[p[1] for p in ring];x0,x1,z0,z1=min(xs),max(xs),min(zs),max(zs)
  assert len(ring)==4 and x0==-4 and x1==4,'Do not rewrite nonrectangular original'
  lo=max(z0,rect[1]);hi=min(z1,rect[3])
  if hi<=lo:rings.append(ring);continue
  points=[[x0,z0],[x1,z0],[x1,lo],[3.6,lo],[3.6,hi],[x1,hi],[x1,z1],[x0,z1]]
  points=[p for i,p in enumerate(points) if p!=points[i-1]]
  # Remove collinear reversals when the notch reaches a boundary.
  if lo==z0:points=[[x0,z0],[3.6,z0],[3.6,hi],[x1,hi],[x1,z1],[x0,z1]]
  if hi==z1:points=[[x0,z0],[x1,z0],[x1,lo],[3.6,lo],[3.6,z1],[x0,z1]]
  if lo==z0 and hi==z1:points=[[x0,z0],[3.6,z0],[3.6,z1],[x0,z1]]
  points=[p for i,p in enumerate(points) if p!=points[i-1]];rings.append(points);segments.append([lo,hi])
  prefix=deck+'_ForeRailEdge_'+str(len(segments))
  box(prefix+'_Ledger',[3.18,y-.44,lo],[3.58,y-.24,hi],'champagne_metal','Continuous bearing beneath exact retained slab; strength certification not claimed')
  box(prefix+'_Plinth',[3.30,y,lo],[3.48,y+.16,hi],'warm_walnut','Solid guarded floor edge outside rail reservation')
  box(prefix+'_Glass',[3.405,y+.16,lo],[3.44,y+1.28,hi],'ArrivalsArchitecturalGlass','Continuous transparent guest protection')
  box(prefix+'_Cap',[3.37,y+1.28,lo],[3.47,y+1.36,hi],'champagne_metal','Continuous guard cap')
  for i in range(math.ceil((hi-lo)/3)+1):
   z=lo+.06+(hi-lo-.12)*i/math.ceil((hi-lo)/3)
   box(prefix+'_Post_'+str(i),[3.34,y-.24,z-.04],[3.50,y+1.36,z+.04],'champagne_metal','Guard post bears in retained slab, not invented floor')
  for end,z in [('North',lo),('South',hi)]:
   # Close only the 0.4m slab recess end; never bridge the vehicle corridor.
   if (end=='North' and lo==z0) or (end=='South' and hi==z1):continue
   box(prefix+'_'+end+'Return',[3.43,y,z-.04],[4,y+1.28,z+.04],'ArrivalsArchitecturalGlass','Close notch end on original slab')
 after['rings']=rings
 assert abs(sum(abs(area(q)) for q in rings)-after['structural_area_m2'])<1e-6
 assert abs(removed-.4*sum(hi-lo for lo,hi in segments))<1e-6
 assert abs(f['structural_area_m2']-after['structural_area_m2']-removed)<1e-6
 for lo,hi in segments:
  assert any(min(p[1] for p in ring)<=lo and max(p[1] for p in ring)>=hi for ring in f['rings'])
 receivers.append({'original_region':f,'replacement_region':after,'cut_rectangle_xz':rect,'segments_z':segments,'removed_m2':removed,'minimum_retained_public_width_m':7.3,'guard_bearing_x':[3.34,3.50],'scope':'Authored edge receiver, not full room-threshold or installed-route acceptance'})
 after['status']='Unselected graded-tram edge successor; room thresholds and installed checks held'
 vertices=[];faces=[]
 for tri in after['triangles']:
  i=len(vertices);vertices.extend([[x,y,z] for x,z in tri]);faces.append([i,i+1,i+2])
  i=len(vertices);vertices.extend([[x,y-f['thickness'],z] for x,z in reversed(tri)]);faces.append([i,i+1,i+2])
 for ring in rings:
  for a,b in zip(ring,ring[1:]+ring[:1]):
   i=len(vertices);vertices.extend([[a[0],y,a[1]],[b[0],y,b[1]],[b[0],y-f['thickness'],b[1]],[a[0],y-f['thickness'],a[1]]]);faces.append([i,i+1,i+2,i+3])
 parts.append({'name':deck+'_ExactForeFloorSuccessor','vertices':vertices,'faces':faces,'material':'warm_stone','purpose':'Exact original triangles outside 0.4m edge recess; all other slabs immutable'})
D.mkdir(parents=True)
receipt={'selected':False,'source_sha256':hashlib.sha256(fpath.read_bytes()).hexdigest(),'plan_sha256':hashlib.sha256(planpath.read_bytes()).hexdigest(),'receivers':receivers,'holds':['Native/runtime verification','Original vehicle/cart/door graded sweep','Full retained room threshold and side-link continuity','Primary core continuation and lower-hall receiving','Production integration and guest/visual acceptance']}
for name,value in [('RECEIVING.json',receipt),('PARTS.json',parts)]: (D/name).write_text(json.dumps(value,indent=2)+'\n')
print(json.dumps({'floors':len(receivers),'parts':len(parts),'removed_m2':sum(r['removed_m2'] for r in receivers),'selected':False}))
