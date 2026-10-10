from pathlib import Path
import json,hashlib,math,shutil,numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reader=(R/'BlenderCatalogue/assets/tidal_d15_service_receiving_20261010/source_geometry.py').read_text().replace("raw=read('Game/assets/models/'+file)","raw=Path(file).read_bytes()");ns={'__file__':str(W/'geometry_reader.py')};exec(compile(reader,'retained_glb_reader','exec'),ns)
manifest=json.loads((R/'BlenderCatalogue/catalogue_manifest.json').read_text());assets=manifest['assets'];assets=list(assets.values())if isinstance(assets,dict)else assets;sources=[]
for cid in ['AST-STF-007','AST-AQU-007']:
 found=[a for a in assets if a['catalogue_id']==cid];assert len(found)==1;a=found[0]
 for kind in ['source','export']:assert sha(R/'BlenderCatalogue'/a[kind])==a['source_sha256'if kind=='source'else'export_sha256']
 sources.append(a)
pins={p:sha(R/p)for p in ['BlenderCatalogue/catalogue_manifest.json','Game/scripts/commons_lift.gd','Game/scripts/service_door.gd','Game/assets/models/AST-RES-TIDAL_lift_fit_r003.glb','Game/data/architecture/TIDAL_D13_LOCAL_SERVICE_FITTINGS.json']}
floors=[]
for deck,y in [(14,88.5),(15,93),(16,97.5),(17,102)]:
 path=f'Game/data/architecture/TIDAL_D{deck}_SERVICE_RECEIVING.json';j=json.loads((R/path).read_text());pins[path]=sha(R/path)
 file='Game/assets/models/'+j['corridor_file'];pins[file]=sha(R/file);tris=list(ns['triangles'](str(R/file)));regions=j.get('floor_regions',j.get('approach_floor_regions',[]));floor=unary_union([Polygon(t)for r in regions for t in r['triangles']])
 retained_west=[]
 for name,t in tris:
  points=t.reshape(-1,3);lo=points.min(axis=0);hi=points.max(axis=0)
  if hi[0]>-63.3 and lo[0]<-58.8 and hi[2]>-498.2 and lo[2]<-483.8:retained_west.append({'mesh':name,'min':lo.tolist(),'max':hi.tolist(),'triangles':len(t)})
 assert retained_west
 assemblies=[];coverage=[]
 for stem,cid,z,role in [('CleanProductWorkCupboard','AST-STF-007',-493,'clean_product_work_cupboard'),('CleanLinenNiche','AST-AQU-007',-490,'dry_clean_linen_niche'),('ClosedReturnsHoldingCupboard','AST-STF-007',-487,'vented_returns_left_compartment_open_preparation_right')]:
  at=[-59.7,y,z];bounds=[-60.055,z-.9,-59.39,z+.9]if cid=='AST-STF-007'else[-60.01,z-.67,-59.39,z+.67];area=box(*bounds);missing=area.difference(floor).area;assert missing<.00001,(deck,stem,missing)
  assemblies.append({'name':f'D{deck}_{stem}','catalogue_id':cid,'position':at,'yaw':-math.pi/2,'persistent_id':f'tidal_d{deck}_{role.split("_")[0]}_{"linen_niche"if cid=="AST-AQU-007"else"product_cupboard"if stem.startswith("Clean")else"returns_cupboard"}_001','role':role})
  coverage.append({'assembly':f'D{deck}_{stem}','bounds_xz':bounds,'footprint_area_m2':area.area,'unsupported_area_m2':missing})
 parking={'persistent_id':f'tidal_d{deck}_empty_cart_parking_bay_001','bounds_xz':[-61.7,-486.2,-60.3,-484.5],'entry':'south','empty':True,'capacity_accepted':False};bay=box(*parking['bounds_xz']);assert bay.difference(floor).area<.00001
 floors.append({'deck':deck,'floor_y':y,'receiver_persistent_id':j['persistent_id'],'shared_door':j['door'],'assemblies':assemblies,'parking':parking,'independent_survey':{'actual_corridor_file':j['corridor_file'],'actual_corridor_sha256':pins[file],'actual_west_bay_meshes':retained_west,'floor_owner_regions':[r['id']for r in regions],'fitting_footprint_coverage':coverage,'parking_unsupported_area_m2':bay.difference(floor).area,'house_entry':j['door']['position'],'placement_reason':'Existing screened west service dead end; keep shared house portal and central/east approach entirely free. Abandoned west mouth closures remain intact; these fittings are approached within the corridor, not through the closed west mouths.'}})
for p in ['Game/scripts/tidal_garden_adoption.gd','Game/tools/validate.py','Game/docs/CURRENT_STATUS.md','Game/docs/FULL_SHIP_SCOPE_INDEX.md']:
 out=W/'predecessors'/p;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/p,out)
P={'schema':'astraea.tidal.upper.local_service_fittings.v1','base_commit':'5e8b1f22b4ae29958b053500daea65f26209fb2b','root_name':'TidalUpperLocalServiceFittings','persistent_id':'tidal_upper_local_service_fittings_001','model_file':'TidalUpperLocalServiceFittings.glb','sources':sources,'preimage_pins':pins,'decks':floors,'derivative_counts_as_new_catalogue_design':False,'operations':'physical_fittings_only_stock_returns_save_on_hold','shared_flow':'sequential_sealed_load_only_unaccepted_hygiene','reference':'BlenderCatalogue/references/landings/staff_corridor_services.png','constraints':['No new cart, room, floor or controller','Vented returns left compartment plus open preparation shelves: no sealing/hygiene claim','Do not alter any service mouth closure, door swing or lift','Full routes, boarding and loaded cart/species turns deferred']}
(W/'FITTINGS_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');print(json.dumps({'status':'PASS','independent_deck_surveys':len(floors),'fitting_footprints':12,'parking_footprints':4,'unsupported_area_m2':0,'pins':len(pins)}))
