"""QA contact sheet only; preserve all six original normal-eye PNG bytes."""
import pathlib,json,sys
from PIL import Image,ImageDraw
R=pathlib.Path(__file__).resolve().parent;unit=int(sys.argv[1]);O=R/'sections'/f'{unit}_deluxe';c=json.loads((O/'SECTION_CONTRACT.json').read_text());views=c['source_views'];assert len(views)==6;canvas=Image.new('RGB',(1600,1422),(20,24,28));draw=ImageDraw.Draw(canvas)
for k,v in enumerate(views):
 image=Image.open(O/v['file']).convert('RGB');assert image.size==(800,450);x=(k%2)*800;y=(k//2)*474;draw.text((x+8,y+5),f"Source unit {unit} | {v['name']} | 1.65m eye | no installed acceptance",fill=(240,240,240));canvas.paste(image,(x,y+24))
p=O/'QA_CONTACT_SHEET.png';canvas.save(p);print(p)
