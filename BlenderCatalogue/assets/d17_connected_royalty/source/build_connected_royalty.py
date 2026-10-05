"""Editable connected D17 architectural slice. Floor previews are never exported.
Run: blender -b --python assets/d17_connected_royalty/source/build_connected_royalty.py
No engine work; source dependencies remain byte-identical.
"""
from pathlib import Path
import bpy,bmesh,json,hashlib,math,subprocess
from mathutils import Vector
R=Path(__file__).resolve().parents[1];C=R.parents[1];AID='AST-RES-006'
D=json.loads((R/'source/connected_contract.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((C/'catalogue_manifest.json').read_text());assert all(a['catalogue_id']!=AID or a['family']=='d17_connected_royalty' for a in manifest['assets'])
COM=C/'assets/starboard_house_upper/source/AST-COM-003.blend';HELD=C/'assets/d17_house_platform/source/AST-RES-005.blend'
BASE=C/'assets/d17_connected_royalty/source/verified_closed_COM003.blend'
# Retained pre-portal file from the existing local Git history, not a replacement working tree.
if not BASE.exists():BASE.write_bytes(subprocess.check_output(['git','-C',str(C),'show','3655b833f99048a109e30b3f5f39146afcc5b829:assets/starboard_house_upper/source/AST-COM-003.blend']))
expected=json.loads((C/'assets/d17_house_platform/source/section_contract.json').read_text())['source_inputs']['catalogue/assets/starboard_house_upper/source/AST-COM-003.blend']
assert sha(BASE)==expected
D['preserved_inputs']={str(p.relative_to(C)):sha(p) for p in [COM,COM.parent.parent/'exports/AST-COM-003.glb',HELD,HELD.parent.parent/'exports/AST-RES-005.glb',C/'assets/starboard_house_upper/source/house_contract.json',C/'assets/d17_house_platform/source/section_contract.json']}
# Preserve all held COM objects except restore the complete fore wall and remove its split additions.
bpy.ops.wm.open_mainfile(filepath=str(COM));fore=['HC_ProfileWall_D17_-1_2','HC_Wainscot_D17_-1_2']
for n in fore:
 for suffix in ['', '_PortalRightStub','_PortalHeader']:
  ob=bpy.data.objects.get(n+suffix)
  if ob:bpy.data.objects.remove(ob,do_unlink=True)
with bpy.data.libraries.load(str(BASE),link=False) as (a,b):b.objects=fore
for ob in b.objects:
 bpy.context.collection.objects.link(ob)
 # Reuse held material identity rather than loaded duplicate data-blocks.
 for i,m in enumerate(ob.data.materials):ob.data.materials[i]=bpy.data.materials[m.name.split('.')[0]]
bpy.context.preferences.filepaths.save_version=0
comsrc=R/'source/AST-COM-003_aft_only.blend';comout=R/'exports/AST-COM-003_aft_only.glb'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(comsrc));bpy.ops.export_scene.gltf(filepath=str(comout),export_format='GLB',export_yup=True,export_extras=True)
# Source material graphs and embedded textures come from existing commons exactly.
mats={name:bpy.data.materials[name] for name in ['ivory_enamel','warm_walnut','warm_stone','champagne_metal','HouseSmokedGlass','GardenOpalLens']}
for m in mats.values():m.use_fake_user=True
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for coll in list(bpy.data.collections):
 if coll.name!='Collection' and coll.users==0:bpy.data.collections.remove(coll)
parts=[];records=[];markers=[]
def xyz(p):return(p[0],-p[2],p[1])
def mesh(name,world,faces,role,category='architecture',support=None):
 me=bpy.data.meshes.new(name);me.from_pydata([xyz(p) for p in world],[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(mats[role]);uv=me.uv_layers.new(name='MetreScaled')
 for f in me.polygons:
  n=f.normal.normalized();u=(Vector((1,0,0))-n*n.x).normalized()if abs(n.z)>.7 else Vector((-n.y,n.x,0)).normalized();v=n.cross(u).normalized();scale=mats[role].get('meters_per_tile_uv',[1,1])
  for li in f.loop_indices:
   p=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u)/scale[0],p.dot(v)/scale[1])
 ob['catalogue_id']=AID;ob['category']=category;ob['source_owner']=name
 if support:ob['support']=support
 parts.append(ob);records.append({'name':name,'material':role,'category':category,'world_vertices':world,'support':support});return ob
faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def box(name,x0,x1,y0,y1,z0,z1,role,category='architecture',support=None):return mesh(name,[[x,y,z]for y in[y0,y1]for x,z in[(x0,z0),(x1,z0),(x1,z1),(x0,z1)]],faces,role,category,support)
def prism(name,poly,lo,hi,role,category='architecture',support=None):
 n=len(poly);ff=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n)for i in range(n)]
 return mesh(name,[[x,y,z]for y in [lo,hi]for x,z in poly],ff,role,category,support)
