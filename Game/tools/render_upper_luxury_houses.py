from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];p=json.loads((R/'data/architecture/D17_LUXURY_HOUSES_PROPOSAL.json').read_text());g=json.loads((R/'data/reference/historical_guest_census.json').read_text())['guest_envelopes'];h=json.loads((R/'data/hull_envelope.json').read_text())['plan_xz_m'];a=[r for r in json.loads((R/'data/reference/directory_allocations.json').read_text())['records']if r['deck']==17]
im=Image.new('RGB',(1440,1050),'#faf9f5');d=ImageDraw.Draw(im)
def f(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
colours={'deluxe':'#dcc68b','premium':'#8db9c3','royalty':'#9976ad','supreme':'#bf6f7e'}
d.text((32,24),'ASTRAEA / D17 LUXURY HOUSE STUDY',font=f(28),fill='#203943')
d.text((32,68),'81 replacements counted within1,000units / 67 footprint proposals / 14central homes still unlocated',font=f(19),fill='#8c4b45')
d.text((32,104),'Partial reversible plan. Original allocations, built rooms, identities and deck heights remain unchanged.',font=f(16),fill='#465962')
def draw_plan(point,width):
 d.polygon([point(x,z)for x,z in h],fill='#e8edee',outline='#617780',width=width)
 for r in a:
  x,z=r['x'],r['z'];d.polygon([point(x[0],z[0]),point(x[1],z[0]),point(x[1],z[1]),point(x[0],z[1])],fill='#607d86',outline='#345460',width=width)
 for index in p['retained_D17_standard_source_indices']:
  r=g[index];x,z=r['x'],r['z'];d.polygon([point(x[0],z[0]),point(x[1],z[0]),point(x[1],z[1]),point(x[0],z[1])],fill='#abb0b0',outline='#646b6d',width=1)
 for r in p['replacements']:
  if r['proposed_floor_boundary']:d.polygon([point(x,z)for x,z in r['proposed_floor_boundary']],fill=colours[r['tier']],outline='#465962',width=width)
draw_plan(lambda x,z:(65+(z+541)*1.2,310+x*1.2),1)
d.text((32,480),'Gold: court-facing deluxe / Blue: space-view premium / Purple: two-level royalty / Slate: protected commons / Grey: retained standards',font=f(16),fill='#465962')
d.text((32,522),'PORT FORWARD HOUSE / architecture and view gaps before furniture',font=f(20),fill='#203943')
# A clipped zoom keeps the full hull drawing from escaping its assigned panel.
zoom=Image.new('RGB',(900,350),'#faf9f5');old=d;d=ImageDraw.Draw(zoom)
draw_plan(lambda x,z:(20+(z+480)*3.5,20+(x+122)*3.5),2)
d=old;im.paste(zoom,(32,560))
d.text((955,580),'Broad commons opening',font=f(19),fill='#203943')
d.text((955,615),'Court-facing inner homes',font=f(17),fill='#756135')
d.text((955,645),'Hull-shaped outer homes',font=f(17),fill='#3f737e')
d.text((955,675),'Local upper pavilions',font=f(17),fill='#765088')
d.text((955,725),'No full-height flat stack',font=f(17),fill='#465962')
d.text((955,753),'is implied by this plan.',font=f(17),fill='#465962')
d.text((32,955),'Central Supreme/Royalty fit, roof sections, private lifts, species support, access, beds and actual windows are still unresolved.',font=f(16),fill='#8c4b45')
d.text((32,990),'Five planning checks pass. This is a footprint study, not an in-engine screenshot or finalized accommodation.',font=f(16),fill='#465962')
im.save(R/'docs/whole_ship_plans/D17_luxury_house_proposal.png')
