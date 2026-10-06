"""Pure source-data builder. No bpy, Godot, runtime writes, or original-source changes.
Public API: build_package() -> JSON-serializable object; write_package(output_path).
Coordinates: vertices_world are XYZ metres, Y up, closed/rest poses. faces are
outward polygons. uv_faces supplies one UV pair per polygon corner. Moving
ownership is explicit in motion_groups; do not bake moving objects into static mesh.
"""
from pathlib import Path
import json, math, hashlib, struct
C=Path('/workspace/shared/astraea-catalogue-continuation-20261002')
OUT=Path(__file__).resolve().parent
PLAN_INPUT_DIR=OUT.parent  # Frozen approved secondary-door plan; repaired output stays here.
FACES=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
SOURCES={'theater':'assets/grand_lantern_theater_section/source/AST-CUL-005.blend','door':'assets/guest_entry_door/source/AST-DOR-002_wide.blend','door_glb':'assets/guest_entry_door/exports/AST-DOR-002_wide.glb','gate':'assets/telescoping_gate/source/AST-DOR-003.blend','gate_glb':'assets/telescoping_gate/exports/AST-DOR-003.glb','cabin':'assets/commons_lift_cabin/source/AST-CIR-003_three_stop.blend','cabin_glb':'assets/commons_lift_cabin/exports/AST-CIR-003_three_stop.glb'}
PINS={'theater':'c91193af1e4a14aac3a4e75c743e7c86b6a57a669981e9a7e7cfb0412e1cb5f5','door':'6d3146db579d33720c749e0523960a64981c349f52f67e477c3fb0212d739d5c','door_glb':'f57ceb601ee3c625b0b5953d9d449527a30216ac5671f184cb98fd727cf0c49e','gate':'da17aa3e66225350af7f3c7abe3a2b3ba99aacd2430f4631fc4c59e27c5dc50c','gate_glb':'975cec2ac763de60279d0e37d32060f909a267cb139954104ca0f8e4b91bade5','cabin':'aed933163f5248de2fea2076b666f0200381dac7f303832eaf9ff416c539a0a8','cabin_glb':'7724dbf3152b486aa7d01354beacd009eb6ba2a67fb8f7a72238ebcc9f6de6d9'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def unit(a):
 n=math.sqrt(dot(a,a));return tuple(x/n for x in a) if n else (1,0,0)
def bounds(v):return [[min(p[i]for p in v)for i in range(3)],[max(p[i]for p in v)for i in range(3)]]
def rounded(v):return [round(float(x),10)for x in v]
def metric_uv(vertices,faces,scale=(1,1)):
 out=[]
 for f in faces:
  n=unit(cross(sub(vertices[f[1]],vertices[f[0]]),sub(vertices[f[2]],vertices[f[0]])))
  u=unit((1-n[0]*n[0],-n[0]*n[1],-n[0]*n[2]))if abs(n[2])>.7 else unit((-n[1],n[0],0));v=unit(cross(n,u))
  out.append([[dot(vertices[i],u)/scale[0],dot(vertices[i],v)/scale[1]]for i in f])
 return out
class Frame:
 def __init__(self,origin,ex,ey,ez):self.o=origin;self.axes=(ex,ey,ez);self.reverse=dot(cross(ex,ey),ez)<0
 def point(self,p):return [self.o[i]+sum(p[j]*self.axes[j][i]for j in range(3))for i in range(3)]
def mainframe(y):return Frame((-34.25,y,-126),(0,0,1),(1,0,0),(0,1,0))
def liftframe(y,z=-123.49):return Frame((-41.5,y,z),(1,0,0),(0,0,1),(0,1,0))
class Builder:
 def __init__(self):
  self.objects=[];self.motions=[];self.markers=[];self.notes=[];self.names=set();self.materials={}
  self.scales=json.loads((C/'materials/material_manifest.json').read_text())['materials']
 def emit(self,name,v,f,mat,frame,motion=None,family='door',uv=None,provenance=None,role=None):
  assert name not in self.names,name;self.names.add(name)
  faces=[list(reversed(q))if frame.reverse else list(q)for q in f]
  if uv is None:uv=metric_uv(v,f,self.scales.get(mat,{}).get('meters_per_tile_uv',[1,1]))
  if frame.reverse:uv=[list(reversed(q))for q in uv]
  # Distinct family material keys preserve source datablocks, even when names match.
  key=family+'/'+mat;self.materials[key]={'source_blend':str(C/SOURCES[family]),'datablock_name':mat,'reuse_original_graph_and_packed_images':True}
  o={'name':name,'vertices_world':[rounded(frame.point(p))for p in v],'faces':faces,'uv_faces':uv,'material_ref':key,'material_family':mat,'role':role or ('moving_mechanism'if motion else 'static_mechanism'),'motion_group':motion,'catalogue_owner':{'door':'AST-DOR-002','gate':'AST-DOR-003','cabin':'AST-CIR-003','theater':'AST-CUL-005'}[family]}
  if provenance:o['source_provenance']=provenance
  self.objects.append(o);return o
 def box(self,name,b,mat,fr,motion=None,family='door',**kw):
  u0,u1,d0,d1,h0,h1=b;assert u1>u0 and d1>d0 and h1>h0,(name,b)
  v=[(u,d,h)for h in[h0,h1]for u,d in[(u0,d0),(u1,d0),(u1,d1),(u0,d1)]]
  return self.emit(name,v,FACES,mat,fr,motion,family,**kw)
 def extrusion(self,name,outline,lo,hi,mat,fr,motion=None,family='door'):
  n=len(outline);v=[(u,d,h)for h in[lo,hi]for u,d in outline];f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
  return self.emit(name,v,f,mat,fr,motion,family)
 def ring_plate(self,name,ub,db,hb,center,radius,mat,fr,motion=None,family='door',n=8):
  """Rectangular plate with a true through-hole; exact outer rectangle, low-poly bore."""
  cu,cd=center;u0,u1=ub;d0,d1=db;h0,h1=hb
  outer=[(u0,d0),(u1,d0),(u1,d1),(u0,d1)];theta0=math.atan2(d0-cd,u0-cu)
  oa=[]
  for u,d in outer:
   t=math.atan2(d-cd,u-cu)
   while t<theta0-1e-12:t+=2*math.pi
   oa.append(t)
  ia=[theta0+2*math.pi*k/n for k in range(n)];inner=[(cu+radius*math.cos(t),cd+radius*math.sin(t))for t in ia]
  loop=outer+inner;count=4+n;v=[(u,d,h)for h in[h0,h1]for u,d in loop];top=[];i=j=0
  while i<4 or j<n:
   onext=oa[i+1]if i+1<4 else theta0+2*math.pi
   inext=ia[j+1]if j+1<n else theta0+2*math.pi
   if i<4 and (j>=n or onext<=inext):top.append((i%4,(i+1)%4,4+j%n));i+=1
   else:top.append((i%4,4+(j+1)%n,4+j%n));j+=1
  f=[tuple(k+count for k in q)for q in top]+[tuple(reversed(q))for q in top]
  f += [(i,(i+1)%4,(i+1)%4+count,i+count)for i in range(4)]
  f += [(4+i,4+i+count,4+(i+1)%n+count,4+(i+1)%n)for i in range(n)]
  return self.emit(name,v,f,mat,fr,motion,family)
 def cylinder(self,name,center,r,length,axis,mat,fr,motion=None,family='door',n=8):
  axes=[k for k in range(3)if k!=axis];v=[]
  for a in[-length/2,length/2]:
   for k in range(n):
    p=list(center);p[axis]+=a;p[axes[0]]+=r*math.cos(2*math.pi*k/n);p[axes[1]]+=r*math.sin(2*math.pi*k/n);v.append(p)
  f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
  if axis==1:f=[tuple(reversed(q))for q in f]
  return self.emit(name,v,f,mat,fr,motion,family)
 def roller_axle(self,name,u,d,h,R,fr,motion,family='door',small=False):
  """Single continuous stepped axle/twin-wheel surface; no overlapping wheel solids."""
  if small:profile=[(-.016,R),(-.008,R),(-.008,.003),(.008,.003),(.008,R),(.016,R)]
  else:profile=[(-.070,R),(-.046,R),(-.046,.008),(.046,.008),(.046,R),(.070,R)]
  n=8;v=[(u+r*math.cos(2*math.pi*k/n),d+t,h+r*math.sin(2*math.pi*k/n))for t,r in profile for k in range(n)];f=[tuple(range(n)),tuple(reversed(range((len(profile)-1)*n,len(profile)*n)))]
  for j in range(len(profile)-1):
   for k in range(n):f.append((j*n+k,(j+1)*n+k,(j+1)*n+(k+1)%n,j*n+(k+1)%n))
  return self.emit(name,v,f,'champagne_metal',fr,motion,family)
 def hanger_bore(self,name,u,d,hole_h,bottom,half_u,half_d,top,r,fr,motion,family):
  # Build a ring plate in the u/h plane, then permute its temporary depth/height axes.
  temp=Frame((0,0,0),(1,0,0),(0,1,0),(0,0,1));start=len(self.objects)
  o=self.ring_plate(name,(u-half_u,u+half_u),(bottom,top),(d-half_d,d+half_d),(u,hole_h),r,'champagne_metal',temp,motion,family,n=8)
  vv=[(p[0],p[2],p[1])for p in o['vertices_world']];faces=[list(reversed(q))for q in o['faces']]
  self.objects.pop();self.names.remove(name);self.emit(name,vv,faces,'champagne_metal',fr,motion,family)
 def marker(self,name,p,fr,motion=None,kind='interaction'):self.markers.append({'name':name,'position_world':rounded(fr.point(p)),'motion_group':motion,'kind':kind})

def load_glb(rel):
 b=(C/rel).read_bytes();chunks={};off=12
 while off<len(b):n,t=struct.unpack_from('<II',b,off);chunks[t]=b[off+8:off+8+n];off+=8+n
 j=json.loads(chunks[0x4e4f534a]);buf=chunks[0x004e4942]
 def acc(i):
  a=j['accessors'][i];bv=j['bufferViews'][a['bufferView']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']];size=struct.calcsize(fmt)*n;start=bv.get('byteOffset',0)+a.get('byteOffset',0);stride=bv.get('byteStride',size)
  return [struct.unpack_from('<'+fmt*n,buf,start+k*stride)for k in range(a['count'])]
 out=[]
 def visit(i,tr=(0,0,0),parent=None):
  node=j['nodes'][i];assert all(k not in node for k in['scale','rotation','matrix']);tr=tuple(a+b for a,b in zip(tr,node.get('translation',[0,0,0])));name=node.get('name',str(i));parent=name if name.startswith('LEAF_')else parent
  if 'mesh'in node:
   for k,p in enumerate(j['meshes'][node['mesh']]['primitives']):
    v=[(x+tr[0],-(z+tr[2]),y+tr[1])for x,y,z in acc(p['attributes']['POSITION'])];idx=[q[0]for q in acc(p['indices'])];f=[idx[i:i+3]for i in range(0,len(idx),3)];uv0=acc(p['attributes']['TEXCOORD_0'])if'TEXCOORD_0'in p['attributes']else None
    out.append({'name':name+'_'+str(k),'parent':parent,'vertices':v,'faces':f,'uv_faces':[[list(uv0[x])for x in face]for face in f]if uv0 else None,'material':j['materials'][p['material']].get('name'),'source_glb':rel})
  for c in node.get('children',[]):visit(c,tr,parent)
 for i in j['scenes'][j.get('scene',0)]['nodes']:visit(i)
 return out

def adapt_uv(row,new_v,scales):
 old=row['vertices'];uv=row['uv_faces'];metric=metric_uv(new_v,row['faces'],scales)
 if not uv:return metric
 out=[]
 for f,old_uv,new_uv in zip(row['faces'],uv,metric):
  rigid=all(abs(math.dist(old[f[i]],old[f[j]])-math.dist(new_v[f[i]],new_v[f[j]]))<1e-6 for i in range(len(f))for j in range(i))
  out.append(old_uv if rigid else new_uv)
 return out

def perforated_roof(B,name,u0,u1,v0,v1,h0,h1,fr,material='champagne_metal',family='door',motion=None,stations=None):
 """Same exact octagonal bores, one closed plate, no hidden tile subdivision faces.
 Delaunay is used only for pure-data generation. Every hole/outer boundary and
 expected area is verified; delivered JSON and Blender append need no SciPy.
 """
 from scipy.spatial import Delaunay
 import numpy as np
 stations=stations or[];outer=[(u0,v0),(u1,v0),(u1,v1),(u0,v1)];loops=[outer]
 theta=math.atan2(-.025,-.012)
 for d in[-.055,.055]:
  for u in stations:
   if u0+.012<u<u1-.012:loops.append([(u+.0035*math.cos(theta+2*math.pi*k/8),d+.0035*math.sin(theta+2*math.pi*k/8))for k in range(8)])
 points=[q for loop in loops for q in loop];offsets=[];count=0
 for loop in loops:offsets.append(count);count+=len(loop)
 def inside(pt,poly):
  return all((poly[(i+1)%len(poly)][0]-a[0])*(pt[1]-a[1])-(poly[(i+1)%len(poly)][1]-a[1])*(pt[0]-a[0])>=-1e-13 for i,a in enumerate(poly))
 def area(poly):return abs(sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(poly,poly[1:]+poly[:1])))*.5
 top=[]
 for tri in Delaunay(np.array(points)).simplices.tolist():
  cen=tuple(sum(points[j][i]for j in tri)/3 for i in[0,1])
  if any(inside(cen,hole)for hole in loops[1:]):continue
  a,b,c=[points[j]for j in tri]
  if (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])<0:tri.reverse()
  top.append(tri)
 edges={}
 for tri in top:
  for a,b in zip(tri,tri[1:]+tri[:1]):edge=tuple(sorted([a,b]));edges[edge]=edges.get(edge,0)+1
 expected=set()
 for off,loop in zip(offsets,loops):
  for i in range(len(loop)):expected.add(tuple(sorted([off+i,off+(i+1)%len(loop)])))
 assert {e for e,n in edges.items()if n==1}==expected,('Roof triangulation boundary mismatch',name)
 assert all(n in[1,2]for n in edges.values()),name
 expected_area=area(outer)-sum(area(h)for h in loops[1:]);actual_area=sum(area([points[j]for j in tri])for tri in top)
 assert abs(expected_area-actual_area)<1e-9,(name,expected_area,actual_area)
 n=len(points);vv=[(u,d,h)for h in[h0,h1]for u,d in points];faces=[list(reversed(t))for t in top]+[[j+n for j in t]for t in top]
 for li,(off,loop)in enumerate(zip(offsets,loops)):
  for k in range(len(loop)):
   a,b=off+k,off+(k+1)%len(loop);face=[a,b,b+n,a+n]
   if li:face.reverse()
   faces.append(face)
 o=B.emit(name,vv,faces,material,fr,motion,family);o['source_provenance']={'optimization':'Exact original octagonal cap/track bores retained; internal subdivision faces removed','bore_count':len(loops)-1,'area_m2':actual_area,'closed_boundary_check':True}


