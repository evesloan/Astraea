"""Bounded utility-port-01 repeated/distant derivative. Original helper unchanged.
The mating outline, 48-sided bore stay exact. The economical variant uses 12-sided holes; the bounded baseline retains 24. The .002 m rear
edge easing is omitted, neck outer ring density is 24, inner bore has endpoints
only, and captive shanks are six-sided. Original six hex heads remain.
"""
import math,importlib.util,bpy,bmesh
import numpy as np
from scipy.spatial import Delaunay
from pathlib import Path
from mathutils import Vector
CAT=Path(__file__).resolve().parents[4]
s=importlib.util.spec_from_file_location('original_utility_ports',CAT/'standards/utility_ports.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
REVISION='utility-flange-economical-01'

def neck(name,face,outward,mat):
 n,u,v=p.basis(outward);base=Vector(face);verts=[];faces=[]
 def ring(axial,radius,count):
  start=len(verts)
  verts.extend(tuple(base+n*axial+radius*(u*math.cos(2*math.pi*i/count)+v*math.sin(2*math.pi*i/count))) for i in range(count))
  return start
 outer=[ring(s,r,24)for s,r in[(-.095,.1),(-.05,.1),(-.038,.112),(-.034,.112)]]
 inner=[ring(s,.08,48)for s in(-.095,-.034)]
 for a,b in zip(outer,outer[1:]):
  faces.extend((a+i,a+(i+1)%24,b+(i+1)%24,b+i)for i in range(24))
 faces.extend((inner[0]+i,inner[1]+i,inner[1]+(i+1)%48,inner[0]+(i+1)%48)for i in range(48))
 for o,inn in[(outer[0],inner[0]),(outer[-1],inner[-1])]:
  for i in range(24):
   a=o+i;b=o+(i+1)%24;c=inn+2*i;d=inn+(2*i+1)%48;e=inn+(2*i+2)%48
   faces.extend([(a,b,d),(a,d,c),(b,e,d)])
 return p.mesh(name,verts,faces,mat)

def add_flange(name,face,outward,materials,hole_segments=12):
 if len(face)!=3 or not all(math.isfinite(float(x))for x in face):raise ValueError('Finite source face required')
 base=Vector(face);n,u,v=p.basis(outward);zinc=materials['staff_zinc'];paint=materials['staff_bluegrey_paint']
 # Triangulate exact planar loops directly. A Boolean at aligned radial
 # phases can leave micron slivers; the explicit planar profile avoids them.
 loops=[]
 for radius,count,centre in[(.16,48,(0,0)),(.08,48,(0,0))]+[(.009,hole_segments,(.13*math.cos(2*math.pi*i/6),.13*math.sin(2*math.pi*i/6)))for i in range(6)]:
  loops.append(np.array([(centre[0]+radius*math.cos(2*math.pi*j/count),centre[1]+radius*math.sin(2*math.pi*j/count))for j in range(count)]))
 points=np.concatenate(loops);tris=Delaunay(points).simplices;centroids=points[tris].mean(1)
 def inside(poly,pts):
  edges=np.roll(poly,-1,axis=0)-poly;rel=pts[:,None,:]-poly[None,:,:]
  return np.all(edges[None,:,0]*rel[:,:,1]-edges[None,:,1]*rel[:,:,0]>=-1e-12,axis=1)
 keep=inside(loops[0],centroids)
 for loop in loops[1:]:keep &= ~inside(loop,centroids)
 tris=tris[keep];N=len(points);verts=[]
 for axial in(-.035,0):verts.extend(tuple(base+n*axial+u*x+v*y)for x,y in points)
 faces=[tuple(int(x)for x in t)for t in tris]+[tuple(int(x+N)for x in t)for t in tris]
 start=0
 for loop in loops:
  count=len(loop)
  faces.extend((start+i,start+(i+1)%count,start+(i+1)%count+N,start+i+N)for i in range(count));start+=count
 ob=p.mesh(name+'_drilled_flange',verts,faces,zinc)
 bm=bmesh.new();bm.from_mesh(ob.data)
 assert all(e.is_manifold for e in bm.edges), 'Planar flange has unexpected boundary'
 bm.free()
 out=[ob,neck(name+'_hollow_neck',face,n,paint)]
 for i in range(6):
  q=base+.13*(u*math.cos(2*math.pi*i/6)+v*math.sin(2*math.pi*i/6))
  out.append(p.solid_cylinder(name+f'_captive_shank_{i+1}',q-n*.052,q-n*.006,.006,zinc,6))
  out.append(p.solid_cylinder(name+f'_rear_hex_{i+1}',q-n*.056,q-n*.036,.014,zinc,6))
 rec=p.port_record(name,face,outward)
 rec['representation_revision']=REVISION
 rec['hole_segments']=hole_segments
 rec['representation_scope']='Repeated/distant derived mesh; exact mating bore/front outline, unchanged hole centres/nominal diameter/phase; hole profile has declared segment count; original detailed source remains authoritative near representation'
 for o in out:o['utility_port_revision']=p.REVISION;o['representation_revision']=REVISION
 return {'objects':out,'record':rec}
