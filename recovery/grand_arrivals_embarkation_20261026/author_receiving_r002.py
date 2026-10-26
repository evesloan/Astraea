"""Authored grade/receiving successor. Preserve originals and production selection."""
import copy,hashlib,json,math,pathlib
R=pathlib.Path(__file__).resolve().parents[2];D=R/'Game/grand_arrivals_tram_20261026/r002'
assert not D.exists()
old=R/'Game/grand_arrivals_tram_20261026/r001/PLAN.json';plan=json.loads(old.read_text());points=plan['route_xyz']
def smooth(u):return u*u*(3-2*u)
def rise(z,lo,hi,ease,total):
 t=max(0,min(hi-lo,z-lo));L=hi-lo;g=total/(L-ease)
 if t<ease:return g*(t/2-ease*math.sin(math.pi*t/ease)/(2*math.pi))
 if t>L-ease:
  u=L-t;return total-g*(u/2-ease*math.sin(math.pi*u/ease)/(2*math.pi))
 return g*(t-ease/2)
start=next(i for i,p in enumerate(points) if abs(p[0]-5.6)<1e-7 and abs(p[2]+455)<1e-7)
end=next(i for i in range(start,len(points)) if points[i][2]>=450-1e-7)
for i in range(start,end+1):
 x,y,z=points[i];y=.1+rise(z,-410,-85,20,22.2)+rise(z,-36,410,10,33.8)
 # Pass the aquatic arrival at the centre of the existing public spine,
 # returning to the core's starboard leg before its north enclosure.
 if 125<z<165:x=5.6*(1-smooth((z-125)/40))
 elif 165<=z<=225:x=0
 elif 225<z<265:x=5.6*smooth((z-225)/40)
 points[i]=[x,y,z]
ascent=points[start:end+1]
grades=[abs(b[1]-a[1])/math.hypot(b[0]-a[0],b[2]-a[2]) for a,b in zip(ascent,ascent[1:])]
assert max(grades)<.08
floorpaths=['Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json']
floors=[(file,r) for file in floorpaths for r in json.loads((R/file).read_text())['regions']]
def area(p):return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))/2
def clip(poly,axis,bound,above):
 result=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=(a[axis]>=bound) if above else (a[axis]<=bound);ib=(b[axis]>=bound) if above else (b[axis]<=bound)
  if ia:result.append(a)
  if ia!=ib:
   f=(bound-a[axis])/(b[axis]-a[axis]);q=[a[j]+f*(b[j]-a[j]) for j in range(2)];q[axis]=bound;result.append(q)
 return result
def subtract(t,rect):
 inside=t;out=[]
 for axis,bound,above in [(0,rect[0],True),(0,rect[2],False),(1,rect[1],True),(1,rect[3],False)]:
  if not inside:break
  outside=clip(inside,axis,bound,not above)
  if len(outside)>2 and abs(area(outside))>1e-10:
   out.extend([[outside[0],outside[i],outside[i+1]] for i in range(1,len(outside)-1) if abs(area([outside[0],outside[i],outside[i+1]]))>1e-10])
  inside=clip(inside,axis,bound,above)
 removed=abs(area(inside)) if len(inside)>2 else 0
 return (out,removed) if removed>1e-10 else ([t],0)
def overlaps(t,rect):
 p=t
 for axis,bound,above in [(0,rect[0],True),(0,rect[2],False),(1,rect[1],True),(1,rect[3],False)]:
  p=clip(p,axis,bound,above)
  if not p:return False
 return abs(area(p))>1e-10
hits=[]
for file,f in floors:
 tri=f['triangles'];y=f['floor_y'];bottom=y-f.get('thickness',.24);vertices=[v for t in tri for v in t]
 if not vertices:continue
 bounds=[min(v[0] for v in vertices),min(v[1] for v in vertices),max(v[0] for v in vertices),max(v[1] for v in vertices)]
 witnesses=[]
 for x,py,z in points[:end+1]:
  if py-.6>y or py+4<bottom:continue
  rect=[x-2.8,z-2.8,x+2.8,z+2.8]
  if rect[2]<bounds[0] or rect[0]>bounds[2] or rect[3]<bounds[1] or rect[1]>bounds[3]:continue
  if any(overlaps(t,rect) for t in tri):witnesses.append([x,py,z])
 if witnesses:hits.append({'source':file,'floor':f['id'],'floor_y':y,'first_xyz':witnesses[0],'last_xyz':witnesses[-1],'samples':len(witnesses)})
