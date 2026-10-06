"""Original vector-authored resort display artwork. No photo/reference pixels.
Creates editable SVG geometry and corresponding packed PNG material sources with
Pillow; this is a texture-authoring step, not Blender/engine scene rendering.
"""
from pathlib import Path
import json,hashlib,math,html
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
FONT=json.loads((ROOT/'content/display_alphabet.json').read_text())['glyphs']
COL={'ivory':'#e9dfc2','sand':'#cbbd92','ink':'#233e41','jade':'#4b806c','deep':'#28574f','sage':'#8ca885','teal':'#3f8989','foam':'#a7cec0','clay':'#c87652','sun':'#dca866','pale':'#c5d7c6','navy':'#263e52'}
class Art:
 def __init__(self,w,h,bg):
  self.w=w;self.h=h;self.s=2;self.im=Image.new('RGB',(w*self.s,h*self.s),bg);self.d=ImageDraw.Draw(self.im);self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',f'<rect width="{w}" height="{h}" fill="{bg}"/>'];self.texts=[]
 def poly(self,p,col):
  self.d.polygon([(round(x*self.s),round(y*self.s))for x,y in p],fill=col);self.svg.append('<polygon points="'+' '.join(f'{x:.3f},{y:.3f}'for x,y in p)+f'" fill="{col}"/>')
 def rect(self,b,col):
  x,y,X,Y=b;self.poly([(x,y),(X,y),(X,Y),(x,Y)],col)
 def ellipse(self,b,col):
  x,y,X,Y=b;self.d.ellipse(tuple(round(v*self.s)for v in b),fill=col);self.svg.append(f'<ellipse cx="{(x+X)/2:.3f}" cy="{(y+Y)/2:.3f}" rx="{(X-x)/2:.3f}" ry="{(Y-y)/2:.3f}" fill="{col}"/>')
 def line(self,p,col,width):
  self.d.line([(round(x*self.s),round(y*self.s))for x,y in p],fill=col,width=max(1,round(width*self.s)),joint='curve');self.svg.append('<polyline points="'+' '.join(f'{x:.3f},{y:.3f}'for x,y in p)+f'" fill="none" stroke="{col}" stroke-width="{width:.3f}" stroke-linejoin="round"/>')
 def text(self,x,y,txt,size,col):
  scale=size/7;start=x
  for ch in txt:
   assert ch==' ' or ch in FONT,ch
   for iy,row in enumerate(FONT.get(ch,['00000']*7)):
    for ix,v in enumerate(row):
     if v=='1':self.rect((x+ix*scale,y+iy*scale,x+(ix+1)*scale,y+(iy+1)*scale),col)
   x+=6*scale
  assert x<=self.w+1,(txt,x,self.w)
  self.texts.append({'text':txt,'bbox_px':[start,y,x,y+size],'glyph_source':'display_alphabet.json'})
 def save(self,name):
  svg=ROOT/'content'/f'{name}.svg';png=ROOT/'textures'/f'{name}.png'
  svg.write_text('\n'.join(self.svg+['</svg>'])+'\n');self.im.resize((self.w,self.h),Image.Resampling.LANCZOS).save(png)
  return svg,png

def wave(a,y,amp,phase,col):
 w,h=a.w,a.h;p=[(0,h),(0,y)]
 for i in range(61):
  x=w*i/60;p.append((x,y+amp*math.sin(x/w*math.pi*2+phase)))
 p.append((w,h));a.poly(p,col)

def leaf(a,base,tip,width,col):
 # Broad, folded original leaf silhouette, one lighter face, not thin scribble stems.
 x,y=base;X,Y=tip;dx,dy=X-x,Y-y;L=math.hypot(dx,dy);nx,ny=-dy/L,dx/L
 p=[(x,y),(x+dx*.28+nx*width*.75,y+dy*.28+ny*width*.75),(x+dx*.67+nx*width,y+dy*.67+ny*width),(X,Y),(x+dx*.62-nx*width*.68,y+dy*.62-ny*width*.68),(x+dx*.25-nx*width*.48,y+dy*.25-ny*width*.48)]
 a.poly(p,col);a.poly([p[0],p[1],p[2],p[3]],COL['sage'])

def sunmark(a,x,y,r,col):
 a.ellipse((x-r,y-r,x+r,y+r),col)
 for j in range(8):
  t=j*math.pi/4;a.line([(x+math.cos(t)*r*1.2,y+math.sin(t)*r*1.2),(x+math.cos(t)*r*1.5,y+math.sin(t)*r*1.5)],col,r*.12)

def header(a,title):
 w,h=a.w,a.h;a.rect((0,0,w,h*.145),COL['ink']);sunmark(a,w*.045,h*.072,h*.023,COL['sun']);a.text(w*.086,h*.044,'SUNCORP',h*.055,COL['ivory']);sz=min(h*.040,w*.42*7/(6*len(title)));a.text(w*.55,h*.051,title,sz,COL['ivory'])

def lagoon(a):
 w,h=a.w,a.h;header(a,'GRAND POOL')
 a.ellipse((w*.52,h*.19,w*.76,h*.19+w*.24),COL['clay'])
 a.poly([(0,h*.56),(w*.13,h*.44),(w*.28,h*.49),(w*.45,h*.57),(w*.65,h*.51),(w*.83,h*.44),(w,h*.51),(w,h),(0,h)],COL['sage'])
 wave(a,h*.60,h*.027,.1,COL['teal']);wave(a,h*.72,h*.038,2,COL['foam']);wave(a,h*.83,h*.03,1,COL['deep'])
 # Elegant foreground foliage occupies one side, leaving the lagoon readable.
 for tx,ty in [(.01,.31),(.14,.24),(.28,.39),(.35,.57),(.00,.56)]:leaf(a,(w*.12,h*.90),(w*tx,h*ty),h*.065,COL['deep'])
 a.text(w*.36,h*.842,'PAUSE BY THE WATER',h*.045,COL['ivory'])

