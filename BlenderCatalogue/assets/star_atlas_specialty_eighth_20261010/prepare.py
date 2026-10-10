from pathlib import Path
import json,hashlib,math,copy,subprocess,numpy as np
from shapely.geometry import Polygon,box,Point
from shapely.ops import unary_union,triangulate
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=json.loads((R/'BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json').read_text())['records'];U=json.loads((R/'Game/data/architecture/STAR_ATLAS_UNITS.json').read_text());manifest=json.loads((R/'BlenderCatalogue/catalogue_manifest.json').read_text());assets=manifest['assets'];assets=list(assets.values())if isinstance(assets,dict)else assets
ids=['AST-RST-QC-001','AST-RST-AQ-001','AST-RST-LN-001','AST-SAN-001','AST-SAN-002','AST-SAN-003','AST-LIB-STUDY-02','AST-GST-003','AST-LIB-008','AST-FUR-002','AST-LIB-007'];sources=[]
for cid in ids:
 found=[a for a in assets if a['catalogue_id']==cid];assert len(found)==1;a=found[0]
 for k in ['source','export']:assert sha(R/'BlenderCatalogue'/a[k])==a['source_sha256'if k=='source'else'export_sha256'],(cid,k)
 sources.append(a)
source_paths=['Game/data/architecture/STAR_ATLAS_UNITS.json','Game/data/architecture/CENTRAL_RESIDENTIAL_STREETS.json','Game/data/architecture/STAR_ATLAS_UPPER_COMMONS.json','Game/data/generated/structural_meshes.json','Game/data/generated/received_structural_meshes.json','Game/scripts/central_homes_adoption.gd','Game/scripts/central_house_connections.gd','Game/scripts/star_atlas_rooms.gd','Game/scripts/night_garden_rooms.gd','Game/scripts/guest_entry_door.gd','Game/scripts/guest_privacy_door.gd','Game/assets/models/STAR_ATLAS_UPPER_COMMONS_r001.glb','BlenderCatalogue/assets/star_atlas_upper_commons_20261009/source/StarAtlasUpperCommons.blend','BlenderCatalogue/catalogue_manifest.json','BlenderCatalogue/assets/residential_production_batch/inputs/PROPOSED_FULL_1000_PRODUCTION_ROWS.json']
pins={p:hashlib.sha256(subprocess.check_output(["git","show","f9332c0b27060afa893835c48031c2b34038df10:"+p],cwd=R)).hexdigest()for p in source_paths};parts=[];rooms=[]
def cube(name,lo,hi,role='ivory_enamel',category='architecture',collision=True):
 v=[[lo[0],lo[1],lo[2]],[hi[0],lo[1],lo[2]],[hi[0],hi[1],lo[2]],[lo[0],hi[1],lo[2]],[lo[0],lo[1],hi[2]],[hi[0],lo[1],hi[2]],[hi[0],hi[1],hi[2]],[lo[0],hi[1],hi[2]]];faces=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[3,7,6,2],[0,4,7,3],[1,2,6,5]];parts.append({'name':name,'verts':v,'faces':faces,'role':role,'category':category,'runtime_collision':collision})
