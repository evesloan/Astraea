from pathlib import Path
import os,json
os.environ.setdefault('MPLCONFIGDIR','/tmp/astraea_gpm_matplotlib')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PatchPolygon,Rectangle
R=Path(__file__).resolve().parents[1];D=json.loads((R/'source/connected_contract.json').read_text())
fig=plt.figure(figsize=(16,10),facecolor='#f5f2eb');gs=fig.add_gridspec(2,2,height_ratios=[1.3,1],hspace=.32,wspace=.18)
colors={'floor':'#e7d7b5','wet':'#b6d9d4','pool':'#5faaa9','ramp':'#dfae62','void':'#f5f2eb','line':'#344a52'}
def poly(ax,p,color,alpha=1,lw=.7):ax.add_patch(PatchPolygon(p,facecolor=color,edgecolor=colors['line'],linewidth=lw,alpha=alpha))
def rect(ax,r,y0,h,color,**kw):ax.add_patch(Rectangle((r[0],y0),r[1]-r[0],h,facecolor=color,**kw))
for idx,(name,fy)in enumerate([('D08 • raised wet floor 46.20 m / arrival 44.00 m',46.2),('D09 • dry gallery + separated wet arrivals 52.50 m',52.5)]):
 ax=fig.add_subplot(gs[0,idx]);ax.set_facecolor(colors['void']);floor=next(f for f in D['floor_regions']if f['id']==('D08_grand_pool_wet'if idx==0 else'D09_orchard_market_gallery'))
 poly(ax,[[-54,-466],[-8,-466],[-8,-398],[-54,-398]],'#ddd8d0')
 poly(ax,floor['boundary'],colors['wet']if idx==0 else colors['floor'])
 for h in floor['holes']:poly(ax,h,colors['void'])
 poly(ax,[[-40,-457],[-22,-457],[-22,-407],[-40,-407]],colors['pool'],.85)
 ax.text(-31,-432,'50 × 18 m\nclear lane',ha='center',va='center',fontsize=10,color='#173d43')
 if idx==0:
  for x0,x1,z0,z1 in[[-13.2,-10.8,-462.2,-449],[-16.4,-14,-462.2,-449],[-16.4,-10.8,-464.6,-462.2]]:poly(ax,[(x0,z0),(x1,z0),(x1,z1),(x0,z1)],colors['ramp'])
  ax.text(-14.5,-469,'2 × 13.2 m ramp runs • 1:12\n2.4 m clear runs and landings',ha='center',va='top',fontsize=8)
  route=D['accessible_ramp']['route_xyz'];ax.plot([p[0]for p in route],[p[2]for p in route],color='#975214',lw=1.5)
  ax.text(-12,-438,'dry\narrival',ha='center',fontsize=8)
 else:
  q=D['market']['adopted_dry_loop_centreline_xz'];ax.plot([p[0]for p in q],[p[1]for p in q],color='#a0522d',lw=1.5,ls='--');ax.text(-51,-432,'orange\nrecessed\nfrontage',ha='center',fontsize=8)
  for z in[-428,-406.9]:ax.plot([-17.13,-11.97],[z,z],color='#7c3026',lw=2)
  ax.text(-12,-420,'wet-side\nlocal link',ha='center',fontsize=7,rotation=90)
 for b in D['bearings']:
  x0,x1=b['x'];z0,z1=b['z'];poly(ax,[(x0,z0),(x1,z0),(x1,z1),(x0,z1)],'#71818c');ax.text((x0+x1)/2,z1+.8,'seat',ha='center',fontsize=6)
 ax.plot([-8,-4],[-432,-432],color='#5e7952',lw=3);ax.text(-3.5,-432,'existing\ncore',ha='left',va='center',fontsize=8)
 ax.set_xlim(-64,1);ax.set_ylim(-474,-394);ax.set_aspect('equal');ax.set_title(name,loc='left',fontsize=11,fontweight='bold');ax.set_xlabel('X (metres)');ax.set_ylabel('Z (metres)');ax.grid(alpha=.16)
ax=fig.add_subplot(gs[1,:]);ax.set_facecolor(colors['void']);ax.add_patch(Rectangle((-466,35.5),68,8.26,facecolor='#e1d9d9',hatch='///',edgecolor='#c6b8b8',lw=.5));ax.text(-432,39.5,'D07 ORBIT COURT • protected clear band • no new material below 43.76 m',ha='center',fontsize=9)
ax.add_patch(Rectangle((-466,61),68,3,facecolor='#e1d9d9',hatch='///',edgecolor='#c6b8b8',lw=.5));ax.text(-432,62.2,'D10 SHARED TABLE • unchanged full allocation above 61.00 m',ha='center',fontsize=9)
ax.add_patch(Rectangle((-466,43.76),68,.24,facecolor='#8d969b'));ax.add_patch(Rectangle((-457.4,44.4),50.8,.4,facecolor='#448889'))
for z in[-451,-440,-429,-418,-408]:ax.add_patch(Rectangle((z-.24,43.76),.48,.64,facecolor='#566672'))
for z0,z1 in[(-466,-457.4),(-406.6,-398)]:ax.add_patch(Rectangle((z0,45.96),z1-z0,.24,facecolor='#8d969b'))
ax.add_patch(Rectangle((-457,44.8),50,1.25,facecolor=colors['pool'],alpha=.7));ax.plot([-457,-407],[46.05,46.05],color='#287b86',lw=1)
for z0,z1 in[(-466,-461),(-403,-398)]:ax.add_patch(Rectangle((z0,52.26),z1-z0,.24,facecolor='#8d969b'))
for z in[-461,-403]:ax.add_patch(Rectangle((z-.24,51.08),.48,1.18,facecolor='#c6b392'));ax.add_patch(Rectangle((z-.05,52.5),.1,8.26,facecolor='#72a7ad',alpha=.8))
for z in[-451,-433,-416]:ax.add_patch(Rectangle((z-.22,59.16),.44,1.60,facecolor='#b5a487'))
ax.add_patch(Rectangle((-466,60.76),68,.24,facecolor='#8d969b'))
for y,label in[(43.76,'43.76 protection'),(44.8,'44.80 basin floor'),(46.2,'46.20 wet'),(52.5,'52.50 market'),(61,'61.00 D10')]:ax.axhline(y,color='#4d6269',ls=':',lw=.6);ax.text(-397.3,y,label,va='center',fontsize=8)
ax.text(-431,49.5,'open pool volume; no bridges or islands in lane',ha='center',fontsize=9);ax.text(-431,57.0,'full-height glazed wet/dry boundary at upper gallery edge\nroof ribs stay below the protected D10 slab',ha='center',fontsize=9)
ax.set_xlim(-470,-388);ax.set_ylim(34.5,64);ax.set_title('Axial pool section at X−31 • perimeter bearings appear in plans above',loc='left',fontsize=11,fontweight='bold');ax.set_xlabel('Z (metres)');ax.set_ylabel('Y (metres)');ax.grid(alpha=.15)
fig.suptitle('GRAND POOL / ORCHARD MARKET • EDITABLE SOURCE SECTION',x=.05,ha='left',fontsize=16,fontweight='bold');fig.text(.05,.025,'Source geometry and exact floor contract only. Compiler-owned slabs are excluded from the GLB. No load certification, water simulation or in-game acceptance.',fontsize=9)
fig.savefig(R/'qa/dimensioned_plan_section.png',dpi=140,bbox_inches='tight');print('dimensioned_plan_section.png')
