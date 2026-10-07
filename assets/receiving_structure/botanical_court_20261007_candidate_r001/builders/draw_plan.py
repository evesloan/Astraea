from pathlib import Path
import json
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon,Rectangle
R=Path(__file__).resolve().parent;g=json.loads((R/'NATIVE_GEOMETRY.json').read_text())
def hull(points):
 p=sorted(set(points));cross=lambda a,b,c:(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);lo=[];hi=[]
 for x in p:
  while len(lo)>1 and cross(lo[-2],lo[-1],x)<=0:lo.pop()
  lo.append(x)
 for x in reversed(p):
  while len(hi)>1 and cross(hi[-2],hi[-1],x)<=0:hi.pop()
  hi.append(x)
 return lo[:-1]+hi[:-1]
fig,ax=plt.subplots(figsize=(8,10));ax.add_patch(Rectangle((-8,-238),16,30,color='#ddd2b8'));ax.add_patch(Rectangle((-4,-242),8,38,color='#afbcb6'))
for o in g['objects']:
 if 'GuardPlinth' in o['name']:ax.add_patch(Polygon(hull([(v[0],v[2]) for v in o['vertices_world']]),color='#615140' if 'PORTAL_CLOSURE' not in o['name'] else '#c05f31'))
for x,txt in [(-6.2,'Moss sanctuary\nENTRY NOT OPEN'),(6.2,'Botanical nursery\nENTRY NOT OPEN')]:
 ax.plot([0,0,x],[-240,-216,-216],color='#286b77',linewidth=2);ax.scatter([x],[-216],color='#286b77');ax.text(x,-211.8,txt,ha='center',fontsize=8,bbox=dict(facecolor='white',alpha=.85,edgecolor='none'))
ax.text(0,-233,'Existing axial route\n8 m kept clear',ha='center');ax.text(-11,-226,'No installed\nroom floor\nor enclosure',ha='center',fontsize=9);ax.text(11,-226,'No installed\nroom floor\nor enclosure',ha='center',fontsize=9)
ax.set_xlim(-14,14);ax.set_ylim(-242,-204);ax.set_aspect('equal');ax.set_xlabel('Ship X / metres');ax.set_ylabel('Ship Z / metres');ax.set_title('Closed interim botanical receiving court\nSource geometry plan, not an engine image');ax.grid(alpha=.2);fig.tight_layout();fig.savefig(R/'CLOSED_RECEIVING_PLAN.png',dpi=150)
