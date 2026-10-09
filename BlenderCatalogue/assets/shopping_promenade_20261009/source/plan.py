"""Source-bound D09 allocation and additive floor proposals; no shared-file writes."""
from pathlib import Path
import json,sys,math
sys.path.insert(0,'C:/Users/cered/Dolphin/AstraeaTools/pythondeps')
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union,triangulate
P=Path(__file__).resolve().parents[1];D=P/'dependencies'
def load(n):return json.loads((D/n).read_text(encoding='utf-8'))
def write(n,d):
 p=P/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
atlas=load('DesignArchive/Planning/Supporting_Analyses/d09-retail-handoff/D09_atlas_vector_evidence.json')
coverage=load('DesignArchive/Planning/Supporting_Analyses/d09-retail-handoff/D09_exact_coverage_rows.json')
canonical={r['id']:r['name'] for r in coverage['rooms'] if r['id'].startswith('R')}
explicit={r['main_plan_evidence_key']:r['stable_id'] for r in atlas['explicitly_labelled_small_shops']}
layout=load('Game/data/spatial_layout.json');ship=load('Game/data/whole_ship_layout.json')
retained=[Polygon(r['boundary'],r.get('holes',[])) for r in layout['regions'] if r.get('deck')=='D09' and r.get('offset_y',0)==0]
voids=[Polygon(r['boundary']) for r in layout['voids'] if 'D09' in r.get('decks',[])]
blocked=unary_union(retained+voids);hull=Polygon(load('Game/data/hull_envelope.json')['plan_xz_m'])
floors=[];chunks=[];rooms=[];connectors=[];claimed=blocked
def polygons(g):
 if g.is_empty:return []
 return [g] if g.geom_type=='Polygon' else [p for s in g.geoms for p in polygons(s)]
def encode(poly):return {'boundary':list(poly.exterior.coords)[:-1],'holes':[list(x.coords)[:-1] for x in poly.interiors],'triangles_xz':[list(t.exterior.coords)[:3] for t in triangulate(poly) if poly.covers(t.representative_point()) and abs(t.intersection(poly).area-t.area)<1e-8]}
def floor(ident,geom,kind):
 global claimed
 shape=geom.difference(claimed)
 parts=polygons(shape);assert all(p.is_valid for p in parts)
 start=sum(r['chunk_id']==ident for r in floors)
 for i,p in enumerate(parts):
  if p.area<.001:continue
  floors.append(dict(id=ident+'__floor_'+str(start+i).zfill(2),chunk_id=ident,deck='D09',floor_y=52.5,thickness=.24,kind=kind,authoring_owner='shopping_promenade_20261009',priority=63,render_cell_m=16,**encode(p)))
 claimed=unary_union([claimed,shape]);return sum(p.area for p in parts)
