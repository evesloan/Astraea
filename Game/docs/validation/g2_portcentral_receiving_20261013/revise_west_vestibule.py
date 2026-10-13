from pathlib import Path
import json,shutil
P=Path(__file__).parent;T=P/'import/Game'
for name in ['build_portcentral_frame.py','inspect_resources.gd','validate_central_receiving.gd','package.gd']:
 shutil.copyfile(P/name,P/(name+'.r001_failed171.txt'))
f=P/'build_portcentral_frame.py';s=f.read_text();s=s.replace("[-81,-62.7,101.76,102,-16,-14.2]","[-81,-67.1,101.76,102,-16,-14.2]")
s=s.replace("box('East_existing_arrival_approach',[-62.7,-60.9,101.76,102,-16,-3.2],'floor')\n",'')
s=s.replace("for z in[-12.,-10.,-8.,-6.,-4.5]:box(f'East_slab_transfer_{z}',[-64.12,-60.95,101.78,101.84,z-.12,z+.12],'east_slab_bearing')\n",'')
a=s.index('segments=');b=s.index('\nfor i,',a)
s=s[:a]+"segments=[(-89,-24,-79,-24),(-79,-24,-79,-16),(-79,-16,-67.1,-16),(-67.1,-14.2,-81,-14.2),(-81,-14.2,-81,-16),(-81,-16,-89,-16),(-89,-16,-89,-24)]"+s[b:]
s=s.replace('55.98','25.02').replace("'guard_batches':['SA_D17_RingLinkGuard_-3.18_Infill','SA_D17_RingLinkGuard_-3.18_Cap']","'guard_batches':['SAB_North_D17R_GuardVestWest_Base','SAB_North_D17R_GuardVestWest','SAB_North_D17R_GuardVestWest_Cap']").replace("'guard_mask':[-62.7,-60.9,101.99,103.17,-3.28,-3.08]","'guard_mask':[-67.12,-66.97,101.99,103.19,-16,-14.2]")
s=s.replace('PORTCENTRAL_RECEIVING_FRAME_r001','PORTCENTRAL_RECEIVING_FRAME_r002');f.write_text(s)
f=P/'inspect_resources.gd';s=f.read_text().replace('Vector3(-61.8,102,-8)','Vector3(-68,102,-15.1)').replace('STAR_ATLAS_UPPER_COMMONS_r001.glb','STAR_ATLAS_D17_STANDARD_BATCH_FRAME_r002.glb');f.write_text(s)
f=P/'package.gd';f.write_text(f.read_text().replace('PORTCENTRAL_RECEIVING_FRAME_r001','PORTCENTRAL_RECEIVING_FRAME_r002'))
shutil.copyfile(P/'package.gd',T/'scripts/group2_portcentral_receiving_20261013/package.gd')
print('STAGED_R002_WEST_VESTIBULE_REVISION_ONLY')