preserved=['D06_atrium_circulation','D07_atrium_circulation','D06_authored_atrium_terrace','D07_authored_atrium_terrace','D08_gentle_waters_floor','D08_aquatic_district_arrival','D09_aft_midship_public_core_floor']
assert not set(preserved)&{h['floor'] for h in hits}, [h for h in hits if h['floor'] in preserved]
# Exact core receiver notch. It leaves the original staircase, lift openings
# and 4.7m west through-corridor unchanged; no new shaft or new core controller.
f=next(f for _,f in floors if f['id']=='D03_fore_midship_public_core_floor')
outer=f['rings'][0];z0=min(v[1] for v in outer);z1=max(v[1] for v in outer)
near=[p for p in ascent if p[1]+4.5>=f['floor_y']-f['thickness'] and p[1]-.7<=f['floor_y'] and z0-3<=p[2]<=z1+3]
rect=[3.6,max(z0,min(p[2] for p in near)-3),7.6,z1]
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
box('ForeMidD03_ReceivingWestLedger',[3.48,y-.30,(lo+hi)/2],[.24,.36,hi-lo],'champagne_metal','Under retained slab; outside 4m rail reservation; bearing/strength not certified')
box('ForeMidD03_ReceivingEastLedger',[7.70,y-.30,(lo+hi)/2],[.20,.36,hi-lo],'champagne_metal','Under retained outer sill; original enclosure remains')
lower=next(f for _,f in floors if f['id']=='D02_fore_midship_public_core_floor')
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
  box('ForeMidD03_'+side+'Bearing_'+str(i),[x,6.025,z],[.28,.05,.36],'champagne_metal','Exact D02 retained slab bearing; no strength certification')
  box('ForeMidD03_'+side+'ReceiverPost_'+str(i),[x,8.90,z],[.14,5.76,.14],'ivory_enamel','Continuous lower-slab-to-ledger receiver outside rail reservation')
box('ForeMidD03_WestGuardPlinth',[3.43,y+.08,(lo+hi)/2],[.18,.16,hi-lo],'warm_walnut','Closes access to narrow right-hand dead edge; west4.7m circulation retained')
box('ForeMidD03_WestGlassGuard',[3.43,y+.70,(lo+hi)/2],[.035,1.12,hi-lo],'ArrivalsArchitecturalGlass','Present glazed guard, no loss of required sightline')
box('ForeMidD03_WestGuardCap',[3.43,y+1.28,(lo+hi)/2],[.10,.08,hi-lo],'champagne_metal','Continuous guarded edge')
if rect[1]>z0:box('ForeMidD03_NorthGlassGuard',[5.52,y+.70,lo-.23],[4.26,1.12,.035],'ArrivalsArchitecturalGlass','Guard intact floor at start of the rail notch')
for i,z in enumerate([lo+.12,lo+(hi-lo)/3,lo+2*(hi-lo)/3,hi-.12]):box('ForeMidD03_WestGuardPost_'+str(i),[3.43,y+.65,z],[.08,1.3,.08],'champagne_metal','Guard support on preserved floor')
proof={'source':'Game/data/generated/structural_meshes.json','original_region':f,'replacement_region':after,'cut_rectangle_xz':rect,'removed_area_m2':removed,'unchanged_area_m2':after['structural_area_m2'],'preserved_lift_and_stair_rings':True,'west_clear_corridor_x':[-7.8,-3.1],'west_width_m':4.7,'lower_bearings':bearings,'status':'UNSELECTED_SOURCE_RECEIVER_NOT_INSTALLED','holds':['Exact retained core enclosure/fixture and stair-guard component sweep','Rail/support continuous swept fit','Complete linked-floor continuity and native/runtime verification','No production replacement until installed gate passes']}
plan.update(schema='astraea.grand_arrivals.lower_route.r002',status='AUTHORED_GRADE_BYPASS_AND_CORE_RECEIVING_UNSELECTED',route_xyz=points,maximum_grade=max(grades),route_length_m=sum(math.dist(a,b) for a,b in zip(points,points[1:])),source_screening={'scope':'Conservative sampled 5.6m-square, -.6..+4m reservation against original floor triangles, not complete vehicle/world acceptance','contacts':hits},profile_reason='Hold Y22.3 beneath the retained north atrium terrace, then rise through its actual void above the D06 south edge while staying below D07. Shift to spine centre around the aquatic arrival, returning at the Aft Midship core. Preserve these seven floor owners without cuts.',preserved_by_alignment=preserved,source_predecessor_sha256=hashlib.sha256(old.read_bytes()).hexdigest())
D.mkdir(parents=True)
for name,value in [('PLAN.json',plan),('CORE_RECEIVING.json',proof),('PARTS.json',parts)]: (D/name).write_bytes((json.dumps(value,indent=2)+'\n').encode())
print(json.dumps({'remaining_floor_owners':[h['floor'] for h in hits],'preserved_uncut':preserved,'grade':max(grades),'core_removed_m2':removed,'parts':len(parts),'core_notch':rect},indent=2))
