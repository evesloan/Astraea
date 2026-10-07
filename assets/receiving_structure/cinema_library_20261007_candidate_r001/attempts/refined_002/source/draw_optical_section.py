from pathlib import Path
import json,sys,hashlib,os
os.environ['MPLCONFIGDIR']='/tmp/astraea_matplotlib_receiving'
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'inputs'));from decode_sections import glb
M,N=glb(O/'exports/cinema_library_receiving_r001.glb',np.zeros(3));fig,ax=plt.subplots(figsize=(15,5.8));fig.patch.set_facecolor('#f4f3ef');ax.set_facecolor('#fbfaf7')
# Exact actual-file X36 cut: collect edge crossings of every triangle.
for m in M:
 if not m['min'][0]-1e-6<=36<=m['max'][0]+1e-6:continue
 for tri in m['vertices'][m['faces']]:
  pts=[]
  for a,b in zip(tri,np.roll(tri,-1,axis=0)):
   aa=a[0]-36;bb=b[0]-36
   if abs(aa)<1e-6:pts.append(a)
   if aa*bb<0:pts.append(a+(b-a)*(-aa/(bb-aa)))
  if len(pts)>=2:ax.plot([p[2] for p in pts],[p[1] for p in pts],color='#43505a',linewidth=.9,zorder=4)
z0=-416.0125;z1=-459.47;ax.fill([z1,z0,z0,z1],[70.7,73.52,73.84,75.7],color='#51a2c3',alpha=.23,label='Complete bounded finite-aperture cone at X36')
ax.plot([z1,z0],[75.7,73.84],color='#297c9b',linewidth=1.8);ax.plot([z1,z1],[70.7,75.7],color='#166590',linewidth=5,label='Retained screen: Y70.70–75.70')
ax.plot([-462,-451.4],[76.95,76.95],'--',color='#a35878',linewidth=1.5,label='WP13 future acoustic finish, NOT in receiving export');ax.plot([-451.4,-398.2],[75.55,75.55],'--',color='#a35878',linewidth=1.5)
ax.scatter([z0],[73.68],color='#166590',s=36);ax.text(z0+1,73.7,'Retained lens aperture',fontsize=9,color='#166590')
critical=json.load(open(O/'inputs/SELECTED_RECEIVING_SECTION_R1.json'))['optical_final'][0]
ax.annotate('Critical front edge: Z−451.4\nStructure clearance: 0.2954 m\nFuture finish clearance: 0.1954 m',xy=(-451.4,75.3546),xytext=(-442.8,70.35),arrowprops={'arrowstyle':'->','color':'#a35878'},fontsize=10,color='#793b56',bbox={'boxstyle':'round,pad=.45','fc':'#fbfaf7','ec':'#c9bcc1'})
ax.text(-464.5,78.23,'Library plate top Y78.00',fontsize=10,color='#43505a');ax.text(-466.6,69.63,'Root D11 plate: Y69.26–69.50',fontsize=9,color='#43505a')
ax.set_xlim(-468,-397);ax.set_ylim(69,79);ax.set_xlabel('Ship world Z (m) · vertical scale exaggerated');ax.set_ylabel('World height Y (m)');ax.grid(alpha=.12);ax.legend(loc='lower right',fontsize=8,framealpha=.9)
fig.suptitle('Cinema / Library receiving candidate · measured optical section at X36',x=.125,ha='left',fontsize=15,fontweight='bold')
fig.text(.125,.012,'Actual decoded GLB section. Dashed finishes are source-owner proposals. Old roof/vault must be revised before adoption. No runtime or engineering certification.',fontsize=8,color='#50535a')
fig.tight_layout(rect=(0,.04,1,.94));fig.savefig(O/'views/05_optical_section_MEASURED.png',dpi=130);fig.savefig(O/'views/05_optical_section_MEASURED.svg')
(O/'qa/optical_section_binding.json').write_text(json.dumps({'source_glb_sha256':hashlib.sha256((O/'exports/cinema_library_receiving_r001.glb').read_bytes()).hexdigest(),'slice_world_x':36,'critical_front_edge_z':-451.4,'retained_screen_extent_y':[70.7,75.7],'full_frustum_checks':'qa/decoded_glb_checks.json','critical':critical,'scope':'Measured diagram, not a render or an installed composition'},indent=2))
