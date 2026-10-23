from pathlib import Path
import bpy,math,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;R=Path('/workspace/shared/Astraea_direct_recovery_20261008_hcozu5z4');F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009';S=F/'port_successor_002';P=json.loads((W/'RECEIVING_PLAN.json').read_text());frozen=json.loads((S/'FROZEN_SUCCESSOR_BATCH.json').read_text());assert all(hashlib.sha256((S/n).read_bytes()).hexdigest()==a['sha256'] for n,a in frozen['files'].items())
sc=(F/'build_source.py').read_text().split('# Elevated axial 68m study.')[0]
sc=sc.replace("OUT=Path(__file__).resolve().parent;R=OUT.parents[2];FAMILY=OUT.name","OUT=W;FAMILY='group4_tram_receiving_module_003'").replace("assert FAMILY=='group4_tram_connections_20261009'",'').replace("IDS=['AST-TRM-G4-001','AST-TRM-G4-002','AST-TRM-G4-003','AST-TRM-G4-004','AST-TRM-G4-005','AST-TRM-G4-006']","IDS=['AST-TRM-G4-017']")
sc=sc.replace("'FORE_MIDSHIP_STATIC_SOURCE','TRAM_EDITABLE_COMPONENT','AFT_MIDSHIP_STATIC_SOURCE','FORWARD_STATIC_SOURCE','CENTRAL_STATIC_SOURCE','AFT_STATIC_SOURCE','UNEXPORTED_REFERENCE_AND_STUDIO'","'RECEIVING_MODULE_SOURCE','UNEXPORTED_REFERENCE_AND_STUDIO'")
sc=sc.replace("bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)","bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)\nfor cc in list(bpy.data.collections):bpy.data.collections.remove(cc)")
exec(sc,globals());current=collections['RECEIVING_MODULE_SOURCE'];receiver_bindings=[];joints=[]
def beam(name,a,b,w,h,role):
 a=Vector(a);b=Vector(b);v=(b-a).normalized();n=Vector((v.z,0,-v.x));vs=[]
 for p in [a,b]:
  for yy,xx in [(-h/2,-w/2),(-h/2,w/2),(h/2,-w/2),(h/2,w/2)]:vs.append(tuple(p+n*xx+Vector((0,yy,0))))
 return mesh(name,vs,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],metal,role)
# Four core-end point labels replaced only by new positive-area receiving members.
for i,e in enumerate(P['core_end_resolutions']):
 x,y,z=e['new_receiver_center'];pr='M003_CoreEnd_'+str(i)
 box(pr+'_Bearing',(x,60.79,z),(.24,.08,.36),metal,'positive-area contact to named retained D10 slab')
 tube(pr+'_Drop',(x,55.72,z),(x,60.78,z),.04,metal,'roof receiving drop outside tram and lower axis')
 box(pr+'_RailShoe',(-4.015,55.695,z),(.38,.19,.40),metal,'positive existing rail-web and drop overlap')
 marker(pr+'_EXACT_RECEIVER',(x,60.76,z),e['contacts'][0]['owner']+'; full0.0864m² source footprint')
 receiver_bindings.append({'member':pr+'_Bearing','xyz':[x,60.76,z],'owner':e['contacts'][0]['owner'],'positive_footprint_xz':e['positive_footprint_xz'],'area_m2':.0864,'replaces_held_identity_only':e['old_ambiguous_point']})
 joints.append({'left':pr+'_Drop','right':pr+'_RailShoe','type':'positive-volume overlap','receiving_asset':'AST-TRM-G4-016_continuous_guideway.glb','receiving_mesh':'V2_Continuous_Web','web_overlap_x':[-4.205,-4],'web_overlap_y':[55.60,55.68]})
