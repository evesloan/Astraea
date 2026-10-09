from pathlib import Path
import json, hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
handoff=json.loads((OUT/'D09_retail_programme_reference_handoff.json').read_text())
scheme=handoff['bounded_relative_plan_section_proposal']
items={p['catalogue_id']:p for p in scheme['components']}
colors={'AST-RTL-001':'#c96b3e','AST-RTL-002':'#bd9b59','AST-RTL-003':'#517f85'}
fig=plt.figure(figsize=(14,9),layout='constrained',facecolor='#f6f4ee')
grid=fig.add_gridspec(2,2,width_ratios=[1.1,1])
plan=fig.add_subplot(grid[:,0]); wallsec=fig.add_subplot(grid[0,1]); worksec=fig.add_subplot(grid[1,1])
for ax in [plan,wallsec,worksec]:
    ax.set_facecolor('#fcfbf7'); ax.grid(color='#d7d6ce',linewidth=.5); ax.set_axisbelow(True)
    ax.tick_params(labelsize=8)

plan.set_title('PLAN | historical outer allocation, new nominal boxes',loc='left',fontsize=11)
plan.add_patch(Rectangle((-6,0),12,12,fill=False,edgecolor='#253d48',linewidth=1.8))
for r in scheme['proposed_keep_clear_test_regions']:
    plan.add_patch(Rectangle((r['x'][0],r['y'][0]),r['x'][1]-r['x'][0],r['y'][1]-r['y'][0],facecolor='#d9ddde',edgecolor='#77888d',linestyle='--',linewidth=.8))
plan.text(0,.65,'Entire arrival band Y0..1.5\nnew proposal',ha='center',va='center',fontsize=8)
plan.text(0,7.2,'X +/-1.2\nnew clear\ntest strip',ha='center',va='center',fontsize=8)
for cid,p in items.items():
    b=p['sample_source_bounds_xyz_m']
    if not b:continue
    col=colors[cid]
    plan.add_patch(Rectangle((b['x'][0],b['y'][0]),b['x'][1]-b['x'][0],b['y'][1]-b['y'][0],facecolor=col,edgecolor='#263c45',linewidth=1))
    for key in ['sample_approach_xy_m','sample_public_approach_xy_m','sample_staff_approach_xy_m']:
        a=p.get(key)
        if a:
            plan.add_patch(Rectangle((a['x'][0],a['y'][0]),a['x'][1]-a['x'][0],a['y'][1]-a['y'][0],facecolor=col,alpha=.15,edgecolor=col,linestyle=':',linewidth=1.4))
    x=sum(b['x'])/2;y=sum(b['y'])/2
    if cid=='AST-RTL-001':
        plan.text(x,y,'001  WALL BAY',ha='center',va='center',fontsize=8,rotation=90,color='white')
        plan.text(-3.65,3.5,'proposed\nbrowse pad',ha='center',va='center',fontsize=7)
    elif cid=='AST-RTL-002':
        plan.text(x,y,'002\nISLAND',ha='center',va='center',fontsize=8)
        plan.text(x,2.75,'proposed\nbrowse pad',ha='center',va='center',fontsize=7)
    else:
        plan.text(x,y,'003 BENCH',ha='center',va='center',fontsize=8,color='white')
        plan.text(x,7.75,'proposed\npublic pad',ha='center',va='center',fontsize=7)
        plan.text(x,10.1,'proposed\nstaff pad',ha='center',va='center',fontsize=7)
plan.plot([0],[0],'o',color='#263c45',ms=5)
plan.annotate('existing symbolic door datum\nwidth / pockets / head UNKNOWN',xy=(0,0),xytext=(0,-1.12),ha='center',fontsize=8,arrowprops={'arrowstyle':'-','color':'#263c45'})
plan.text(-5.75,11.5,'R070  Kind Curios / 070\n12 x 12 m allocation',fontsize=8,va='top')
plan.annotate('0.30 m nominal gap',xy=(-4.85,1.8),xytext=(-5.9,2.5),fontsize=7,ha='left',arrowprops={'arrowstyle':'-','color':'#263c45'})
plan.set_xlim(-6.6,6.6);plan.set_ylim(-1.7,12.5);plan.set_aspect('equal');plan.set_xlabel('source X (m)');plan.set_ylabel('source Y inward (m)')
plan.set_xticks(range(-6,7,2));plan.set_yticks(range(0,13,2))

def section(ax,title,cids):
    ax.set_title(title,loc='left',fontsize=10)
    ax.axhline(0,color='#253d48',linewidth=1.5)
    ax.axhline(8.25,color='#7e6660',linestyle='--',linewidth=1)
    ax.text(.15,7.95,'8.25 m deck allowance; local ceiling/support UNKNOWN',fontsize=8,va='top',color='#674f49')
    for cid in cids:
        b=items[cid]['sample_source_bounds_xyz_m']
        ax.add_patch(Rectangle((b['y'][0],0),b['y'][1]-b['y'][0],b['z'][1],facecolor=colors[cid],edgecolor='#263c45',linewidth=1))
        ax.text(sum(b['y'])/2,b['z'][1]+.18,f'{cid[-3:]} nominal {b["z"][1]:g} m',fontsize=8,ha='center',va='bottom')
    ax.set_xlim(0,12);ax.set_ylim(-.25,8.65);ax.set_xlabel('source Y inward (m)',fontsize=9);ax.set_ylabel('source Z up (m)',fontsize=9)
    ax.set_xticks(range(0,13,2));ax.set_yticks([0,2,4,6,8.25])
section(wallsec,'SECTION A | source X = -4.85 m | wall-bay nominal box',['AST-RTL-001'])
section(worksec,'SECTION B | source X = +3.20 m | island and workbench',['AST-RTL-002','AST-RTL-003'])
fig.suptitle('R070 partial source inspection | every furnishing size and pad is adjustable',fontsize=14,fontweight='bold',color='#253d48')
fig.supxlabel('Arithmetic box screen only. No actual door sweep, finished host polygon, facility slots, species/cart fit or installed support is established.\nSource-to-ship: (x,y,z) = (78-sourceY, 52.5+sourceZ, 236-sourceX). Container 004 sits on independently verified asset support later.',fontsize=9,color='#3d5058')
fig.savefig(OUT/'R070_nominal_plan_section_screen.png',dpi=160)
plt.close(fig)
meta={'schema':'astraea.d09_nominal_plan_section_screen.v1',
      'source_handoff':'D09_retail_programme_reference_handoff.json','source_handoff_sha256':sha(OUT/'D09_retail_programme_reference_handoff.json'),
      'image':'R070_nominal_plan_section_screen.png','image_sha256':sha(OUT/'R070_nominal_plan_section_screen.png'),
      'basis':'Historical source R070 outer allocation plus parent Batch18 nominal proposals, exactly as embedded in the handoff.',
      'section_planes_source_x_m':[-4.85,3.2],
      'all_furnishings_and_pads_adjustable':True,'actual_host_door_and_slot_geometry_known':False,
      'not_a_masterplan_or_finished_room':True,'image_uses_nominal_boxes_not_authored_asset_meshes':True}
(OUT/'R070_nominal_plan_section_screen.json').write_text(json.dumps(meta,indent=2)+'\n')
(OUT/'SHA256.json').write_text(json.dumps({p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256.json'},indent=2)+'\n')
print(json.dumps(meta,indent=2))
