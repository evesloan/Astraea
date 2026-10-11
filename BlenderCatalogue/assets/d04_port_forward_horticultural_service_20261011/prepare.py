from pathlib import Path
import json,hashlib,copy
from shapely.geometry import Polygon,box
R=Path(__file__).resolve().parents[3];W=Path(__file__).resolve().parent;O=R/'BlenderCatalogue/assets/d04_port_forward_commons_service_20261010';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ns={'__file__':str(W/'prepare.py')};s=(R/'BlenderCatalogue/assets/d04_port_forward_homes_second_20261010/prepare.py').read_text();exec(s[:s.index('from shapely import affinity')],ns);parts=ns['parts'];cube=ns['cube'];prism=ns['prism']
p=json.load(open(O/'RUNTIME_PLAN.json'));pins=dict(p['source_pins'])
for f in sorted(O.iterdir()):
 if f.is_file():pins[str(f.relative_to(R))]=sha(f)
for f in ['Game/scripts/cleaning_cart.gd','Game/scripts/physics_tether.gd','Game/scripts/player.gd','Game/scripts/cart_handle.gd','Game/data/architecture/cleaning_cart_contacts.json']:pins[f]=sha(R/f)
# No new catalogue family or identity: programme-owned fittings plus one rigid original cabinet.
source=next(a for a in json.load(open(R/'BlenderCatalogue/catalogue_manifest.json'))['assets'] if a['catalogue_id']=='AST-STF-007')
poly=Polygon([(-68.7,-357.4),(-67.2,-357.4),(-67.1,-357.3),(-67.1,-356.65),(-67.2,-356.55),(-68.7,-356.55),(-68.8,-356.65),(-68.8,-357.3)])
prism('D04HS_TrayWorktop',poly,17.32,17.4,role='warm_walnut',category='workbench')
for i,(x,z) in enumerate([(-68.65,-357.25),(-67.25,-357.25),(-68.65,-356.7),(-67.25,-356.7)]):cube('D04HS_WorkbenchLeg_'+str(i),[x-.05,16.5,z-.05],[x+.05,17.32,z+.05],category='workbench')
for i,x in enumerate([-68.45,-67.95,-67.45]):
 z=-356.98;cube('D04HS_CleanTrayBase_'+str(i),[x-.19,17.4,z-.16],[x+.19,17.435,z+.16],role='ivory_enamel',category='clean_tray')
 for j,(lo,hi) in enumerate([([x-.19,17.435,z-.16],[x-.16,17.54,z+.16]),([x+.16,17.435,z-.16],[x+.19,17.54,z+.16]),([x-.16,17.435,z-.16],[x+.16,17.54,z-.13]),([x-.16,17.435,z+.13],[x+.16,17.54,z+.16])]):cube('D04HS_CleanTrayRim_%s_%s'%(i,j),lo,hi,role='ivory_enamel',category='clean_tray')
 cube('D04HS_TrayHandle_'+str(i),[x-.19,17.54,z-.03],[x+.19,17.59,z+.03],category='clean_tray')
prism('D04HS_ClosedCuttings',box(-69.05,-359.45,-68.25,-358.65).buffer(-.12).buffer(.12,quad_segs=3),16.5,17.32,role='ivory_enamel',category='closed_cuttings')
prism('D04HS_CuttingsLid',box(-69.08,-359.48,-68.22,-358.62).buffer(-.12).buffer(.12,quad_segs=3),17.32,17.4,role='warm_walnut',category='closed_cuttings')
cube('D04HS_CuttingsHandle',[-68.85,17.4,-359.10],[-68.45,17.47,-359.0],category='closed_cuttings')
cube('D04HS_WorkReturnScreen',[-69.45,16.5,-358.04],[-67.1,17.55,-357.9],role='ivory_enamel',category='separation_screen')
cube('D04HS_LampHousing',[-67,20.12,-359.1],[-66.1,20.25,-358.2],category='light_source');cube('D04HS_LampLens',[-66.94,20.08,-359.04],[-66.16,20.12,-358.26],role='opal_glow',category='light_source')
work=copy.deepcopy(parts);parts.clear();pre=next(q for q in p['parts']if q['name']=='D04CS_QuietGardenGlass');edges=[-84.82,-84.575,-83.425,-82.975,-81.825,-81.375,-80.225,-79.89]
for i,(x,X) in enumerate(zip(edges,edges[1:])):cube(('D04HS_Sash_'if i%2 else'D04HS_FixedGlass_')+str(i//2),[x,17.25,-357.48],[X,20.1,-357.3],role='hospitality_glass',category='moving_sash'if i%2 else'fixed_glass')
new={'schema':'astraea.d04.horticultural_service.v1','base_commit':'8e30b506f7ba4f4b2fb1ddb1ae0f24f6a9ff76c8','programme_key':'D04_directory_01','new_floor_m2':0,'existing_service_bay_bounds':[[-69.71,16.5,-360.01],[-63.28,20.46,-356.38]],'parts':work,'successor_parts':copy.deepcopy(parts),'sources':[source],'components':[{'catalogue_id':'AST-STF-007','name':'HorticulturalToolsCabinet','position':[-65.3,16.5,-356.9],'yaw':3.141592653589793}],'source_pins':pins,'preimage':pre,'base_structure_model':p['structure']['model_file'],'base_structure_sha256':p['structure']['model_sha256'],'open_garden_service':False,'connection_accepted':False,'sashes':[{'name':'D04HS_Sash_'+str(i),'pivot':[x,20.1,-357.48],'angle_degrees':60,'worker_stance':[x,16.5,-357.82]}for i,x in enumerate([-84,-82.4,-80.8])],'service_stations':[[-66.3,16.5,-358.8],[-65.3,16.5,-358.45],[-67.8,16.5,-358.6]],'lights':[{'name':'D04HS_WorkLight','at':[-66.55,20.06,-358.65]}],'all_twenty_allocations_unchanged':p['all_twenty_allocations_unchanged'],'limits':['Partial horticultural workbay/common garden access only; private-court service and full programme unfinished','Clean trays/tool stock east approach, closed cuttings west approach; shared public gallery crossing remains uncontrolled/operationally held','No new plants, guest capacities, biology parameters, stock/save/refill or waste-processing gameplay','No claim of service-only network or cart-safe vertical connection','Static cart poses differ from separately tested original production-cart force-tether exercise','Primary engineering/habitat/final normal-play graphics remain held']}
assert not(W/'PLAN.json').exists();(W/'PLAN.json').write_text(json.dumps(new,indent=2)+'\n');print('PLAN',len(work),len(parts),len(pins))