# High headers sit above the retained running clearance top60.1, not above a shrunken envelope.
for i,s in enumerate(P['central_tie_header_sites']):
 pr='M003_Site_'+str(i);a,b=[r['center_xz'] for r in s['leg_receivers']]
 beam(pr+'_Header',(a[0],60.34,a[1]),(b[0],60.34,b[1]),.18,.32,'crossheader above reserved60.1 running clearance')
 for j,r in enumerate(s['leg_receivers']):
  x,z=r['center_xz'];q=s['center_xz'];v=Vector((x-q[0],0,z-q[1])).normalized()
  box(pr+'_Bearing_'+str(j),(x,60.79,z),(.24,.08,.36),metal,'full positive-area contact to named retained slab')
  tube(pr+'_Drop_'+str(j),(x,55.72,z),(x,60.78,z),.04,metal,'receiver drop outside vehicle sweep')
  a0=Vector((q[0],55.695,q[1]))+v*1.48;b0=Vector((q[0],55.695,q[1]))+v*1.82
  beam(pr+'_RailShoe_'+str(j),a0,b0,.38,.19,'positive underweb/drop contact, no wheel-channel fill')
  marker(pr+'_EXACT_RECEIVER_'+str(j),(x,60.76,z),r['contacts'][0]['owner']+'; full0.0864m² source footprint')
  receiver_bindings.append({'member':pr+'_Bearing_'+str(j),'xyz':[x,60.76,z],'owner':r['contacts'][0]['owner'],'footprint_xz':[x-.12,z-.18,x+.12,z+.18],'area_m2':.0864})
  joints.append({'left':pr+'_RailShoe_'+str(j),'right':pr+'_Drop_'+str(j),'type':'positive-volume overlap','receiving_asset':'AST-TRM-G4-016_continuous_guideway.glb','receiving_mesh':'V2_Continuous_Web'})
# Close all previously declared core-hanger/web gaps with small side shoes. No duplicate hanger exports.
old=json.loads((S/'MESH_PARTS.json').read_text());clips=0
for r in old:
 if not r['mesh'].startswith('V2_Core_RailHanger_'):continue
 x=(r['min'][0]+r['max'][0])/2;z=(r['min'][2]+r['max'][2])/2;c=-7.27 if x< -5.6 else -4.015
 name='M003_ExistingCoreHangerShoe_'+str(clips);box(name,(c,55.695,z),(.38,.19,.4),metal,'additive shoe closes frozen hanger-to-web0.07m gap')
 joints.append({'left':name,'right':r['mesh'],'receiving_asset':'AST-TRM-G4-016_continuous_guideway.glb','type':'positive-volume receiving contact'});clips+=1
# Station-carrier roof drops use a slightly higher shoe to meet their existing55.85m endpoints.
station_clips=0
for r in old:
 if '__GuidewayRoof_' not in r['mesh'] or not r['mesh'].endswith('_Hanger'):continue
 x=(r['min'][0]+r['max'][0])/2;z=(r['min'][2]+r['max'][2])/2
 name='M003_StationRailHangerShoe_'+str(station_clips);box(name,(x,55.745,z),(.38,.29,.4),metal,'additive frozen station guideway-roof drop/web receiving shoe')
 joints.append({'left':name,'right':r['mesh'],'type':'positive-volume contact','receiving_asset':'AST-TRM-G4-013_forward_source.glb' if 'FORWARD' in r['mesh'] else 'AST-TRM-G4-015_aft_source.glb'});station_clips+=1
# Longitudinal underweb transfers around all four corners, below actual wheels and preserving3.05m soffit.
route=json.loads((S/'SUCCESSOR_INTERFACE.json').read_text())['guideway']['route_points_xz'];pts=[p for p in route if -85.3-1e-6<=p[1]<=92+1e-6]
# Long axis and curved sections share exactly the frozen route vertices; do not alter rail or reservation.
def ribbon(offset):
 vs=[]
 for i,p in enumerate(pts):
  a=pts[max(0,i-1)];b=pts[min(len(pts)-1,i+1)];v=Vector((b[0]-a[0],0,b[1]-a[1])).normalized();n=Vector((v.z,0,-v.x))
  for y,w in [(55.55,offset-.10),(55.55,offset+.10),(55.71,offset-.10),(55.71,offset+.10)]:vs.append((p[0]+n.x*w,y,p[1]+n.z*w))
 fs=[(0,2,3,1)]
 for i in range(len(pts)-1):
  a=4*i;b=a+4;fs += [(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),(a,b,b+2,a+2),(a+1,a+3,b+3,b+1)]
 a=4*(len(pts)-1);fs.append((a,a+1,a+3,a+2));mesh('M003_UnderwebGirder_'+str(offset),vs,fs,metal,'continuous positive rail-web receiving transfer, capacity unaccepted')