reader=(R/'BlenderCatalogue/assets/tidal_d15_service_receiving_20261010/source_geometry.py').read_text();ns={'__file__':str(W/'geometry_reader.py')};exec(compile(reader,'retained_reader','exec'),ns)
for idx,profile,rest_id in [(569,'double_quiet_parallel_folio_lounge','AST-RST-QC-001'),(575,'double_aquatic_offset_transfer_folio','AST-RST-AQ-001')]:
 row=next(r for r in rows if r['source_envelope_index']==idx);assert row['house']=='port_central_upper_house'and row['proposed_rest_place_count']in[1,2];z=sum(row['allocation_z'])/2;x=row['allocation_x'][0];y=row['floor_y'];assert y==93
 below=next(u for u in U['units']if u['deck']=='D14'and u['allocation_x']==row['allocation_x']and u['allocation_z']==row['allocation_z']);proto=next(p for p in U['prototypes']if p['key']==below['source_recipe_key']);file='Game/assets/models/'+proto['model_file'];pins[file]=sha(R/file);tri=list(ns['triangles'](proto['model_file'],below['source_origin_world_xyz'],below['source_yaw_godot']));roof=[]
 source_roofs=json.load(open(W/'ROOF_SOURCE_TRIANGLES.json'))['rooms'][str(idx)]
 assert sha(R/source_roofs['native_source'])==source_roofs['native_sha256']
 original_vertices=np.unique(np.concatenate([t.reshape(-1,3)for n,t in tri]),axis=0)
 for record in source_roofs['triangles']:
  face=np.array(record['vertices']);poly=Polygon(face[:,[0,2]])
  if poly.area>.01:
   delta=np.sqrt(((face[:,None,:]-original_vertices[None,:,:])**2).sum(2)).min(1);assert delta.max()<.00003
   roof.append((face,poly,'native:'+record['name']))
 receiving=[];start=len(parts)
 def c(stem,ulo,uhi,ylo,yhi,vlo,vhi,role='ivory_enamel',cat='architecture',collision=True):cube(f'SA{idx}_{stem}',[x+ulo,y+ylo,z+vlo],[x+uhi,y+yhi,z+vhi],role,cat,collision)
 c('RoomFloor',0,12.9,-.24,0,-3.6,3.6,'warm_stone','floor')
 c('NorthSide',0,12.9,0,3.74,-3.6,-3.48);c('SouthSide',0,12.9,0,3.74,3.48,3.6)
 c('EntryShoulderNorth',0,.12,0,3.74,-3.48,-1.74);c('EntryShoulderSouth',0,.12,0,3.74,1.74,3.48);c('EntryHeader',0,.12,2.76,3.74,-1.8,1.8)
 c('Ceiling',0,12.9,3.74,3.9,-3.6,3.6)
 # Offset wash enclosure leaves entry and rest approach independent.
 c('WashEntrySide',1.8,1.92,0,3.74,.8,3.48);c('WashRearSide',5.4,5.52,0,3.74,.8,3.48)
 c('WashFrontLeft',1.92,2.61,0,3.74,.8,.92);c('WashFrontRight',3.79,5.4,0,3.74,.8,.92);c('WashHeader',2.61,3.79,2.3,3.74,.8,.92)
 c('EntryPrivacyDogleg',1.45,1.6,0,2.2,-3.48,-1.3,'warm_walnut','privacy')
 # Deep oval atrium aperture; no invented sky or hull outlook.
 center_y=1.95;radius_y=1.48;radius_z=3.0;oval=Polygon([(radius_z*math.cos(i*math.tau/32),center_y+radius_y*math.sin(i*math.tau/32))for i in range(32)])
 profile_poly=box(-3.48,0,3.48,3.74).difference(oval);vs=[];fs=[]
 for t in triangulate(profile_poly):
  if not profile_poly.covers(t.representative_point()):continue
  vv=list(t.exterior.coords)[:3];base=len(vs);vs.extend([[x+12.74,y+yy,z+zz]for zz,yy in vv]);fs.append([base+2,base+1,base])
 parts.append({'name':f'SA{idx}_OvalWindowReveal','verts':vs,'faces':fs,'role':'warm_walnut','category':'window_reveal','runtime_collision':True})
 glassverts=[[x+12.79,y+center_y,z]]+[[x+12.79,y+yy,z+zz]for zz,yy in oval.exterior.coords[:-1]];glassfaces=[[0,1+i,1+(i+1)%32]for i in range(32)];parts.append({'name':f'SA{idx}_OvalAtriumGlass','verts':glassverts,'faces':glassfaces,'role':'hospitality_glass','category':'window','runtime_collision':True})
 # Full deep reveal ring bridges oval face to wall/window depth.
 outer=[[x+12.58,y+yy,z+zz]for zz,yy in oval.exterior.coords[:-1]];inner=[[x+12.79,y+yy,z+zz]for zz,yy in oval.exterior.coords[:-1]];parts.append({'name':f'SA{idx}_OvalDepthReturn','verts':outer+inner,'faces':[[i,(i+1)%32,(i+1)%32+32,i+32]for i in range(32)],'role':'champagne_metal','category':'window_reveal','runtime_collision':True})
 # Distinct activity and storage silhouettes; a shaped screen protects rest from the arrival view.
 for i in range(4):c(f'BelongingsShelf_{i}',6.0,7.6,.35+i*.38,.39+i*.38,2.98,3.45,'warm_walnut','storage')
 c('BelongingsBack',6.0,7.6,0,1.75,3.4,3.48,'warm_walnut','storage')
 if profile.startswith('aquatic'):
  c('DryTransferBench',6.2,7.55,0,.4,-3.25,-2.65,'warm_walnut','dry_transfer');c('DryTransferPad',6.2,7.55,.4,.44,-3.25,-2.65,'teal_weave','dry_transfer');c('WetDryLowDivider',7.0,7.1,0,.18,-3.45,-2.65,'champagne_metal','wet_dry_boundary');c('RinseServiceMount',10.8,11.6,0,1.15,2.94,3.45,'ivory_enamel','environmental_fitting')
 rest_at=[x+(9.2 if idx!=437 else 8.6),y,z+(-1.15 if idx!=437 else-1.3)]
 bindings=[{'name':'ReservedRestSupport','catalogue_id':rest_id,'position':rest_at,'yaw':math.pi/2,'rest_slot_id':row['proposed_rest_slot_ids'][0]}, {'name':'LibraryStudyEdge','catalogue_id':'AST-LIB-STUDY-02','position':[x+10.8,y,z+1.95],'yaw':math.pi/2},{'name':'PersonalConsole','catalogue_id':'AST-GST-003','position':[x+4.2,y,z-2.9],'yaw':0}, {'name':'WashBasin','catalogue_id':'AST-SAN-001','position':[x+1.91,y,z+2.5],'yaw':0},{'name':'Toilet','catalogue_id':'AST-SAN-002','position':[x+3.3,y,z+2.8],'yaw':0},{'name':'Shower','catalogue_id':'AST-SAN-003','position':[x+4.72,y,z+2.35],'yaw':0}]
 bindings.append({'name':'DayReadingChair','catalogue_id':'AST-FUR-002','position':[x+9.15,y,z+1.95],'yaw':math.pi/2})
 if idx==437:bindings[1]['position']=[x+10.5,y,z+2.15];bindings[2]['position']=[x+7.8,y,z+2.7];bindings[-1]['position']=[x+8.85,y,z+2.15]
 desk=bindings[1]['position']
 bindings.extend([{'name':'SupportedOpenFolio','catalogue_id':'AST-LIB-007','position':[desk[0]+.05,y+.752,desk[2]-.10],'yaw':math.pi/2},{'name':'HousedStudyTaskFixture','catalogue_id':'AST-LIB-008','position':[desk[0]+.18,y+.752,desk[2]+.30],'yaw':math.pi/2}])
 doors=[{'name':'EntryDoor','persistent_id':row['proposed_runtime_id']+':entry','position':[x+.12,y,z],'yaw':-math.pi/2,'controller':'guest_entry_door.gd'},{'name':'WashDoor','persistent_id':row['proposed_runtime_id']+':wash','position':[x+3.2,y,z+.86],'yaw':0,'controller':'guest_privacy_door.gd'}]
 lights=[]
 for k,(u,v)in enumerate([(2.2,-1.6),(8.7,.25)]):
  c(f'LightHousing_{k}',u-.28,u+.28,3.42,3.55,v-.14,v+.14,'champagne_metal','fixture');c(f'LightDiffuser_{k}',u-.22,u+.22,3.40,3.42,v-.10,v+.10,'opal_glow','fixture',False);lights.append({'name':f'SA{idx}_PhysicalCeilingLight_{k}','position':[x+u,y+3.385,z+v],'range':7,'energy':1.1})
 # Four specialty doubles across both sides of the real shared street.
 aquatic=rest_id=='AST-RST-AQ-001';outer=row['allocation_x'][1]==-86.05;assert outer and row['proposed_rest_place_count']==(2 if idx in [569,575]else 1)
 bindings=[b for b in bindings if b['name']!='ReservedRestSupport']
 desk_at={497:(4.6,-1.85),503:(8.9,-1.85),569:(4.6,-1.85),575:(4.8,-1.95)}[idx];chair_at={497:(1.1,-2.55,-math.pi/2),503:(7.15,-1.85,math.pi/2),569:(2.9,-1.85,math.pi/2),575:(1.1,-2.55,-math.pi/2)}[idx]
 for b in bindings:
  if b['name']=='LibraryStudyEdge':b['position']=[x+desk_at[0],y,z+desk_at[1]]
  if b['name']=='DayReadingChair':b['position']=[x+chair_at[0],y,z+chair_at[1]];b['yaw']=chair_at[2]
  if b['name']=='PersonalConsole':b['position']=[x+1.1,y,z+2.6]
 desk=next(b['position']for b in bindings if b['name']=='LibraryStudyEdge')
 for b in bindings:
  if b['name']=='SupportedOpenFolio':b['position']=[desk[0]+.05,y+.752,desk[2]-.10]
  if b['name']=='HousedStudyTaskFixture':b['position']=[desk[0]+.18,y+.752,desk[2]+.30]
 # The west bank has no established hull/court opening. Its real street-facing pane is retained in a screened activity bay.
 parts[:]=[q for q in parts if q['name']not in [f'SA{idx}_OvalWindowReveal',f'SA{idx}_OvalAtriumGlass',f'SA{idx}_OvalDepthReturn',f'SA{idx}_EntryShoulderNorth',f'SA{idx}_EntryPrivacyDogleg']]
 c('OpaqueRearBoundary',12.74,12.9,0,3.74,-3.48,3.48)
 c('StreetWindowLower',0,.12,0,1.25,-3.48,-1.74);c('StreetWindowUpper',0,.12,2.70,3.74,-3.48,-1.74)
 c('StreetWindowOuterPier',0,.12,1.25,2.70,-3.48,-3.25);c('StreetWindowInnerMullion',0,.12,1.25,2.70,-1.95,-1.74)
 c('ScreenedStreetGlass',.065,.085,1.25,2.70,-3.25,-1.95,'hospitality_glass','window');c('StreetReadingSill',.12,.32,1.18,1.25,-3.25,-1.95,'warm_walnut','joinery')
 c('EntryPrivacyDogleg',2.1,2.23,0,2.2,-3.48,-1.95,'warm_walnut','privacy')
 if aquatic:
  bindings.append({'name':'StudyChair','catalogue_id':'AST-FUR-002','position':[x+(2.9 if idx==497 else 3.1),y,z+desk_at[1]],'yaw':math.pi/2})
  if idx==497:
   c('NegativeWetPrivacyBlade',6.35,6.47,0,1.65,-3.48,-.1,'teal_weave','privacy');c('PositiveDryTransferBench',8.1,10.0,0,.40,2.2,2.85,'warm_walnut','dry_transfer');c('PositiveDryTransferPad',8.1,10.0,.40,.44,2.2,2.85,'teal_weave','dry_transfer')
  else:
   c('PositiveWetPrivacyBlade',5.75,5.87,0,1.65,.2,3.48,'teal_weave','privacy');c('NegativeDryTransferBench',8.2,9.5,0,.40,-2.9,-2.3,'warm_walnut','dry_transfer');c('NegativeDryTransferPad',8.2,9.5,.40,.44,-2.9,-2.3,'teal_weave','dry_transfer');c('ArrivalFolioUpperReturn',2.8,4.6,2.3,2.38,-3.48,-2.95,'warm_walnut','joinery')
   for q in parts[start:]:
    if 'Belongings'in q['name']:
     for v in q['verts']:v[0]+=4.4
 else:
  bindings.append({'name':'StreetReadingChair','catalogue_id':'AST-FUR-002','position':[x+1.1,y,z-2.55],'yaw':-math.pi/2})
  c('ArrivalBelongingsBench',2.1,4.6,0,.40,-3.40,-2.80,'warm_walnut','joinery');c('ArrivalBelongingsPad',2.1,4.6,.40,.44,-3.40,-2.80,'teal_weave','joinery')
  if idx==503:c('ArrivalUpperFolioShelf',2.8,5.0,2.3,2.38,-3.48,-2.95,'warm_walnut','joinery')
  else:c('PositiveQuietGalleryShelf',10.4,12.3,2.6,2.68,2.95,3.45,'warm_walnut','joinery')
 if idx==575:
  # Two retained basins need separate front transfer positions and a central service aisle.
  parts[start:]=[q for q in parts[start:]if not any(t in q['name']for t in ['PositiveWetPrivacyBlade','NegativeDryTransferBench','NegativeDryTransferPad'])]
  c('NegativeWetPrivacyBlade',5.75,5.87,0,1.65,-3.48,-.7,'teal_weave','privacy');c('PositiveWetPrivacyBlade',6.4,6.52,0,1.65,.7,3.48,'teal_weave','privacy')
  for q in parts[start:]:
   if 'Belongings'in q['name']:
    for v in q['verts']:v[0]-=4.4
 if idx==569:
  c('ParallelArrivalDisplay',5.8,6.8,.65,.73,-3.40,-2.85,'ivory_enamel','joinery')
 refs=json.load(open(R/'Game/data/architecture/STAR_ATLAS_EIGHT_HABITATS.json'))['references'];ref=next(r for r in refs if r['key']==rest_id);rest_fittings=[]
 placements={497:[(8.95,-1.0,-math.pi/2)],503:[(9.25,1.3,math.pi/2)],569:[(8.7,-1.65,math.pi/2),(8.7,1.65,math.pi/2)],575:[(8.2,-1.9,-math.pi/2),(9.7,1.9,math.pi/2)]}[idx]
 for slot,(ru,rv,yaw)in zip(row['proposed_rest_slot_ids'],placements):
  n=len(rest_fittings)+1;at=[x+ru,y,z+rv];binding={'name':f'ReservedRestSupport_{n:02d}','catalogue_id':rest_id,'position':at,'yaw':yaw,'rest_slot_id':slot};bindings.append(binding)
  def world(v):return [at[0]+v[0]*math.cos(yaw)+v[2]*math.sin(yaw),at[1]+v[1],at[2]-v[0]*math.sin(yaw)+v[2]*math.cos(yaw)]
  fit={'rest_slot_id':slot,'binding':binding,'approach_world':world([0,0,-2.7 if aquatic else-2.4]),'actual_reference_bottom_contacts_world':[world(v)for v in ref['contact_probes']],'frame_origin':at,'yaw':yaw}
  if aquatic:
   fit['service_stance_world']=world([2.05,0,-.47]);fit['actual_reference_immersed_vertices_world']=[]
   # Original measured reference native mesh top pole vertices, not invented body dimensions.
   author_ref=json.load(open(R/'BlenderCatalogue/assets/star_atlas_eight_habitat_20261010/PHYSICAL_PLAN.json'))['references'];author_ref=next(a for a in author_ref if a['key']==rest_id)
   fit['actual_reference_immersed_vertices_world']=[world(b['verts'][0])for b in author_ref['parts']if 'Head'not in b['name']]
   fit['environment_role']='source-contained non-solid wet detector and actual basin/rest geometry; water/cleaning/chemistry/temperature operations held'
  else:
   for stem,lo,hi,role in [('LeftLiner',[-1.28,0,-1.74],[-1.22,2.44,1.62],'teal_weave'),('RightLiner',[1.22,0,-1.74],[1.28,2.44,1.62],'teal_weave'),('RearLiner',[-1.22,0,1.56],[1.22,2.44,1.62],'teal_weave'),('Roof',[-1.28,2.44,-1.74],[1.28,2.50,1.62],'ivory_enamel'),('FrontLeftJamb',[-1.22,0,-1.74],[-.59,2.44,-1.68],'warm_walnut'),('FrontRightJamb',[.59,0,-1.74],[1.22,2.44,-1.68],'warm_walnut'),('DoorHeader',[-.59,2.23,-1.74],[.59,2.44,-1.68],'warm_walnut')]:
    cube(f'SA{idx}_Cocoon{n:02d}_'+stem,lo,hi,role,'cocoon_privacy');parts[-1]['verts']=[world(v)for v in parts[-1]['verts']]
   door={'name':f'CocoonPrivacyDoor_{n:02d}','persistent_id':slot+':privacy','position':world([0,0,-1.71]),'yaw':yaw,'controller':'cocoon_privacy_door.gd'};doors.append(door);fit['privacy_door_name']=door['name'];fit['environment_role']='closeable physical quiet-cocoon enclosure; acoustic/molting/biological operations held'
  rest_fittings.append(fit)
 # Rotate the exterior-bank interior180degrees so its entry actually faces the shared street.
 # Source-fitted roof posts below remain in their exact world coordinates.
 if outer:
  cx=sum(row['allocation_x'])/2
  def turn(v):return [2*cx-v[0],v[1],2*z-v[2]]
  for q in parts[start:]:q['verts']=[turn(v)for v in q['verts']]
  for b in bindings+doors:b['position']=turn(b['position']);b['yaw']+=math.pi
  for light in lights:light['position']=turn(light['position'])
  for f in rest_fittings:
   f['frame_origin']=turn(f['frame_origin']);f['yaw']+=math.pi
   for key in ['approach_world','service_stance_world']:
    if key in f:f[key]=turn(f[key])
   for key in ['actual_reference_bottom_contacts_world','actual_reference_immersed_vertices_world']:
    if key in f:f[key]=[turn(v)for v in f[key]]
 # Geometric receiving feet on exact retained D14 roof; capacity remains held.
 for wanted_u in [6.15,11.55]:
  for wanted_v in [-2.6,2.6]:
   choices=[]
   for du in [0,.05,-.05,.1,-.1,.15,-.15,.2,-.2,.3,-.3,.4,-.4,.5,-.5]:
    u=wanted_u+du;v=wanted_v;toe=box(x+u-.1,z+v-.1,x+u+.1,z+v+.1)
    for face,polygon,name in roof:
     if polygon.covers(toe):
      a,b,cc=face;normal=np.cross(b-a,cc-a)
      def height(xx,zz):return float(a[1]-(normal[0]*(xx-a[0])+normal[2]*(zz-a[2]))/normal[1])
      # A contained triangle can be a ceiling underside. Require the exposed
      # uppermost source surface at every toe corner before considering it.
      exposed=True
      for xx,zz in [(x+u+dx,z+v+dz)for dx in [-.1,0,.1]for dz in [-.1,0,.1]]:
       candidate_y=height(xx,zz)
       for other,other_poly,other_name in roof:
        if other_poly.buffer(1e-7).covers(Point(xx,zz)):
         aa,bb,ccc=other;nn=np.cross(bb-aa,ccc-aa)
         if abs(nn[1])>1e-10:
          other_y=float(aa[1]-(nn[0]*(xx-aa[0])+nn[2]*(zz-aa[2]))/nn[1])
          if other_y>candidate_y+1e-5:exposed=False
      if exposed:choices.append((height(x+u,z+v),u,v,face.tolist(),name))
   assert choices,(idx,wanted_u,wanted_v)
   center_height,u,v,face,name=max(choices,key=lambda q:q[0]);a,b,cc=np.array(face);normal=np.cross(b-a,cc-a)
   def height(xx,zz):return float(a[1]-(normal[0]*(xx-a[0])+normal[2]*(zz-a[2]))/normal[1])
   lo=[x+u-.1,center_height,z+v-.1];hi=[x+u+.1,92.6,z+v+.1];cube(f'SA{idx}_FittedRoofPost_{u}_{v}',lo,hi,'champagne_metal','receiving');part=parts[-1]
   for vertex in part['verts']:
    if vertex[1]==center_height:vertex[1]=height(vertex[0],vertex[2])
   receiving.append({'position':[x+u,center_height,z+v],'bottom_contact_vertices':[q for q in part['verts']if q[1]<92.59],'source_roof_triangle':face,'source_roof_mesh':name,'source_roof_file':proto['model_file'],'source_below_identity':below['rebuild_identity'],'full_toe_area_m2':.04,'basis':'Exact sloped source roof contact; cantilevered receiving design and roof load capacity unaccepted'})
 for v in [-2.6,2.6]:c(f'ReceivingBeam_{v}',0,12.78,-.4,-.24,v-.1,v+.1,'champagne_metal','receiving')
 ownparts=parts[start:];parts=parts[:start]
 rooms.append({'allocation':row,'profile_proposal':profile,'species_assignment':None,'proposed_design_species':('Baelins'if aquatic else'Mantelids'),'orientation_yaw':(math.pi if outer else 0),'window_view':('actual shared receiving street, screened activity bay; no hull/court claim'if outer else'actual atrium-facing inner bank'),'species_ready':False,'rest_fittings':rest_fittings,'parts':ownparts,'components':bindings,'doors':doors,'lights':lights,'receiving_contacts':receiving,'below_unit':below,'model_file':f'StarAtlasSpecialty_{idx}.glb','runtime_collision_policy':'Respect retained component NO_SOLID_COLLISION water/ripple policies; exact concave surfaces for basin','operations_hold':['body/rest animation and habitat compatibility','water/thermal/chemistry/rinse/cleaner operation','quiet/acoustic/molting and occupancy/privacy permission routines','stock/save and primary load capacity']})
P={'schema':'astraea.star_atlas_specialty_eighth.v1','base_commit':'f9332c0b27060afa893835c48031c2b34038df10','root_name':'StarAtlasSpecialtyEighthCandidates','sources':sources,'preimage_pins':pins,'rooms':rooms,'selected_source_indices':[569,575],'retained_specialty_reservations':46,'physical_interior_batch':2,'new_units':0,'rest_reservations':4,'source_ids_unchanged':True,'limits':['16 specialty interiors remain unbuilt','One proposed Baelin and one Mantelid design target; four existing rests; no canonical body/rig/animation or biological gameplay acceptance','Lower roof receiving is geometric contact only, no primary structural or roof load certification','New D15 street/commons joins must be source-supported and bounded-tested before adoption']}
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');P['aquatic_wet_cells_local']=json.load(open(R/'Game/data/architecture/STAR_ATLAS_EIGHT_HABITATS.json'))['rooms'][1]['wet_cells_local'];P['aquatic_wet_source_sha256']=sha(R/'Game/assets/models/AST-RST-AQ-001.glb');P['aquatic_wet_volume_m3']=.890574106542032
(W/'PLAN.json').write_text(json.dumps(P,indent=2)+'\n');print('Prepared final two retained D15 specialty doubles with four rests')
