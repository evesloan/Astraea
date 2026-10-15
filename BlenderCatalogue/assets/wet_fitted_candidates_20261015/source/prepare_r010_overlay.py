from pathlib import Path
import json,zipfile
D=Path(__file__).resolve().parent;I=D/'fitted_r010_import/Game';native=json.loads((D/'FITTED_NATIVE_VERIFICATION_r010.json').read_text());p=json.loads((D/'FITTED_CONFIG_r005.json').read_text());p.update(models=native['models'],lights=native['lights'],plan=json.loads((D/'FITTED_SUCCESSOR_PLAN_r010.json').read_text()),canopies=json.loads((D/'CANOPY_EXACT_PREIMAGES_r007.json').read_text()))
for row,new in zip(native['doors'],p['doors']):row['persistent_id']=new['persistent_id']
p['doors']=native['doors'];p['fixture_mounts']=native['fixture_mounts']
for row in p['loose_furniture_moves']:
 if row['name']=='D17_QuietReading_1':row['target_xyz']=[90,102,-383.2]
 if row['name']=='D17_QuietReading_2':row['target_xyz']=[90,102,-380.2]
 if row['name']=='D17_SharedTable_1':row['target_xyz']=[88.5,102,-381.2]
for row in p['roofs']:row['mask'][:2]=p['plan'][row['kit']]['roof_patch_world_x']
(D/'FITTED_CONFIG_r010.json').write_text(json.dumps(p,indent=2)+'\n')
(D/'fitted_package_r010.gd').write_text((D/'fitted_package.gd').read_text().replace('r005','r010').replace(' var furniture:Array=[]',' load("res://scripts/fitted_wet_pavilions_20261015/canopy_successor.gd").apply(ship,group,p.canopies)\n var furniture:Array=[]'))
log=(D/'FITTED_IMPORT010.log').read_text();assert 'ERROR:'not in log and 'DONE' in log
(D/'FITTED_IMPORT010.json').write_text(json.dumps({'exit_code':0,'passed':True,'models':2,'log':'FITTED_IMPORT010.log'},indent=2)+'\n')
with zipfile.ZipFile(D/'FITTED_CANDIDATE_OVERLAY_r010.zip','w',zipfile.ZIP_DEFLATED)as z:
 for f in I.rglob('*'):
  if f.is_file()and (f.suffix in['.glb','.import']or('.godot/imported/'in str(f)and f.suffix in['.scn','.md5'])):z.write(f,f.relative_to(I))
 with zipfile.ZipFile(D/'FITTED_CANDIDATE_OVERLAY_r005.zip')as old:
  for name in old.namelist():
   if name.startswith('scripts/group2_vip_pavilions/'):z.writestr(name,old.read(name))
 z.write(D/'canopy_successor_r007.gd','scripts/fitted_wet_pavilions_20261015/canopy_successor.gd')
 z.write(D/'fitted_package_r010.gd','scripts/fitted_wet_pavilions_20261015/package.gd');z.write(D/'fitted_roof_successor.gd','scripts/fitted_wet_pavilions_20261015/roof_successor.gd');z.write(D/'FITTED_CONFIG_r010.json','data/fitted_wet_pavilions_20261015/FITTED_CONFIG_r010.json')
s=(D/'inspect_fitted_r005.gd').read_text().replace('r005','r010').replace('R005','R010').replace('if str(mesh.name).contains("ColumnBase"):', 'if str(mesh.name).contains("ColumnBase") or str(mesh.name).ends_with("_Foot"):')
(D/'inspect_fitted_r010.gd').write_text(s)
print('R010 overlay prepared')