for o in [-1.25,1.25]:ribbon(o)
# Last two south-tie sections have no outside-axis D10 slab. Use existing D09 feet and cantilever trusses.
for i,(z,track) in enumerate([(84,-3.665247584249852),(92,-5.6)]):
 pr='M003_SouthFoot_'+str(i)
 for x in [-2.4,2.4]:
  box(pr+'_Pad_'+str(x),(x,52.54,z),(.42,.08,.75),metal,'positive named D09 axial slab contact')
  box(pr+'_Pier_'+str(x),(x,54.12,z),(.30,3.08,.4),ivory,'receiver pier outside lower4m main axis')
  receiver_bindings.append({'member':pr+'_Pad_'+str(x),'xyz':[x,52.5,z],'owner':'D09_aft_route','footprint_xz':[x-.21,z-.375,x+.21,z+.375],'area_m2':.315})
 left=track-1.8;right=2.8
 box(pr+'_Beam',((left+right)/2,55.63,z),(right-left,.16,.55),metal,'south-tie cantilever beam to exact existing axial feet')
 tube(pr+'_Diagonal',(-2.4,54.1,z),(left+.2,55.60,z),.10,metal,'visible receiving truss outside lower axis')
 box(pr+'_RailSeat',(track,55.675,z),(3.5,.10,.55),metal,'positive cantilever/web transfer, top55.725 below wheel minimum55.74')
# Source exports are additive members only. No frozen rail/station mesh, slab fill/cut or operating controller.
bpy.ops.object.select_all(action='DESELECT')
for ob in current.objects:ob.select_set(True)
bpy.context.view_layer.objects.active=next(iter(current.objects))
file='AST-TRM-G4-017_receiving_module.glb';bpy.ops.export_scene.gltf(filepath=str(W/file),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
rows=[]
for ob in parts:
 ps=[G(ob.matrix_world@v.co) for v in ob.data.vertices];rows.append({'mesh':ob.name,'role':ob['role'],'policy':ob['collision_policy'],'min':[min(p[i] for p in ps) for i in range(3)],'max':[max(p[i] for p in ps) for i in range(3)],'faces':len(ob.data.polygons)})
(W/'MESH_PARTS.json').write_text(json.dumps(rows,indent=2)+'\n')
meta={'schema':'astraea.group4.additive_receiving_source.v1','source_only':True,'whole_group_complete':False,'family':FAMILY,'catalogue_id':'AST-TRM-G4-017','asset':file,'frozen_successor_receipt_sha256':P['frozen_successor_receipt_sha256'],'compiled_floor_sha256':P['slab_sha256'],'receiver_bindings':receiver_bindings,'joints':joints,'existing_hanger_gap_shoes':clips,'station_guideway_gap_shoes':station_clips,'resolved_core_end_interfaces':P['core_end_resolutions'],'floor_recesses':'All five successor002 proposals remain root-owned and uncut. Central17.6m² ownerD09_atrium_circulation; outer-port foremid pit belongs to new receiving annex. No floor is exported or changed.','operating_bindings':'Reuse frozen station commons_lift/AST-CIR-003 interfaces. Root supplies operating tram, doors/gates/bridge/bogies/clamps through existing E/RMB interactions; no parallel controller.','structure_status':'geometric positive receiving construction only; primary hull, load paths beyond named slab, capacity/deflection/vibration not accepted','central_boundary':'exact protected source polyline and4m strip unchanged; Group7 X43..46.5/Z−25..−19/floor reservations preserved','remaining':['root geometric integration and actual-main receiving/import review','lower annex/foundation/fill/pits and central secondary stair receivers','primary structural capacity/hull/load path','all operating transport and remaining destination links','normal boarding, species and final in-engine/CRT/GPU review'],'retained_material_pins':texture_pins}
(W/'MODULE_INTERFACE.json').write_text(json.dumps(meta,indent=2)+'\n')
for im in bpy.data.images:
 if im.source=='FILE' and im.size[0]>0:im.pack()
bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(W/'Group4_Receiving_Module_003.blend'),compress=True)
print('RECEIVING_SOURCE_EXPORTED',len(parts),'members',len(receiver_bindings),'positive receivers',clips,'existing hanger shoes')
