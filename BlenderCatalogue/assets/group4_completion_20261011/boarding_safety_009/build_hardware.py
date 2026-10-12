from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Matrix
W=Path(__file__).resolve().parent;R=W.parents[3]
F=R/'BlenderCatalogue/assets/group4_tram_connections_20261009'
P=json.loads((W/'SAFETY_PLAN.json').read_text());family='group4_boarding_safety_009'
sc=(F/'build_source.py').read_text().split('# Elevated axial 68m study.')[0]
sc=sc.replace("OUT=Path(__file__).resolve().parent;R=OUT.parents[2];FAMILY=OUT.name",'OUT=W;FAMILY=family')
sc=sc.replace("assert FAMILY=='group4_tram_connections_20261009'",'')
sc=sc.replace("IDS=['AST-TRM-G4-001','AST-TRM-G4-002','AST-TRM-G4-003','AST-TRM-G4-004','AST-TRM-G4-005','AST-TRM-G4-006']","IDS=['AST-TRM-G4-025','AST-TRM-G4-026']")
sc=sc.replace("['FORE_MIDSHIP_STATIC_SOURCE','TRAM_EDITABLE_COMPONENT','AFT_MIDSHIP_STATIC_SOURCE','FORWARD_STATIC_SOURCE','CENTRAL_STATIC_SOURCE','AFT_STATIC_SOURCE','UNEXPORTED_REFERENCE_AND_STUDIO']","['BARRIER_RECEIVERS','RESTRAINT_HARDWARE','UNEXPORTED_REFERENCE_AND_STUDIO']")
exec(sc,globals());current=collections['BARRIER_RECEIVERS'];barrier_rows=[]
def world(s,p):
 x,y,z=p;a=s['yaw'];return (s['origin'][0]+x*math.cos(a)+z*math.sin(a),s['origin'][1]+y,s['origin'][2]-x*math.sin(a)+z*math.cos(a))
for s in P['station_mounts']:
 # Source fitting feet lie outside the 2.18m gate aperture. Mounts have positive floor embed.
 for k,z in enumerate([-1.65,1.65]):
  for suffix,c,size,mat,role in [
    ('Shoe',[-.32,-.03,z],[.30,.08,.25],metal,'source floor/standard gate-foot lap'),
    ('Cap',[-.32,.006,z],[.25,.006,.20],ivory,'profiled outer foot cap outside aperture'),
    ('Anchor',[-.32,-.035,z],[.20,.08,.16],metal,'75mm positive station slab embed')]:
   ob=box(s['station']+'_Barrier_'+suffix+'_'+str(k),world(s,c),size,mat,role)
   barrier_rows.append({'mesh':ob.name,'station':s['station'],'role':role})
 # Short shoulders meet the actual retained portal header and the original gate crown.
 for k,z in enumerate([-1.20,1.20]):
  ob=box(s['station']+'_Barrier_HeaderShoulder_'+str(k),world(s,[-.10,2.53,z]),[.26,.06,.16],metal,'5mm gate-crown embed and positive original portal-header receiving')
  barrier_rows.append({'mesh':ob.name,'station':s['station'],'role':ob['role']})
 marker(s['station']+'_STANDARD_GATE_ROOT',world(s,[-.32,0,0]),'original lift_gate adapter; yaw+PI/2 relative bridge; exact preserved2.41m header and2.18m nominal width in SAFETY_PLAN.json')
current=collections['RESTRAINT_HARDWARE'];fixed=marker('RESTRAINT_FIXED_ROOT',(0,0,0),'one existing cart only; source datum matches original car anchors')
jaw_rows=[];fixed_rows=[]
for side in [-1,1]:
 for j,z in enumerate([-.52,.77]):
  label=('PORT' if side<0 else 'STARBOARD')+'_'+str(j)
  def hardware(suffix,c,size,mat,role,parent):
   ob=box(label+'_'+suffix,(side*c[0],c[1],c[2]),size,mat,role,'root_owned_convex_candidate' if parent!=fixed else 'static_receiver_candidate')
   ob.parent=parent;ob['hardware_group']=parent.name;return ob
  for suffix,c,size,mat,role in [
   ('AnchorShoe',[.61,.010,z],[.15,.06,.10],metal,'original restraint anchor positive embed'),
   ('DrivePod',[.61,.130,z],[.14,.22,.13],ivory,'sliding jaw drive housing'),
   ('PodCrown',[.61,.245,z],[.16,.05,.15],metal,'weighted drive crown; ordinary mechanical source')]:
   o=hardware(suffix,c,size,mat,role,fixed);fixed_rows.append(o.name)
  # Explicit zero-origin group means motion is translation only, with untouched local geometry.
  root=marker('CLAMP_MOVING_'+label,(0,0,0),'open jaw; close localX'+str(-side*.139)+'m without moving or cloning cart')
  contact_z=-.35 if j==0 else .64
  for suffix,c,size,mat,role in [
   ('SliderArm',[.655,.240,z],[.29,.07,.10],metal,'drive carriage receives pod throughout stroke'),
   ('CornerFinger',[.515,.240,(z+contact_z)/2],[.05,.07,abs(z-contact_z)+.10],metal,'L-shaped outboard finger; clears caster entry when open'),
   ('ContactPad',[.515,.240,contact_z],[.05,.07,.10],rubber,'closed inner faceX±.351;1mm nominal chassis clearance')]:
   o=hardware(suffix,c,size,mat,role,root)
   jaw_rows.append({'mesh':o.name,'group':root.name,'side':side,'anchor_z':z,'target_cart_z':contact_z,'open_to_closed_translation_xyz':[-side*.139,0,0]})
for im in bpy.data.images:
 if im.source=='FILE' and im.size[0]>0:im.pack()
def export(co,file):
 bpy.ops.object.select_all(action='DESELECT')
 for o in co.objects:o.select_set(True)
 bpy.context.view_layer.objects.active=next(o for o in co.objects if o.type=='MESH')
 bpy.ops.export_scene.gltf(filepath=str(W/file),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
export(collections['BARRIER_RECEIVERS'],P['station_receiver_asset']);export(collections['RESTRAINT_HARDWARE'],P['restraint_asset'])
bpy.ops.wm.save_as_mainfile(filepath=str(W/'Group4_Barrier_Receivers_and_Restraints_r003.blend'),compress=True)
(W/'HARDWARE_INTERFACE.json').write_text(json.dumps({'schema':'astraea.group4.safety_hardware.v1','barrier_receivers':barrier_rows,'restraint_fixed_meshes':fixed_rows,'restraint_moving_meshes':jaw_rows,'source_material_pins':texture_pins,'native':'Group4_Barrier_Receivers_and_Restraints_r003.blend','barrier_asset':P['station_receiver_asset'],'restraint_asset':P['restraint_asset'],'source_only':True,'whole_group_complete':False},indent=2)+'\n')
print('HARDWARE_BUILT',len(barrier_rows),'station receiver meshes;',len(fixed_rows)+len(jaw_rows),'restraint meshes; explicit fixed/moving groups')
