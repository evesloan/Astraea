"""Contact sheets use intact640x360 evidence pixels; only labels are added."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
BASE=Path(__file__).resolve().parents[1];render=BASE/'renders';font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
labels={'near':'Immutable original inlet: 2,327 triangles','baseline':'Exact-profile baseline: 1,608 triangles','economical':'Economical derivative: 1,320 triangles'}
def tile(distance,variant,angle):
 image=Image.open(render/f'{distance}_{variant}_{angle:+03d}deg_640.png').convert('RGB');assert image.size==(640,360)
 out=Image.new('RGB',(640,400),(20,25,29));out.paste(image,(0,40));draw=ImageDraw.Draw(out);draw.text((12,5),labels[variant],font=font,fill='white');draw.text((12,22),f'{distance}: camera orbit {angle:+d} degrees',font=font,fill=(192,206,217));return out
static=Image.new('RGB',(1920,800));
for y,distance in enumerate(('near','repeated')):
 for x,variant in enumerate(('near','baseline','economical')):static.paste(tile(distance,variant,0),(x*640,y*400))
static.save(render/'static_three_way_comparison.png')
metrics=[];files=[]
for distance in('near','repeated'):
 orbit=Image.new('RGB',(1280,1200));frames=[]
 for y,angle in enumerate((-4,0,4)):
  a=tile(distance,'near',angle);b=tile(distance,'economical',angle);orbit.paste(a,(0,y*400));orbit.paste(b,(640,y*400));frame=Image.new('RGB',(1280,400));frame.paste(a,(0,0));frame.paste(b,(640,0));frames.append(frame)
  near=np.asarray(Image.open(render/f'{distance}_near_{angle:+03d}deg_640.png').convert('RGB')).astype(float);eco=np.asarray(Image.open(render/f'{distance}_economical_{angle:+03d}deg_640.png').convert('RGB')).astype(float);diff=np.abs(near-eco);metrics.append({'distance':distance,'angle_degrees':angle,'mean_absolute_rgb_difference_8bit':float(diff.mean()),'pixels_with_any_channel_difference_over8':int((diff.max(2)>8).sum()),'all_pixels':640*360,'interpretation':'Whole-image diagnostic only. Does not isolate visibility, score quality or predict temporal behavior.'})
 orbit.save(render/f'{distance}_controlled_angle_comparison.png');frames[0].save(render/f'{distance}_controlled_angle_comparison.apng',save_all=True,append_images=[frames[1],frames[2],frames[1]],duration=650,loop=0,disposal=0,blend=0)
for path in sorted(render.glob('*')):files.append({'path':str(path.relative_to(BASE)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pixels':list(Image.open(path).size),'kind':'original actual-GLB render'if'_640.png'in path.name else'Lossless contact sheet or APNG with unchanged evidence pixels and labels'})
(BASE/'qa/comparison_media.json').write_text(json.dumps({'scope':'Three static variants and bounded -4/0/+4degree actual640 comparisons; contact sheet pixels are not resampled','files':files,'diagnostic_image_differences':metrics},indent=2)+'\n')
print('COMPARISON_MEDIA_COMPLETE',len(files))
