from pathlib import Path
import json,math,hashlib,numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union,triangulate
from shapely.strtree import STRtree
W=Path(__file__).resolve().parent;R=W.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ns={'__file__':str(W/'reader.py')};exec((R/'BlenderCatalogue/assets/tidal_d15_service_receiving_20261010/source_geometry.py').read_text(),ns)
P=json.load(open(W/'ALLOCATION_PROPOSAL.json'));parts=[]
def cube(name,lo,hi,role='ivory_enamel',collision=True):
 vs=[[x,y,z]for z in [lo[2],hi[2]]for y in [lo[1],hi[1]]for x in [lo[0],hi[0]]];faces=[[0,2,3,1],[4,5,7,6],[0,1,5,4],[2,6,7,3],[0,4,6,2],[1,3,7,5]];return {'name':name,'verts':vs,'faces':faces,'material':role,'runtime_collision':collision}
def at(v,rest):
 x,y,z=v;cy,sy=math.cos(rest['yaw']),math.sin(rest['yaw']);p=rest['position'];return [p[0]+x*cy+z*sy,p[1]+y,p[2]-x*sy+z*cy]
meshes={k:list(ns['triangles'](k+'.glb'))for k in ['AST-RST-QC-001','AST-RST-AQ-001','AST-RST-LN-001']}
support_names={'AST-RST-QC-001':'Concave stretched rest membrane','AST-RST-AQ-001':'Contoured broad immersed rest support','AST-RST-LN-001':'NestContouredSupport'}
def top(tris,x,z):
 ans=[]
 for t in tris:
  a=t[0];v1=t[1]-a;v2=t[2]-a;det=v1[0]*v2[2]-v1[2]*v2[0]
  if abs(det)<1e-9:continue
  b1=((x-a[0])*v2[2]-(z-a[2])*v2[0])/det;b2=(v1[0]*(z-a[2])-v1[2]*(x-a[0]))/det
  if b1>=-1e-6 and b2>=-1e-6 and b1+b2<=1.000001:ans.append(a[1]+b1*v1[1]+b2*v2[1])
 assert ans,(x,z);return max(ans)
support={k:np.concatenate([t for n,t in v if n==support_names[k]])for k,v in meshes.items()}
# Wet detector cells are conservative source-derived volumes, never solid water.
water=unary_union([Polygon(t[:,[0,2]])for n,ts in meshes['AST-RST-AQ-001']if n=='WaterSurface_VisualOnly'for t in ts]);assert water.is_valid
solidtris=[];polys=[]
for name,ts in meshes['AST-RST-AQ-001']:
 if 'Water' in name or 'ripple' in name.lower():continue
 for t in ts:
  po=Polygon(t[:,[0,2]])
  if po.area>1e-10:solidtris.append(t);polys.append(po)
tree=STRtree(polys);cells=[];grid=.28
for x in np.arange(-1.26,1.27,grid):
 for z in np.arange(-1.68,1.69,grid):
  clipped=water.intersection(box(x,z,x+grid,z+grid))
  for triangle in triangulate(clipped):
   if not clipped.covers(triangle)or triangle.area<1e-7:continue
   floor=.16
   for ii in tree.query(triangle):
    overlap=triangle.intersection(polys[int(ii)])
    if overlap.is_empty:continue
    t=solidtris[int(ii)];a=t[0];v1=t[1]-a;v2=t[2]-a;det=v1[0]*v2[2]-v1[2]*v2[0]
    if overlap.geom_type=='Polygon':points=list(overlap.exterior.coords)
    elif hasattr(overlap,'coords'):points=list(overlap.coords)
    else:continue
    for xx,zz in points:
     b1=((xx-a[0])*v2[2]-(zz-a[2])*v2[0])/det;b2=(v1[0]*(zz-a[2])-v1[2]*(xx-a[0]))/det;floor=max(floor,a[1]+b1*v1[1]+b2*v2[1])
   # 2mm dry safety clearance above any source solid inside the entire cell footprint.
   floor+=.002
   if floor>=.568:continue
   xyz=list(triangle.exterior.coords)[:3];vs=[[xx,y,zz]for y in [floor,.57]for xx,zz in xyz];cells.append({'vertices':vs,'faces':[[0,2,1],[3,4,5],[0,1,4,3],[1,2,5,4],[2,0,3,5]],'volume_m3':triangle.area*(.57-floor)})