def build_main_doors(B,door_rows):
 stations=[.45*k for k in range(-11,12)]
 for deck,y in [('D11',69.5),('D12',78),('D13',84)]:
  pre='THEATER_'+deck+'_MAIN';fr=mainframe(y)
  # Exactly six cap replacements plus three central heads; caller removes old caps.
  for label,a,b in [('fore',-5.3,-2.6),('head',-2.6,2.6),('aft',2.6,5.3)]:
   q=pre+'_CAP_'+label
   for side,d0,d1 in [('back',-.25,-.09),('front',.09,.25)]:B.box(q+'_'+side,(a,b,d0,d1,3.4,3.6),'champagne_metal',fr,family='door',role='approved_cap_derivative')
   perforated_roof(B,q+'_roof',a,b,-.25,.25,3.6,3.65,fr,stations=stations)
  for side in[-1,1]:
   a,b=sorted([side*5.12,side*5.3]);B.box(pre+'_CAP_end_'+str(side),(a,b,-.09,.09,3.4,3.6),'champagne_metal',fr)
  for side in[-1,1]:
   d0,d1=sorted([side*.085,side*.075]);B.box(pre+'_TRACK_side_'+str(side),(-5.1,5.1,d0,d1,3.49,3.59),'champagne_metal',fr)
   d0,d1=sorted([side*.085,side*.025]);B.box(pre+'_TRACK_ledge_'+str(side),(-5.1,5.1,d0,d1,3.475,3.49),'champagne_metal',fr)
   a,b=sorted([side*4.92,side*4.98]);B.box(pre+'_TRACK_hard_stop_'+str(side),(a,b,-.07,.07,3.49,3.575),'champagne_metal',fr)
  perforated_roof(B,pre+'_TRACK_top',-5.1,5.1,-.085,.085,3.59,3.60,fr,stations=stations)
  # Five paired attachment stations retain a real distributed roof load path.
  # All46 original cap/track bore locations remain; unpopulated ones are spare mounts.
  for k,u in enumerate([-4.95,-2.70,0,2.70,4.95]):
   for side in[-1,1]:
    d=side*.055;n=pre+'_SUSP_%02d_%s'%(k,side)
    B.cylinder(n+'_shank',(u,d,3.6275),.003,.075,2,'champagne_metal',fr,n=8)
    B.cylinder(n+'_head',(u,d,3.585),.009,.010,2,'champagne_metal',fr,n=6)
    B.ring_plate(n+'_washer',(u-.012,u+.012),(d-.012,d+.012),(3.65,3.655),(u,d),.0035,'champagne_metal',fr,n=8)
    # Open-bore square nut deliberately low-detail; avoids hidden solid/bolt overlap.
    B.ring_plate(n+'_nut',(u-.006,u+.006),(d-.006,d+.006),(3.655,3.665),(u,d),.0035,'champagne_metal',fr,n=8)
  for side,label in[(-1,'LEFT'),(1,'RIGHT')]:
   motion=pre+'_LEAF_'+label;root=side*1.31
   B.motions.append({'id':motion,'kind':'paired_sliding_leaf','parent':None,'closed_root_world':rounded(fr.point((root,0,0))),'axis_world':[0,0,side],'travel_m':2.65,'mechanical_stop_travel_m':2.67,'catalogue_family':'AST-DOR-002','scale':[1,1,1],'includes':['complete retained leaf','hangers','roller axle assemblies']})
   for row in door_rows:
    if row['parent']!='LEAF_'+label:continue
    new=[]
    for u,d,h in row['vertices']:
     u,d,h=(round(x,6)for x in (u,d,h))
     u-=side*.6;u=u+math.copysign(.71,u) if abs(u)>1e-8 else u
     if h>2.0:h+=.90
     new.append((root+u,d,h))
    uv=adapt_uv(row,new,B.scales.get(row['material'],{}).get('meters_per_tile_uv',[1,1]))
    B.emit(motion+'_'+row['name'],new,row['faces'],row['material'],fr,motion,'door',uv,{'retained_glb':row['source_glb'],'retained_node':row['name'],'derivation':'named dimensional coordinate extension; no root scaling'})
   for i,off in enumerate([-.9,.9]):
    u=root+off;n=motion+'_TROLLEY_'+str(i)
    B.roller_axle(n+'_roller_axle',u,0,3.53,.04,fr,motion)
    B.hanger_bore(n+'_hanger',u,0,3.5295,3.397,.015,.012,3.55,.0085/math.cos(math.pi/8),fr,motion,'door')
    B.box(n+'_foot',(u-.05,u+.05,-.025,.025,3.385,3.397),'champagne_metal',fr,motion)
  # Existing-family inside call plate on the actual acoustic wall's inner face.
  B.box(pre+'_call_plate',(-4.91,-4.69,-.535,-.500,1.02,1.42),'champagne_metal',fr)
  B.box(pre+'_call_lens',(-4.87,-4.73,-.545,-.535,1.12,1.30),'GardenOpalLens',fr)
  B.marker(pre+'_call_button',(-4.80,-.550,1.21),fr)
 B.notes.append('External X>-34 call plates/landing surfaces are not authored; interior call plates meet existing acoustic wall at X=-34.75.')

