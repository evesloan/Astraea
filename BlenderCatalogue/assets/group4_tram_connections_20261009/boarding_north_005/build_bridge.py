from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Matrix
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009';S=F/'port_successor_002';IDS0=['AST-TRM-G4-019'];family='group4_boarding_bridge_005';cat=json.loads((R/'BlenderCatalogue/catalogue_manifest.json').read_text())
def scan(v):
 if isinstance(v,dict):
  for x in v.values():
   if isinstance(x,str) and x in IDS0:assert any(a.get('catalogue_id')==x and a.get('family')==family for a in cat['assets']),x+' already owned'
   scan(x)
 elif isinstance(v,list):
  for x in v:scan(x)
scan(cat);assert not (R/'Game/assets/models/AST-TRM-G4-019.glb').exists()
sc=(F/'build_source.py').read_text().split('# Elevated axial 68m study.')[0].replace("OUT=Path(__file__).resolve().parent;R=OUT.parents[2];FAMILY=OUT.name","OUT=W;FAMILY=family").replace("assert FAMILY=='group4_tram_connections_20261009'",'').replace("IDS=['AST-TRM-G4-001','AST-TRM-G4-002','AST-TRM-G4-003','AST-TRM-G4-004','AST-TRM-G4-005','AST-TRM-G4-006']","IDS=IDS0").replace("'FORE_MIDSHIP_STATIC_SOURCE','TRAM_EDITABLE_COMPONENT','AFT_MIDSHIP_STATIC_SOURCE','FORWARD_STATIC_SOURCE','CENTRAL_STATIC_SOURCE','AFT_STATIC_SOURCE','UNEXPORTED_REFERENCE_AND_STUDIO'","'BOARDING_BRIDGE_SOURCE','UNEXPORTED_REFERENCE_AND_STUDIO'").replace("bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)","bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)\nfor c in list(bpy.data.collections):bpy.data.collections.remove(c)")
exec(sc,globals());current=collections['BOARDING_BRIDGE_SOURCE'];root=marker('BRIDGE_FIXED_RECEIVER_ROOT',(0,0,0),'platform-edge origin; local+X faces vehicle, local+Z is portal longitudinal axis');pivot=marker('BRIDGE_MOVING_PANEL',(0,0,0),'root-owned rotating group; local Z+90 degrees folds up; Y-up hinge(0,0,0)');r=1.0925925925925928;half=1.09;mov=[];fixed=[]
def tagged(o,group):
 o['moving_group']=group;o['collision_policy']='root_owned_animatable_convex_candidate' if group=='BRIDGE_MOVING_PANEL' else 'static_receiver_candidate';(mov if group=='BRIDGE_MOVING_PANEL' else fixed).append(o);return o