def wall(name,a,b,lo,hi,width,role,category='architecture',support=None):
 va,vb=Vector(a),Vector(b);t=(vb-va).normalized();n=Vector((-t.y,t.x))*width/2
 return prism(name,[list(va+n),list(vb+n),list(vb-n),list(va-n)],lo,hi,role,category,support)
def datum(name,p,kind):
 ob=bpy.data.objects.new('DATUM_'+name,None);bpy.context.collection.objects.link(ob);ob.location=xyz(p);ob['kind']=kind;markers.append({'name':ob.name,'position_world':p,'kind':kind});return ob
# Minimal unchanged source subset: three accepted bearings/piers, two top transfers; no full-height bracing.
reuse=['D17_SeatedHullFooting_0','D17_SeatedHullFooting_1','D17_SeatedHullFooting_2','D17_RoyaltyPier_Fore','D17_RoyaltyPier_Aft','D17_RoyaltyPier_WestFore','D17_RoyaltyTransfer','D17_RoyaltyTransverseTransfer']
with bpy.data.libraries.load(str(HELD),link=False) as (a,b):b.objects=reuse
for ob in b.objects:
 bpy.context.collection.objects.link(ob)
 for i,m in enumerate(ob.data.materials):ob.data.materials[i]=mats[m.name.split('.')[0]]
 # Retained source identity and vertex/UV data are untouched, ownership explicit in contract.
 parts.append(ob);world=[[v.co.x,v.co.z,-v.co.y] for v in ob.data.vertices];records.append({'name':ob.name,'material':ob.data.materials[0].name,'category':'reused_proven_structure','world_vertices':world,'support':ob.get('support'),'retained_owner':'AST-RES-005/'+ob.name})
# Aft frame only. Original held paired portal kit is not copied wholesale.
for name,x0,x1 in [('Left',78.22,78.5),('Right',81.5,81.78)]:box('CR_Portal_'+name,x0,x1,102,104.82,12.75,13.65,'ivory_enamel','portal','existing D17 floor')
box('CR_Portal_Header',78.22,81.78,104.82,105.06,12.75,13.65,'ivory_enamel','portal','CR_Portal_Left + CR_Portal_Right')
for name,x0,x1 in [('Left',78.43,78.5),('Right',81.5,81.57)]:box('CR_PortalFillet_'+name,x0,x1,102.04,104.84,12.73,12.77,'champagne_metal','portal')
box('CR_PortalFillet_Header',78.43,81.57,104.82,104.89,12.73,12.77,'champagne_metal','portal')
# Exact union perimeter. No guard across the old floor seam or internal floor-owner joins.
perimeter=[[78.5,14],[81.5,14],[81.5,20],[83.7,22],[91,22],[94,23.5],[94,29],[107,29],[110,30],[115,33],[118,38],[118,42],[115,47],[110,50],[108,51],[94,51],[94,35.5],[91,35.5],[91,28],[90,28],[87.5,29],[82.5,29],[78.5,26]]
guards=[]
for i,(a,b) in enumerate(zip(perimeter,perimeter[1:]+perimeter[:1])):
 if i==0:continue
 # Source-matching guard runs, full positive glass above solid base, corners overlap safely.
 tag=f'{i:02d}';wall('CR_Fascia_'+tag,a,b,101.76,102.025,.16,'ivory_enamel','fascia')
 wall('CR_GuardBase_'+tag,a,b,102.025,102.35,.10,'warm_walnut','guard')
 wall('CR_GuardGlass_'+tag,a,b,102.35,103.01,.024,'HouseSmokedGlass','guard')
 wall('CR_GuardCap_'+tag,a,b,103.01,103.09,.12,'champagne_metal','guard')
 guards.append({'id':tag,'a_xz':a,'b_xz':b,'base_y':[102.025,102.35],'glass_y':[102.35,103.01],'cap_y':[103.01,103.09],'collision':'actual source meshes; no separate larger hidden wall','removable_future_closure':i in [16,21,22,15]})