# Gate helper includes its actual double-depth pockets, hollow header, two tracks and real hangers.
def build_gate(B,pre,fr,gate_rows,parent_motion=None,clear_height=3.0,opaque_material=None):
 first_object=len(B.objects);family='gate';H=3.0
 for side in[-1,1]:
  a,b=sorted([side*1.7,side*2.65]);e0,e1=sorted([side*2.63,side*2.65])
  for j,(d0,d1)in enumerate([(-.095,-.075),(.060,.085)]):B.box(pre+'_pocket_skin_%s_%s'%(side,j),(a,b,d0,d1,0,H),'ivory_enamel',fr,parent_motion,family)
  B.box(pre+'_pocket_end_'+str(side),(e0,e1,-.095,.085,0,3.14),'champagne_metal',fr,parent_motion,family)
  B.box(pre+'_pocket_base_'+str(side),(a,b,-.095,.085,0,.020),'champagne_metal',fr,parent_motion,family)
 # Hollow family header instead of a concealed solid behind moving hangers.
 B.box(pre+'_header_roof',(-2.67,2.67,-.105,.095,3.14,3.20),'warm_walnut',fr,parent_motion,family)
 for label,a,b in [('front',-.105,-.095),('back',.085,.095)]:B.box(pre+'_header_'+label,(-2.67,2.67,a,b,3.0,3.14),'warm_walnut',fr,parent_motion,family)
 for rank,dc in [('INNER',-.030),('OUTER',.025)]:
  for side in[-1,1]:
   d0,d1=sorted([dc+side*.021,dc+side*.018]);B.box(pre+'_rail_%s_side%s'%(rank,side),(-2.62,2.62,d0,d1,3.045,3.085),'champagne_metal',fr,parent_motion,family)
   d0,d1=sorted([dc+side*.021,dc+side*.006]);B.box(pre+'_rail_%s_ledge%s'%(rank,side),(-2.62,2.62,d0,d1,3.035,3.045),'champagne_metal',fr,parent_motion,family)
  B.box(pre+'_rail_'+rank+'_top',(-2.62,2.62,dc-.021,dc+.021,3.085,3.095),'champagne_metal',fr,parent_motion,family)
  for k,u in enumerate([-2.5,-1.25,0,1.25,2.5]):B.box(pre+'_rail_%s_roof_hanger%s'%(rank,k),(u-.035,u+.035,dc-.016,dc+.016,3.095,3.14),'champagne_metal',fr,parent_motion,family)
  for side,label in[(-1,'LEFT'),(1,'RIGHT')]:
   motion=pre+'_LEAF_'+label+'_'+rank;root=side*(.425 if rank=='INNER' else 1.275);old=side*(.3 if rank=='INNER'else.9);travel=1.74 if rank=='INNER'else.89
   B.motions.append({'id':motion,'kind':'telescoping_leaf','parent':parent_motion,'closed_root_world':rounded(fr.point((root,dc,0))),'axis_world':[side*a for a in fr.axes[0]],'travel_m':travel,'catalogue_family':'AST-DOR-003','scale':[1,1,1],'rank':rank,'synchronization':'same normalized opening fraction for all four leaves'})
   for row in gate_rows:
    if row['parent']!='LEAF_'+label+'_'+rank:continue
    vv=[]
    for u,d,h in row['vertices']:
     u,d,h=(round(x,6)for x in (u,d,h))
     u-=old;u=u+math.copysign(.125,u)if abs(u)>1e-8 else u
     if h>2.:h+=.35
     vv.append((root+u,d,h))
    uv=adapt_uv(row,vv,B.scales.get(row['material'],{}).get('meters_per_tile_uv',[1,1]))
    B.emit(motion+'_'+row['name'],vv,row['faces'],row['material'],fr,motion,family,uv,{'retained_glb':row['source_glb'],'retained_node':row['name'],'derivation':'quarter-panel width/upper height extension; original glazing, rails, seal and material hierarchy'})
   for k,off in enumerate([-.25,.25]):
    u=root+off;n=motion+'_trolley_'+str(k)
    B.roller_axle(n+'_roller_axle',u,dc,3.06,.015,fr,motion,family,small=True)
    B.hanger_bore(n+'_hanger',u,dc,3.0598,2.985,.010,.003,3.073,.0032/math.cos(math.pi/8),fr,motion,family)
    B.box(n+'_foot',(u-.035,u+.035,dc-.006,dc+.006,2.98,2.985),'champagne_metal',fr,motion,family)

 if abs(clear_height-3.0)>1e-9:
  delta=clear_height-3.0
  for o in B.objects[first_object:]:
   o['vertices_world']=[[v[0],v[1]+(delta if v[1]-fr.o[1]>2.5 else 0),v[2]]for v in o['vertices_world']]
   o['uv_faces']=metric_uv(o['vertices_world'],o['faces'],B.scales.get(o['material_family'],{}).get('meters_per_tile_uv',[1,1]))
 if opaque_material:
  family_key,datablock=opaque_material
  B.materials[family_key+'/'+datablock]={'source_blend':str(C/SOURCES[family_key]),'datablock_name':datablock,'reuse_original_graph_and_packed_images':True}
  for o in B.objects[first_object:]:
   if o['material_family']=='LiftGateTintedGlass' or (family_key=='theater' and o['material_family'] in ['ivory_enamel','warm_walnut']):
    o['material_ref']=family_key+'/'+datablock;o['material_family']=datablock;o['source_provenance']={**o.get('source_provenance',{}),'approved_finish_derivative':'Opaque secondary guest/staff infill; retained framed opening geometry'}