def bx(n,c,s,m,role,group='BRIDGE_MOVING_PANEL'):return tagged(box(n,c,s,m,role),group)
def tb(n,a,b,rr,m,role,group='BRIDGE_MOVING_PANEL'):return tagged(tube(n,a,b,rr,m,role),group)
# Flat walking deck plus a named receiving tongue. All main deck hardware stays under the surface.
poly=[(0,-half),(r,-half),(r,half),(0,half)];vs=[(x,y,z) for y in [-.04,0] for x,z in poly];tagged(mesh('BRIDGE_MainDeck',vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],stone,'nominal1.0925926m gap span;2.18m clear width'),'BRIDGE_MOVING_PANEL')
# The tongue overlaps the car floor by20mm. Its shallow1.5mm top avoids coplanar visual overlap.
vs=[(x,y,z) for z in [-half,half] for x,y in [(r-.03,-.018),(r+.02,-.018),(r+.02,.0015),(r-.03,0)]];tagged(mesh('BRIDGE_CabinReceivingTongue_20mm',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],metal,'20mm positive cabin-floor bearing proposal, no cabin source cut'),'BRIDGE_MOVING_PANEL')
for j,z in enumerate([-.87,-.52,-.17,.17,.52,.87]):bx('BRIDGE_UnderRib_'+str(j),(r*.49,-.085,z),(r*.76,.11,.065),metal,'underfloor deck rib')
for z in [-.96,.96]:bx('BRIDGE_UnderStringer_'+str(z),(r*.49,-.15,z),(r*.79,.05,.08),metal,'closed underfloor edge stringer')
for z in [-1.065,1.065]:bx('BRIDGE_ProfiledEdge_'+str(z),(r*.5,-.055,z),(r,.05,.05),ivory,'weighted edge below walking surface')
for j,x in enumerate([.18,.36,.54,.72,.90]):bx('BRIDGE_RecessedGrip_'+str(j),(x,.00065,0),(.04,.0013,2.02),rubber,'1.3mm shallow anti-slip source strip')
def d_hinge(name,z0,z1,rad,inner,group):
 start=1.5*math.pi if inner else math.pi;steps=3 if inner else 6
 outer=[(rad*math.cos(start+i*math.pi/6),rad*math.sin(start+i*math.pi/6)) for i in range(steps+1)]
 poly=outer+list(reversed([(inner*math.cos(start+i*math.pi/6),inner*math.sin(start+i*math.pi/6)) for i in range(steps+1)])) if inner else outer
 vs=[(x,y,z) for z in [z0,z1] for x,y in poly];n=len(poly);fs=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)];return tagged(mesh(name,vs,fs,metal,'closed front-quadrant moving collar or flush fixed D-pin; mechanical capacity open'),group)
for j,z in enumerate([-.84,-.28,.28,.84]):d_hinge('BRIDGE_MovingKnuckle_'+str(j),z-.095,z+.095,.045,.030,'BRIDGE_MOVING_PANEL')
d_hinge('BRIDGE_FixedHingePin',-1.04,1.04,.026,0,'BRIDGE_FIXED_RECEIVER_ROOT')
# Four receiving lugs give explicit static platform contacts without raised caster obstructions.
for j,z in enumerate([-.995,-.555,.555,.995]):
 bx('BRIDGE_FixedAnchor_'+str(j),(-.27,-.14,z),(.26,.12,.15),metal,'fixed platform underside positive-volume receiver','BRIDGE_FIXED_RECEIVER_ROOT')
 bx('BRIDGE_FixedLugWeb_'+str(j),(-.075,-.085,z),(.15,.11,.085),metal,'anchor-to-pin solid receiver web','BRIDGE_FIXED_RECEIVER_ROOT')
 bx('BRIDGE_FixedLugCap_'+str(j),(-.01,-.0525,z),(.05,.065,.14),ivory,'fixed bearing cap below standing surface','BRIDGE_FIXED_RECEIVER_ROOT')
 for dx in [-.08,.08]:tb('BRIDGE_ReceiverFastener_'+str((j,dx)),(-.27+dx,-.195,z),(-.27+dx,-.083,z),.012,metal,'small recessed receiving fastener','BRIDGE_FIXED_RECEIVER_ROOT')
for z in [-.68,.68]:bx('BRIDGE_HingeDriveHousing_'+str(z),(-.285,-.25,z),(.31,.18,.20),ivory,'root-owned hinge-drive physical housing; no powered operation supplied','BRIDGE_FIXED_RECEIVER_ROOT')
# Reparent without changing authored component-space vertices. Explicit group pivots survive export.
for group,obs in [(pivot,mov),(root,fixed)]:
 for o in obs:
  mat=o.matrix_world.copy();o.parent=group;o.matrix_world=mat
