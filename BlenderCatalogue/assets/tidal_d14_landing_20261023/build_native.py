import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];N=R/'BlenderCatalogue/assets/tidal_d14_landing_20261023';G=R/'Game/tidal_d14_landing_20261023';D=json.loads((R/'Game/data/architecture/TIDAL_LIFT_RECEIVING_CANDIDATE.json').read_text())
assert not (N/'TidalD14Landing_r001.blend').exists(), 'Use a named successor; preserve the existing native revision'
assert not (G/'TidalD14Landing_r001.glb').exists(), 'Preserve the existing runtime export'
assert hashlib.sha256((R/'Game/assets/models'/D['model_file']).read_bytes()).hexdigest()==D['source_sha256']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
materials={}
for name,color in {'ivory':(.69,.63,.49,1),'wood':(.24,.115,.055,1),'brass':(.40,.28,.13,1),'teal':(.075,.21,.18,1),'soil':(.075,.055,.035,1),'light':(1,.76,.40,1)}.items():
 m=bpy.data.materials.new('TidalLanding_'+name);m.diffuse_color=color;m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Roughness'].default_value=.72
 if name=='light':p.inputs['Emission Color'].default_value=color;p.inputs['Emission Strength'].default_value=2
 materials[name]=m
parts=[];objects=[]
def box(name,c,size,mat,bevel=.03,collision=True):
 bpy.ops.mesh.primitive_cube_add(size=1,location=(c[0],-c[2],c[1]));o=bpy.context.object;o.name='T14L_'+name;o.scale=(size[0],size[2],size[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Authored softened edges','BEVEL');mod.width=bevel;mod.segments=2;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.materials.append(materials[mat]);o['runtime_collision']=collision;o['architecture_owner']='tidal_d14_landing_r001';o['role']=name
 parts.append({'name':o.name,'center':c,'size':size,'material':mat,'collision':collision});objects.append(o);return o
# Four visible, floor-bearing, tiered supports; open front and side outlooks.
for i,(x,z) in enumerate([(-92,-393),(-82,-393),(-92,-386.4),(-82,-386.4)]):
 box(f'PierFoot_{i}',[x,88.66,z],[.72,.32,.72],'wood',.07)
 box(f'FlutedPier_{i}',[x,90.25,z],[.40,2.86,.48],'ivory',.08)
 box(f'PierCapital_{i}',[x,91.80,z],[.74,.28,.76],'wood',.06)
 box(f'CapitalBand_{i}',[x,91.96,z],[.78,.06,.80],'brass',.02)
# Perimeter canopy and two raised roof fields leave a generous central longitudinal opening.
for i,x in enumerate([-92,-82]):
 box(f'LongCanopyBeam_{i}',[x,92.06,-389.7],[.62,.20,7.5],'wood',.05)
for i,z in enumerate([-393.4,-386.0]):
 box(f'CrossCanopyBeam_{i}',[-87,92.06,z],[10.6,.20,.64],'wood',.05)
for i,x in enumerate([-90.65,-83.35]):
 box(f'FloatingCofferField_{i}',[x,92.19,-389.7],[2.08,.16,6.8],'ivory',.08)
 box(f'CofferInset_{i}',[x,92.08,-389.7],[1.72,.06,6.35],'teal',.04)
 for j,z in enumerate([-392.7,-390.7,-388.7,-386.7]):box(f'CofferRib_{i}_{j}',[x,92.035,z],[2.05,.10,.10],'wood',.03)
# Rear enclosure rises behind the unchanged chairs. Front access and cross-court view stay open.
for i in range(9):
 x=-91.4+i*1.1;z=-393.7+.035*((x+87)/4.4)**2
 box(f'AcousticBacking_{i}',[x,89.71,z],[1.04,2.42,.20],'ivory',.035)
 box(f'WalnutLowerPanel_{i}',[x,89.12,z+.12],[1.04,1.12,.10],'wood',.025)
 box(f'UpperReveal_{i}',[x,91.02,z+.025],[1.06,.12,.30],'brass',.02)
# Two contained planted beds, lifted visually by layered stone/wood rims. No replacement floor.
for i,x in enumerate([-90.0,-84.0]):
 box(f'PlanterBase_{i}',[x,88.80,-392.2],[3.6,.60,1.1],'wood',.10)
 box(f'PlanterRim_{i}',[x,89.14,-392.2],[3.7,.10,1.2],'ivory',.06)
 box(f'ContainedSoil_{i}',[x,89.201,-392.2],[3.3,.022,.82],'soil',.035,False)
# Two ceiling-mounted practical fixtures, integrated with source-budgeted runtime lights.
lights=[]
for i,x in enumerate([-90,-84]):
 box(f'FixtureStem_{i}',[x,91.78,-389.6],[.10,.42,.10],'brass',.02)
 box(f'FixtureHousing_{i}',[x,91.52,-389.6],[.72,.14,.62],'wood',.05)
 box(f'FixtureDiffuser_{i}',[x,91.43,-389.6],[.60,.035,.50],'light',.03,False)
 lights.append({'name':f'TidalD14LandingFixture_{i}','position':[x,91.35,-389.6],'range':9.0,'energy':1.4,'color':[1.0,.80,.58]})
# Existing catalogue plants remain linked native sources and instanced runtime sources.
plants=[{'catalogue_id':'AST-BOT-002' if i%2==0 else 'AST-BOT-003','position':[x,89.22,-392.2],'scale':.62,'yaw':i*.8} for i,x in enumerate([-91.1,-90,-88.9,-85.1,-84,-82.9])]
# Exact retained-floor containment for all new floor-bearing members.
def ring_contains(pt,ring):
 x,y=pt;inside=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if ((a[1]>y)!=(b[1]>y)) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside
def contains(pt,geo):
 polygons=[geo['coordinates']] if geo['type']=='Polygon' else geo['coordinates']
 return any(ring_contains(pt,p[0]) and not any(ring_contains(pt,h) for h in p[1:]) for p in polygons)
floor=next(x for x in D['floor_regions'] if x['name']=='D14_OffsetTidalLanding')['geometry']
checks=0
for p in parts:
 if p['center'][1]-p['size'][1]/2<88.501:
  for dx in [-.5,.5]:
   for dz in [-.5,.5]:
    assert contains((p['center'][0]+dx*p['size'][0],p['center'][2]+dz*p['size'][2]),floor),p['name'];checks+=1
 assert p['center'][2]+p['size'][2]/2<-384.5,p['name']
assert min(p['center'][1]-p['size'][1]/2 for p in parts if 'Canopy' in p['name'] or 'Coffer' in p['name'])-88.5>=3.45
# Export only new architecture. Linked botanical sources remain editable references, not duplicated exports.
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(G/'TidalD14Landing_r001.glb'),use_selection=True,export_format='GLB',export_extras=True,export_yup=True)
for i,p in enumerate(plants):
 src=R/'BlenderCatalogue'/D['retained_asset_definitions'][p['catalogue_id']]['source']
 with bpy.data.libraries.load(str(src),link=True) as (available,chosen):chosen.collections=[available.collections[0]] if available.collections else []
 if chosen.collections:
  e=bpy.data.objects.new('LinkedPlant_'+str(i),None);e.instance_type='COLLECTION';e.instance_collection=chosen.collections[0];bpy.context.scene.collection.objects.link(e);e.location=(p['position'][0],-p['position'][2],p['position'][1]);e.scale=(p['scale'],)*3;e.rotation_euler.z=-p['yaw']
for library in bpy.data.libraries:library.filepath=bpy.path.relpath(library.filepath,start=str(N))
bpy.ops.wm.save_as_mainfile(filepath=str(N/'TidalD14Landing_r001.blend'))
plan={'status':'authored_candidate_not_visual_accepted','original_definition':'Game/data/architecture/TIDAL_LIFT_RECEIVING_CANDIDATE.json','original_definition_sha256':hashlib.sha256((R/'Game/data/architecture/TIDAL_LIFT_RECEIVING_CANDIDATE.json').read_bytes()).hexdigest(),'source_model_sha256':D['source_sha256'],'floor_owner':'D14_OffsetTidalLanding','floor_y':88.5,'parts':parts,'plants':plants,'lights':lights,'floor_corner_checks':checks,'unchanged_furniture':['D14_LandingSeat_-89','D14_LandingSeat_-85','D14_LandingTable'],'new_floors':0,'new_guest_units':0,'new_reserved_rests':0,'protected_dry_route_z':[-374,-366],'minimum_new_canopy_clearance':3.45,'native':str((N/'TidalD14Landing_r001.blend').relative_to(R))}
plan['glb_sha256']=hashlib.sha256((G/'TidalD14Landing_r001.glb').read_bytes()).hexdigest();plan['native_sha256']=hashlib.sha256((N/'TidalD14Landing_r001.blend').read_bytes()).hexdigest();(G/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n');print('TIDAL_LANDING_AUTHORED',len(parts),'parts',checks,'floor checks')