def build_cabin(B,cabin_rows,gate_rows):
 fr=liftframe(69.5);motion='THEATER_LIFT_CABIN';B.motions.append({'id':motion,'kind':'lift_translation','parent':None,'axis_world':[0,1,0],'closed_root_world':[-41.5,69.5,-123.49],'stops_world_y':[69.5,78,84],'translation_range_m':[0,14.5],'catalogue_family':'AST-CIR-003','scale':[1,1,1]})
 for row in cabin_rows:
  vv=[]
  for u,d,h in row['vertices']:
   u,d,h=(round(x,6)for x in (u,d,h))
   u=u+math.copysign(.49,u)if abs(u)>1e-8 else u
   if d>2.5:d+=1.38
   # Retained roof and side wall are combined in one ivory mesh; separate by vertex elevation/position.
   if row['material']=='ivory_enamel':
    if abs(d)<1e-6 and h>2.7:d=.24
    if abs(d-.14)<1e-5:d=.30
   if h>2.5:h+=.37
   vv.append((u,d,h))
  uv=adapt_uv(row,vv,B.scales.get(row['material'],{}).get('meters_per_tile_uv',[1,1]))
  B.emit('THEATER_CABIN_'+row['name'],vv,row['faces'],row['material'],fr,motion,'cabin',uv,{'retained_glb':row['source_glb'],'retained_node':row['name'],'derivation':'4.98m outer dimension, retained rear corner facets and bench sizes; roof+0.37m; front sidewalls set back for gate'})
 # The new independent gate is 0.14m inside the actual moving platform front.
 gf=liftframe(69.5,-123.35);build_gate(B,'THEATER_CABIN_GATE',gf,gate_rows,motion)
 # Exact face-to-face bridge between gate header rear d=.235 and cabin roof front d=.24.
 for side in[-1,1]:
  a,b=sorted([side*1.80,side*2.30]);B.box('THEATER_CABIN_GATE_ROOF_BRIDGE_'+str(side),(a,b,.235,.24,3.17,3.20),'champagne_metal',fr,motion,'cabin')
 for i,d in enumerate([.55,.84,1.13]):
  B.marker('THEATER_CABIN_floor_button_'+str(i),(2.22,d,1.27),fr,motion)
  B.cylinder('THEATER_CABIN_button_rim_'+str(i),(2.235,d,1.27),.060,.010,0,'champagne_metal',fr,motion,'cabin',n=8)
  B.cylinder('THEATER_CABIN_button_lens_'+str(i),(2.228,d,1.27),.040,.004,0,'GardenOpalLens',fr,motion,'cabin',n=8)
 for side in[-1,1]:B.marker('THEATER_CABIN_light_'+str(side),(side*2.19,2.415,2.97),fr,motion,'lens_attachment')
 for deck,y in [('D11',69.5),('D12',78),('D13',84)]:
  gf=liftframe(y,-123.63);pre='THEATER_'+deck+'_LANDING_GATE';build_gate(B,pre,gf,gate_rows)
  for side in[-1,1]:
   a,b=sorted([side*1.9,side*2.5])
   for k,h in enumerate([.25,2.65]):B.box(pre+'_jamb_mount_%s_%s'%(side,k),(a,b,-.120,-.095,h,h+.12),'champagne_metal',gf,family='gate')
  B.marker(pre+'_call_button',(2.8,-.420,1.21),gf)
  B.box(pre+'_call_plate',(2.69,2.91,-.405,-.370,1.02,1.42),'champagne_metal',gf,family='gate')
  B.box(pre+'_call_lens',(2.73,2.87,-.415,-.405,1.12,1.30),'GardenOpalLens',gf,family='gate')
 return motion

