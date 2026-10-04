"""Author a readable local route diagram from the current D13 floor geometry."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
im=Image.new('RGB',(1024,512),(20,32,42));d=ImageDraw.Draw(im)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
d.text((36,24),'D13',font=font(58),fill=(239,194,112))
d.text((36,104),'STARBOARD',font=font(34),fill=(236,230,210));d.text((36,148),'SUITES',font=font(34),fill=(236,230,210))
d.text((36,231),'13017 / 13041',font=font(28),fill=(236,230,210))
d.text((36,293),'Atrium gallery',font=font(24),fill=(205,210,205));d.text((36,332),'Commons + lift',font=font(24),fill=(205,210,205))
d.text((36,418),'LOCAL ROUTE',font=font(23),fill=(239,194,112));d.text((36,454),'Bow is up on this plan',font=font(18),fill=(186,198,202))
def p(x,z):return(420+(x-50)*13,44+(z+54)*13)
layout=json.loads((R/'data/spatial_layout.json').read_text())
for region in layout['regions']:
 if region['id'] in ['D13_address13017','D13_address13041','D13_residential_street_connection','D13_residential_street_pilot']:
  points=[p(x,z)for x,z in region['boundary']];d.polygon(points,fill=(78,97,102) if 'address' in region['id'] else(198,202,192));d.line(points+[points[0]],fill=(224,215,189),width=2)
for address,z in [('13017',-42),('13041',-49.4)]:
 x,y=p(70,z);d.text((x,y-13),address,font=font(25),fill=(255,235,175))
route=[p(52,-28.7),p(84,-28.7),p(84,-50.5)];d.line(route,fill=(234,176,85),width=6)
x,y=p(74.5,-27.42);d.ellipse((x-9,y-9,x+9,y+9),fill=(255,198,84));d.text((570,435),'YOU ARE HERE',font=font(23),fill=(255,198,84))
x,y=p(84,-26.2);d.line([(x,y),(x,465)],fill=(234,176,85),width=6);d.polygon([(x-10,455),(x+10,455),(x,475)],fill=(234,176,85));d.text((835,478),'COMMONS',font=font(18),fill=(235,227,206))
x,y=p(52,-28.7);d.polygon([(x-17,y),(x-2,y-10),(x-2,y+10)],fill=(234,176,85));d.text((398,387),'ATRIUM',font=font(18),fill=(235,227,206))
d.line([(950,90),(950,48)],fill=(235,227,206),width=3);d.polygon([(943,58),(957,58),(950,42)],fill=(235,227,206));d.text((926,101),'BOW',font=font(17),fill=(235,227,206))
im.save(R/'assets/textures/D13_residential_local_map.png')
