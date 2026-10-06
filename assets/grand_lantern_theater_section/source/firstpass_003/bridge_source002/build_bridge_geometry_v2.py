"""Approved compact receiving portico. Compiler owns the 183m² slab."""
from pathlib import Path
import json,math,hashlib,numpy as np
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');objects=[];lights=[];F=69.5
FACES=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
def emit(name,v,f,mat,role,**extra):
 v=np.array(v,dtype=float);center=v.mean(0);volume=sum(np.dot(v[q[0]]-center,np.cross(v[q[i]]-center,v[q[i+1]]-center))/6 for q in f for i in range(1,len(q)-1))
 if volume<0:f=[list(reversed(q))for q in f];volume=-volume
 counts={}
 for q in f:
  for a,b in zip(q,q[1:]+q[:1]):key=tuple(sorted((a,b)));counts[key]=counts.get(key,0)+1
 assert volume>1e-9 and all(n==2 for n in counts.values()),name
 objects.append({'name':name,'vertices_world':v.tolist(),'faces':f,'material_family':mat,'role':role,'closed_volume_m3':volume,**extra})
def box(name,lo,hi,mat,role,**kw):
 x0,y0,z0=lo;x1,y1,z1=hi;v=[[x,y,z]for y in [y0,y1]for x,z in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]];emit(name,v,FACES,mat,role,**kw)
# Beam upper faces meet the compiler slab underside at69.26. Four simple fixed
# end plates carry geometrically verified receiving pads; no bolt-detail scope.
for side,z in [('FORE',-128.8),('AFT',-123.2)]:
 box('TB_'+side+'_SIDE_BEAM',[-33.92,68.55,z-.15],[-4.08,69.26,z+.15],'ivory_enamel','static_support',support='Compiler slab underside Y69.26; end plates at X-34/-4')
 for end,x0,x1 in [('WEST',-34,-33.92),('EAST',-4.08,-4)]:
  box('TB_'+side+'_'+end+'_END_PLATE',[x0,68.55,z-.15],[x1,69.48,z+.15],'champagne_metal','fixed_receiver_plate',receiver_plane_x=x0 if end=='WEST' else x1,receiver_contact_y=[69.28,69.48],receiver_contact_z=[z-.15,z+.15],scope='Exact geometric fixed face contact only; no load certification')
for i,x in enumerate([-32,-27,-22,-17,-12,-7]):box('TB_CROSS_BEAM_%d'%i,[x-.12,69.00,-128.65],[x+.12,69.26,-123.35],'champagne_metal','static_support',support='Full top meets slab underside; ends meet side beams')
posts=[-33.93,-29,-24,-19,-14,-9,-4.07]
for side,z in [('FORE',-128.8),('AFT',-123.2)]:
 for i,x in enumerate(posts):
  if x in [-29,-19,-9]:continue
  box('TB_'+side+'_POST_%d'%i,[x-.07,F,z-.07],[x+.07,F+1.16,z+.07],'champagne_metal','guard_post',support='Compiler slab top; side-strip footing')
 for i,(a,b)in enumerate(zip(posts,posts[1:])):
  a+=.14 if a in [-29,-19,-9] else .07;b-=.14 if b in [-29,-19,-9] else .07
  box('TB_'+side+'_GLASS_%d'%i,[a,F+.12,z-.009],[b,F+1.06,z+.009],'gallery_glass','guard_glass',support='Toe/head channels and adjacent post faces')
  box('TB_'+side+'_TOE_%d'%i,[a,F+.085,z-.035],[b,F+.145,z+.035],'champagne_metal','guard_frame')
  box('TB_'+side+'_HANDRAIL_%d'%i,[a,F+1.055,z-.055],[b,F+1.14,z+.055],'warm_walnut','guard_handrail')