def build_guides(B,motion):
 """T guides on independent posts; geometric foundation-side and solid-head contacts."""
 fr=liftframe(69.5);dc=2.49
 for side in[-1,1]:
  def box(n,u0,u1,d0,d1,h0,h1,owner=None):
   a,b=sorted([side*u0,side*u1]);return B.box('THEATER_GUIDE_'+str(side)+'_'+n,(a,b,dc+d0,dc+d1,h0,h1),'champagne_metal',fr,owner,'cabin')
  box('fixed_flange',2.615,2.635,-.035,.035,-.22,18.10)
  box('fixed_stem',2.635,2.685,-.008,.008,-.22,18.10)
  box('independent_post',2.685,2.725,-.070,.070,-.22,18.20)
  anchor=box('foundation_inner_side_bracket',2.725,2.750,-.100,.100,-.22,-.02)
  anchor['intentional_fixed_bearing']={'target':'approved D11 foundation shaft-side INNER FACE','plane_world_x':-41.5+side*2.75,'contact_world_y':[69.28,69.48],'contact_world_z':[-121.10,-120.90],'penetration_m':0,'source_pane_min_y':69.5,'pane_vertical_clearance_m':.02,'scope':'Geometric fixed face contact, not load certification'}
  for k,h in enumerate([.20,2.75]):
   box('shoe_%s_arm'%k,2.49,2.595,-.020,.020,h+.05,h+.20,motion)
   box('shoe_%s_back'%k,2.595,2.610,-.045,.045,h,h+.25,motion)
   for rank,sgn in enumerate([-1,1]):
    d0,d1=sorted([sgn*.038,sgn*.045]);box('shoe_%s_outer_%s'%(k,rank),2.610,2.648,d0,d1,h,h+.25,motion)
    d0,d1=sorted([sgn*.012,sgn*.038]);box('shoe_%s_return_%s'%(k,rank),2.640,2.648,d0,d1,h,h+.25,motion)
  B.marker('THEATER_GUIDE_%s_foundation_contact'%side,(side*2.75,dc,-.12),fr,kind='fixed_foundation_side_contact')
 # Fixed head frame bears only on original SOLID front jamb/head tops, never the pane.
 o=B.box('THEATER_GUIDE_HEAD_front_bearing_beam',(-3,3,-.51,-.26,18.15,18.35),'champagne_metal',fr,family='cabin')
 o['intentional_fixed_bearing']={'targets':['lift_gate_pocket_port','D13_lift_gate_head','lift_gate_pocket_starboard'],'plane_world_y':87.65,'contact_rectangle_xz':[-44.5,-124,-38.5,-123.75],'area_m2':1.5,'penetration_m':0,'scope':'Geometric top bearing, not certified structural capacity'}
 for side in[-1,1]:
  a,b=sorted([side*2.675,side*2.735]);B.box('THEATER_GUIDE_HEAD_side_arm_'+str(side),(a,b,-.26,2.59,18.20,18.35),'champagne_metal',fr,family='cabin')
 B.box('THEATER_GUIDE_HEAD_crossbar',(-2.675,2.675,2.41,2.59,18.20,18.35),'champagne_metal',fr,family='cabin')
 B.notes.append('Independent guide posts bear through tagged foundation INNER SIDE contacts atY69.28..69.48 below the pane and fixed head frame on solid front jamb/head tops atY87.65. No glass load path, foundation cut or pane penetration is claimed. Frame top87.85; moving-box crossing members begin87.70,100mm above approved moving top. Source face-bearing proof is included; strength/anchors are not certified.')

