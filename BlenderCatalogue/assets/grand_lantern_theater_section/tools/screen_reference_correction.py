"""Prove approved reference application changes material application only."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];CAT=R.parents[1];P=Path('/workspace/shared/astraea-godot-production-20261003/docs/references/cruise_atrium_20261006')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
g=json.load(open(R/'source/geometry.json'));baseline=json.load(open(R/'qa/REFERENCE_CORRECTION_BASELINE.json'));mc=json.load(open(R/'contracts/material_reuse_contract.json'));keys=['name','vertices_world','faces','role','collision_owner','surface_region']
sig=hashlib.sha256(json.dumps([{k:o.get(k) for k in keys} for o in g['objects']],sort_keys=True,separators=(',',':')).encode()).hexdigest();approved={n for names in mc['sources'].values() for n in names};bad=[];soffits=0
for o in g['objects']:
 fm=o.get('face_material_families',[o['material_family']]*len(o['faces']))
 if len(fm)!=len(o['faces']):bad.append(dict(object=o['name'],error='face/material count mismatch'))
 if set(fm)-approved:bad.append(dict(object=o['name'],error='unapproved material',materials=list(set(fm)-approved)))
 for f,m in zip(o['faces'],fm):
  if m=='warm_walnut':
   soffits+=1;n=len(o['vertices_world'])//2
   if not all(i>=n for i in f):bad.append(dict(object=o['name'],error='warm walnut outside lower soffit faces'))
shaft={o['name']:o['material_family'] for o in g['objects'] if o['name'] in ['lift_shaft_west','lift_shaft_east','lift_shaft_rear']};jambs={o['name']:o['material_family'] for o in g['objects'] if o['name'].startswith('lift_gate_pocket_')}
checks=dict(geometric_envelopes_faces_collisions_and_ids_unchanged=sig==baseline['before_geometry_material_independent_sha256'],eight_surface_manifests_unchanged=sha(R/'contracts/surface_manifest.json')==baseline['before_surface_manifest_sha256'],places_and_counts_unchanged=sha(R/'contracts/place_instances.json')==baseline['before_place_instances_sha256'],original_chair_bytes_unchanged=sha(CAT/'assets/auditorium_use/source/AST-CUL-003.blend')==baseline['before_chair_sha256'],three_static_glazed_panels=set(shaft.values())=={'gallery_glass'} and len(shaft)==3,full_height_opaque_jambs_unchanged=set(jambs.values())=={'champagne_metal'} and len(jambs)==2,material_assignments_valid=not bad and soffits>0)
assert all(checks.values()),checks
report=dict(checks=checks,static_glazed_panels=shaft,opaque_jambs=jambs,warm_walnut_soffit_faces=soffits,material_errors=bad,after_geometry_material_independent_sha256=sig,reference_sha256={str(p):sha(p) for p in [P/'cruise_lift_towers.png',P/'grand_atrium_lift_banks.png',P/'DESIGN_APPLICATION.md',P/'SOURCE_PROVENANCE.json']},retained_material_sources_sha256={rel:sha(CAT/'assets'/rel) for rel in mc['sources']},scope='Static shaft side/rear glazing and existing warm_walnut on same-depth gallery lower faces only; no engine run or real cabin/rail/gate/pocket sweep evidence.')
(R/'qa/reference_correction_screen.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['checks'],indent=2));print('Soffit faces',soffits)
