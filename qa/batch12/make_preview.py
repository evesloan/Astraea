"""Contact sheet of actual frozen inspection frames; pixels are not altered."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
ROOT=Path(__file__).resolve().parents[2];base=ROOT/'qa/batch12/assembly/r02'
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';f=lambda n:ImageFont.truetype(font,n)
canvas=Image.new('RGB',(1280,892),(26,32,36));d=ImageDraw.Draw(canvas)
d.text((24,16),'ASTRAEA / FORWARD CARE COMPONENTS',font=f(25),fill=(242,238,226))
d.text((24,52),'Four editable source designs; shown in a fictional D05 component inspection arrangement',font=f(17),fill=(200,210,211))
frames=[('privacy_closed_arrival','Privacy closed / standing inspection'),('privacy_open_arrival','Privacy open / same camera and lights'),('clinical_working_side','Support, wash and supply / working-side view'),('wash_work_view','Real wash recess / ordinary 1.65m close inspection')];inputs=[]
for i,(name,label) in enumerate(frames):
 p=base/(name+'.png');im=Image.open(p).convert('RGB');assert im.size==(640,360);x=i%2*640;y=84+i//2*390;canvas.paste(im,(x,y));d.text((x+14,y+365),label,font=f(14),fill=(230,228,219));inputs.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
d.text((24,871),'State derivatives count once. Original room fit, operating behavior and species suitability remain to be checked.',font=f(14),fill=(197,205,207))
out=ROOT/'qa/batch12/Astraea_Batch12_Component_Preview.png';canvas.save(out)
(ROOT/'qa/batch12/preview_manifest.json').write_text(json.dumps({'scope':'Labelled actual imported-component views with unchanged raw pixels','inputs':inputs,'output':str(out.relative_to(ROOT)),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2)+'\n');print(out)