banks=[-72,-100,72,100]
for bank,cx in enumerate(banks):
 slots=sorted([r for r in atlas['small_shop_footprints'] if r['allocation']['center_xz_m'][0]==cx],key=lambda r:r['allocation']['center_xz_m'][1])
 assert len(slots)==25
 for slot,r in enumerate(slots):
  proposed='R%03d'%(bank*25+slot+1);sid=explicit.get(r['evidence_key']);cz=r['allocation']['center_xz_m'][1]
  if sid:assert sid==proposed,'Proposal contradicts labelled evidence'
  sgn=(1 if cx>0 else -1)*(1 if abs(cx)==72 else -1)
  key='SHOP_D09_'+('P' if cx<0 else 'S')+str(abs(cx))+'_'+('F' if cz<0 else 'A')+str(abs(int(cz))).zfill(3)
  row={'chunk_id':key,'evidence_key':r['evidence_key'],'stable_room_id':sid,'proposed_room_id':proposed,'name':canonical[proposed],'identity_status':'explicit_atlas_join' if sid else 'proposed_only_requires_root_registry_join','position':[cx,52.5,cz],'front_sign_x':sgn,'allocation_x':r['allocation']['bounds_xz_m']['x'],'allocation_z':r['allocation']['bounds_xz_m']['z'],'door_world':[cx+sgn*6,52.5,cz],'public_door_clear_m':[3.6,3.8],'service_door_world':[cx-sgn*5.8,52.5,cz-3.5],'service_door_clear_m':[2.2,3.0],'ceiling_y_max':60.05,'family_index':(int(proposed[1:])-1)%10,'variation':(int(proposed[1:])-1)//10,'retained':proposed=='R070','activity_and_persistence':'Reserved interfaces only; no new inventory, purchase, identity migration or NPC occupancy','exports':{} if proposed=='R070' else {k:'exports/'+key+'__'+k+'.glb' for k in ['floor','shell','fitout']}}
  if proposed!='R070':floor(key,box(cx-6,cz-6,cx+6,cz+6),'shop_floor')
  rooms.append(row)
# Two public streets on each side, in bounded three-row courts. The gap at
# midship belongs to the retained salon/makers and atrium, not a new mall slab.
zs=sorted({r['position'][2] for r in rooms})
for side in [-1,1]:
 for segment,values in [('F',[z for z in zs if z<0]),('A',[z for z in zs if z>0])]:
  for j in range(0,len(values),3):
   v=values[j:j+3];a=v[0]-13 if j else v[0]-6;b=v[-1]+13 if j+3<len(values) else v[-1]+6
   # Exact butt joints halfway between adjacent rows, no coincident slabs.
   if j:a=(values[j-1]+v[0])/2
   if j+3<len(values):b=(v[-1]+values[j+3])/2
   key='COURT_D09_'+('P' if side<0 else 'S')+segment+'_'+str(j//3).zfill(2)
   geom=box(min(side*78,side*94),a,max(side*78,side*94),b)
   floor(key,geom,'public_street');chunks.append({'chunk_id':key,'kind':'court','position':[side*86,52.5,(a+b)/2],'bounds_xz':[[min(side*78,side*94),max(side*78,side*94)],[a,b]],'clear_through_x':[min(side*82,side*90),max(side*82,side*90)],'exports':{k:'exports/'+key+'__'+k+'.glb' for k in ['floor','shell','fitout']},'shop_chunks':[r['chunk_id'] for r in rooms if (r['position'][0]>0)==(side>0) and a<=r['position'][2]<=b],'purpose':['Continuous level public street','Profiled colonnade and open ceiling coffers','Recessed planted rest pockets clear of through route','Addressed frontage and court directions']})
  for lane,x0,x1 in [('inner',60.5,66),('outer',106,108)]:
   # Service floor is independently bounded to matching court lengths.
   for j in range(0,len(values),3):
    v=values[j:j+3];a=v[0]-6 if not j else (values[j-1]+v[0])/2;b=v[-1]+6 if j+3>=len(values) else (v[-1]+values[j+3])/2
    key='SERVICE_D09_'+('P' if side<0 else 'S')+segment+'_'+lane+'_'+str(j//3).zfill(2)
    geom=box(min(side*x0,side*x1),a,max(side*x0,side*x1),b);floor(key,geom,'service_street')
    chunks.append({'chunk_id':key,'kind':'service','position':[side*(x0+x1)/2,52.5,(a+b)/2],'bounds_xz':[[min(side*x0,side*x1),max(side*x0,side*x1)],[a,b]],'exports':{k:'exports/'+key+'__'+k+'.glb' for k in ['floor','shell']},'purpose':['Continuous rear stock/repair/delivery access','Opaque service edge and seated roof','No operational stocking or staff permissions implemented']})
 # Public links cross only empty gaps between allocated buildings and large rooms.
 for z,label in [(-379,'Orchard approach'),(-301,'Orchard Exchange and Food Hall'),(-145,'Forward shops'),(-69,'Atrium fore'),(69,'Atrium aft'),(145,'Aft shops'),(301,'Post parcels and Living Gifts'),(379,'Bakery and Companion Games approach')]:
  endz=372 if z==379 else z
  pts=[(side*4,z),(side*86,z)]
  if z==379:pts.append((side*86,endz))
  geom=LineString(pts).buffer(2.2,cap_style='flat',join_style='mitre')
  key='LINK_D09_'+('P' if side<0 else 'S')+str(z).replace('-','F')
  floor(key,geom,'public_connector');chunks.append({'chunk_id':key,'kind':'link','position':[side*45,52.5,z],'points_xz':pts,'exports':{k:'exports/'+key+'__'+k+'.glb' for k in ['floor','shell']},'purpose':[label,'4.4 m level public branch; intersects retained floors by ownership subtraction']})
  connectors.append({'id':key,'kind':'public','label':label,'route_xz':pts,'floor_y':52.5,'clear_width_m':4.4,'root_socket':'Existing D09 axial or atrium floor, butt connection at X +/-4 or +/-54','vertical_alternative':'Retain all existing public cores; Food Hall retains orchard_exchange_lift_001 and its switchback','activity':'Architectural proposal; exhaustive movement/cart acceptance deferred'})
 # Side-only staff cross-links join both rear service lanes around bank ends.
 for z in [-404,-69,69,378]:
  key='STAFFLINK_D09_'+('P' if side<0 else 'S')+str(z).replace('-','F')
  # Stay within the outer hull with a taper at the final aft link.
  outer=108 if z<300 else 106.6
  pts=[(side*60.5,z),(side*outer,z)];geom=LineString(pts).buffer(1.0,cap_style='flat',join_style='mitre')
  floor(key,geom,'service_connector');chunks.append({'chunk_id':key,'kind':'service_link','position':[side*84,52.5,z],'points_xz':pts,'exports':{k:'exports/'+key+'__'+k+'.glb' for k in ['floor','shell']},'purpose':['Side-local rear service crosslink','Service joins to ship risers remain root-owned sockets']})
  # Short rear lane end turns reach this connector without changing shop allocations.
  for x in [side*63.25,side*107]:
   edge=-398 if z==-404 else -74 if z==-69 else 74 if z==69 else 372
   endpoint=side*106.5 if z==378 and abs(x)>100 else x
   ext=LineString([(x,edge),(endpoint,z)]).buffer(1.0,cap_style='flat',join_style='mitre')
   floor(key,ext,'service_connector')
  connectors.append({'id':key,'kind':'service','route_xz':pts,'floor_y':52.5,'clear_width_m':2.0,'root_socket':'Rear district circuits are built. Shared ship staff riser routing/door permissions require root coordination; no new shaft.'})
large=[r for r in ship['programmes'] if r['deck']=='D09']
result={'schema':'astraea.shopping_promenade.construction.v1','datum_y':52.5,'maximum_local_height_m':7.55,'adjacent_D10_datum_y':61,'rooms':rooms,'chunks':chunks,'floor_proposals':floors,'connectors':connectors,'retained_large_destinations':large,'retained_room':'R070','identity_gate':{'proven_address_joins':16,'unproven_address_joins':84,'proposal':'Four banks ordered -72,-100,+72,+100; fore-to-aft25 rows per bank. This matches every labelled join but is not original registry evidence. Adopt only after explicit root reconciliation. Physical chunks use immutable footprint keys.'},'runtime_contract':{'shells':'Separate per-room bounded native mesh batches with actual aperture metadata','fitout':'Separate per-room static furnishing batches. Persistent/interactive stock must be separate owned nodes later. No entire-promenade merged mesh.','courts':'18 public chunks, each at most three rows/78 m plus16m width; service similarly bounded','activation':'Root may load a current room plus direct neighbours and current court; keep floor and contact resident before rendering/unloading. Hysteresis/streaming implementation is later root work.','visibility':'Glass excluded from opaque occluders; no occluders across portals, streets, protected voids or full AABBs.'},'unfinished':['84 exact registry joins','Root consolidated snapshot integration and floor compiler ownership adoption','Shared staff riser tie-ins/controlled doors','Transactions/persistent stock/player retail/commerce/NPCs','Exhaustive route, movement, cart, species, visual-quality and hardware passes']}
write('docs/PLACEMENT_AND_CONNECTORS.json',result)
checks=[]
for r in floors:
 poly=Polygon(r['boundary'],r.get('holes',[]));checks.append({'id':r['id'],'retained_overlap_m2':poly.intersection(blocked).area,'outside_plan_hull_m2':poly.difference(hull).area})
write('qa/plan_fit.json',{'rooms':len(rooms),'constructed_room_targets':sum(not r['retained'] for r in rooms),'labelled_address_matches':all(explicit.get(r['evidence_key'],r['proposed_room_id'])==r['proposed_room_id'] for r in rooms),'floor_rows':len(floors),'checks':checks,'passed':all(r['retained_overlap_m2']<1e-7 and r['outside_plan_hull_m2']<1e-7 for r in checks),'limits':'Plan hull only; per-height hull is not resolved in retained source. No exhaustive routes or current-cloud-parent collision certification.'})
print('SHOP_PLAN',len(rooms),len(chunks),len(floors))
if __name__=='__main__':assert all(r['retained_overlap_m2']<1e-7 and r['outside_plan_hull_m2']<1e-7 for r in checks),[r for r in checks if r['outside_plan_hull_m2']>1e-7]
