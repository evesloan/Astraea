from pathlib import Path
import re,shutil
R=Path('/workspace/Astraea');E=Path('/workspace/family-d16-integration');D=R/'BlenderCatalogue/assets/family_d16_staff_receiving_20261016'
for kind in ['scripts','data']:(R/f'Game/{kind}/family_d16_receiving_20261016').mkdir(exist_ok=True)
s=(R/'Game/scripts/family_d15_receiving_20261016/package.gd').read_text().replace('family_d15','family_d16').replace('FamilyD15','FamilyD16');(R/'Game/scripts/family_d16_receiving_20261016/package.gd').write_text(s);shutil.copy2(D/'RECEIPT.json',R/'Game/data/family_d16_receiving_20261016/RECEIPT.json')
for name in ['check.gd','installed.gd']:
 s=Path('/workspace/family-d15-integration/'+name).read_text();before,after=s.split(' var adjacent:Array=[]',1)
 before=before.replace('family_d15','family_d16').replace('family-d15','family-d16').replace('FamilyD15','FamilyD16').replace('F15_','F16_').replace('FT_Batch_330','FT_Batch_345').replace('FT_Batch_332','FT_Batch_347').replace('"FT_Batch_71"','"FT_Batch_101"').replace('floor_staff_floor_starboard_service_riser_5_D15','floor_staff_floor_starboard_service_riser_5_D16').replace('lobby_wall_staff_white_paint_y11','lobby_wall_staff_white_paint_y12')
 before=re.sub(r'(?<![\w.])(92\.76|93\.03|93\.4|93|94\.6|94|95\.2|95\.78|95\.795|95\.82)(?![\w.])',lambda m:format(float(m[0])+4.5,'.6f').rstrip('0').rstrip('.'),before)
 before=before.replace('ship.get_node("ShipSpace/FamilyD14StaffReceiving")]:','ship.get_node("ShipSpace/FamilyD14StaffReceiving"),ship.get_node("ShipSpace/FamilyD15StaffReceiving"),ship.get_node("ShipSpace/D17StarboardStandardReceiving")]:')
 after=after.replace('for fy in [84.0,88.5]:','for fy in [84.0,88.5,93.0]:').replace('protected_Family_D13_D14_legs','protected_Family_D13_D14_D15_legs').replace('FAMILY_D15','FAMILY_D16')
 (E/name).write_text(before+' var adjacent:Array=[]'+after)
for name in ['compare_import.gd','verify_remote.py']:(E/name).write_text(Path('/workspace/family-d15-integration/'+name).read_text().replace('family-d15','family-d16').replace('family_d15','family_d16').replace('FAMILY_D15','FAMILY_D16'))
