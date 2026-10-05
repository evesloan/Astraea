"""Extend the actual commons ownership in section; preserve all guest envelopes."""
from pathlib import Path
import json
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
base=json.loads((R/'data/architecture/D13_D14_starboard_commons.json').read_text());layout=json.loads((R/'data/spatial_layout.json').read_text());census=json.loads((R/'data/reference/historical_guest_census.json').read_text())['guest_envelopes'];outer=Polygon(base['envelope_xz_m']);lift=Polygon(base['lift']['floor_hole_xz_m'])
east_hole=box(86.10,4.72,90.82,11.42);west_hole=Polygon(base['upper_stair_void_xz_m'])
main={15:Polygon([(72,-6),(76,-8),(83.5,-6),(85.5,-1),(81.5,2),(74,1)]),16:Polygon([(75,-3),(83.5,-4),(86.3,0),(84.8,7.8),(79,10),(73,6),(73,0)]),17:Polygon([(70,-5),(73,-8),(80,-6),(83,0),(80,6),(73,7),(69.5,3)])}
arrivals={15:[[50,0],[54,0],[59,9.5],[63,9.5]],16:[[50,0],[63,0]],17:[[50,0],[54,0],[59,-11.8],[63,-11.8]]}
def encode(g):
 assert g.is_valid and g.geom_type=='Polygon'
 triangles=constrained_delaunay_triangles(g)
 assert abs(sum(t.area for t in triangles.geoms)-g.area)<1e-6
 return {'boundary':[list(p)for p in g.exterior.coords[:-1]],'holes':[[list(p)for p in h.coords[:-1]]for h in g.interiors],'triangles':[[list(p)for p in t.exterior.coords[:3]]for t in triangles.geoms]}
records=[];regions=[]
for deck,y in [(15,93),(16,97.5),(17,102)]:
 stair=west_hole if deck==16 else east_hole
 connector=box(72.8,-3.5,75.5,-1.5) if deck==16 else Polygon()
 void=unary_union([main[deck],stair,connector,lift])
 footprint=outer.union(LineString(arrivals[deck]).buffer(2.2,cap_style='flat',join_style='mitre'))
 for room in census:
  if room['deck']==deck:assert footprint.intersection(box(room['x'][0],room['z'][0],room['x'][1],room['z'][1])).area<1e-6
 shape=footprint.difference(void);data=encode(shape)
 record={'deck':'D'+str(deck),'floor_y':y,'programme_key':'D%d_directory_04'%deck,'arrival':arrivals[deck],'main_void':[list(p)for p in main[deck].exterior.coords[:-1]],'stair_hole':[list(p)for p in stair.exterior.coords[:-1]],**data};records.append(record)
 regions.append({'id':'D%d_starboard_house_extension'%deck,'authoring_owner':'starboard_house_extension','deck':'D'+str(deck),'boundary':data['boundary'],'holes':data['holes'],'priority':65,'thickness':.24,'programme_owner':record['programme_key'],'status':'Reviewed allocation; upper house geometry, access and final art under integration'})
regions.append({'id':'D18_starboard_house_cover','authoring_owner':'starboard_house_extension','deck':'D18','boundary':base['envelope_xz_m'],'priority':-10,'thickness':.24,'programme_owner':'D18_directory_06','walkable_public':False,'status':'Opaque house cover and future Bridge briefing floor substrate only; no new D18 programme or access claim'})
layout['regions']=[r for r in layout['regions'] if r.get('authoring_owner')!='starboard_house_extension']+regions
extension={'id':'D13_D17_starboard_house_extension','status':'Implementation under integration; no completed residential house or guest-unit claim','preserved_programme_keys':['D13_directory_05','D14_directory_04','D15_directory_04','D16_directory_04','D17_directory_04'],'floors':[84,88.5,93,97.5,102],'roof_top':106.5,'roof_underside':106.26,'protected_above':'D18_directory_06 Bridge briefing','floor_regions':records,'base_roof_cuts':[records[0]['main_void'],records[0]['stair_hole'],base['lift']['floor_hole_xz_m']],'pendant_bearing_patch':{'xz':[79,4],'top_y':92.4,'must_remain_solid':True},'east_stair':{'first_x':[86.25,88.25],'second_x':[88.65,90.65],'z':[4.70,9.40],'landing_z':[9.40,11.40],'steps':15,'half_rise':2.25,'flight_width':2.0},'west_stair':base['stair'],'new_stair_bases':[{'y':88.5,'type':'east'},{'y':93,'type':'west'},{'y':97.5,'type':'east'}],'roof_reveal_rings':[[list(p)for p in Polygon(v).buffer(.04,join_style=2).exterior.coords[:-1]] for v in [records[0]['main_void'],records[0]['stair_hole']]],'preserved_piers':base['support_intent']['commons_piers_xz_m'],'support_start_y':92.16,'guest_overlap_count':0,'rebuild_policy':'Keep existing D13/D14 rooms, stairs, identities and furniture; retain real pendant bearing and old roof outside coordinated cuts. New upper slabs are newly authored, not recovered. Actual collider sweeps and visual review remain required.'}
# Preserve an explicitly adopted current programme relocation on regeneration.
ledger_path=R/'data/programme_ledger.json'
if ledger_path.exists():
 briefing=next(r for r in json.loads(ledger_path.read_text())['destinations'] if r['programme_key']=='D18_directory_06')
 if briefing.get('current_geometry_owner')=='scripts/central_command_crown.gd':
  cover=next(r for r in regions if r['id']=='D18_starboard_house_cover')
  cover['previous_programme_reservation']='D18_directory_06';cover['programme_owner']=None
  cover['status']='Retained opaque starboard-house cover; former Bridge briefing reservation relocated to central crown. No new room or private pavilion assigned here.'
  extension['historical_protected_above']='D18_directory_06 Bridge briefing'
  extension['protected_above']='Retained physical cover; Bridge briefing now assigned to the central crown shell'
assert not unary_union([Polygon(v)for v in extension['base_roof_cuts']]).buffer(.25).contains(__import__('shapely').geometry.Point(79,4))
(R/'data/architecture/D13_D17_starboard_house_extension.json').write_text(json.dumps(extension,indent=2)+'\n');(R/'data/spatial_layout.json').write_text(json.dumps(layout,indent=2)+'\n')
family=C/'assets/starboard_house_upper';(family/'source').mkdir(parents=True,exist_ok=True);(family/'exports').mkdir(exist_ok=True);(family/'source/house_contract.json').write_text(json.dumps(extension,indent=2)+'\n')
p=C/'assets/vertical_commons/source/architecture_contract.json';d=json.loads(p.read_text());d['house_extension']=extension;p.write_text(json.dumps(d,indent=2)+'\n')
print('Authored three upper floor regions and separately owned D18 cover; zero guest-envelope overlaps; actual integration pending')
