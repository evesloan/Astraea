from pathlib import Path
import json,math,hashlib
from shapely.geometry import MultiPoint,Point,Polygon
from shapely.strtree import STRtree
R=Path(__file__).resolve().parents[1];C=R.parents[1];G=C.parent/'astraea-godot-production-20261003'
P=json.loads((R/'source/geometry_parts.json').read_text())['parts']+json.loads((C/'assets/aft_command/source/geometry_parts.json').read_text())['parts']+json.loads((R/'qa/open_shared_door_geometry.json').read_text())
polys=[MultiPoint([(v[0],v[2])for v in p['vertices_world']]).convex_hull for p in P];tree=STRtree(polys);K=json.loads((G/'data/architecture/cleaning_cart_contacts.json').read_text());samples=[]
def transform(x,z,yaw,p):
 c,s=math.cos(yaw),math.sin(yaw);return(x+c*p[0]+s*p[2],z-s*p[0]+c*p[2])
def test(x,z,yaw,label):
 shapes=[]
 for p in K['boxes']+ [{'name':'loaded_tray','size':[.65,.26,.96],'center':[0,1.05,0]}]:
  a,b,c=p['center'];u,v,w=[q/2 for q in p['size']];poly=Polygon([transform(x,z,yaw,(xx,b,zz))for xx,zz in[(a-u,c-w),(a+u,c-w),(a+u,c+w),(a-u,c+w)]]);shapes.append((p['name'],poly,106.53+b-v,106.53+b+v))
 for i,p in enumerate(K['wheel_contacts']):
  r=p['radius'];q=p['center'];shapes.append(('wheel%s'%i,Point(transform(x,z,yaw,q)).buffer(r,resolution=12),106.53+q[1]-r,106.53+q[1]+r))
 q=transform(x,z,yaw,(0,.91,1.62));shapes.append(('driver',Point(q).buffer(.3,resolution=16),106.54,108.34))
 for name,shape,y0,y1 in shapes:
  for j in tree.query(shape):
   b=P[j]['world_aabb']
   if min(y1,b[3])-max(y0,b[2])>1e-6 and shape.intersection(polys[j]).area>1e-7:raise AssertionError((label,x,z,yaw,name,P[j]['name']))
 samples.append([label,x,z,yaw])
def line(a,b,yaw,label):
 n=math.ceil(math.dist(a,b)/.10)
 for i in range(n+1):t=i/max(1,n);test(a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t,yaw,label)
def turn(x,z,a,b,label):
 for i in range(91):test(x,z,a+(b-a)*i/90,label)
for sign in[-1,1]:
 outgoing=math.pi if sign<0 else-math.pi;side='port'if sign<0 else'starboard';across=math.pi/2 if sign<0 else-math.pi/2
 line((sign*7.5,98.5),(sign*7.5,104.2),outgoing,side+'_door_out')
 turn(sign*7.5,104.2,outgoing,across,side+'_crosslink_out_turn')
 line((sign*7.5,104.2),(sign*32,104.2),across,side+'_crosslink_out')
 turn(sign*32,104.2,across,outgoing,side+'_outer_out_turn')
 line((sign*32,104.2),(sign*32,145),outgoing,side+'_terminal_out')
 # Return cart center is0.4m forward: its trailing driver stays below rear wall105.8 during turn.
 line((sign*31.8,145),(sign*31.8,103.8),0,side+'_terminal_return')
 turn(sign*31.8,103.8,0,-across,side+'_outer_return_turn')
 line((sign*31.8,103.8),(sign*7.5,103.8),-across,side+'_crosslink_return')
 turn(sign*7.5,103.8,-across,0,side+'_crosslink_return_turn')
 line((sign*7.5,103.8),(sign*7.5,98.5),0,side+'_door_return')
report={'pass':True,'pose_count':len(samples),'source_005_sha256':hashlib.sha256((R/'source/AST-CMD-005.blend').read_bytes()).hexdigest(),'source_002_sha256':hashlib.sha256((C/'assets/aft_command/source/AST-CMD-002.blend').read_bytes()).hexdigest(),'actual_cart_contact_source_sha256':hashlib.sha256((G/'data/architecture/cleaning_cart_contacts.json').read_bytes()).hexdigest(),'cart_shapes':len(K['boxes'])+len(K['wheel_contacts'])+2,'open_doors':4,'samples':samples,'turn_center_z_outgoing':104.2,'turn_center_z_return':103.8,'clear_crosslink_width':3.6,'limits':'Source geometry only; uses actual cart boxes/wheels, upper load and0.3m driver radius1.62m behind. Parent must physically drive loaded carts and retain products; stationary centreline pivot atZ104 is not assumed safe.'}
(R/'qa/loaded_cart_source_routes.json').write_text(json.dumps(report,indent=2)+'\n');print('LOADED_CART_SOURCE_PASS',len(samples))
