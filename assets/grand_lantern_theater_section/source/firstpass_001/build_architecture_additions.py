"""Pure NEW first-pass architecture. No engine or existing production writes."""
from pathlib import Path
import json,math,hashlib
import numpy as np
import shapely
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
R=Path(__file__).resolve().parent;P=Path('/workspace/shared/astraea-catalogue-continuation-20261002/assets/grand_lantern_theater_section');G=json.loads((P/'source/geometry.json').read_text());objects=[]
def mesh(name,vertices,faces,material,role='firstpass_static_architecture',**extras):
 obj={'name':name,'vertices_world':[[float(v)for v in p]for p in vertices],'faces':[list(f)for f in faces],'material_family':material,'role':role,**extras};objects.append(obj);return obj

def prism(name,poly,bottom,top,mat,**extras):
 for index,p in enumerate(shapely.get_parts(poly)):
  if p.geom_type!='Polygon'or p.area<1e-9:continue
  p=orient(shapely.set_precision(p,1e-8),sign=1.0)
  xy=[];lookup={}
  def vi(v):
   key=(round(v[0],10),round(v[1],10))
   if key not in lookup:lookup[key]=len(xy);xy.append([float(v[0]),float(v[1])])
   return lookup[key]
  tris=[]
  for t in shapely.constrained_delaunay_triangles(p).geoms:
   assert p.covers(t)
   if t.area<1e-9:continue
   ids=[vi(v)for v in list(t.exterior.coords)[:3]]
   if len(set(ids))<3:continue
   xyz=[xy[i]for i in ids];signed=sum(xyz[j][0]*xyz[(j+1)%3][1]-xyz[(j+1)%3][0]*xyz[j][1]for j in range(3))
   tris.append(list(reversed(ids))if signed>0 else ids)
  rings=[]
  for ring in [p.exterior,*p.interiors]:rings.append([vi(v)for v in list(ring.coords)[:-1]])
  n=len(xy);verts=[[x,top,z]for x,z in xy]+[[x,bottom,z]for x,z in xy];faces=tris+[[n+i for i in reversed(t)]for t in tris]
  for ring in rings:
   for a,b in zip(ring,ring[1:]+ring[:1]):
    if a!=b:faces.append([a,b,n+b,n+a])
  mesh(name+(f'_{index}'if index else''),verts,faces,mat,**extras)

def cuboid(name,lo,hi,mat,**extras):prism(name,box(lo[0],lo[2],hi[0],hi[2]),lo[1],hi[1],mat,**extras)
def rod(name,a,b,radius,mat,n=8,**extras):
 a=np.array(a,dtype=float);b=np.array(b,dtype=float);d=(b-a)/np.linalg.norm(b-a);seed=np.array([1.,0.,0.])if abs(d[0])<.9 else np.array([0.,1.,0.]);u=np.cross(d,seed);u/=np.linalg.norm(u);v=np.cross(d,u);points=[(p+radius*(u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n))).tolist()for p in [a,b]for i in range(n)];faces=[list(reversed(range(n))),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)];return mesh(name,points,faces,mat,**extras)

# Shaped ceiling fields: real closed solids; one cap, no duplicate walking slab.
# The west cornice follows the actual old sloped-wall inner/top edge exactly.
west=next(o for o in G['objects']if o['name']=='west_acoustic_tapered_return');top_outer=west['vertices_world'][2];top_inner=west['vertices_world'][6];slope=8.9/4.5;normal=math.hypot(1,slope);bottom_y=91.12;bottom_x=-117.65+slope*(bottom_y-87)+.12*normal
section=[[top_outer[0],top_outer[1]],[-108.3,91.5],[-108.3,bottom_y],[bottom_x,bottom_y],[top_inner[0],top_inner[1]]]
n=len(section);v=[[x,y,z]for z in [-263,-116]for x,y in section];f=[list(reversed(range(n))),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n]for i in range(n)];mesh('FP_west_acoustic_cornice',v,f,'warm_walnut',expected_retained_contact='west_acoustic_tapered_return inner/top faces only')
field=box(-108.3,-263,-34.75,-116)
def ellipse(rx,rz,steps=120):return Polygon([(-76+rx*math.sin(i*math.tau/steps),-207+rz*math.cos(i*math.tau/steps))for i in range(steps)])
inner=ellipse(23,14);halo=ellipse(24.15,15.15)
prism('FP_inner_oval_acoustic_recess',inner,91.4,91.5,'auditorium_navy_fibre')
prism('FP_ring_backing_cap',halo.difference(inner),91.4,91.5,'ivory_enamel')
outer=field.difference(halo);rear=outer.intersection(box(-200,-153,0,0));front=outer.difference(rear)
prism('FP_rear_foyer_acoustic_ceiling',rear,91.4,91.5,'ivory_enamel')
# Twelve intentionally broad radial finish fields follow the existing ellipse.
for i in range(12):
 a0=i*math.tau/12;a1=(i+1)*math.tau/12;p=Polygon([(-76,-207),(-76+300*math.sin(a0),-207+300*math.cos(a0)),(-76+300*math.sin(a1),-207+300*math.cos(a1))]);part=front.intersection(p)
 prism(f'FP_radial_acoustic_field_{i:02}',part,91.12,91.5,'warm_walnut'if i in [2,5,8,11]else'ivory_enamel')
