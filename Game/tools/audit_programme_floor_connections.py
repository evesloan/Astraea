"""Audit compiled floor connectivity to the installed central core.
This deliberately ignores wall/door clearances and does not certify a playable route.
"""
from pathlib import Path
import json,hashlib
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union,nearest_points
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text())
def target_geometry(source_record,ledger_record):
 historical=box(source_record['x'][0],source_record['z'][0],source_record['x'][1],source_record['z'][1])
 current=ledger_record.get('current_boundary_xz')
 if current is None:return historical,'historical_allocation',historical.area
 assert ledger_record.get('current_geometry_owner'),('Current boundary requires a geometry owner',source_record['programme_key'])
 target=Polygon(current)
 assert target.is_valid and not target.is_empty,('Invalid current boundary',source_record['programme_key'])
 return target,'adopted_current_geometry',historical.area

def build():
 source='data/generated/structural_meshes.json';compiled=read(source)
 layout=read('data/spatial_layout.json')
 contract=read('data/design_contract.json');directory=read('data/reference/directory_allocations.json')['records']
 elevations={d['deck_id']:d['floor_elevation_m']for d in contract['deck_datums']}
 ledger={r['programme_key']:r for r in read('data/programme_ledger.json')['destinations']}
 decks=[];records=[]
 for deck in contract['deck_datums']:
  d=deck['deck_id'];y=deck['floor_elevation_m']
  # A local mezzanine at another height cannot bridge a hole at this deck datum.
  regions=[r for r in compiled['regions']if abs(r['floor_y']-y)<1e-6]
  asset_floors=[]
  for r in layout['regions']:
   if not r.get('provided_by_asset')or abs(elevations[r['deck']]+r.get('offset_y',0)-y)>1e-6:continue
   shape=Polygon(r['boundary'],r.get('holes',[]))
   for v in layout['voids']:
    if r['deck']in v['decks']and v['id']not in r.get('void_exemptions',[]):shape=shape.difference(Polygon(v['boundary']))
   asset_floors.append(shape)
  floor=unary_union([Polygon(t)for r in regions for t in r['triangles']]+asset_floors)
  pieces=list(floor.geoms)if floor.geom_type=='MultiPolygon'else[floor]
  seed=Point(5.5,-100)
  selected=[p for p in pieces if p.buffer(1e-6).covers(seed)]
  assert len(selected)==1,(d,'Central core bypass must have one floor component')
  connected=selected[0]
  # Erosion excludes point/zero-width contacts, but is only a coarse floor-width probe.
  inset=floor.buffer(-.45,join_style=2)
  inset_pieces=list(inset.geoms)if inset.geom_type=='MultiPolygon'else[inset]
  safe=[p for p in inset_pieces if p.buffer(1e-6).covers(seed)]
  assert len(safe)==1,(d,'Central bypass must fit the floor-width probe')
  safe=safe[0]
  local=[]
  for r in directory:
   if f"D{r['deck']:02}"!=d:continue
   target,basis,historical_area=target_geometry(r,ledger[r['programme_key']])
   hit=connected.intersection(target)
   near,targetpoint=nearest_points(connected,target)
   width_hit=safe.intersection(target.buffer(-.45,join_style=2))
   item={'programme_key':r['programme_key'],'name':r['name'],'deck':d,'geometry_owner':ledger[r['programme_key']].get('current_geometry_owner'),'connected_floor_overlap_m2':round(hit.area,3),'allocation_area_m2':round(target.area,3),'target_boundary_basis':basis,'historical_allocation_area_m2':round(historical_area,3),'nearest_floor_gap_m':round(connected.distance(target),3),'nearest_floor_xz':[round(near.x,3),round(near.y,3)],'nearest_allocation_xz':[round(targetpoint.x,3),round(targetpoint.y,3)],'floor_width_probe_reaches_allocation':width_hit.area>1e-6,'status':'Connected structural floor intersects allocation'if hit.area>1e-6 else 'No connected structural floor within allocation','route_accepted':False}
   local.append(item);records.append(item)
  decks.append({'deck':d,'floor_y':y,'floor_components':len(pieces),'declared_asset_floor_regions':len(asset_floors),'central_connected_floor_area_m2':round(connected.area,3),'programmes':len(local),'with_connected_floor_overlap':sum(r['connected_floor_overlap_m2']>0 for r in local),'without_connected_floor_overlap':sum(r['connected_floor_overlap_m2']==0 for r in local)})
 assert len(records)==161 and len({r['programme_key']for r in records})==161
 return {'schema':1,'scope':'Targets use explicitly adopted current programme boundaries when present; otherwise preserved historical allocations. Compiled structural floor topology plus explicitly declared asset-owned floor footprints; the latter are not extracted mesh verification. Same-deck connectivity only; working inter-deck lifts may join otherwise separate components. Includes guest and staff surfaces without access classification; ignores walls, furniture, gates and exact cart shape. Absent recorded floor coverage needs construction or source reconciliation; it is not proof of missing runtime geometry. No route or finished-room acceptance.', 'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()for p in [source,'data/spatial_layout.json','data/reference/directory_allocations.json','data/programme_ledger.json']},'seed_xz':[5.5,-100],'floor_width_probe_radius_m':.45,'decks':decks,'programmes':records,'summary':{'all_programmes':len(records),'with_connected_floor_overlap':sum(r['connected_floor_overlap_m2']>0 for r in records),'without_connected_floor_overlap':sum(r['connected_floor_overlap_m2']==0 for r in records),'floor_width_probe_reaches':sum(r['floor_width_probe_reaches_allocation']for r in records),'fully_accepted_routes':0}}
if __name__=='__main__':
 result=build();(ROOT/'docs/PROGRAMME_FLOOR_CONNECTION_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['summary']))
