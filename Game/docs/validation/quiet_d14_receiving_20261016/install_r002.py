from pathlib import Path
import shutil,hashlib,re,subprocess,json
R=Path('/workspace/Astraea');E=Path('/workspace/quiet-d14-integration');D=R/'BlenderCatalogue/assets/quiet_d14_staff_receiving_20261016/r002'
assert json.loads((D/'NATIVE_VERIFICATION.json').read_text())['status']=='PASS'
assert all(r['reached'] and r['floor_contact'] for r in json.loads((E/'THRESHOLD_r002.json').read_text())['legs'])
shutil.copy2(R/'Game/data/quiet_d14_receiving_20261016/RECEIPT.json',E/'RECEIPT_r001_RUNTIME.json')
shutil.copy2(D/'RECEIPT.json',R/'Game/data/quiet_d14_receiving_20261016/RECEIPT.json')
f='QUIET_D14_STAFF_RECEIVING_r002.glb';dest=R/'Game/assets/quiet_d14_receiving_20261016';dest.mkdir(exist_ok=True);assert not (dest/f).exists();shutil.copy2(D/f,dest/f)
s=(R/'Game/assets/quiet_d15_receiving_20261016/QUIET_D15_STAFF_RECEIVING_r004.glb.import').read_text();s=re.sub(r'^uid=.*\n','',s,flags=re.M);s=s.replace('quiet_d15_receiving','quiet_d14_receiving').replace('QUIET_D15_STAFF_RECEIVING_r004.glb',f);md5=hashlib.md5(('res://assets/quiet_d14_receiving_20261016/'+f).encode()).hexdigest();s=s.replace('3a29c57686218dc1fdd7ca47676294df',md5);(dest/(f+'.import')).write_text(s)
p=R/'Game/project.godot';original=p.read_bytes();assert hashlib.sha256(original).hexdigest()=='42dfd175fd8135e51094d66347802a51f6622475a06b4b2c11227af29884bdc0'
try:
 p.write_bytes(original+b'\n[filesystem]\nimport/blender/enabled=false\n')
 with (E/'import-r002.log').open('w') as log:result=subprocess.run(['godot','--headless','--editor','--path','Game','--import'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 assert result.returncode==0,result.returncode
finally:p.write_bytes(original)
print('Imported r002; retained r001 asset and original project settings.')
