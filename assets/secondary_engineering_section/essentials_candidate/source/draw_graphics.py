"""Original static engineering pigment artwork; no telemetry or emission."""
from pathlib import Path
import runpy,json,hashlib
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
# Reuse the original editable atlas layout, not any reference photograph.
s=(C/'assets/utility_console/textures/draw_console_graphics.py').read_text()
s=s.replace("ROOT=Path(__file__).resolve().parent",f"ROOT=Path({str(R/'textures')!r})")
s=s.replace('UTILITY RETURN','PLANT INSPECTION').replace('FLOW PATH  /  03','CONTAINED ASSEMBLY / 02').replace('WATER RECOVERY','ENGINEERING').replace("'UC-03'","'SE-02'").replace("'FILTER'","'CORE'").replace("'CIRCULATE'","'SUPPORT'").replace("'RETURN'","'INSPECT'").replace("'START'","'VIEW'").replace('CONTROL WIRING  /  UC-03','STATIC PANEL / NOT COMMISSIONED').replace("'ΔP'","'REF'").replace("'RELATIVE'","'REFERENCE'")
exec(compile(s,'retained_console_atlas_layout','exec'),{'__file__':str(R/'source/draw_graphics.py')})
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
labels=[('SECONDARY ENGINEERING','CONTAINED PLANT / VIEWING GALLERY'),('SERVICE WORKBAY','INSPECTION  •  REPAIR  •  RETURN'),('HAND TOOLS','RETURN TO OUTLINE AFTER USE'),('TECHNICAL SPARES','CLOSED STORAGE / IDENTIFY CONTENTS'),('CLEAN RETURNS','BAGGED ITEMS / AWAITING COLLECTION'),('ISOLATION PANEL','STATIC INSTALLATION / NOT COMMISSIONED'),('MAINTENANCE INSTRUMENT','REFERENCE DISPLAY / NO LIVE READINGS'),('LOCAL CONTROL','PRINTED SCHEMATIC / NO LIVE READINGS'),('QUARANTINE HOLD','UNASSESSED PARTS / KEEP SEPARATE'),('CONSUMABLES','CLEAN SUPPLIES / CLOSED STORAGE')]
im=Image.new('RGB',(1024,1280),(39,52,56));d=ImageDraw.Draw(im)
for i,(title,sub) in enumerate(labels):
 y=i*128;d.rounded_rectangle((8,y+8,1016,y+120),radius=12,fill=(184,192,185),outline=(96,122,128),width=4);d.rectangle((20,y+20,33,y+108),fill=(58,85,100));d.text((54,y+21),title,font=ImageFont.truetype(font,37),fill=(38,52,57));d.text((56,y+76),sub,font=ImageFont.truetype(font,22),fill=(63,77,78))
im.save(R/'textures/engineering_signs.png')
(R/'textures/artwork_manifest.json').write_text(json.dumps({'scope':'Original static printed artwork, no live values or emission','labels':labels,'console_layout_source':'assets/utility_console/textures/draw_console_graphics.py','font':font,'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'textures').glob('*.png')}},indent=2)+'\n')
