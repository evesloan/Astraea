from pathlib import Path
import json,hashlib,datetime
from PIL import Image
O=Path(__file__).parent;G=Path('/workspace/shared/astraea-godot-production-20261003');C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
paths=[G/'artifacts/grand_pool_market_bays_clear_world_capture.png',G/'artifacts/grand_pool_market_bays_presentation_capture.png',G/'artifacts/grand_pool_long_view_clear_world_capture.png',G/'artifacts/grand_pool_long_view_presentation_capture.png',G/'docs/references/cruise_atrium_20261006/retro_atrium_quality_benchmark.png',C/'references/aquatic/image(20261001-035517).png',C/'assets/botanical_cluster/qa/Botanical_Clusters_Source_Imported_Comparison.png',C/'assets/botanical_canopy/qa/canopy_imported_full_640.png']
observations=[
'Actual market pixels inspected: broad black soil dominates the trough; thin upright plus two isolated low rosettes; almost empty shelf; bench back faces camera, but true viewing axis is established independently from source.',
'Actual presentation pixels inspected: same sparse bed and empty stock hierarchy at the target-sized 640x360 world inset; neither foliage nor meaningful bench viewing accommodation reads.',
'Actual pool pixels inspected: loungers face across water, isolated tiny pots disappear in the long view, large plain pale/gray structure and flat illumination remain.',
'Actual presentation pixels inspected: pools and loungers still read, but planting is almost absent as a designed spatial layer.',
'Actual benchmark inspected: planter mass covers beds, middle foliage connects crowns to soil, trailing groups soften edges; repeated living masses accompany meaningful light and architectural hierarchy. No instruction to copy its images or add its building geometry.',
'Actual aquatic reference inspected: lush connected beds, upper/middle/low silhouettes, broad bright green masses and flower accents; repeated planting frames water views rather than blocking routes or filling central voids.',
'Actual botanical cluster source/import comparison inspected: retained fan crown, trailing cluster and flowering bank have useful low-poly source vocabulary, but are individually sparse and need composition/fitted derivatives to meet the new request.',
'Actual retained canopy GLB image inspected: valuable asymmetric branching form; foliage is still relatively sparse. Its broad 2.006 m depth cannot be dropped unchanged into a 0.96 m-deep Grand Pool bed.'
]
rows=[]
for p,n in zip(paths,observations):
 im=Image.open(p);rows.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pixels_inspected':True,'dimensions_px':list(im.size),'observation':n})
(O/'INSPECTED_IMAGES.json').write_text(json.dumps({'review_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'images':rows},indent=2)+'\n')
inputs=[C/'catalogue_manifest.json',C/'assets/grand_pool_first_pass/source/placement_contract.json',G/'data/architecture/GRAND_POOL_FIRST_PASS_RUNTIME.json',C/'assets/grand_pool_orchard_section/source/connected_contract.json',C/'assets/grand_pool_first_pass/finish_envelope/source/finish_contract.json',C/'assets/grand_pool_first_pass/finish_envelope/stock/stock_placement_contract.json',C/'assets/grand_pool_first_pass/finish_envelope/stock/geometry.py']
(O/'INPUT_PINS.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in inputs},indent=2)+'\n')