def market(a):
 w,h=a.w,a.h;header(a,'ORCHARD MARKET')
 a.ellipse((w*.56,h*.24,w*.90,h*.24+w*.34),COL['sun']);a.rect((0,h*.78,w,h),COL['clay'])
 # Still life: broad plant in a terracotta bowl, market fruit, shade shapes.
 a.poly([(w*.49,h*.56),(w*.83,h*.56),(w*.79,h*.83),(w*.55,h*.83)],COL['clay']);a.rect((w*.475,h*.545,w*.845,h*.61),COL['ink'])
 for tx,ty in [(.43,.35),(.47,.19),(.60,.17),(.73,.21),(.89,.31),(.92,.53)]:leaf(a,(w*.65,h*.565),(w*tx,h*ty),h*.053,COL['deep'])
 a.text(w*.04,h*.25,'LIVING',h*.085,COL['ink']);a.text(w*.04,h*.36,'GIFTS',h*.085,COL['ink'])
 for j,col in enumerate([COL['sun'],COL['sage'],COL['ivory']]):a.ellipse((w*(.08+j*.09),h*.58,w*(.08+j*.09)+h*.13,h*.71),col)
 a.text(w*.055,h*.865,'PLEASE KEEP WALKWAYS CLEAR',h*.043,COL['ivory'])

def ambient(a):
 w,h=a.w,a.h;header(a,'QUIET MOMENTS')
 a.rect((0,h*.145,w,h),COL['navy']);a.ellipse((w*.47,h*.20,w*.76,h*.20+w*.29),COL['sun']);a.ellipse((w*.505,h*.173,w*.765,h*.173+w*.26),COL['navy'])
 a.poly([(0,h*.59),(w*.19,h*.46),(w*.35,h*.53),(w*.53,h*.59),(w*.77,h*.50),(w,h*.57),(w,h),(0,h)],COL['jade'])
 wave(a,h*.67,h*.026,.4,COL['teal']);wave(a,h*.79,h*.025,2.4,COL['foam']);wave(a,h*.89,h*.028,.4,COL['deep'])
 for x,y,r in [(.11,.30,.004),(.27,.24,.003),(.38,.34,.004),(.83,.26,.003),(.92,.39,.003)]:a.ellipse((w*x-h*r,h*y-h*r,w*x+h*r,h*y+h*r),COL['ivory'])
 a.rect((0,h*.835,w,h),COL['deep']);a.text(w*.07,h*.882,'A MOMENT TO UNWIND',h*.048,COL['ivory'])

def pool(a):
 w,h=a.w,a.h;header(a,'GRAND POOL')
 a.ellipse((w*.54,h*.20,w*.82,h*.20+w*.28),COL['clay']);a.poly([(0,h*.52),(w*.19,h*.37),(w*.36,h*.45),(w*.60,h*.50),(w*.86,h*.42),(w,h*.50),(w,h),(0,h)],COL['sage'])
 wave(a,h*.55,h*.036,0,COL['teal']);wave(a,h*.67,h*.048,1.6,COL['foam']);wave(a,h*.81,h*.029,2.5,COL['deep'])
 for tx,ty in [(.0,.22),(.12,.18),(.29,.29),(.37,.43)]:leaf(a,(w*.12,h*.58),(w*tx,h*ty),h*.048,COL['deep'])
 a.text(w*.075,h*.852,'PLEASE WALK ON WET DECKS',h*.039,COL['ivory'])

if __name__=='__main__':
 specs=[('sun_corp_lagoon',1536,838,lagoon,'Original SunCorp Grand Pool welcome and calm lagoon composition.'),('orchard_market_still_life',1536,812,market,'Original Orchard Market living-gifts still life and clear-walkways courtesy notice.'),('sun_corp_orbital_tide',1536,812,ambient,'Original abstract orbital-tide ambient vista, quiet-moments resort content.'),('grand_pool_wet_deck',1536,988,pool,'Original Grand Pool water vista and walk-on-wet-decks courtesy notice.')]
 records={}
 for name,w,h,maker,description in specs:
  a=Art(w,h,COL['ivory']);maker(a);svg,png=a.save(name)
  records[name]={'file':str(png.relative_to(ROOT)),'svg_source':str(svg.relative_to(ROOT)),'sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'svg_sha256':hashlib.sha256(svg.read_bytes()).hexdigest(),'size_px':[w,h],'description':description,'texts':a.texts,'roughness':.34,'emission_strength':.18,'base_color_and_emission':'same original packed image','uv_mapping':'one full artwork per image face; positive handedness independently tested','third_party_pixel_inputs':[],'interactive_or_streaming_function':False}
 manifest={'revision':'grand-pool-leisure-art-01','generator':'content/make_pool_leisure_art.py','generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'glyphs':'content/display_alphabet.json','glyphs_sha256':hashlib.sha256((ROOT/'content/display_alphabet.json').read_bytes()).hexdigest(),'provenance':'Original geometric vector composition and in-world static resort courtesy copy. Family alphabet reused; no original library UI or external reference pixels. SVG shapes and packed PNG are reproducible. No functioning controls, schedule, live state, streaming or destination claims.','material_roles':records}
 (ROOT/'content_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('ART_SOURCES_READY',len(records))