# Four visible short ring-to-cap contacts. They join only the ring and new roof.
for i,t in enumerate([0,math.pi/2,math.pi,3*math.pi/2]):
 x=-76+23.5*math.sin(t);z=-207+14.5*math.cos(t);cuboid(f'FP_ring_short_contact_{i}',[x-.045,91.35,z-.045],[x+.045,91.4,z+.045],'champagne_metal',expected_retained_contact='Actual canopy ring topY91.35')
# A real thin opal annulus, divided into16segments. Point lights sit outside it.
for i in range(16):
 verts=[]
 for k in range(9):
  t=(i+k/8)*math.tau/16;verts.append((-76+23.57*math.sin(t),-207+14.57*math.cos(t)))
 for k in reversed(range(9)):
  t=(i+k/8)*math.tau/16;verts.append((-76+23.43*math.sin(t),-207+14.43*math.cos(t)))
 prism(f'FP_ring_opal_segment_{i:02}',Polygon(verts),90.97,91.0,'hospitality_opal',expected_retained_contact='Actual canopy lower faceY91.0',fixture_id=f'canopy_ring_emitter_{i:02}')
# Backstage closure stays outside the exact3.4m crossroute and real bay doors.
for label,x0,x1 in [('port',-116.25,-116),('starboard',-36,-35.75)]:cuboid('FP_backstage_'+label+'_side_closure',[x0,69.5,-263],[x1,74.3,-258.7],'staff_bluegrey_paint',expected_retained_contact='Fore/bay wall ends; fixed support on proposed D11 floor')
for i,(x0,x1)in enumerate([(-116,-96),(-95.75,-76),(-75.75,-56),(-55.75,-36)]):
 prism(f'FP_backstage_bay_ceiling_{i}',box(x0,-262.75,x1,-258.95),74.12,74.3,'staff_white_paint',expected_retained_contact='Existing fore/partition/front wall edges')
prism('FP_backstage_corridor_soffit',box(-116,-258.7,-36,-255.3),74.12,74.3,'staff_white_paint')
# The courtyard remains an actual stage, with folded textile and visible rigging.
# Shrink each side pack inside its reviewed envelope to keep100mm to orchestra walls.
for side,x0,x1 in [('port',-95.65,-94.1),('starboard',-57.9,-56.35)]:
 wave=[]
 for i in range(25):wave.append((x0+(x1-x0)*i/24,-240.55+(.12 if i%2 else-.12)))
 cloth=Polygon(wave+[(x,z-.008)for x,z in reversed(wave)])
 prism('FP_'+side+'_stowed_stage_drape',cloth,70.15,85.9,'auditorium_amber_velvet',role='static_theatrical_textile_no_behavior')
 rod('FP_'+side+'_drape_track',[x0,86.02,-240.55],[x1,86.02,-240.55],.025,'champagne_metal')
 for i,x in enumerate([x0+.15,x1-.15]):
  cuboid(f'FP_{side}_drape_fixed_saddle_{i}',[x-.03,85.98,-240.58],[x+.03,86.20,-239.985],'champagne_metal',expected_retained_contact='Bounded fixed saddle into back/underside of proscenium head; no moving contact')
 for i in range(8):
  x=x0+(x1-x0)*(i+.5)/8;rod(f'FP_{side}_drape_runner_{i}',[x,85.9,-240.55],[x,86.02,-240.55],.012,'champagne_metal')
wave=[]
for i in range(81):wave.append((-93.8+35.6*i/80,-251.7+(.12 if i%2 else-.12)))
prism('FP_original_navy_cyclorama',Polygon(wave+[(x,z-.008)for x,z in reversed(wave)]),70.15,85.8,'auditorium_navy_fibre',role='static_theatrical_textile_no_behavior')
rod('FP_cyclorama_top_rail',[-93.85,85.92,-251.7],[-58.15,85.92,-251.7],.05,'champagne_metal',n=10)
for i,x in enumerate([-90,-76,-62]):
 rod(f'FP_visible_scenic_hanger_{i}',[x,85.92,-251.7],[x,91.12,-251.7],.022,'champagne_metal',expected_retained_contact='NEW roof underside; no hidden unsupported endpoint')
 cuboid(f'FP_scenic_ceiling_plate_{i}',[x-.09,91.115,-251.79],[x+.09,91.13,-251.61],'champagne_metal',expected_retained_contact='NEW radial acoustic roof only')