def build_secondary(B,gate_rows):
 plan_path=PLAN_INPUT_DIR/'SECONDARY_INTERFACE_DOOR_PLAN.json';plan=json.loads(plan_path.read_text())
 for door in plan['doors']:
  y=door['frame_and_continuous_leaf_sweep_bounds']['min'][1];z=sum(door['clear_opening_world_z'])/2;fr=Frame((-34.865,y,z),(0,0,1),(1,0,0),(0,1,0));pre='THEATER_'+door['id']
  opaque=('theater','ASTRAEA_staff_bluegrey_paint')if'staff'in door['id']else('door','warm_walnut')
  build_gate(B,pre,fr,gate_rows,clear_height=3.4,opaque_material=opaque)
  for k,contact in enumerate(door['fixed_wall_bearings']):
   x,cy,cz=contact['point_world'];lo,hi=contact['fixed_bracket_range_x'];u=cz-z;h=cy-y
   o=B.box(pre+'_wall_bearing_'+str(k),(u-.080,u+.080,lo-fr.o[0],hi-fr.o[0],h-.040,h+.040),'champagne_metal',fr,family='gate')
   o['intentional_fixed_bearing']={'target':contact['actual_unchanged_wall_part'],'point_world':contact['point_world'],'approved_engagement_m':.015,'scope':'Only this fixed bearing may enter existing wall; moving geometry remains clear','plan_sha256':sha(plan_path)}
  # Flush face call plate: remains inside exact 200mm assembly depth.
  a,b=-2.51,-2.29
  for lab,ub,hb in [('L',(a,a+.04),(1.02,1.42)),('R',(b-.04,b),(1.02,1.42)),('B',(a+.04,b-.04),(1.02,1.12)),('T',(a+.04,b-.04),(1.30,1.42))]:B.box(pre+'_call_frame_'+lab,(*ub,-.105,-.095,*hb),'champagne_metal',fr,family='gate')
  B.box(pre+'_call_lens',(a+.04,b-.04,-.105,-.100,1.12,1.30),'GardenOpalLens',fr,family='gate')
  B.marker(pre+'_call_button',(-2.4,-.110,1.21),fr)
 B.notes.append('Four secondary guest/staff assemblies follow hash-bound SECONDARY_INTERFACE_DOOR_PLAN.json, including24 explicitly authorized fixed wall bearing contacts. They are opaque infill derivatives of retained AST-DOR-003, not a new identity or scaled controller.')


def build_package(include_guides=True):
 for k,p in SOURCES.items():assert sha(C/p)==PINS[k],('retained input changed',k)
 B=Builder();doors=load_glb(SOURCES['door_glb']);gates=load_glb(SOURCES['gate_glb']);cabins=load_glb(SOURCES['cabin_glb'])
 build_main_doors(B,doors);motion=build_cabin(B,cabins,gates);build_secondary(B,gates)
 # Preserve original theater material graph for the six cap replacements/three new matching heads.
 B.materials['theater/ASTRAEA_champagne_metal']={'source_blend':str(C/SOURCES['theater']),'datablock_name':'ASTRAEA_champagne_metal','reuse_original_graph_and_packed_images':True}
 for o in B.objects:
  if '_CAP_'in o['name']:o['catalogue_owner']='AST-CUL-005';o['material_ref']='theater/ASTRAEA_champagne_metal'
 if include_guides:build_guides(B,motion)
 # Recovery01: gate source drops unused lens datablock; use exact retained door palette lens.
 B.materials['gate/GardenOpalLens']['source_blend']=str(C/SOURCES['door'])
 package={'schema':1,'package':'ASTRAEA_THEATER_FIRSTPASS_MECHANISMS_001','optimization':'Compact game-relevant hidden hardware; exact cap bores, channels, visible family meshes,39motiongroups and assembly outer envelopes retained' ,'coordinate_system':'World XYZ metres, Y-up; vertices at closed/rest state','source_input_sha256':{str(C/SOURCES[k]):v for k,v in PINS.items()},'original_theater_unchanged':True,'baseline_removal_by_parent_only':[d+'_door_pocket_'+s+'_cap'for d in['D11','D12','D13']for s in['fore','aft']],'material_refs':B.materials,'objects':B.objects,'motion_groups':B.motions,'markers':B.markers,'proposed_instance_records':{'main_doors':3,'landing_telescoping_gates':3,'cabin_telescoping_gates':1,'cabin':1,'secondary_guest_staff_doors':4},'moving_lift_envelope_world_xz':[-44.17,-123.49,-38.83,-118.51],'moving_lift_vertical_sweep_y':[69.32,87.60],'notes':B.notes+['Compact octagonal integral roller/axles retain exact axle/roller outer envelopes and real hanger bores. Main rail hardware uses five paired fastener stations per entrance; all46 original cap/track bores remain geometrically unchanged, with unused bores treated as spare mounting positions.','No motor, belt, brake, interlock, software behavior, load certification or engine acceptance is implied.','Cap roofs and track top plates have actual bolt bores. Cap replacements must not be stacked onto original solid caps.'],'guide_anchor_adoption_pending':False,'fixed_guide_contacts_require_parent_review':include_guides,'secondary_plan_sha256':sha(PLAN_INPUT_DIR/'SECONDARY_INTERFACE_DOOR_PLAN.json')}
 package['pure_checks']=check_package(package)
 return package