assert cells and sum(c['volume_m3']for c in cells)>.5
references=[]
for k in meshes:
 species={'AST-RST-QC-001':'Mantelids','AST-RST-AQ-001':'Baelins','AST-RST-LN-001':'Humans'}[k];st=support[k]
 # Dimensioned segmented rest mannequins, never saved NPCs or canonical rigs.
 body=[]
 segments=[('Torso',0,-.03,.27,.48,.23),('Head',0,.65,.22,.23,.22),('LeftFoldedLeg',-.145,-.62,.12,.29,.14),('RightFoldedLeg',.145,-.62,.12,.29,.14),('LeftArm',-.34,.04,.075,.37,.10),('RightArm',.34,.04,.075,.37,.10)]
 if species=='Baelins':segments[0]=('SoftBroadTorso',0,-.03,.32,.5,.24);segments[1]=('RoundedHead',0,.65,.26,.25,.23)
 if species=='Mantelids':segments[0]=('SegmentedThorax',0,-.03,.235,.48,.19);segments[1]=('HeadReference',0,.65,.20,.23,.19)
 for name,cx,cz,rx,rz,height in segments:
  vs=[];faces=[];N=16;M=8
  for j in range(M+1):
   theta=math.pi*j/M
   for i in range(N):
    a=2*math.pi*i/N;xx=cx+rx*math.sin(theta)*math.cos(a);zz=cz+rz*math.sin(theta)*math.sin(a);yy=top(st,xx,zz)+.005+height*(1+math.cos(theta))*.5;vs.append([xx,yy,zz])
  for j in range(M):
   for i in range(N):ii=(i+1)%N;faces.append([j*N+i,j*N+ii,(j+1)*N+ii,(j+1)*N+i])
  body.append({'name':name,'verts':vs,'faces':faces,'material':'teal_weave','runtime_collision':False})
 bounds=np.array([v for b in body for v in b['verts']]);contacts=[b['verts'][-16]for b in body]
 refs={'key':k,'proposed_design_species':species,'model_file':'StarAtlasBodyFit_'+k+'.glb','parts':body,'bounds_min':bounds.min(0).tolist(),'bounds_max':bounds.max(0).tolist(),'measured_dimensions_xyz_m':np.ptp(bounds,axis=0).tolist(),'contact_probes':contacts,'support_top_triangles':st.tolist(),'status':'original measured construction-reference rest mannequin; canonical body, joint rig, animation and biological ranges absent'}
 references.append(refs)
for room in P['rooms']:
 idx=room['source_envelope_index'];rest=room['rest_source'];k=rest['catalogue_id'];room['reference_key']=k;room['rest_contacts_world']=[at(v,rest)for v in next(r for r in references if r['key']==k)['contact_probes']];room['approach_world']=at([0,0,-2.70 if k!='AST-RST-QC-001'else-2.4],rest)
 room['environment_state']='proposed_species_design_target_physical_witnesses_pending';room['species_ready']=False
 if k=='AST-RST-QC-001':
  for name,lo,hi,role in [('LeftLiner',[-1.28,0,-1.74],[-1.22,2.44,1.62],'teal_weave'),('RightLiner',[1.22,0,-1.74],[1.28,2.44,1.62],'teal_weave'),('RearLiner',[-1.22,0,1.56],[1.22,2.44,1.62],'teal_weave'),('Roof',[-1.28,2.44,-1.74],[1.28,2.50,1.62],'ivory_enamel'),('FrontLeftJamb',[-1.22,0,-1.74],[-.59,2.44,-1.68],'warm_walnut'),('FrontRightJamb',[.59,0,-1.74],[1.22,2.44,-1.68],'warm_walnut'),('DoorHeader',[-.59,2.23,-1.74],[.59,2.44,-1.68],'warm_walnut')]:
   q=cube(f'SA{idx}_Cocoon_'+name,lo,hi,role);q['verts']=[at(v,rest)for v in q['verts']];parts.append(q)
  room['privacy_door']={'position':at([0,0,-1.71],rest),'yaw':rest['yaw'],'persistent_id':room['unit_proposal_id']+':cocoon_privacy','controller':'guest_privacy_door.gd','operation':'reuse existing interaction/motion/obstruction controller; no acoustic attenuation implied'}
  room['quiet_zone']={'center':at([0,1.22,-.06],rest),'size':[2.44,2.44,3.24],'yaw':rest['yaw'],'purpose':'physical rest enclosure detection only; no audio attenuation or molting behavior'}
  if idx==437:room['remove_source_meshes']=['SA437_QuietArrivalScreen'];room['approach_world']=at([0,0,-2.4],rest)
 if k=='AST-RST-AQ-001':
  room['wet_cells_local']=cells;room['wet_volume_m3']=sum(c['volume_m3']for c in cells)
  room['wet_probes_world']=[at(b['verts'][0],rest)for b in next(r for r in references if r['key']==k)['parts']if 'Head'not in b['name']]
 if idx==485:room['remove_source_meshes']=['SA485_WetDryLandingBench']
P.update(schema='astraea.eight_habitat_physical_construction.v1',parts=parts,references=references,wet_cell_count=len(cells),wet_volume_m3=sum(c['volume_m3']for c in cells),wet_volume_policy='Nonblocking conservative triangular cells clipped to exact source visual-water footprint, each floor above highest source solid over that footprint; excludes 2mm safety margin and support/rim/bolsters. No fluids/flow/buoyancy/temperature/chemistry.',runtime_model_file='StarAtlasEightHabitatFittings.glb',source_pins={k:sha(R/'Game/assets/models'/(k+'.glb'))for k in meshes},removed_meshes_policy='Only newly superseded437 arrival-screen obstruction and duplicate485 nested bench; original native/GLB exports retained unchanged')
(W/'PHYSICAL_PLAN.json').write_text(json.dumps(P,indent=2)+'\n');print(json.dumps({'rooms':8,'privacy_shell_parts':len(parts),'wet_cells_per_basin':len(cells),'wet_volume_m3_per_basin':P['wet_volume_m3'],'references':[{k:r[k]for k in ['key','proposed_design_species','measured_dimensions_xyz_m']}for r in references]}))