# Actual cyclorama tabs contact the pleated upper hem and the visible rail.
for i in range(40):
 x=-93.8+35.6*(i+.5)/40
 rod(f'FP_cyclorama_tab_{i:02}',[x,85.79,-251.584],[x,85.92,-251.7],.008,'champagne_metal')
# Six real fixed stage-head yoke hangers, outside the retained moving hood.
for i,x in enumerate([-91,-85,-79,-73,-67,-61]):
 for side in [-1,1]:
  rod(f'FP_stage_yoke_saddle_{i}_{side}',[x+side*.215,85.93,-238.8],[x+side*.215,86.12,-238.8],.012,'champagne_metal',expected_retained_contact='Upper fixed end20mm into proscenium head underside; lower end10mm into fixed yoke pointed top, positive section bearing; no moving hood contact')
# Low-profile textile islands are visual finishes, never duplicate floor colliders.
finish=json.loads((R/'SURFACE_CONTENTS_AND_FINISH_PLAN.json').read_text())
for rug in finish['floor_finish_islands']:
 shape=Polygon(rug['boundary_xz']);inside=shape.buffer(-rug['border_width_m'],join_style='mitre')
 prism(rug['id']+'_border',shape.difference(inside),rug['top_y']-.002,rug['top_y'],rug['edge_material'],role='visual_finish_nonwalking')
 prism(rug['id']+'_field',inside,rug['top_y']-.002,rug['top_y'],rug['inner_material'],role='visual_finish_nonwalking')
# Six new pier mounts copy only the original bounded bracket profile.
lights=json.loads((R/'LIGHTING_ENCLOSURE_VIEW_PLAN.json').read_text())['fixtures']
for l in lights:
 if l.get('group')=='added_pier':
  x,y,z=l['new_fixed_mount_world'];cuboid(l['id']+'_actual_bracket',[x-.1,y-.15,z-.12],[x+.1,y+.15,z+.12],'champagne_metal',expected_retained_contact='Existing rear lantern pier face only')
# Canonical float32 source authoring removes only collapsed zero-area cells.
# This prevents false support from microscopic triangulation slivers in new roof fields.
cleanup=[]
for o in objects:
 original=np.array(o['vertices_world'],dtype=float);quant=original.astype(np.float32).astype(float);vertices=[];lookup={};mapping={}
 for i,v in enumerate(quant):
  key=tuple(v)
  if key not in lookup:lookup[key]=len(vertices);vertices.append(list(v))
  mapping[i]=lookup[key]
 faces=[];removed=0
 for f in o['faces']:
  ids=[]
  for i in f:
   j=mapping[i]
   if not ids or ids[-1]!=j:ids.append(j)
  if len(ids)>1 and ids[0]==ids[-1]:ids.pop()
  if len(set(ids))<3:removed+=1;continue
  a=np.array([vertices[i]for i in ids]);area_vec=sum((np.cross(a[j]-a[0],a[j+1]-a[0])for j in range(1,len(a)-1)),np.zeros(3))
  if np.linalg.norm(area_vec)<1e-11:removed+=1;continue
  faces.append(ids)
 volume=sum(np.dot(np.array(vertices[f[0]]),np.cross(np.array(vertices[f[j]]),np.array(vertices[f[j+1]])))/6 for f in faces for j in range(1,len(f)-1))
 if volume<0:faces=[list(reversed(f))for f in faces];volume=-volume
 assert volume>1e-10,(o['name'],volume)
 o['vertices_world']=vertices;o['faces']=faces;o['positive_signed_volume_m3']=float(volume)
 cleanup.append({'object':o['name'],'removed_collapsed_faces':removed,'maximum_float32_coordinate_error_m':float(np.linalg.norm(quant-original,axis=1).max()),'positive_signed_volume_m3':float(volume)})
# Every source addition stays inside original allocation and top envelope.
allv=np.array([v for o in objects for v in o['vertices_world']]);assert allv[:,0].min()>=-118 and allv[:,0].max()<=-34 and allv[:,2].min()>=-265 and allv[:,2].max()<=-115 and allv[:,1].max()<=91.50000001
report={'status':'Pure new architecture geometry; unbuilt source, no rendered/runtime acceptance','base_geometry_sha256':hashlib.sha256((P/'source/geometry.json').read_bytes()).hexdigest(),'objects':objects,'new_mesh_cleanup':cleanup,'expected_contacts_are_bounded_fixed_joints_not_moving_exemptions':True,'roof_max_y':float(allv[:,1].max()),'bounds_world':{'min':allv.min(0).tolist(),'max':allv.max(0).tolist()},'not_claimed':['Source mesh/export parity','Actual source light receiver checks','Pressure/load certification','Runtime/visual acceptance']};(R/'ARCHITECTURE_ADDITIONS_GEOMETRY.json').write_text(json.dumps(report,indent=2)+'\n');print('New architecture objects',len(objects),'vertices',len(allv),'bounds',report['bounds_world'])
