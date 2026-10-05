from pathlib import Path
import json,textwrap
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];p=json.loads((R/'data/architecture/D18_COMMAND_CROWN_PROPOSAL.json').read_text())
im=Image.new('RGB',(1440,1020),'#faf9f5');d=ImageDraw.Draw(im)
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
d.text((35,25),'ASTRAEA / D18 COMMAND CROWN STUDY',font=font(28),fill='#203943')
d.text((35,67),'Reversible proposal: ten programmes retained, with a compact raised upper profile. No rooms or source allocations moved.',font=font(16),fill='#8c4b45')
def point(x,z):return(88+(z+180)*3.5,340+x*3.5)
for c in p['screened_side_corridor_reservations']:
 d.polygon([point(x,z)for x,z in [(c['x'][0],c['z'][0]),(c['x'][1],c['z'][0]),(c['x'][1],c['z'][1]),(c['x'][0],c['z'][1])]],fill='#bdcdd4')
c=p['public_gallery_reservation'];d.polygon([point(x,z)for x,z in [(c['x'][0],c['z'][0]),(c['x'][1],c['z'][0]),(c['x'][1],c['z'][1]),(c['x'][0],c['z'][1])]],fill='#d9c795')
d.polygon([point(x,z)for x,z in p['preserved_central_core']['boundary']],fill='#68b39c',outline='#296b5d',width=2)
for r in p['programmes']:
 pts=r['proposed_floor_boundary'];d.polygon([point(x,z)for x,z in pts],fill='#dbe6e8'if r['programme_key'].endswith('09')else'#e2e3dc',outline='#465962',width=2)
 x=(min(t[0]for t in pts)+max(t[0]for t in pts))/2;z=(min(t[1]for t in pts)+max(t[1]for t in pts))/2
 lines=textwrap.wrap(r['name'],16);px,py=point(x,z)
 for i,line in enumerate(lines):d.text((px,py+(i-len(lines)/2)*18),line,font=font(13),fill='#203943',anchor='mm')
d.text((35,120),'PROPOSED / 350m long × 72m wide / floor106.5m / roof still to resolve within118m envelope',font=font(19),fill='#203943')
d.text((35,155),'Bow left / port above. Green: installed central core. Ochre: public gallery. Blue-grey: screened side corridors.',font=font(16),fill='#465962')
d.text((35,500),'The bridge is a shaped controlled terminal; Upper Horizon is a separate public viewing destination.',font=font(18),fill='#203943')
d.text((35,536),'Corridor colours show intent, not tested access. Staff-riser links, doors, glazing, supports and station layouts remain to fit.',font=font(16),fill='#465962')
d.text((35,593),'INHERITED D18 ALLOCATIONS / same programme identities, currently spanning932m',font=font(19),fill='#203943')
def oldpt(x,z):return(95+(z+541)*1.15,760+x*1.15)
for r in p['programmes']:
 a=r['source_allocation'];pts=[(a['x'][0],a['z'][0]),(a['x'][1],a['z'][0]),(a['x'][1],a['z'][1]),(a['x'][0],a['z'][1])]
 d.polygon([oldpt(x,z)for x,z in pts],fill='#e7d7d3',outline='#a34b46',width=2)
 x=sum(a['x'])/2;z=sum(a['z'])/2;d.text(oldpt(x,z),r['programme_key'][-2:],font=font(13),fill='#6f3935',anchor='mm')
d.line([oldpt(0,-541),oldpt(0,541)],fill='#b2b7b8',width=1)
d.text((35,925),'D17 guest houses and81luxury replacements still need a coordinated section. Counts and existing built architecture remain unchanged.',font=font(16),fill='#8c4b45')
d.text((35,960),'A massing/layout study, not an in-engine view or completed ship. Source reference composition guides the stepped silhouette.',font=font(16),fill='#465962')
im.save(R/'docs/whole_ship_plans/D18_command_crown_proposal.png')
