import copy,json,pathlib,ast,hashlib
R=pathlib.Path(__file__).resolve().parents[2];D=R/'Game/grand_arrivals_tram_20261026/r005'
assert not D.exists()
source=R/'recovery/grand_arrivals_embarkation_20261026/author_receiving_r002.py'
tree=ast.parse(source.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['area','clip','subtract','overlaps']],type_ignores=[]),str(source),'exec'))
floors=[('Game/data/generated/structural_meshes.json',f) for f in json.loads((R/'Game/data/generated/structural_meshes.json').read_text())['regions']]
f=next(f for _,f in floors if f['id']=='D05_primary_atrium_core_floor')
outer=f['rings'][0];z0=min(v[1] for v in outer);z1=max(v[1] for v in outer)
rect=[3.6,z0,7.6,z1]
assert rect[1]>=z0 and rect[1]<z1
after=copy.deepcopy(f);out=[];removed=0
for t in f['triangles']:
 pieces,a=subtract(t,rect);out.extend(pieces);removed+=a
assert abs(removed-(rect[2]-rect[0])*(rect[3]-rect[1]))<1e-7
after['triangles']=out;after['structural_area_m2']=sum(abs(area(t)) for t in out)
if rect[1]==z0:
 after['rings'][0]=[[-7.8,z0],[3.6,z0],[3.6,z1],[-7.8,z1]]
 after['rings'].append([[7.6,z0],[7.8,z0],[7.8,z1],[7.6,z1]])
else:after['rings'][0]=[[-7.8,z0],[7.8,z0],[7.8,z1],[7.6,z1],[7.6,rect[1]],[3.6,rect[1]],[3.6,z1],[-7.8,z1]]
assert area(after['rings'][0])>0
for chunk in after.get('render_chunks',[]):chunk['triangles']=[p for t in chunk['triangles'] for p in subtract(t,rect)[0]]
assert after['rings'][1:len(f['rings'])]==f['rings'][1:]
assert all(not overlaps(t,rect) for t in out)
parts=[]
def box(name,c,size,role,purpose):
 x,y,z=c;dx,dy,dz=[v/2 for v in size]
 vertices=[[x+a*dx,y+b*dy,z+c*dz] for a,b,c in [(-1,-1,-1),(1,-1,-1),(-1,1,-1),(1,1,-1),(-1,-1,1),(1,-1,1),(-1,1,1),(1,1,1)]]
 parts.append({'name':name,'vertices':vertices,'faces':[[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]],'material':role,'purpose':purpose})
lo=rect[1];hi=rect[3];y=f['floor_y']
box('PrimaryD05_ReceivingWestLedger',[3.48,y-.30,(lo+hi)/2],[.24,.36,hi-lo],'champagne_metal','Under retained slab; outside 4m rail reservation; bearing/strength not certified')
box('PrimaryD05_ReceivingEastLedger',[7.70,y-.30,(lo+hi)/2],[.20,.36,hi-lo],'champagne_metal','Under retained outer sill; original enclosure remains')
lower=next(f for _,f in floors if f['id']=='D04_primary_atrium_core_floor')
bearings=[]
for i,z in enumerate([lo+.35,lo+(hi-lo)/3,lo+2*(hi-lo)/3,hi-.35]):
 for side,x in [('West',3.45),('East',7.65)]:
  footprint=[x-.14,z-.18,x+.14,z+.18]
  overlap=0
  for triangle in lower['triangles']:
   poly=triangle
   for axis,bound,above in [(0,footprint[0],True),(0,footprint[2],False),(1,footprint[1],True),(1,footprint[3],False)]:
    poly=clip(poly,axis,bound,above)
    if not poly:break
   if poly:overlap+=abs(area(poly))
  assert abs(overlap-.28*.36)<1e-7,('Lower bearing not fully received',x,z,overlap)
  bearings.append({'side':side,'xz':[x,z],'source':lower['id'],'overlap_m2':overlap})
  box('PrimaryD05_'+side+'Bearing_'+str(i),[x,16.525,z],[.28,.05,.36],'champagne_metal','Exact D04 retained slab bearing; no strength certification')
  box('PrimaryD05_'+side+'ReceiverPost_'+str(i),[x,18.65,z],[.14,4.26,.14],'ivory_enamel','Continuous lower-slab-to-ledger receiver outside rail reservation')
box('PrimaryD05_WestGuardPlinth',[3.43,y+.08,(lo+hi)/2],[.18,.16,hi-lo],'warm_walnut','Closes access to narrow right-hand dead edge; west4.7m circulation retained')
box('PrimaryD05_WestGlassGuard',[3.43,y+.70,(lo+hi)/2],[.035,1.12,hi-lo],'ArrivalsArchitecturalGlass','Present glazed guard, no loss of required sightline')
box('PrimaryD05_WestGuardCap',[3.43,y+1.28,(lo+hi)/2],[.10,.08,hi-lo],'champagne_metal','Continuous guarded edge')
if rect[1]>z0:box('PrimaryD05_NorthGlassGuard',[5.52,y+.70,lo-.23],[4.26,1.12,.035],'ArrivalsArchitecturalGlass','Guard intact floor at start of the rail notch')
for i,z in enumerate([lo+.12,lo+(hi-lo)/3,lo+2*(hi-lo)/3,hi-.12]):box('PrimaryD05_WestGuardPost_'+str(i),[3.43,y+.65,z],[.08,1.3,.08],'champagne_metal','Guard support on preserved floor')
proof={'source':'Game/data/generated/structural_meshes.json','original_region':f,'replacement_region':after,'cut_rectangle_xz':rect,'removed_area_m2':removed,'unchanged_area_m2':after['structural_area_m2'],'preserved_lift_and_stair_rings':True,'west_clear_corridor_x':[-7.8,-3.1],'west_width_m':4.7,'lower_bearings':bearings,'status':'UNSELECTED_SOURCE_RECEIVER_NOT_INSTALLED','holds':['Exact retained core enclosure/fixture and stair-guard component sweep','Rail/support continuous swept fit','Complete linked-floor continuity and native/runtime verification','No production replacement until installed gate passes']}

D.mkdir(parents=True)
for name,value in [('CORE_RECEIVING.json',proof),('PARTS.json',parts)]: (D/name).write_text(json.dumps(value,indent=2)+'\n')
print(json.dumps({'parts':len(parts),'cut':rect,'removed_m2':removed,'bearings':len(bearings),'selected':False}))
