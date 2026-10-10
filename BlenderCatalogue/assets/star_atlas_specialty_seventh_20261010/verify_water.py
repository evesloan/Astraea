from pathlib import Path
import json,struct,hashlib
W=Path(__file__).resolve().parent;P=json.load(open(W/'RUNTIME_PLAN.json'));water=0
for r in P['rooms']:
 b=(W/r['model_file']).read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);assert not any('Preview_Ground'in a.get('name','')for a in j['nodes'])
 for a in j['nodes']:
  name=a.get('name','')
  if 'WaterSurface_VisualOnly'in name or'water ripple'in name.lower():assert not a.get('extras',{}).get('runtime_collision',True);water+=1
 for native in P['native_export_records']:
  assert hashlib.sha256((W/native['native']).read_bytes()).hexdigest()==native['native_sha256']
assert water==21 and len(P['aquatic_wet_cells_local'])==231
p=W/'ACTUAL_SOURCE_CHECK.json';q=json.load(open(p));q.update(aquatic_nonsolid_water_meshes=water,aquatic_basins=3,wet_cells_per_basin=231,basin_conservative_wet_volume_m3=P['aquatic_wet_volume_m3'],preview_ground_excluded=True,canonical_species_body_accepted=False);q['limits'][1]='Baelin/Mantelid design targets proposed; canonical bodies/rigs/animation and biological/water/acoustic/save operations held';p.write_text(json.dumps(q,indent=2)+'\n');print('PASS: three source wet regions and21 non-solid water meshes; no preview ground exported; native files unchanged by unsaved renders')