# Three cross-vault ribs, no continuous ceiling that hides the ship volume.
for i,x in enumerate([-29,-19,-9]):
 zz=[-3.05,-2.8,-2.2,-1.5,-1.2,0,1.2,1.5,2.2,2.8,3.05]
 def top(z):return F+3.95-.40*(.5-.5*math.cos(math.pi*max(0,(abs(z)-1.5)/(3.05-1.5))))
 n=len(zz);v=[[xx,y,-126+z]for xx in [x-.25,x+.25]for fn in [lambda z:top(z)-.24,top]for z in zz for y in [fn(z)]];f=[]
 for j in range(n-1):f.extend([[j,j+1,n+j+1,n+j],[2*n+j,3*n+j,3*n+j+1,2*n+j+1],[j,2*n+j,2*n+j+1,j+1],[n+j,n+j+1,3*n+j+1,3*n+j]])
 f.extend([[0,n,3*n,2*n],[n-1,2*n-1,4*n-1,3*n-1]]);emit('TB_VAULT_%d'%i,v,f,'ivory_enamel','arrival_vault')
 for side,z in [('FORE',-128.8),('AFT',-123.2)]:
  zs=sorted(set([z-.14,z+.14]+[-126+a for a in zz if z-.14 < -126+a < z+.14]));nn=len(zs)
  under=lambda a:float(np.interp(a+126,zz,[top(t)-.24 for t in zz]));pv=[[xx,yy,a]for xx in [x-.14,x+.14]for fn in [lambda a:F,under]for a in zs for yy in [fn(a)]];pf=[]
  for j in range(nn-1):pf.extend([[j,j+1,nn+j+1,nn+j],[2*nn+j,3*nn+j,3*nn+j+1,2*nn+j+1],[j,2*nn+j,2*nn+j+1,j+1],[nn+j,nn+j+1,3*nn+j+1,3*nn+j]])
  pf.extend([[0,nn,3*nn,2*nn],[nn-1,2*nn-1,4*nn-1,3*nn-1]]);emit('TB_'+side+'_RIB_PIER_%d'%i,pv,pf,'ivory_enamel','arrival_pier',support='Full foot on side-strip compiler floor; upper profile matches actual piecewise planar vault underside')
 # Physically mounted hollow coffer with real open aperture and retained opal.
 mount=F+3.71;box('TB_COFF_%d_BACK'%i,[x-.235,mount-.035,-127.35],[x+.235,mount,-124.65],'ivory_enamel','fixture_mount')
 for side,z in [('FORE',-127.35),('AFT',-124.65)]:box('TB_COFF_%d_%s_END'%(i,side),[x-.235,mount-.15,z-.025],[x+.235,mount-.035,z+.025],'champagne_metal','fixture_frame')
 for side,xx in [('L',x-.235),('R',x+.235)]:box('TB_COFF_%d_%s_SIDE'%(i,side),[xx-.025,mount-.15,-127.35],[xx+.025,mount-.035,-124.65],'champagne_metal','fixture_frame')
 box('TB_COFF_%d_LENS'%i,[x-.225,mount-.13,-127.325],[x+.225,mount-.115,-124.675],'hospitality_opal','physical_luminous_lens')
 lights.append({'id':'TB_SOURCE_%d'%i,'fixture':'TB_COFF_%d_LENS'%i,'position_world':[x,mount-.16,-126],'aim_world':[0,-1,0],'type':'SPOT','full_cone_degrees':130,'range_m':18,'source_preview_watts':900,'godot_initial_energy':1.6,'color_linear':[1,.91,.80],'shadow_candidate':True,'illumination_anchor':[x,F+.04,-126]})
# All parts stay within the exact183m² plan. The four end pads touch existing
# or approved receiving faces only; no old source/pressure shell cut is implied.
for o in objects:
 a=np.array(o['vertices_world']);assert a[:,0].min()>=-34-1e-8 and a[:,0].max()<=-4+1e-8;assert a[:,2].min()>=-129.05-1e-8 and a[:,2].max()<=-122.95+1e-8
report={'status':'Approved source-authoring geometry proposal; bridge not installed','source_003_sha256':'dfb0948338a471104896d322bc4576df6140798a458f14eebff1e125f6b1e530','receiver_screen_sha256':hashlib.sha256((R.parent/'BRIDGE_TERMINAL_CONTACT_SCREEN.json').read_bytes()).hexdigest(),'compiler_slab':{'boundary':[[-34,-129.05],[-4,-129.05],[-4,-122.95],[-34,-122.95]],'top_y':69.5,'thickness':.24,'area_m2':183,'not_part_of_source_export':True},'clear_route':{'x':[-34,-4],'z':[-128.6,-123.4],'floor_y':69.5,'required_headroom_m':3},'objects':objects,'lights':lights,'limits':['No D10 columns/cuts','No retained door-pocket modification','No load capacity certification','Actual imported collision and continuous walking/cart/door state still gated']};out=R/'BRIDGE_GEOMETRY_002.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'parts':len(objects),'triangles':sum(sum(len(f)-2 for f in o['faces'])for o in objects),'maximum_y':max(v[1]for o in objects for v in o['vertices_world']),'minimum_y':min(v[1]for o in objects for v in o['vertices_world'])}))
