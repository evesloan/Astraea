from pathlib import Path
import json,hashlib
D=Path(__file__).parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p={'status':'STAGED_PROPOSAL_REQUIRES_CURRENT_RECEIVING_GATE','floor_rectangles':[[4.00005,64,168,172],[60,64,172,231.7],[54.00005,60,228.3,231.7]],'floor_outline_xz':[[4.00005,168],[64,168],[64,231.7],[54.00005,231.7],[54.00005,228.3],[60,228.3],[60,172],[4.00005,172]],'floor_y':61,'new_floor_area_m2':499.19963,'source_native':'BlenderCatalogue/assets/group8_orchard_service_20261011/OrchardService_r003.blend','source_native_sha256':'5fd7fb04e2f421c1fac25fb10bd0e78f3fe529fc8dd7976dae4ffad9164477f2','source_pins':{k:sha(G/k)for k in ['assets/models/AST-DIN-003.glb','assets/models/AST-DIN-004.glb','assets/models/AST-AQU-012.glb','data/generated/structural_meshes.json','scripts/vesper_service.gd','scripts/player.gd','scripts/commons_lift.gd']},'source_receiving':'D10_vesper_floor east edge Z228.3..231.7; retained D10_aft_route X4 at Z168..172','master_basis':'Chapter7 body166 food/provisions D01 synthesis andD10 finishing galleys; chapter5 connected authored routes; no extra programme/capacity or unsupported staff lift stop','original_sources_modified':False,'service_operation_species_cart_and_primary_load_accepted':False}
(D/'NATIVE_PLAN.json').write_text(json.dumps(p,indent=2)+'\n')
s=Path('/workspace/astraea-integration-cutoff-20261013/orchard_external_receiving_20261015/build_native.py').read_text();a=s.index("B=lambda p:");s='''from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Matrix
from mathutils.geometry import tessellate_polygon
D=Path(__file__).resolve().parent;G=Path('/workspace/astraea-protected-integration-20261012/Game');plan=json.loads((D/'NATIVE_PLAN.json').read_text());assert bpy.app.version[:3]==(4,3,2)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);made=[];rows=[]
'''+s[a:];s=s.replace('for obj in made:obj.location=B(origin)','');a=s.index('for j,z in enumerate([-215.1');b=s.index('# Four rigid source-profile',a)
s=s[:a]+'''for j,z in enumerate([229.,230.,231.]):box(f'ORX_EmbeddedDiningTie{j}',(53.7,60.78,z-.12),(54.3,60.86,z+.12),metal)
for j,z in enumerate([168.7,170.,171.3]):box(f'ORX_EmbeddedAxialTie{j}',(3.7,60.78,z-.12),(4.3,60.86,z+.12),metal)
for j in range(16):girder(f'ORX_AxialCross{j}',(4+j*4,168.1),(4+j*4,171.9))
for j in range(16):girder(f'ORX_GalleryCross{j}',(60,172+j*3.8),(64,172+j*3.8))
for j,z in enumerate([228.5,230.,231.5]):girder(f'ORX_GatewayCross{j}',(54,z),(64,z))
'''+s[b:]
s=s.replace('(4,-178.15),(4,-177.7)','(4,168),(4,168.3)').replace('(4,-174.3),(4,-173.85)','(4,171.7),(4,172)').replace('(4,-177.7),(4,-174.3)','(4,168.3),(4,171.7)')
s=s.replace('[(62,64.1,-214),(62,64.1,-194),(42,64.1,-176),(16,64.1,-176)]','[(62,64.1,230),(62,64.1,210),(62,64.1,188),(42,64.1,170),(16,64.1,170)]')
s=s.replace('or abs','or abs')
s=s.replace('ORCHARD_SERVICE_GATEWAY_r001','VESPER_SERVICE_RECEIVER_r001').replace('orchard_external_receiving_20261015','vesper_service_receiving_20261015').replace('ORCHARD_EXTERNAL_RECEIVING','VESPER_SERVICE_RECEIVING').replace('ORX_','VSR_')
s=s.replace("and sha(src if isinstance(src,Path)else G/'assets/models/AST-DIN-008.glb')==expected",'')
s=s.replace("'source_file':'AST-DIN-008.glb','source_sha256':expected,",'').replace("'authoring_meshes':len(parts)+2,'runtime_meshes':len(batchrows)+2","'authoring_meshes':len(parts),'runtime_meshes':len(batchrows)")
s=s.replace("'new_room_ids_capacity_or_lift_stops':0","'native_file':native.name,'new_room_ids_capacity_or_lift_stops':0")
(D/'build_native.py').write_text(s)
s=Path('/workspace/astraea-integration-cutoff-20261013/orchard_external_receiving_20261015/verify_native.py').read_text().replace('ORCHARD_SERVICE_GATEWAY_r001','VESPER_SERVICE_RECEIVER_r001');(D/'verify_native.py').write_text(s)
print('PREPARED_STAGED_NATIVE_PLAN')
