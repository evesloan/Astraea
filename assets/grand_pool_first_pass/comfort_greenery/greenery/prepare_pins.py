"""Pin read-only inputs; write pins only inside this installed source package."""
import json,hashlib,sys
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
CAT=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
AUDIT=HERE.parent/'reference_audit'
if not AUDIT.is_dir():
    AUDIT=Path('/workspace/scratch/375c2e438292/pool-seating-greenery-audit')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin_name(path):
    path=Path(path).resolve()
    return '../'+str(path.relative_to(HERE.parent)) if path.is_relative_to(HERE.parent) else str(path)
inv=json.loads((AUDIT/'SOURCE_INVENTORY.json').read_text());pins={};sources={}
for ident in ['AST-BOT-002','AST-BOT-003','AST-BOT-007','AST-BOT-012','AST-AQU-016']:
    row=inv[ident];sources[ident]=str(CAT/row['source'])
    for key in ['source','export']:
        path=CAT/row[key];actual=sha(path);assert actual==row[key+'_sha256'],str(path)+' differs from source audit';pins[str(path)]=actual
for rel in ['assets/botanical_understory/source/build_botanical_understory.py','assets/botanical_cluster/source/build_botanical_cluster.py','standards/botanical_materials.py','materials/botanical/manifest.json','assets/grand_pool_orchard_section/source/connected_contract.json','assets/grand_pool_first_pass/source/placement_contract.json','assets/grand_pool_first_pass/finish_envelope/stock/geometry.py']:
    pins[str(CAT/rel)]=sha(CAT/rel)
materials=json.loads((CAT/'materials/botanical/manifest.json').read_text())
for role,row in materials['materials'].items():
    p=CAT/'materials/botanical'/row['file'];assert sha(p)==row['sha256'];pins[str(p)]=sha(p)
for f in ['PLANTING_ENVELOPE_CANDIDATES.json','WET_POT_FULLNESS_CANDIDATES.json','SOURCE_INVENTORY.json','INPUT_PINS.json','MEDIA_FITTING_CANDIDATES.json']:
    pins[pin_name(AUDIT/f)]=sha(AUDIT/f)
relocation_file=AUDIT/'REFERENCE_RELOCATION.json'
assert relocation_file.is_file(),'Retained reference archive and REFERENCE_RELOCATION.json are required before pinning baseline images'
relocation=json.loads(relocation_file.read_text())
assert relocation.get('schema')==1 and isinstance(relocation.get('paths'),dict),'Expected reference relocation schema 1'
pins[pin_name(relocation_file)]=sha(relocation_file)
pins[pin_name(AUDIT/'INSPECTED_IMAGES.json')]=sha(AUDIT/'INSPECTED_IMAGES.json')
for row in json.loads((AUDIT/'INSPECTED_IMAGES.json').read_text())['images']:
    relocated=relocation['paths'][row['path']]
    assert relocated['sha256']==row['sha256'],'Relocation hash differs from original inspected audit record'
    relative=Path(relocated['relative_path']);assert not relative.is_absolute(),'Archive path must be package-relative'
    target=(HERE.parent/relative).resolve()
    assert target.is_relative_to(AUDIT.resolve()),'Retained reference must stay inside sibling reference_audit'
    assert sha(target)==row['sha256'],'Retained image differs from inspected audit bytes: '+row['path']
    pins[pin_name(target)]=row['sha256']
out=dict(schema='pool_greenery_input_pins_v1',immutable_inputs=pins,source_libraries=sources,material_spec=materials,contract_sha256=sha(HERE/'greenery_contract.json'),source_formula_lineage=['AST-BOT-002: cupped broad-leaf profile, root/stem/petiole support','AST-BOT-003: spoon rosette, folded flowers, physical basal crown','AST-BOT-007: closed joined stems, pleated fan topology and root-to-tip UVs'],authoring_method='New deterministic parameterized derivatives of retained construction; material datablocks append from exact pinned source, not a palette recreation or GLB extraction')
(HERE/'INPUT_PINS.json').write_text(json.dumps(out,indent=2)+'\n');print('Pinned',len(pins),'read-only inputs')
