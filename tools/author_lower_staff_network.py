"""Fit bounded lower staff routes while preserving all existing slab owners."""
from pathlib import Path
import json
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/lower_staff_network/source/section_contract.json')
owner='port_forward_staff_network'
def rect(v):return box(v[0],v[2],v[1],v[3])
def ring(v):return [list(p) for p in v.coords[:-1]]
def author():
 c=json.loads(C.read_text());l=json.loads((R/'data/spatial_layout.json').read_text())
 l['regions']=[x for x in l['regions'] if x.get('authoring_owner')!=owner]
 l['voids']=[x for x in l['voids'] if x.get('authoring_owner')!=owner]
 originals=list(l['regions']);allowed={'D01_port_service_spine','D02_fusion_screened_service','D03_protected_crew_cover'}
 records=json.loads((R/'data/reference/directory_allocations.json').read_text())['records']+json.loads((R/'data/reference/D03_crew_envelopes.json').read_text())['records']
 shaft=rect(c['lift']['floor_shaft_exclusion']);overlaps=[]
 for d in c['decks']:
  deck='D%02d'%d['deck'];p=unary_union([Polygon(v) for v in d['floor_union_polygons_xz']])
  assert p.is_valid and p.geom_type=='Polygon'
  for old in originals:
   if old['deck']!=deck or old.get('offset_y',0)!=0:continue
   q=Polygon(old['boundary'],old.get('holes',[]));area=p.intersection(q).area
   if area>1e-6:
    assert old['id'] in allowed,('Unexpected floor overlap',old['id'],area)
    overlaps.append({'deck':deck,'preserved_owner':old['id'],'area_m2':area});p=p.difference(q)
   assert shaft.intersection(q).area<1e-6,('Shaft would cut existing floor',old['id'])
  # New threshold areas are the only intended programme-envelope intrusions.
  for record in records:
   if record.get('deck')!=d['deck']:continue
   area=p.intersection(box(record['x'][0],record['z'][0],record['x'][1],record['z'][1])).area
   assert area<1e-6 or (deck=='D03' and box(-54,-219,-48,-213).covers(p.intersection(box(record['x'][0],record['z'][0],record['x'][1],record['z'][1])))),record
  parts=list(p.geoms) if p.geom_type=='MultiPolygon' else [p]
  for i,part in enumerate(parts):
   l['regions'].append({'id':f'{deck}_port_forward_staff_floor_{i}','authoring_owner':owner,'deck':deck,'boundary':ring(part.exterior),'holes':[ring(x) for x in part.interiors],'priority':80,'thickness':.24,'render_cell_m':20,'material_role':'staff_floor','status':'Bounded service route under construction; no completed home, depot or full staff network claim'})
 l['voids'].append({'id':owner+'_lift','authoring_owner':owner,'decks':['D01','D02','D03'],'boundary':ring(shaft.exterior),'source':'Three-stop staff lift, with separate source-authored pit pan'})
 c['runtime_floor_owner']=owner;c['preserved_floor_overlaps']=overlaps
 (R/'data/architecture/LOWER_STAFF_NETWORK.json').write_text(json.dumps(c,indent=2)+'\n')
 (R/'data/spatial_layout.json').write_text(json.dumps(l,indent=2)+'\n')
 print(json.dumps({'new_regions':len(l['regions'])-len(originals),'preserved_overlaps':overlaps,'status':'Authored floor source; runtime acceptance pending'}))
if __name__=='__main__':author()