def check_package(p):
 errors=[];names={};triangles=0
 for o in p['objects']:
  if o['name']in names:errors.append('duplicate '+o['name'])
  names[o['name']]=o
  if len(o['faces'])!=len(o['uv_faces']):errors.append('uv faces '+o['name'])
  for f,uv in zip(o['faces'],o['uv_faces']):
   if len(f)!=len(uv):errors.append('uv corners '+o['name'])
   if len(f)<3 or any(i<0 or i>=len(o['vertices_world'])for i in f):errors.append('face indices '+o['name'])
   if not all(math.isfinite(x)for q in uv for x in q):errors.append('uv finite '+o['name'])
   triangles+=len(f)-2
  if not all(math.isfinite(x)for q in o['vertices_world']for x in q):errors.append('vertices finite '+o['name'])
 motions={m['id']:m for m in p['motion_groups']}
 def in_cabin(mid):
  while mid:
   if mid=='THEATER_LIFT_CABIN':return True
   mid=motions[mid].get('parent')
  return False
 moving=[o for o in p['objects']if in_cabin(o['motion_group'])]
 maxb=[[-44.17,69.32,-123.49],[-38.83,73.10,-118.51]]
 for o in moving:
  # Every cabin leaf position is bounded at both endpoints; the interpolation is linear.
  m=motions[o['motion_group']];dx=m.get('travel_m',0);axis=m.get('axis_world',[0,0,0])
  for fraction in[0,1]:
   vv=[[v[i]+fraction*dx*axis[i]for i in range(3)]for v in o['vertices_world']];b=bounds(vv)
   if any(b[0][i]<maxb[0][i]-2e-5 or b[1][i]>maxb[1][i]+2e-5 for i in range(3)):errors.append('moving envelope '+o['name']+' '+str(b))
 for k,path in SOURCES.items():
  if sha(C/path)!=PINS[k]:errors.append('source hash changed '+k)
 return {'status':'PASS'if not errors else'FAIL','object_count':len(p['objects']),'triangles_if_fan_triangulated':triangles,'motion_group_count':len(p['motion_groups']),'moving_lift_objects_checked':len(moving),'finite_mesh_uv_and_indices':not errors,'closed_and_open_lift_envelope_checked':True,'retained_hashes_unchanged':True,'errors':errors,'limits':['Source-data checks only, no Blender or export/import or live physics','Detailed component intersection/phase/support checks remain parent serial-slot work','Tagged guide foundation/head contacts need parent acceptance; no structural load claim']}
def write_package(output_path=None,include_guides=True):
 path=Path(output_path or OUT/'mechanism_package_compact.json');assert path.resolve().is_relative_to(OUT.resolve()),'Scratch-only builder output';p=build_package(include_guides);path.write_text(json.dumps(p,separators=(',',':'))+'\n');(path.with_suffix('.checks.json')).write_text(json.dumps(p['pure_checks'],indent=2)+'\n');return p
if __name__=='__main__':
 p=write_package();print(json.dumps(p['pure_checks'],indent=2))


LAST_MATERIAL_LOAD_REPORT = None


def _material_preservation_snapshot(material):
 """Use the parent's existing tested graph/packed-image helpers; primitives only."""
 from firstpass_common import material_record,digest
 record=material_record(material)
 return {'datablock_name':material.name,'graph_sha256':digest(record),'packed_images':[node['image']for node in record['nodes']if 'image'in node]}


def get_last_material_load_report():
 """Return only a primitive copy suitable for the parent's JSON receipt."""
 return json.loads(json.dumps(LAST_MATERIAL_LOAD_REPORT,allow_nan=False))


def load_retained_materials_for_blender(package):
 """Parent Blender slot only. Reuse exact same-open-file material IDs; append all other sources.
 No source save, material edits or graph/image modifications are performed.
 Per-file flushed logs distinguish a hypothesis from the next observed failing path.
 """
 import bpy,os
 global LAST_MATERIAL_LOAD_REPORT
 def canonical(path):return os.path.normcase(os.path.realpath(bpy.path.abspath(path)))
 active=canonical(bpy.data.filepath)if bpy.data.filepath else None
 def log(event,**fields):print('MATERIAL_LIBRARY '+json.dumps({'event':event,**fields},sort_keys=True,allow_nan=False),flush=True)
 out={};by_file={}
 for key,ref in package['material_refs'].items():by_file.setdefault(ref['source_blend'],[]).append((key,ref['datablock_name']))
 baseline={};before={};allowed={'ASTRAEA_staff_bluegrey_paint','ASTRAEA_champagne_metal'}
 LAST_MATERIAL_LOAD_REPORT={'status':'IN_PROGRESS','active_source':active,'files':[],'reused_baseline_materials':[],'baseline_preserved':None}
 # Capture the current baseline before any external append can affect it.
 for path,rows in by_file.items():
  if active and canonical(path)==active:
   requested=list(dict.fromkeys(name for _,name in rows))
   if not set(requested)<=allowed:raise RuntimeError('Same-open-file reuse exceeds approved two-material scope: '+str(requested))
   expected=package['source_input_sha256'].get(path)
   if expected is None or sha(path)!=expected:raise RuntimeError('Same-open-file baseline source pin missing or changed: '+path)
   for name in requested:
    material=bpy.data.materials.get(name)
    if material is None or material.library is not None:raise RuntimeError('Exact already-loaded local baseline material unavailable: '+name)
    log('BASELINE_SNAPSHOT_BEGIN',source=path,datablock=name)
    baseline[name]=material;before[name]=_material_preservation_snapshot(material)
    log('BASELINE_SNAPSHOT_SUCCESS',source=path,datablock=name,graph_sha256=before[name]['graph_sha256'])
 def verify_baseline():
  for name,original in baseline.items():
   current=bpy.data.materials.get(name)
   if current is None or current.as_pointer()!=original.as_pointer():raise RuntimeError('Baseline material identity changed: '+name)
   after=_material_preservation_snapshot(current)
   if after!=before[name]:raise RuntimeError('Baseline graph or packed-image fingerprint changed: '+name)
 for index,(path,rows)in enumerate(by_file.items()):
  requested=list(dict.fromkeys(name for _,name in rows));same_open=bool(active and canonical(path)==active);mode='reuse_open_file'if same_open else'append_external'
  log('BEGIN',index=index,source=path,mode=mode,datablocks=requested)
  entry={'index':index,'source':path,'mode':mode,'datablocks':requested,'status':'BEGIN'};LAST_MATERIAL_LOAD_REPORT['files'].append(entry)
  try:
   if same_open:
    material_by_name={name:baseline[name]for name in requested}
   else:
    with bpy.data.libraries.load(path,link=False)as(src,dst):
     missing=set(requested)-set(src.materials)
     if missing:raise RuntimeError('Retained material datablocks missing: '+path+' '+str(sorted(missing)))
     dst.materials=requested[:]
    if len(dst.materials)!=len(requested)or any(m is None for m in dst.materials):raise RuntimeError('Incomplete retained material append: '+path)
    material_by_name=dict(zip(requested,dst.materials))
   for key,name in rows:out[key]=material_by_name[name]
   verify_baseline();entry['status']='SUCCESS'
   log('SUCCESS',index=index,source=path,mode=mode,datablocks=requested,baseline_fingerprints_unchanged=True)
  except Exception as exc:
   entry['status']='ERROR';entry['error']=str(exc);LAST_MATERIAL_LOAD_REPORT['status']='ERROR'
   log('ERROR',index=index,source=path,mode=mode,error=str(exc));raise
 verify_baseline();LAST_MATERIAL_LOAD_REPORT['status']='PASS';LAST_MATERIAL_LOAD_REPORT['baseline_preserved']=True
 LAST_MATERIAL_LOAD_REPORT['reused_baseline_materials']=[before[name]for name in sorted(before)]
 # This report has hashes/strings/lists only; live material objects stay in the transient map.
 json.dumps(LAST_MATERIAL_LOAD_REPORT,allow_nan=False)
 return out


