"""Original starboard residential house: staggered upper commons, alternating stairs and fitted enclosure."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];CAT=ROOT.parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mats={};parts=[];material_contract=json.loads((CAT/'materials/material_manifest.json').read_text())['materials']
for role in ['ivory_enamel','warm_walnut','warm_stone','champagne_metal','teal_weave','botanical_soil','oatmeal_weave','clay_weave']:
 m=bpy.data.materials.new(role);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Roughness'].default_value=material_contract.get(role,{}).get('roughness',.82);b.inputs['Metallic'].default_value=material_contract.get(role,{}).get('metallic',0);m['meters_per_tile_uv']=material_contract.get(role,{}).get('meters_per_tile_uv',[1,1])
 path=CAT/'materials'/('botanical/'+role+'.png' if role.startswith('botanical') else role+'.png')
 t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(path));t.interpolation='Closest';m.node_tree.links.new(t.outputs['Color'],b.inputs['Base Color']);mats[role]=m
m=bpy.data.materials.new('GardenOpalLens');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(1,.95,.84,1);b.inputs['Emission Color'].default_value=(1,.91,.75,1);b.inputs['Emission Strength'].default_value=.7;mats['lens']=m

def mesh(name,vertices,faces,role):
 d=bpy.data.meshes.new(name);d.from_pydata(vertices,[],faces);d.update();bm=bmesh.new();bm.from_mesh(d);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(d);bm.free();o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);d.materials.append(mats[role]);parts.append(o);uv=d.uv_layers.new(name='MetreScaled')
 for p in d.polygons:
  n=p.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized() if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u).normalized();scale=mats[role].get('meters_per_tile_uv',[1,1])
  for li in p.loop_indices:
   q=d.vertices[d.loops[li].vertex_index].co
   uv.data[li].uv=(q.dot(u)/scale[0],q.dot(v)/scale[1])
 return o

def extrusion(name,outline,bottom,top,role):
 n=len(outline);v=[(x,y,z)for z in [bottom,top]for x,y in outline];f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)];return mesh(name,v,f,role)

def beam(name,points,width,depth,role):
 v=[]
 for i,p in enumerate(points):
  p=Vector(p);t=(Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])).normalized();side=Vector((0,1,0)) if abs(t.y)<.95 else Vector((1,0,0));side=(side-t*t.dot(side)).normalized();up=t.cross(side).normalized()
  for w,h in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]:v.append(tuple(p+side*w+up*h))
 f=[(3,2,1,0),tuple(range(len(v)-4,len(v)))]+[(i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j)for i in range(len(points)-1)for j in range(4)];return mesh(name,v,f,role)

def datum(name,p):
 o=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(o);o.location=p



AID='AST-COM-003';D=json.loads((ROOT/'source/house_contract.json').read_text())
assert all(a['catalogue_id']!=AID or a['family']=='starboard_house_upper' for a in json.loads((CAT/'catalogue_manifest.json').read_text())['assets'])
def xyz(x,y,z):return(x-63,-z,y-84)
def xy(p):return(p[0]-63,-p[1])
def wall(name,a,b,lo,hi,width,role):
 a=Vector(xy(a));b=Vector(xy(b));t=(b-a).normalized();n=Vector((-t.y,t.x))*width/2
 return extrusion(name,[tuple(a+n),tuple(b+n),tuple(b-n),tuple(a-n)],lo-84,hi-84,role)
def slab(name,x0,x1,z0,z1,lo,hi,role):return extrusion(name,[xy(p)for p in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]],lo-84,hi-84,role)
def roof_height(x):
 stations=[(63,105.35),(68,105.70),(75,106.05),(85,106.05),(93,105.60),(97,105.35)]
 for (xa,ya),(xb,yb)in zip(stations,stations[1:]):
  if xa<=x<=xb:return ya+(yb-ya)*(x-xa)/(xb-xa)
 return 105.35
m=bpy.data.materials.new('HouseSmokedGlass');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.25,.46,.49,.38);b.inputs['Alpha'].default_value=.38;mats['glass']=m
# Continue the existing piers rather than putting new posts through the Night garden.
for i,(x,z)in enumerate(D['preserved_piers']):
 cx,cy=xy((x,z));q=[(cx-.245,cy-.32),(cx+.245,cy-.32),(cx+.32,cy-.245),(cx+.32,cy+.245),(cx+.245,cy+.32),(cx-.245,cy+.32),(cx-.32,cy+.245),(cx-.32,cy-.245)]
 extrusion('HC_PierExtension_'+str(i),q,92.16-84,106.26-84,'warm_stone')
 for y in [92.76,97.26,101.76,106.26]:
  q2=[(cx+(a-cx)*1.05,cy+(b-cy)*1.05)for a,b in q]
  extrusion('HC_Bearing_%s_%s'%(i,y),q2,y-84-.18,y-84,'champagne_metal')
# Perimeter transfers stay outside the intermediate stair landing headroom.
for y in [92.76,97.26,101.76,106.26]:
 for i,(a,b)in enumerate([((63.2,-12),(94,-12)),((64,12),(94,12)),((63.2,-12),(63.2,12)),((94,-11.5),(94,-2.16)),((94,2.16),(94,11.5)),((94,11.5),(94,12)),((94,-11.5),(94,-12)),((64,12),(63.2,12))]):
  wall('HC_PerimeterTransfer_%s_%s'%(y,i),a,b,y-.36,y,.30,'warm_walnut')
# New enclosed shaft interfaces begin exactly at the retained lower enclosure.
for side in [-1,1]:wall('HC_ShaftSide_'+str(side),(92.02,side*2.1),(95.96,side*2.1),92.16,106.26,.12,'ivory_enamel')
wall('HC_ShaftRear',(95.96,-2.1),(95.96,2.1),92.16,106.26,.12,'warm_walnut')
for i,(lo,hi)in enumerate([(92.16,93),(95.86,97.5),(100.36,102),(104.86,106.26)]):wall('HC_ShaftFrontBand_'+str(i),(92.1,-2.04),(92.1,2.04),lo,hi,.12,'ivory_enamel')
# Profiled exterior room edges belong to the same ship; openings differ by level.
for record in D['floor_regions']:
 y=record['floor_y'];tag=record['deck']
 for side in [-1,1]:
  points=[(63,side*14),(72,side*14),(78,side*13.2),(82,side*13.2),(86,side*14),(93,side*14),(97,side*10)]
  for i,(a,b)in enumerate(zip(points,points[1:])):
   top=106.26 if y==102 else y+4.26 # Walls meet structural cover behind the shaped ceiling, closing roof-edge gaps.
   wall('HC_ProfileWall_%s_%s_%s'%(tag,side,i),a,b,y,top,.16,'ivory_enamel')
   wall('HC_Wainscot_%s_%s_%s'%(tag,side,i),a,b,y,y+.70,.16,'warm_walnut')
 wall('HC_RearWall_'+tag,(96.9,-10),(96.9,10),y,106.26 if y==102 else y+4.26,.18,'ivory_enamel')
 # Bridge frames span into the existing atrium and commons end supports.
 for i,(a,b)in enumerate(zip(record['arrival'],record['arrival'][1:])):
  wall('HC_ArrivalUnderframe_%s_%s'%(tag,i),a,b,y-.65,y-.24,3.65,'ivory_enamel')
  wall('HC_ArrivalCanopy_%s_%s'%(tag,i),a,b,y+3.65,y+3.80,3.80,'oatmeal_weave')
 # Ring edges: leave real seams and stair exits open, retain actual shaft protection.
 for ri,ring in enumerate([record['boundary']]+record['holes']):
  for j,(a,b)in enumerate(zip(ring,ring[1:]+ring[:1])):
   if abs(a[0]-50)<.001 and abs(b[0]-50)<.001:continue
   if ri>0 and min(a[0],b[0])>92:continue
   if ri==0 and min(a[0],b[0])>=63 and max(a[0],b[0])<=97 and max(abs(a[1]),abs(b[1]))<=14.001 and (abs(a[1])>=13 or abs(b[1])>=13 or min(a[0],b[0])>=96.8):continue
   segments=[(a,b)];east=tag in ['D15','D17']
   if abs(a[1]-b[1])<.001 and ((east and abs(a[1]-4.72)<.001)or(not east and abs(a[1]+9.58)<.001)):
    lower,upper=(88.60,90.70)if east else(67.15,69.25);lo,hi=sorted([a[0],b[0]]);segments=[]
    if lo<lower:segments.append(([lo,a[1]],[min(hi,lower),a[1]]))
    if hi>upper:segments.append(([max(lo,upper),a[1]],[hi,a[1]]))
   for k,(aa,bb)in enumerate(segments):
    width=.14
    if east and abs(aa[1]-11.42)<.001 and abs(bb[1]-11.42)<.001:
     aa=[aa[0],11.455];bb=[bb[0],11.455];width=.07
    name='%s_%s_%s_%s'%(tag,ri,j,k)
    wall('HC_Fascia_'+name,aa,bb,y-.24,y+.025,width,'ivory_enamel')
    wall('HC_GuardBase_'+name,aa,bb,y+.025,y+.35,min(width,.10),'warm_walnut')
    wall('HC_GuardGlass_'+name,aa,bb,y+.35,y+1.01,.024,'glass')
    wall('HC_GuardCap_'+name,aa,bb,y+1.01,y+1.09,min(width,.12),'champagne_metal')
# Three alternating, explicit switchback stairs; smooth contacts are supplied in runtime.
for index,entry in enumerate(D['new_stair_bases']):
 base=entry['y'];east=entry['type']=='east';spec=D['east_stair'] if east else None
 first=spec['first_x'] if east else D['west_stair']['first_flight']['x'];second=spec['second_x']if east else D['west_stair']['second_flight']['x'];z0,z1=spec['z']if east else D['west_stair']['first_flight']['z'];lz=spec['landing_z']if east else D['west_stair']['middle_landing']['z'];run=(z1-z0)/15
 for flight,xs in enumerate([first,second]):
  low=base+flight*2.25
  for step in range(15):
   a=z0+step*run if flight==0 else z1-(step+1)*run
   slab('HC_Step_%s_%s_%s'%(index,flight,step),xs[0],xs[1],a,a+run,low+step*.15,low+(step+1)*.15,'warm_stone')
  for side,x in enumerate([xs[0]-.05,xs[1]+.05]):
   ya,yb=(low,low+2.25)if flight==0 else(low+2.25,low)
   for role,lo,hi,width in [('warm_walnut',.05,.33,.10),('glass',.33,1.02,.024),('champagne_metal',1.02,1.10,.12)]:
    v=[xyz(x+dx,y+h,z)for dx in [-width/2,width/2]for z,y,h in [(z0,ya,lo),(z1,yb,lo),(z1,yb,hi),(z0,ya,hi)]]
    mesh('HC_StairGuard_%s_%s_%s_%s'%(index,flight,side,role),v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],role)
   v=[xyz(x+dx,y,z)for dx in [-.04,.04]for z,y in [(z0,base),(z1,base),(z1,yb),(z0,ya)]]
   mesh('HC_UnderflightSide_%s_%s_%s'%(index,flight,side),v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'warm_walnut')
 slab('HC_Midlanding_'+str(index),first[0],second[1],lz[0],lz[1],base+2.01,base+2.25,'warm_stone')
 back=lz[1]+(.045 if east else .05);backwidth=.09 if east else .10
 wall('HC_MidlandingBack_'+str(index),(first[0]-.05,back),(second[1]+.05,back),base,base+3.35,backwidth,'warm_walnut')
 for x in [first[0]-.05,second[1]+.05]:wall('HC_MidlandingSide_%s_%s'%(index,x),(x,lz[0]),(x,lz[1]),base,base+3.35,.10,'warm_walnut')
 wall('HC_StairWellGuard_'+str(index),(first[1],lz[0]),(second[0],lz[0]),base+2.25,base+3.35,.10,'warm_walnut')
 wall('HC_HighFlightFront_'+str(index),(second[0]-.05,z0),(second[1]+.05,z0),base,base+4.5,.10,'warm_walnut')
 wall('HC_CentreClosure_'+str(index),(first[1],z0),(second[0],z0),base,base+2.25,.10,'warm_walnut')
# Top ceiling is shaped under, never through, the separate D18-owned opaque cover.
stations=[(63,105.35),(68,105.70),(75,106.05),(85,106.05),(93,105.60),(97,105.35)]
for i,((xa,ya),(xb,yb))in enumerate(zip(stations,stations[1:])):
 wa=14-max(0,xa-93);wb=14-max(0,xb-93);q=[xyz(xa,ya,-wa),xyz(xb,yb,-wb),xyz(xb,yb,wb),xyz(xa,ya,wa)]
 mesh('HC_TopCeiling_'+str(i),q+[(x,y,z+.07)for x,y,z in q],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'ivory_enamel')
for z in [-10,-5,0,5,10]:beam('HC_TopCeilingRib_'+str(z),[xyz(x,y-.02,z)for x,y in stations],.18,.12,'warm_walnut')
fixture_sets=[(93,[(75,-11),(83,-11),(75,10),(83,10)]),(97.5,[(75,-11),(84,-11),(68,7),(89,0)]),(102,[(75,-11),(86,-8),(67,7),(89,0)])]
for level,(floor,positions)in enumerate(fixture_sets):
 for index,(x,z)in enumerate(positions):
  ceiling=roof_height(x)if floor==102 else floor+4.26;h=min(floor+3.65,ceiling-.14);cx,cy=xy((x,z))
  extrusion('HC_LampHousing_%s_%s'%(level,index),[(cx-.40,cy-.22),(cx+.40,cy-.22),(cx+.40,cy+.22),(cx-.40,cy+.22)],h-84,h-84+.12,'champagne_metal')
  extrusion('HC_LampLens_%s_%s'%(level,index),[(cx-.35,cy-.18),(cx+.35,cy-.18),(cx+.35,cy+.18),(cx-.35,cy+.18)],h-84-.015,h-84,'lens')
  beam('HC_LampMount_%s_%s'%(level,index),[xyz(x,h+.12,z),xyz(x,ceiling,z)],.04,.04,'champagne_metal')
  datum('light_%s_%s'%(level,index),xyz(x,h-.03,z))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source))
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Starboard residential commons upper section and alternating stairs','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'status':'Authored reviewed section; runtime sweeps, circulation and final visual acceptance pending'}
(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
