from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
B=Path(__file__).parent;out=B/'artwork';out.mkdir(exist_ok=True)
I=Image.new('RGB',(1100,1400),'#dfd2b1');d=ImageDraw.Draw(I)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
f=lambda n,b=False:ImageFont.truetype(bold if b else font,n)
d.rectangle((0,0,1100,145),fill='#214c4c');d.text((60,37),'GRAND POOL',font=f(68,True),fill='#eee4c8');d.text((60,173),'D09  /  EAST GALLERY',font=f(39,True),fill='#214c4c')
d.rounded_rectangle((245,355,735,915),radius=100,fill='#4e9290',outline='#294f50',width=8);d.text((332,590),'POOL',font=f(65,True),fill='#e4dfc3')
d.rounded_rectangle((130,285,920,985),radius=145,outline='#7e4931',width=25);d.line((890,360,1030,360),fill='#7e4931',width=14);d.ellipse((895,340,935,380),fill='#c36135');d.text((727,395),'YOU ARE HERE',font=f(31,True),fill='#914827')
d.rectangle((35,415,125,615),fill='#a65c37');d.text((40,648),'MARKET',font=f(33,True),fill='#214c4c');d.line((145,970,870,970),fill='#dfd2b1',width=15)
d.line((150,292,915,292),fill='#7e4931',width=26);d.text((280,232),'FORE RING',font=f(35,True),fill='#7e4931');d.polygon([(780,272),(780,312),(724,292)],fill='#eee4c8')
d.rectangle((906,845,965,900),fill='#b67c3d');d.text((746,802),'POOL LIFT',font=f(29,True),fill='#214c4c')
d.line((50,1100,1050,1100),fill='#7e4931',width=4);d.text((60,1140),'←  MARKET VIA FORE RING',font=f(43,True),fill='#214c4c');d.text((60,1230),'POOL LIFT / AFT GALLERY  →',font=f(38,True),fill='#214c4c');d.text((60,1320),'SunCorp  •  A brighter tomorrow',font=f(29),fill='#7e4931')
p=out/'ORIGINAL_GALLERY_DIRECTORY.png';I.save(p)
(out/'CONTENT_MANIFEST.json').write_text(json.dumps({'status':'ORIGINAL_SOURCE_ROUTE_DIAGRAM_PENDING_NATIVE_LEGIBILITY','image_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'content':'Original D09 east-gallery diagram; fore ring to Orchard Market, aft gallery to existing east-gate pool lift. Not a new facility or direct west shaft entry.','map_not_to_scale':True,'source_geometry':'grand_pool_orchard_section/source/connected_contract.json'},indent=2)+'\n')
print(p)