# Compressed reveal then rising approach canopy. Front underside equals portal head.
world=[[x,y,z]for x in [78.22,81.78]for y,z in [(104.82,13.65),(105.65,20),(105.87,20),(105.04,13.65)]]
mesh('CR_ApproachRisingSoffit',world,faces,'ivory_enamel','ceiling')
# Parallel overhead edge roots intersect the unchanged commons aft perimeter transfer at Z12.
for n,x,z1 in [('West',78.42,26),('East',81.58,20.3)]:
 box('CR_ApproachRoofBeam_'+n,x-.12,x+.12,105.86,106.26,11.85,z1,'warm_walnut','structure','HC_PerimeterTransfer_106.26_1')
# Small connective ribs between the rising soffit and high rooting edge beams.
for i,z in enumerate([14,16.5,19]):
 low=104.82+(105.65-104.82)*(z-13.65)/(20-13.65)
 for n,x in [('West',78.42),('East',81.58)]:box(f'CR_ApproachRib_{i}_{n}',x-.06,x+.06,low+.13,105.9,z-.08,z+.08,'champagne_metal','structure')
court=D['floor_regions'][1]['boundary'];prism('CR_CourtCanopy',court,105.84,106.02,'ivory_enamel','ceiling')
for i,(a,b) in enumerate(zip(court,court[1:]+court[:1])):
 wall(f'CR_CourtRoofRim_{i:02d}',a,b,105.82,106.26,.30,'warm_walnut','structure')
 # Outer ivory fascia unifies the plan turn without a second bridge grid.
 wall(f'CR_CourtRoofEdge_{i:02d}',a,b,105.86,106.1,.37,'ivory_enamel','ceiling')
# Lane overhead continuation, kept inside clear width except slender edge hangers.
box('CR_LaneCanopy',91,94,105.84,106.02,27.8,35.5,'ivory_enamel','ceiling')
for x in [91,94]:box('CR_LaneRoofBeam_'+str(x),x-.12,x+.12,105.82,106.26,27.8,35.5,'warm_walnut','structure')
# Main asymmetric lower room roof. Its top is the future upper slab soffit, with no hole yet.
royal=D['floor_regions'][3]['boundary'];prism('CR_RoyaltyLowerRoof',royal,106.08,106.26,'ivory_enamel','ceiling')
for i,(a,b) in enumerate(zip(royal,royal[1:]+royal[:1])):
 wall(f'CR_RoyaltyRoofBeam_{i:02d}',a,b,105.82,106.26,.36,'warm_walnut','structure')
 wall(f'CR_RoyaltyRoofFascia_{i:02d}',a,b,105.9,106.30,.46,'ivory_enamel','ceiling')
# Proven footings root reused transfers; above-floor shoes/columns root roof ring.
for label,x,z in [('WestFore',100,29.6),('InnerFore',108,29.6),('InnerAft',108,50.4)]:
 box('CR_RoofRoot_'+label,x-.16,x+.16,101.76,106.26,z-.18,z+.18,'champagne_metal','structure','retained transfer top Y101.76')
