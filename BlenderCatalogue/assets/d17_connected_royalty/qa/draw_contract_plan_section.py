from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle
R=Path(__file__).resolve().parents[1];D=json.loads((R/'source/connected_contract.json').read_text())
fig,(ax,sec)=plt.subplots(1,2,figsize=(16,10),gridspec_kw={'width_ratios':[1.1,1]});fig.patch.set_facecolor('#f5f3ed')
colors=['#ddcab2','#c6ddd5','#decbb4','#e5dfcd']
for r,c in zip(D['floor_regions'],colors):ax.add_patch(Polygon(r['boundary'],facecolor=c,edgecolor='#344740',lw=1.5))
for g in D['guards']:ax.plot([g['a_xz'][0],g['b_xz'][0]],[g['a_xz'][1],g['b_xz'][1]],color='#537f82',lw=3)
for key,color in [('private_stair','#aa6771'),('private_lift_and_landing','#8476aa'),('care_service','#9d8448')]:
 r=D['reservations'][key];ax.add_patch(Rectangle((r['x'][0],r['z'][0]),r['x'][1]-r['x'][0],r['z'][1]-r['z'][0],fill=False,edgecolor=color,ls='--',lw=1.5));ax.text(sum(r['x'])/2,sum(r['z'])/2,key.replace('private_','').replace('_and_landing','').replace('_','\n')+'\nreserved',ha='center',va='center',fontsize=7,color=color)
for z0,z1 in [(29.15,30.9),(33.9,35.25)]:ax.add_patch(Rectangle((96.84,z0),.32,z1-z0,color='#7e6a52'))
ax.plot([99.2,99.2,101.5],[35.5,39.8,41.5],color='#7e6a52',lw=3)
route=[[80,14],[80,21.5],[82,25],[88,25],[92,25.9],[92.4,30],[95,32.4],[101,33],[107,36],[113,40]]
ax.plot(*zip(*route),color='#30618a',ls='--',lw=1.2);ax.scatter(*zip(*route),s=8,color='#30618a')
ax.text(79.8,16.7,'3 m approach',rotation=90,ha='center',fontsize=8);ax.text(85.7,24,'Faceted court\nlanding',ha='center',fontsize=9);ax.text(109,40,'ROYALTY 790\nLower platform 461.5 m²\nView-led asymmetric edge',ha='center',fontsize=9)
ax.text(99,31,'Recessed arrival\n3 m clear at X97',fontsize=7);ax.text(95,53,'814 reserved at Z51..61\nNo historical overlapping allocation adopted',fontsize=8)
ax.plot([78.5,81.5],[14,14],color='#cf733a',lw=4);ax.annotate('Existing floor seam Z14\nAft portal Z13.2; fore closed',(80,14),(84,15),arrowprops={'arrowstyle':'->'},fontsize=8)
ax.set(xlim=(75,120),ylim=(11,57),xlabel='World X (m)',ylabel='World Z aft (m)',title='Plan: 605.2 m² desired union, compiler-owned slab');ax.set_aspect('equal');ax.grid(alpha=.15)
sec.add_patch(Rectangle((86.05,97.5),12.9,4.26,facecolor='#ded3ca',edgecolor='#9d6a62',hatch='//',alpha=.5));sec.text(93,99.5,'Protected D16 source590\nNo dropped beam or pit',ha='center',fontsize=9)
sec.add_patch(Rectangle((94,101.76),24,.24,facecolor='#bdb3a0',edgecolor='#344740'));sec.add_patch(Rectangle((107.6,100.56),.8,1.2,facecolor='#aa8859'));sec.text(109,100.8,'Exact retained X108\ntop transfer',fontsize=8)
sec.add_patch(Rectangle((94,106.08),24,.18,facecolor='#d8c8b7',edgecolor='#344740'))
for x in [94,118]:sec.add_patch(Rectangle((x-.05,101.76),.1,4.22,facecolor='#aa8859'))
sec.plot([94,118],[106.5,106.5],ls='--',color='#7c6b94');sec.plot([94,118],[112,112],ls='--',color='#7c6b94');sec.text(105,108.5,'Same-unit upper reserved\nNo upper opening or shaft pit built',ha='center',color='#7c6b94',fontsize=10)
for y,label in [(97.5,'D16 97.5'),(101.76,'Slab soffit101.76'),(102,'D17 floor102'),(106.26,'Lower roof106.26'),(106.5,'Private upper106.5'),(112,'Reserved roof≤112')]:
 sec.annotate(label,(118,y),(120,y+(0.3 if y in [102,106.5]else -.25 if y in [101.76,106.26]else 0)),fontsize=8,arrowprops={'arrowstyle':'-','lw':.6},va='center')
sec.set(xlim=(85,130),ylim=(96,113),xlabel='World X (m)',ylabel='World Y up (m)',title='Section Z42: lower home volume protected');sec.set_aspect('equal');sec.grid(alpha=.15)
fig.suptitle('AST-RES-006 / Connected aft D17 architectural source contract',fontsize=16)
fig.text(.5,.035,'Source plan and reservation section only. No engine, occupied capacity, private upper completion, or whole-ship acceptance claimed.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.06,1,.94));fig.savefig(R/'qa/dimensioned_plan_section.png',dpi=160)