marker('DATUM_VEHICLE_RECEIVING_EDGE',(r,0,0),'actual car floor edge; tongue+20mm is the separate bearing overlap')
marker('DATUM_ROOT_INTERLOCK_BINDING',(-.27,-.14,0),'reuse root existing lift_gate/controller semantics; no parallel controller supplied')
for j,z in enumerate([-.995,-.555,.555,.995]):marker('DATUM_PLATFORM_RECEIVER_'+str(j),(-.27,-.14,z),'four fixed anchors must overlap actual station slab')
file='AST-TRM-G4-019_boarding_bridge.glb';bpy.ops.object.select_all(action='DESELECT')
for o in current.objects:o.select_set(True)
bpy.context.view_layer.objects.active=mov[0];bpy.ops.export_scene.gltf(filepath=str(W/file),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
rows=[]
for o in parts:
 ps=[G(o.matrix_world@v.co) for v in o.data.vertices];rows.append({'mesh':o.name,'group':o['moving_group'],'role':o['role'],'collision_policy':o['collision_policy'],'min':[min(p[i] for p in ps) for i in range(3)],'max':[max(p[i] for p in ps) for i in range(3)]})
(W/'BRIDGE_MESH_PARTS.json').write_text(json.dumps(rows,indent=2)+'\n');i=json.loads((S/'SUCCESSOR_INTERFACE.json').read_text());placements=[]
for q in i['stations']:
 placements.append({'station':q['label'],'station_asset':q['asset'],'origin_xyz':[q['boarding_edge_x'],56.1,q['catchment_z']],'yaw_rad':0 if q['vehicle_door_side']=='port' else math.pi,'car_origin_xyz':[q['track_x'],56.1,q['catchment_z']],'source_fit_gate':'HELD_FOREMID_PAPERMOON' if q['label']=='FORE_MIDSHIP' else 'CHECK_PENDING','protected_catchment_z':q['catchment_z']})
pins={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in ['BlenderCatalogue/catalogue_manifest.json','BlenderCatalogue/assets/group4_tram_connections_20261009/build_source.py','BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002/SUCCESSOR_INTERFACE.json','Game/scripts/lift_gate.gd','Game/scripts/commons_lift.gd','Game/data/generated/received_structural_meshes.json','Game/data/generated/structural_meshes.json']}
for q in i['stations']:p='BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002/'+q['asset'];pins[p]=hashlib.sha256((R/p).read_bytes()).hexdigest()
p='BlenderCatalogue/assets/group4_tram_connections_20261009/port_successor_002/AST-TRM-G4-011_cart_tram_component.glb';pins[p]=hashlib.sha256((R/p).read_bytes()).hexdigest()
meta={'schema':'astraea.group4.boarding_bridge.source.v1','source_only':True,'whole_group_complete':False,'catalogue_id':'AST-TRM-G4-019','family':family,'asset':file,'native':'Group4_Boarding_Bridge_005.blend','component_origin':'Platform edge at boarding-floor top; local+X faces vehicle, local+Z runs along portal. Y-up metres.','nominal_gap_span_m':r,'clear_width_m':2.18,'receiving_tongue_overlap_m':.02,'tongue_top_step_m':.0015,'full_deployed_reach_m':r+.02,'hinge_pivot_xyz':[0,0,0],'moving_group':'BRIDGE_MOVING_PANEL','fixed_group':'BRIDGE_FIXED_RECEIVER_ROOT','proposed_game_stow_rotation':'local Z+90 degrees about the explicit hinge pivot, no driver supplied','member_count':len(parts),'moving_members':len(mov),'fixed_members':len(fixed),'placements':placements,'retained_source_pins':pins,'source_material_pins':texture_pins,'operating_gate':'Root binds existing interaction, pause, docking/gates/interlock and AnimatableBody3D physics. No new controller, cabin, gates, stock or tram movement supplied. Bridge deployment/stow must only happen under root interlock; physical load/carry and repeated traversal remain open.','foremid_gate':'Original fore-midship source intersects retained Paper Moon; do not install its original bridge placement. Separate north successor study may propose bindings, but current runtime stays unchanged.','limits':['Source-only three-pose stationary fit checks, not dynamic traversal.','Hinge/drive geometry does not establish load capacity or mechanical operation.','Runtime floor collision and existing controllers remain root-owned integration.']}
(W/'BRIDGE_INTERFACE.json').write_text(json.dumps(meta,indent=2)+'\n')
for im in bpy.data.images:
 if im.source=='FILE' and im.size[0]>0:im.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(W/meta['native']),compress=True);print('BRIDGE_SOURCE_EXPORTED',len(parts),'editable members')