# Roof transfers join columns to the perimeter above D16, never under its west-home soffit.
wall('CR_RoofCrossFore',(94,29.6),(108.2,29.6),105.82,106.26,.34,'warm_walnut','structure')
wall('CR_RoofCrossAft',(94,50.4),(108.2,50.4),105.82,106.26,.34,'warm_walnut','structure')
# Short perimeter hangers also read as glazed view mullions; no new supports below the slab.
hangers=[(78.5,18),(78.5,25.9),(81.5,19.9),(83.7,22),(87.5,29),(94,25.5),(91,32.8),(94,38),(94,44),(94,50.8),(107,29),(115,33),(118,38),(118,42),(115,47),(110,50)]
for i,(x,z) in enumerate(hangers):box(f'CR_EdgeHanger_{i:02d}',x-.05,x+.05,101.76,105.98,z-.05,z+.05,'champagne_metal','structure')
# A real recessed threshold: wide jamb/pocket volume stays within790, never in the lane.
for label,z0,z1 in [('Fore',29.15,30.9),('Aft',33.9,35.25)]:box('CR_PrivateJamb_'+label,96.84,97.16,102,104.82,z0,z1,'ivory_enamel','private_threshold')
box('CR_PrivateThresholdHead',96.84,97.16,104.82,105.06,29.15,35.25,'warm_walnut','private_threshold')
box('CR_PrivateBayCanopy',94,99.4,105.04,105.24,29.15,35.25,'ivory_enamel','ceiling')
# Tie lowered bay canopy to primary roof, keeping the portal and receiving zone open.
for x in [94.15,97]:
 for z in [29.25,35.15]:box('CR_BayRoofLink_%s_%s'%(x,z),x-.06,x+.06,105.20,106.12,z-.06,z+.06,'champagne_metal','structure')
wall('CR_PrivacyReturn_0',(99.2,35.5),(99.2,39.8),102,104.3,.18,'warm_walnut','privacy_screen')
wall('CR_PrivacyReturn_1',(99.2,39.8),(101.5,41.5),102,104.3,.18,'ivory_enamel','privacy_screen')
# Smaller nested bay before the main view fan, off the receiving route and future vertical reservations.
sidebay=[[103.4,29.8],[106.8,29.8],[109.7,31],[108.3,34.1],[104.3,34.1]]
prism('CR_NestedBayOverhead',sidebay,105.32,105.5,'ivory_enamel','ceiling')
for i,(a,b) in enumerate(zip(sidebay,sidebay[1:]+sidebay[:1])):wall('CR_NestedBayBand_'+str(i),a,b,105.20,105.44,.20,'warm_walnut','ceiling')
for i,(x,z)in enumerate([(104,30.4),(108.5,31.8)]):box('CR_NestedBayRoofLink_'+str(i),x-.06,x+.06,105.44,106.12,z-.06,z+.06,'champagne_metal','structure')
# View-led broad reveal follows the outward sweep, keeping the actual ship/celestial aperture unclaimed.
for i in range(3,7):
 a,b=royal[i],royal[i+1]
 wall('CR_ViewReveal_'+str(i),a,b,105.62,105.94,1.15,'ivory_enamel','view_reveal')
 wall('CR_ViewFillet_'+str(i),a,b,105.59,105.65,1.02,'champagne_metal','view_reveal')
# Visible physical light fixtures with source markers for root's established light setup.
fixtures=[('Portal',80,15.5,104.92),('Court',84.5,25.2,105.68),('Lane',92.5,30,105.68),('PrivateBay',95.5,32.4,104.88),('Receiving',101,33,105.92),('Nested',106,32,105.16),('ViewFore',113,36,105.92),('ViewAft',113,43,105.92),('CourtView',97,42,105.92)]
for label,x,z,y in fixtures:
 box('CR_LampHousing_'+label,x-.35,x+.35,y,y+.12,z-.18,z+.18,'champagne_metal','fixture')
 box('CR_LampLens_'+label,x-.30,x+.30,y-.018,y,z-.145,z+.145,'GardenOpalLens','fixture')
 # Root all housing tops into the nearest authored overhead surface.
 ceiling=105.04 if label=='PrivateBay' else 105.32 if label=='Nested' else 105.84 if label in ['Court','Lane'] else 106.08
 if label=='Portal':ceiling=104.82+(105.65-104.82)*(z-13.65)/(20-13.65)
 if ceiling>y+.12:box('CR_LampStem_'+label,x-.025,x+.025,y+.12,ceiling+.02,z-.025,z+.025,'champagne_metal','fixture')
 datum('light_'+label,[x,y-.04,z],'visible fixture light')