def append_to_blender(package,material_map,parent_root=None,collection=None):
 """CALL ONLY IN PARENT'S RESERVED BLENDER SLOT. No save, export, import or engine action.
 Caller removes the six original semantic cap ranges in its NEW derivative.
 material_map is keyed by material_refs keys. parent_root, if provided, must have
 identity world matrix. Geometry stays semantic/editable; motion roots use real
 rest pivots and hierarchical relative translations, with scale1 everywhere.
 """
 import bpy
 from mathutils import Matrix
 collection=collection or bpy.context.collection
 if parent_root is not None:
  if any(abs(parent_root.matrix_world[i][j]-(1 if i==j else 0))>1e-8 for i in range(4)for j in range(4)):raise ValueError('Expected identity-world parent source root')
 def blender(p):return (p[0],-p[2],p[1])
 nodes={};rest={};specs={m['id']:m for m in package['motion_groups']}
 pending=list(package['motion_groups'])
 while pending:
  progress=False
  for m in pending[:]:
   if m.get('parent') and m['parent']not in nodes:continue
   if bpy.data.objects.get(m['id']):raise RuntimeError('Do not overwrite surviving object '+m['id'])
   ob=bpy.data.objects.new(m['id'],None);collection.objects.link(ob);world=m['closed_root_world'];par=m.get('parent');par_world=rest[par]if par else[0,0,0]
   ob.parent=nodes[par]if par else parent_root;ob.location=blender([world[i]-par_world[i]for i in range(3)])
   ob['mechanism_spec']=json.dumps(m,separators=(',',':'));ob['rest_location_blender']=list(ob.location);ob['source_only']=True;ob['scale_contract']='unit scale; explicit source dimensions';nodes[m['id']]=ob;rest[m['id']]=world;pending.remove(m);progress=True
  if not progress:raise RuntimeError('Cycle or missing motion parent')
 objects=[]
 for spec in package['objects']:
  if bpy.data.objects.get(spec['name']):raise RuntimeError('Do not overwrite surviving object '+spec['name'])
  mid=spec.get('motion_group');origin=rest[mid]if mid else[0,0,0]
  verts=[blender([p[i]-origin[i]for i in range(3)])for p in spec['vertices_world']]
  me=bpy.data.meshes.new(spec['name']);me.from_pydata(verts,[],spec['faces']);me.update(calc_edges=True)
  if len(me.polygons)!=len(spec['faces']):raise RuntimeError('Blender altered polygon count '+spec['name'])
  mat=material_map[spec['material_ref']];me.materials.append(mat)
  uv=me.uv_layers.new(name='MetreScaled');uv.active_render=True
  for face,values in zip(me.polygons,spec['uv_faces']):
   if len(face.loop_indices)!=len(values):raise RuntimeError('UV loop count '+spec['name'])
   for li,value in zip(face.loop_indices,values):uv.data[li].uv=value
  ob=bpy.data.objects.new(spec['name'],me);collection.objects.link(ob);ob.parent=nodes[mid]if mid else parent_root
  ob['catalogue_owner']=spec['catalogue_owner'];ob['material_ref']=spec['material_ref'];ob['collision_role']=spec['role'];ob['motion_group']=mid or'';ob['source_only']=True
  if 'intentional_fixed_bearing'in spec:ob['intentional_fixed_bearing']=json.dumps(spec['intentional_fixed_bearing'],separators=(',',':'))
  if 'source_provenance'in spec:ob['source_provenance']=json.dumps(spec['source_provenance'],separators=(',',':'))
  objects.append(ob)
 for marker in package['markers']:
  name='DATUM_'+marker['name']
  if bpy.data.objects.get(name):raise RuntimeError('Do not overwrite surviving marker '+name)
  ob=bpy.data.objects.new(name,None);collection.objects.link(ob);mid=marker.get('motion_group');origin=rest[mid]if mid else[0,0,0];ob.parent=nodes[mid]if mid else parent_root;ob.location=blender([marker['position_world'][i]-origin[i]for i in range(3)]);ob['marker_spec']=json.dumps(marker,separators=(',',':'));ob['source_only']=True
 return {'object_names':[o.name for o in objects],'motion_root_names':{k:o.name for k,o in nodes.items()},'marker_count':len(package['markers']),'no_save_or_export_performed':True}
