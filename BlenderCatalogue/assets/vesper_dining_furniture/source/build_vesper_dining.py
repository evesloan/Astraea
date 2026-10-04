"""Original Vesper dining furniture, profiled for fitted table groups."""
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


import sys
CHAIR='--chair' in sys.argv
SIX='--six' in sys.argv
AID='AST-DIN-002' if CHAIR else ('AST-DIN-001_six' if SIX else 'AST-DIN-001')
def rings(name,rows,role,n=24,cap_top=True):
 v=[(cx+rx*math.cos(2*math.pi*i/n),cy+ry*math.sin(2*math.pi*i/n),h)for cx,cy,rx,ry,h in rows for i in range(n)]
 f=[tuple(reversed(range(n)))]+([tuple(range((len(rows)-1)*n,len(rows)*n))]if cap_top else[])+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i)for j in range(len(rows)-1)for i in range(n)]
 return mesh(name,v,f,role)
if not CHAIR:
 rx,ry=(1.20,.72)if SIX else(.85,.85)
 for cx in ([-.56,.56]if SIX else[0]):
  rings('DIN_WeightedPedestal_'+str(cx),[(cx,0,.32,.28,0),(cx,0,.34,.30,.035),(cx,0,.28,.24,.065),(cx,0,.15,.12,.12),(cx,0,.095,.085,.52),(cx,0,.14,.12,.66),(cx,0,.28,.24,.725)],'warm_walnut')
  rings('DIN_FootTrim_'+str(cx),[(cx,0,.34,.30,.029),(cx,0,.34,.30,.041)],'champagne_metal')
 rings('DIN_ProfiledTableRim',[(0,0,rx-.03,ry-.03,.725),(0,0,rx,ry,.744),(0,0,rx,ry,.773),(0,0,rx-.025,ry-.025,.79)],'warm_walnut',32,False)
 v=[((rx-inset)*math.cos(2*math.pi*i/32),(ry-inset)*math.sin(2*math.pi*i/32),.79)for inset in [.025,.065]for i in range(32)]
 mesh('DIN_InlayBorder',v,[(i,(i+1)%32,(i+1)%32+32,i+32)for i in range(32)],'warm_walnut')
 rings('DIN_InsetStoneTop',[(0,0,rx-.07,ry-.07,.779),(0,0,rx-.065,ry-.065,.787)],'warm_stone',32)
 datum('table_surface',(0,0,.79));datum('floor_contact',(0,0,0))
 seats=[(-.62,-1.08),(.62,-1.08),(-.62,1.08),(.62,1.08),(-1.54,0),(1.54,0)]if SIX else[(-1.2,0),(1.2,0),(0,-1.2),(0,1.2)]
 for i,(x,y)in enumerate(seats):datum('seat_anchor_'+str(i),(x,y,0))
else:
 # Splayed legs and a swept open back keep the dining chair lighter than lounge seating.
 for side in [-1,1]:
  for back in [-1,1]:
   cx=side*.26;cy=back*.23
   rings('DIN_SplayedLeg_%s_%s'%(side,back),[(cx,cy,.035,.035,0),(side*.235,back*.21,.042,.038,.08),(side*.21,back*.18,.035,.038,.405)],'warm_walnut',8)
 rings('DIN_SeatShell',[(0,0,.31,.295,.38),(0,0,.35,.315,.405),(0,0,.35,.315,.44),(0,0,.32,.29,.454)],'warm_walnut',24)
 rings('DIN_TailoredCushion',[(0,-.018,.315,.278,.447),(0,-.018,.33,.292,.465),(0,-.018,.30,.27,.49)],'clay_weave',24)
 # Curved back shell section, open below the shoulder, with a tailored upholstered insert.
 for name,half,z0,z1,thick,role in [('DIN_SweptBack',.35,.58,.99,.075,'warm_walnut'),('DIN_BackCushion',.307,.63,.944,.035,'clay_weave')]:
  v=[];n=12
  for edge in [-1,1]:
   for h in [z0,z1]:
    for i in range(n+1):
     x=-half+2*half*i/n; y=.22+.12*(h-.58)/.41+.09*(1-(x/half)**2)+edge*thick/2
     if role=='clay_weave':y-=.06
     v.append((x,y,h))
  k=n+1;f=[]
  for i in range(n):f.extend([(i,i+1,k+i+1,k+i),(2*k+i,3*k+i,3*k+i+1,2*k+i+1),(i,2*k+i,2*k+i+1,i+1),(k+i,k+i+1,3*k+i+1,3*k+i)])
  f.extend([(0,k,3*k,2*k),(n,2*k+n,3*k+n,k+n)]);mesh(name,v,f,role)
 for side in [-1,1]:beam('DIN_BackStile_'+str(side),[(side*.28,.20,.40),(side*.31,.23,.60),(side*.31,.34,.96)],.055,.055,'warm_walnut')
 datum('seat_contact',(0,-.018,.49));datum('front_approach',(0,-.85,0));datum('floor_contact',(0,0,0))
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;bpy.ops.file.pack_all();source=ROOT/'source'/(AID+'.blend');export=ROOT/'exports'/(AID+'.glb');bpy.ops.wm.save_as_mainfile(filepath=str(source));tri=0
for o in parts:o.data.calc_loop_triangles();tri+=len(o.data.loop_triangles)
bpy.ops.export_scene.gltf(filepath=str(export),export_format='GLB',export_yup=True,export_extras=True)
record={'catalogue_id':AID,'name':'Vesper swept dining chair'if CHAIR else'Vesper profiled pedestal dining table','source':'source/'+AID+'.blend','export':'exports/'+AID+'.glb','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'export_sha256':hashlib.sha256(export.read_bytes()).hexdigest(),'triangles':tri,'status':'Editable authored component; source roundtrip, fitted placement and visual review pending; no species-wide seating acceptance'};(ROOT/(AID+'.manifest.json')).write_text(json.dumps(record,indent=2)+'\n');print(record)