for name,p in [('CommonsReturn',[80,102,12]),('CourtTurn',[82,102,25]),('CourtPause',[85,102,27.5]),('LaneTurn',[92.4,102,26.5]),('PrivateArrival',[95,102,32.4]),('ReceivingTurn',[101,102,33]),('ViewStanding',[113,102,40]),('StairReservation',[96.5,102,45]),('LiftReservation',[101.5,102,46]),('ServiceReservation',[96.5,102,38])]:datum(name,p,'route or reserved interface')
# Editable desired floors are wire previews only, deliberately omitted from runtime exports.
preview=[]
for f in D['floor_regions']:
 o=prism('PREVIEW_ONLY_'+f['id'],f['boundary'],101.76,102,'warm_stone','floor_preview');o.hide_render=True;o.display_type='WIRE';o['runtime_export']=False;preview.append(o)
D['perimeter_xz']=perimeter;D['guards']=guards;D['fixtures']=[m for m in markers if m['kind']=='visible fixture light'];D['markers']=markers
D['source_parts']=records;D['reused_retained_parts']=reuse;D['new_full_height_braces']=0;D['exported_walkable_floor_meshes']=0
D['support_strategy']='Minimal exact retained three-pier/two-transfer source subset, commons-rooted narrow canopy, connected above-floor roof/perimeter system and short edge hangers. No west-strip deep beams, pits or X84/Z24 pier. Positive geometric joints only, not engineering certification.'
D['contact_roots']=[{'part':'CR_ApproachRoofBeam_West','existing':'HC_PerimeterTransfer_106.26_1','witness_world':[78.42,106.02,12]},{'part':'CR_ApproachRoofBeam_East','existing':'HC_PerimeterTransfer_106.26_1','witness_world':[81.58,106.02,12]}]
D['status']='BUILT_SOURCE_QA_PENDING_ROOT_RUNTIME_ADOPTION';(R/'source/connected_contract.json').write_text(json.dumps(D,indent=2)+'\n')
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1;bpy.ops.file.pack_all()
src=R/'source/AST-RES-006.blend';out=R/'exports/AST-RES-006.glb';bpy.ops.wm.save_as_mainfile(filepath=str(src))
# Selected geometry batches by material and bounded spatial zone, identities retained in source contract.
parts=[ob for ob in parts if ob not in preview]
for ob in preview:bpy.data.objects.remove(ob,do_unlink=True)
groups={}
for ob in parts:
 if ob.name.startswith('PREVIEW_ONLY_'):continue
 vs=[ob.matrix_world@v.co for v in ob.data.vertices];centre=sum(vs,Vector())/len(vs);x,z=centre.x,-centre.y
 zone='support' if min(v.z for v in vs)<101 else 'approach' if z<21 else 'court' if z<29 else 'lane_private' if x<100 else 'royalty'
 # Preserve all reused object names as individual independent batches for exact ownership and census.
 key=(ob.name if ob.name in reuse else zone,ob.data.materials[0].name);groups.setdefault(key,[]).append(ob)
for key,obs in sorted(groups.items()):
 bpy.ops.object.select_all(action='DESELECT')
 for ob in obs:ob.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();obs[0].name='CR_Batch_'+'_'.join(key)
bpy.ops.export_scene.gltf(filepath=str(out),export_format='GLB',export_yup=True,export_extras=True)
M={'catalogue_id':AID,'family':'d17_connected_royalty','name':'Connected aft commons court and Royalty790 lower platform architecture','source':'source/AST-RES-006.blend','export':'exports/AST-RES-006.glb','source_sha256':sha(src),'export_sha256':sha(out),'editable_mesh_count':len(records),'floor_preview_meshes':len(preview),'runtime_mesh_batches':len(groups),'runtime_slab_owner':'Existing floor compiler only','status':'Source authored; QA and root-coordinated runtime acceptance pending','variant_dependencies':[{'catalogue_id':'AST-COM-003','variant':'aft_only','source':'source/AST-COM-003_aft_only.blend','export':'exports/AST-COM-003_aft_only.glb','source_sha256':sha(comsrc),'export_sha256':sha(comout),'original_held_source_preserved':True}],'new_units':0,'new_berths':0}
(R/'AST-RES-006.manifest.json').write_text(json.dumps(M,indent=2)+'\n');print(json.dumps(M,indent=2))
